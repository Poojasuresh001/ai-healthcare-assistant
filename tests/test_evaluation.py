"""Evaluation metrics remain testable without Gemini API calls."""

import unittest

from app.evaluation.metrics import evaluate_response, summarize_evaluation


class EvaluationMetricTests(unittest.TestCase):
    def test_source_routing_hit_and_citation_score(self) -> None:
        result = evaluate_response(
            expected_source_type=["document", "database"],
            expected_source_contains="Group Renewal Guide",
            response={
                "answer": "The case remains on hold [D1] [S1].",
                "source_type": ["document", "database"],
                "sources": [
                    {"id": "D1", "title": "Group Renewal Guide"},
                    {"id": "S1", "title": "Synthetic renewal record for ABC123"},
                ],
            },
        )

        self.assertTrue(result["pass"])
        self.assertEqual(
            summarize_evaluation([result]),
            {
                "case_count": 1,
                "source_hit_rate": 1.0,
                "routing_accuracy": 1.0,
                "citation_rate": 1.0,
                "pass_rate": 1.0,
            },
        )

    def test_wrong_source_type_fails_routing_accuracy(self) -> None:
        result = evaluate_response(
            expected_source_type=["database"],
            expected_source_contains="Synthetic claims",
            response={
                "answer": "No synthetic record was found.",
                "source_type": ["document"],
                "sources": [],
            },
        )

        self.assertFalse(result["pass"])
        self.assertFalse(result["routing_correct"])


if __name__ == "__main__":
    unittest.main()
