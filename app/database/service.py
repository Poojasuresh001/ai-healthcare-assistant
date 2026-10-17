"""Read-only access to the project's synthetic SQLite database."""

from pathlib import Path
from contextlib import closing
import sqlite3

from app.config import DATABASE_PATH, PROJECT_ROOT


SCHEMA_AND_SEED = PROJECT_ROOT / "scripts" / "create_synthetic_db.sql"


class HealthcareDatabase:
    """Initialize the synthetic database and expose fixed, parameterized reads."""

    def __init__(self, database_path: Path = DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        if str(self.database_path) != ":memory:":
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Create the tables and insert the fictional sample rows if missing."""
        script = SCHEMA_AND_SEED.read_text(encoding="utf-8")
        with closing(self._connect()) as connection:
            connection.executescript(script)
            connection.commit()

    def get_group(self, group_id: str) -> dict:
        with closing(self._connect()) as connection:
            group = connection.execute(
                """SELECT group_id, group_name, status, industry, state_code
                   FROM groups WHERE group_id = :group_id""",
                {"group_id": group_id},
            ).fetchone()
            if group is None:
                return {"found": False, "message": "No synthetic group record matched that ID."}
            plans = connection.execute(
                """SELECT plan_id, plan_name, plan_type, effective_date,
                          termination_date, network_label, status
                   FROM plans WHERE group_id = :group_id ORDER BY effective_date""",
                {"group_id": group_id},
            ).fetchall()
        return {
            "found": True,
            "group": dict(group),
            "plans": [dict(plan) for plan in plans],
        }

    def get_group_renewal(self, group_id: str) -> dict:
        with closing(self._connect()) as connection:
            renewal = connection.execute(
                """SELECT r.renewal_id, r.group_id, g.group_name, r.status,
                          r.requested_effective_date, r.signed_effective_date,
                          r.reason, r.open_items, r.updated_date
                   FROM renewals AS r
                   JOIN groups AS g ON g.group_id = r.group_id
                   WHERE r.group_id = :group_id
                   ORDER BY r.updated_date DESC LIMIT 1""",
                {"group_id": group_id},
            ).fetchone()
        if renewal is None:
            return {"found": False, "message": "No synthetic renewal record matched that group ID."}
        record = dict(renewal)
        record["open_items"] = [item for item in record["open_items"].split("|") if item]
        return {"found": True, "renewal": record}

    def get_member_claims(self, member_id: str) -> dict:
        with closing(self._connect()) as connection:
            member = connection.execute(
                """SELECT member_id, group_id, plan_id, coverage_start, coverage_end, status
                   FROM members WHERE member_id = :member_id""",
                {"member_id": member_id},
            ).fetchone()
            if member is None:
                return {"found": False, "message": "No synthetic member record matched that ID."}
            claims = connection.execute(
                """SELECT c.claim_id, c.service_date, c.received_date, c.processed_date,
                          c.status, c.billed_amount, c.allowed_amount, c.paid_amount,
                          c.explanation_code, c.explanation, p.provider_id, p.provider_name
                   FROM claims AS c
                   JOIN providers AS p ON p.provider_id = c.provider_id
                   WHERE c.member_id = :member_id
                   ORDER BY c.service_date DESC""",
                {"member_id": member_id},
            ).fetchall()
        return {
            "found": True,
            "member": dict(member),
            "claims": [dict(claim) for claim in claims],
        }

    def get_provider(self, provider_id: str) -> dict:
        with closing(self._connect()) as connection:
            provider = connection.execute(
                """SELECT provider_id, provider_name, provider_type, network_label,
                          state_code, status
                   FROM providers WHERE provider_id = :provider_id""",
                {"provider_id": provider_id},
            ).fetchone()
        if provider is None:
            return {"found": False, "message": "No synthetic provider record matched that ID."}
        return {"found": True, "provider": dict(provider)}
