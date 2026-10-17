"""Create the SQLite database and load its fictional seed records."""

from app.config import DATABASE_PATH
from app.database.service import HealthcareDatabase


def main() -> int:
    database = HealthcareDatabase()
    group = database.get_group("ABC123")
    if not group["found"]:
        raise RuntimeError("The sample SQL seed did not create group ABC123.")
    print("Synthetic SQLite database is ready.")
    print(f"Database file: {DATABASE_PATH.resolve()}")
    print("Sample group: ABC123")
    print("Seed tables: groups, plans, members, claims, renewals, providers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
