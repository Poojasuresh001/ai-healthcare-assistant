"""Deterministic source selection and synthetic ID extraction tests."""

import unittest

from app.agents.routing import classify_sources, extract_identifiers


class RoutingTests(unittest.TestCase):
    def test_document_only_questions_route_to_rag(self) -> None:
        self.assertEqual(
            classify_sources("What is the renewal process for an existing group?"),
            ["document"],
        )
        self.assertEqual(
            classify_sources("According to the policy, what happens on a date mismatch?"),
            ["document"],
        )

    def test_structured_questions_route_to_database(self) -> None:
        self.assertEqual(
            classify_sources("Show claims for member M1001."),
            ["database"],
        )
        self.assertEqual(
            classify_sources("What is the plan effective date for group ABC123?"),
            ["database"],
        )

    def test_questions_that_name_policy_and_record_route_to_both(self) -> None:
        self.assertEqual(
            classify_sources("According to the renewal policy, why is group ABC123 on hold?"),
            ["document", "database"],
        )

    def test_identifier_extraction_only_returns_synthetic_id_shapes(self) -> None:
        self.assertEqual(
            extract_identifiers("Check ABC123 and M1001 with provider P1001"),
            {"group_id": "ABC123", "member_id": "M1001", "provider_id": "P1001"},
        )
        self.assertEqual(
            extract_identifiers("Check ABC123 OR 1=1"),
            {"group_id": "ABC123", "member_id": None, "provider_id": None},
        )


if __name__ == "__main__":
    unittest.main()
