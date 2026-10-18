"""Regression tests for wording review and conservative evidence aggregation."""
import copy
import json
from pathlib import Path
import unittest

from agrupacion import compile_review, fingerprint


def fixture():
    def question(qid, values, ambiguous=()):
        return {
            "id": qid, "category": "tema", "statement": qid,
            "positions": {
                party: {"proposedValue": val, "evidence": [{"proposalId": qid}] if val is not None or party in ambiguous else []}
                for party, val in values.items()
            },
        }
    bank = {
        "version": "test", "scope": {"analyzedParties": ["a", "b"]},
        "categories": [{"id": "tema", "title": "Tema"}],
        "questions": [question("q1", {"a": 2, "b": None}), question("q2", {"a": 2, "b": -2}), question("q3", {"a": None, "b": 2})],
    }
    review = {
        "schemaVersion": 1, "version": "test", "reviewedAt": "2026-10-18",
        "status": "proposed-wording-review", "liveEligible": False,
        "bankVersion": "test", "bankFingerprint": fingerprint(bank),
        "scope": {"questionCount": 3, "candidatePairsReviewed": 1},
        "selectionDesign": {"status": "proposal-only", "implemented": False, "targetLength": None, "categoryQuotas": None},
        "reviews": [{"id": "r1", "questionIds": ["q1", "q2"], "relation": "equivalent", "rationale": "Misma decisión."}],
    }
    return bank, review


class GroupingReviewTests(unittest.TestCase):
    def test_one_equivalent_decision_does_not_gain_weight_from_repeated_evidence(self):
        bank, review = fixture()
        before = copy.deepcopy(bank)
        result = compile_review(bank, review)
        self.assertEqual(bank, before)
        self.assertEqual(result["counts"]["proposedUnits"], 2)
        self.assertEqual(result["counts"]["potentialReduction"], 1)
        group = result["equivalentGroups"][0]
        self.assertEqual(group["positions"]["a"]["candidateValue"], 2)
        self.assertEqual(group["positions"]["b"]["candidateValue"], -2)
        self.assertEqual(len(group["positions"]["a"]["sourceQuestionIds"]), 2)
        self.assertFalse(group["liveEligible"])

    def test_conflicting_positions_are_not_resolved_by_majority(self):
        bank, review = fixture()
        bank["questions"][1]["positions"]["a"]["proposedValue"] = -2
        review["bankFingerprint"] = fingerprint(bank)
        group = compile_review(bank, review)["equivalentGroups"][0]
        self.assertIsNone(group["positions"]["a"]["candidateValue"])
        self.assertEqual(group["positions"]["a"]["status"], "conflicting-draft")

    def test_ambiguous_evidence_blocks_a_candidate_instead_of_becoming_zero(self):
        bank, review = fixture()
        bank["questions"][1]["positions"]["a"]["proposedValue"] = None
        review["bankFingerprint"] = fingerprint(bank)
        group = compile_review(bank, review)["equivalentGroups"][0]
        self.assertIsNone(group["positions"]["a"]["candidateValue"])
        self.assertEqual(group["positions"]["a"]["status"], "ambiguous-draft")

    def test_related_and_contrasting_questions_are_not_merged_or_inverted(self):
        for relation in ["related", "contrasting", "distinct"]:
            bank, review = fixture()
            review["reviews"][0]["relation"] = relation
            result = compile_review(bank, review)
            self.assertEqual(result["counts"]["proposedUnits"], 3)
            self.assertEqual(result["counts"]["potentialReduction"], 0)

    def test_transitive_merge_cannot_erase_a_recorded_difference(self):
        bank, review = fixture()
        review["reviews"] += [
            {"id": "r2", "questionIds": ["q2", "q3"], "relation": "equivalent", "rationale": "Misma decisión."},
            {"id": "r3", "questionIds": ["q1", "q3"], "relation": "related", "rationale": "Hay una condición diferente."},
        ]
        review["scope"]["candidatePairsReviewed"] = 3
        with self.assertRaisesRegex(AssertionError, "transitividad"):
            compile_review(bank, review)

    def test_editing_the_bank_invalidates_its_old_review(self):
        bank, review = fixture()
        bank["questions"][0]["statement"] = "Condición modificada."
        with self.assertRaisesRegex(AssertionError, "edición actual"):
            compile_review(bank, review)

    def test_unreviewed_pairs_do_not_collapse_through_an_equivalent_bridge(self):
        bank, review = fixture()
        review["reviews"].append({"id": "r2", "questionIds": ["q2", "q3"], "relation": "equivalent", "rationale": "Misma decisión."})
        review["scope"]["candidatePairsReviewed"] = 2
        with self.assertRaisesRegex(AssertionError, "cada par"):
            compile_review(bank, review)

    def test_duplicate_pairs_and_missing_questions_are_rejected(self):
        bank, review = fixture()
        review["reviews"].append({**review["reviews"][0], "id": "r2", "questionIds": ["q2", "q1"]})
        review["scope"]["candidatePairsReviewed"] = 2
        with self.assertRaisesRegex(AssertionError, "Par repetido"):
            compile_review(bank, review)
        bank, review = fixture()
        review["reviews"][0]["questionIds"][0] = "missing"
        with self.assertRaises(AssertionError):
            compile_review(bank, review)

    def test_group_identity_and_totals_do_not_depend_on_bank_order(self):
        bank, review = fixture()
        first = compile_review(bank, review)
        bank["questions"].reverse()
        review["bankFingerprint"] = fingerprint(bank)
        second = compile_review(bank, review)
        self.assertEqual(first["counts"], second["counts"])
        self.assertEqual(first["equivalentGroups"], second["equivalentGroups"])

    def test_live_sampling_is_not_enabled_by_the_research(self):
        bank, review = fixture()
        review["selectionDesign"]["implemented"] = True
        with self.assertRaises(AssertionError):
            compile_review(bank, review)

    def test_a_selection_family_keeps_variants_distinct_and_includes_their_aliases(self):
        bank, review = fixture()
        review["selectionFamilies"] = [{"id": "family", "title": "Variante", "questionIds": ["q1", "q3"], "status": "proposal-only", "maxPerShortSessionProposed": 1, "rationale": "Distinto alcance, mismo debate."}]
        result = compile_review(bank, review)
        family = result["selectionFamilies"][0]
        self.assertEqual(family["expandedQuestionIds"], ["q1", "q2", "q3"])
        self.assertEqual(len(family["proposedUnitIds"]), 2)
        self.assertNotIn("positions", family)
        self.assertEqual(result["counts"]["proposedUnits"], 2)
        self.assertFalse(family["liveEligible"])

    def test_aliases_cannot_hide_overlapping_selection_families(self):
        bank, review = fixture()
        first = {"id": "family1", "title": "Variante", "questionIds": ["q1", "q3"], "status": "proposal-only", "maxPerShortSessionProposed": 1, "rationale": "Distinto alcance, mismo debate."}
        review["selectionFamilies"] = [first, {**first, "id": "family2", "questionIds": ["q2", "q3"]}]
        with self.assertRaisesRegex(AssertionError, "solapadas"):
            compile_review(bank, review)

    def test_real_review_preserves_the_important_threshold_and_instrument_differences(self):
        folder = Path(__file__).resolve().parents[1]
        bank = json.loads((folder / "analisis.json").read_text(encoding="utf-8"))
        review = json.loads((folder / "agrupacion.json").read_text(encoding="utf-8"))
        result = compile_review(bank, review)
        pairs = {frozenset(r["questionIds"]): r["relation"] for r in review["reviews"]}
        for a, b in [
            ("q-eh-bildu23-g0002-04", "q-bng23-g0008-01"),
            ("q-pp23-146-a", "q-psoe23-g0623-a"),
            ("q-pp23-114-a", "q-vox23-g0245-b"),
            ("q-pp23-286-a", "q-vox23-g0064-b"),
            ("q-erc23-g0040-05", "q-pacma23-g0020-01"),
        ]:
            self.assertEqual(pairs[frozenset((a, b))], "related")
        self.assertEqual(result["counts"]["bankQuestions"], 3673)
        self.assertEqual(result["counts"]["reviewedPairs"], 189)
        self.assertEqual(result["counts"]["approvedForProduction"], 0)
        self.assertEqual(result["counts"]["commonToAllParties"], 0)
        self.assertEqual(result["counts"]["proposedSelectionFamilies"], 12)


if __name__ == "__main__":
    unittest.main()
