"""Guards for decisions whose source scope must not be inferred from ideology."""
import json
from pathlib import Path
import unittest


class ProgrammeScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((Path(__file__).resolve().parents[1] / "analisis.json").read_text(encoding="utf-8"))
        cls.questions = {q["id"]: q for q in cls.bank["questions"]}

    def test_referendum_is_not_a_documented_vote_to_leave_nato(self):
        q = self.questions["q-bng23-g0042-05"]
        self.assertEqual(q["positions"]["registro-6040"]["proposedValue"], 2)
        position = q["positions"]["registro-7400"]
        self.assertIsNone(position["proposedValue"])
        self.assertEqual(position["status"], "undetermined")
        self.assertTrue(position["evidence"])

    def test_pcte_eu_and_euro_exit_retain_political_condition(self):
        proposals = [p for p in self.bank["proposals"] if p["party"] == "registro-6040" and p["concept"] == "Salida de UE y euro condicionada"]
        self.assertEqual(len(proposals), 1)
        for qid in proposals[0]["questionIds"]:
            self.assertIn("implantación del poder obrero", self.questions[qid]["statement"])
        self.assertEqual(proposals[0]["source"]["pdfPages"], [19])

    def test_salf_is_territorial_and_covers_its_actual_document(self):
        sources = {s["id"]: s for s in self.bank["sources"]}
        found = []
        for q in self.questions.values():
            position = q["positions"]["registro-7458"]
            if not position["evidence"]:
                continue
            found.append(q)
            self.assertEqual(q["territorialScope"]["territory"], "Castilla y León")
            for evidence in position["evidence"]:
                self.assertEqual(sources[evidence["documentId"]]["kind"], "territorial")
        self.assertGreater(len(found), 100)
        for party, pages in [("registro-6040", 24), ("registro-7400", 28), ("registro-7458", 22)]:
            units = [u for u in self.bank["sourceUnits"] if u["party"] == party]
            self.assertEqual(sorted(u["number"] for u in units), list(range(1, pages + 1)))


if __name__ == "__main__":
    unittest.main()
