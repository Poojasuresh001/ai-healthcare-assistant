"""Read-only synthetic database and tool tests; no external services are used."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.database.service import HealthcareDatabase
from app.config import PROJECT_ROOT
from app.tools.database_tools import build_database_tools


class HealthcareDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory(dir=PROJECT_ROOT)
        self.database = HealthcareDatabase(Path(self.temp_dir.name) / "sample.sqlite3")
        self.tools = build_database_tools(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_group_plan_and_renewal_records_are_available(self) -> None:
        group = self.tools["lookup_group"].invoke({"group_id": "ABC123"})
        renewal = self.tools["lookup_group_renewal"].invoke({"group_id": "ABC123"})

        self.assertTrue(group["found"])
        self.assertEqual(group["group"]["group_id"], "ABC123")
        self.assertEqual(group["plans"][0]["effective_date"], "2026-01-01")
        self.assertEqual(renewal["renewal"]["status"], "NEEDS_RECONCILIATION")

    def test_member_claims_include_provider_and_recorded_status(self) -> None:
        result = self.tools["lookup_member_claims"].invoke({"member_id": "M1001"})

        self.assertTrue(result["found"])
        self.assertEqual(len(result["claims"]), 2)
        self.assertEqual(result["claims"][0]["provider_id"], "P1002")
        self.assertEqual(result["claims"][0]["status"], "DENIED")

    def test_tools_reject_malformed_identifiers_before_querying(self) -> None:
        result = self.tools["lookup_group"].invoke({"group_id": "ABC123' OR 1=1 --"})

        self.assertFalse(result["found"])
        self.assertIn("fictional group ID", result["message"])


if __name__ == "__main__":
    unittest.main()
