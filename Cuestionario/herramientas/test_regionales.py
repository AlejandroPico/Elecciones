"""Semantic guards for regional sources and internally conflicting commitments."""
import json
from pathlib import Path
import unittest


class RegionalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((Path(__file__).resolve().parents[1] / "analisis.json").read_text(encoding="utf8"))

    def matching(self, party, fragment):
        return [q for q in self.bank["questions"] if fragment.casefold() in q["statement"].casefold() and q["positions"][party]["evidence"]]

    def test_different_3030_units_are_not_merged(self):
        soria = self.matching("registro-6972", "treinta minutos")
        teruel = self.matching("registro-6779", "treinta kilómetros")
        self.assertTrue(soria)
        self.assertTrue(teruel)
        self.assertFalse({q["id"] for q in soria} & {q["id"] for q in teruel})

    def test_ambiguous_retirement_ages_remain_unscored(self):
        for age in (62, 64):
            questions = self.matching("registro-6620", f"{age} años")
            self.assertTrue(questions)
            for q in questions:
                p = q["positions"]["registro-6620"]
                self.assertIsNone(p["proposedValue"])
                self.assertEqual(p["status"], "undetermined")
                self.assertTrue(any(8 in e["pdfPages"] and 29 in e["pdfPages"] for e in p["evidence"]))

    def test_drago_has_no_unscoped_attribution(self):
        linked = [q for q in self.bank["questions"] if q["positions"]["registro-7039"]["evidence"]]
        self.assertGreater(len(linked), 100)
        for q in linked:
            self.assertEqual(q["territorialScope"], {"kind": "autonomous", "territory": "Canarias", "sourceElection": "2023-05-28"})

    def test_numbered_sources_keep_all_official_numbers(self):
        for party, count in [("registro-6972", 73), ("cc", 52)]:
            units = [u for u in self.bank["sourceUnits"] if u["party"] == party and u["kind"] == "official-number"]
            self.assertEqual(sorted(u["number"] for u in units), list(range(1, count + 1)))

    def test_d21_preserves_government_exception_and_budget_presentation(self):
        questions = self.matching("coalicion-d21-2026", "aforamiento")
        self.assertTrue(questions)
        self.assertTrue(any("Gobierno" in q["statement"] for q in questions))
        budgets = self.matching("coalicion-d21-2026", "presupuestos")
        self.assertTrue(budgets)
        self.assertTrue(any("presentar" in q["statement"] for q in budgets))
        self.assertFalse(any("aprobar" in q["statement"] for q in budgets))
        sources = [s for s in self.bank["sources"] if s["organization"] == "coalicion-d21-2026"]
        self.assertEqual({s["format"] for s in sources}, {"PDF", "TXT"})
        self.assertFalse(any(s["organization"] == "registro-7631" for s in self.bank["sources"]))

    def test_contextual_manifesto_does_not_generate_sectoral_positions(self):
        proposals = [p for p in self.bank["proposals"] if p["source"]["documentId"] == "coalicion-d21-2026-manifiesto"]
        self.assertTrue(proposals)
        self.assertTrue(all(not p["questionIds"] and p["coverage"] == "context-only" for p in proposals))


if __name__ == "__main__":
    unittest.main()
