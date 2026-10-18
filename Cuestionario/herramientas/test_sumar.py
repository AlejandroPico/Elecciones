"""Preserve the edition, identity and conditional decisions of Sumar's 2023 source."""
import json
from pathlib import Path
import unittest


PARTY = "sumar-coalicion-2023"


class SumarProgrammeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((Path(__file__).resolve().parents[1] / "analisis.json").read_text(encoding="utf8"))
        cls.questions = {q["id"]: q for q in cls.bank["questions"]}

    def matching(self, fragment):
        return [q for q in self.bank["questions"] if fragment.casefold() in q["statement"].casefold() and q["positions"][PARTY]["evidence"]]

    def test_historical_coalition_keeps_its_source_and_page_anchors(self):
        s = next(s for s in self.bank["sources"] if s["organization"] == PARTY)
        self.assertEqual(s["electionDate"], "2023-07-23")
        self.assertEqual(s["kind"], "historical")
        self.assertEqual(s["pages"], 182)
        self.assertFalse(s["scoringEligible"])
        self.assertEqual(s["referencedBy"], ["sumar"])
        self.assertEqual(s["sha256"], "d5ccdac0d20f1b93a5f703f180d086041bd988835072dd5cb5d1378bf0195820")
        units = [u for u in self.bank["sourceUnits"] if u["party"] == PARTY]
        self.assertEqual([u["number"] for u in units], list(range(1, 183)))
        self.assertNotIn("sumar", self.bank["scope"]["analyzedParties"])
        self.assertNotIn("coalicion-frente-amplio-2026", self.bank["scope"]["analyzedParties"])

    def test_two_incompatible_mortgage_horizons_are_unscored(self):
        for horizon in ["dos años anteriores", "diez años anteriores"]:
            questions = self.matching(horizon)
            self.assertTrue(questions)
            for q in questions:
                p = q["positions"][PARTY]
                self.assertIsNone(p["proposedValue"])
                self.assertEqual(p["status"], "undetermined")
                self.assertTrue(any(8 in e["pdfPages"] and 77 in e["pdfPages"] for e in p["evidence"]))

    def test_dialogue_towards_32_hours_is_not_immediate_implementation(self):
        self.assertIsNone(self.questions["q-eh-bildu23-g0002-04"]["positions"][PARTY]["proposedValue"])
        dialogue = self.matching("diálogo social para avanzar hacia una jornada de 32")
        self.assertEqual(len(dialogue), 1)
        self.assertEqual(dialogue[0]["positions"][PARTY]["proposedValue"], 2)
        self.assertTrue(self.matching("37,5 horas"))

    def test_territorial_pact_does_not_prove_independence(self):
        self.assertIsNone(self.questions["q-junts23-g0005-01"]["positions"][PARTY]["proposedValue"])
        pact = self.matching("acuerdo territorial negociado")
        self.assertEqual(len(pact), 1)
        self.assertTrue(any(122 in e["pdfPages"] for e in pact[0]["positions"][PARTY]["evidence"]))

    def test_european_security_shift_is_not_explicit_nato_exit(self):
        self.assertIsNone(self.questions["q-bng23-g0042-05"]["positions"][PARTY]["proposedValue"])
        shift = self.matching("desplazarse progresivamente")
        self.assertTrue(shift)
        self.assertTrue(all(q["positions"][PARTY]["proposedValue"] == 2 for q in shift))

    def test_study_is_not_a_final_decision(self):
        study = self.matching("circunscripción electoral exterior")
        self.assertTrue(study)
        self.assertTrue(all(q["positions"][PARTY]["proposedValue"] is None for q in study))

    def test_parliamentary_selection_is_not_direct_election_by_judges(self):
        self.assertEqual(self.questions["q-pp23-237-a"]["positions"][PARTY]["proposedValue"], -2)
        self.assertIsNone(self.questions["q-coalicion-d21-2026-r26-g0012-01"]["positions"][PARTY]["proposedValue"])

    def test_privileged_rates_do_not_mean_abolishing_every_socially_conditioned_incentive(self):
        questions = self.matching("Las SICAV y las SOCIMI")
        self.assertEqual(len(questions), 1)
        self.assertIn("1 %", questions[0]["statement"])
        self.assertIn("0 %", questions[0]["statement"])
        self.assertNotIn("todos los beneficios", questions[0]["statement"])
        proposal = next(p for p in self.bank["proposals"] if questions[0]["id"] in p["questionIds"] and p["party"] == PARTY)
        self.assertIn("valor social", proposal["editorialNotes"])


if __name__ == "__main__":
    unittest.main()
