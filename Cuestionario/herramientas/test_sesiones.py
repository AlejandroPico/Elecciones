"""Protect the research-to-runtime migration, especially uncertain positions and scope."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RuntimeBank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = json.loads((ROOT / "analisis.json").read_text(encoding="utf-8"))
        cls.runtime = json.loads((ROOT / "sesiones-banco.json").read_text(encoding="utf-8"))

    def test_no_questions_or_scopes_are_lost(self):
        original = {q["id"]: q for q in self.canonical["questions"]}
        actual = {q["id"]: q for q in self.runtime["questions"]}
        self.assertEqual(set(original), set(actual))
        self.assertEqual(len(actual), 5861)
        for qid, q in actual.items():
            self.assertEqual(q["text"], original[qid]["statement"])
            self.assertEqual(q["category"], original[qid]["category"])
            self.assertEqual(q["scope"], original[qid].get("territorialScope"))

    def test_runtime_does_not_resolve_ambiguity_or_transfer_positions(self):
        original = {q["id"]: q for q in self.canonical["questions"]}
        for q in self.runtime["questions"]:
            for party, pos in q["positions"].items():
                source = original[q["id"]]["positions"][party]
                self.assertEqual(pos["value"], source["proposedValue"])
                self.assertEqual(pos["basis"], source["basis"])
                self.assertEqual([e["proposalId"] for e in pos["evidence"]], [e["proposalId"] for e in source["evidence"]])
            for party, pos in original[q["id"]]["positions"].items():
                if party not in q["positions"]:
                    self.assertIsNone(pos["proposedValue"])
                    self.assertFalse(pos["evidence"])

    def test_all_topics_have_ten_decisions_and_all_originals_are_local(self):
        self.assertEqual(len(self.runtime["categories"]), 40)
        for c in self.runtime["categories"]:
            pool = {q["selectionKey"] for q in self.runtime["questions"] if q["category"] == c["id"]}
            self.assertGreaterEqual(len(pool), 10)
        for source in self.runtime["sources"]:
            self.assertTrue((ROOT.parent / source["file"]).is_file(), source["id"])


if __name__ == "__main__":
    unittest.main()
