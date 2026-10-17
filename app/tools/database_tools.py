"""Allowlisted LangChain tools for reading fabricated database records."""

import re

from langchain_core.tools import tool

from app.database.service import HealthcareDatabase


GROUP_ID_PATTERN = re.compile(r"^[A-Z]{3}\d{3}$")
MEMBER_ID_PATTERN = re.compile(r"^M\d{4}$")
PROVIDER_ID_PATTERN = re.compile(r"^P\d{4}$")


def build_database_tools(database: HealthcareDatabase) -> dict:
    """Bind read-only SQL tools to a database service; no arbitrary SQL is accepted."""

    @tool("lookup_group")
    def lookup_group(group_id: str) -> dict:
        """Read one synthetic group and its plan records by group ID, such as ABC123."""
        if not GROUP_ID_PATTERN.fullmatch(group_id):
            return {"found": False, "message": "Use a fictional group ID such as ABC123."}
        return database.get_group(group_id)

    @tool("lookup_group_renewal")
    def lookup_group_renewal(group_id: str) -> dict:
        """Read the latest synthetic renewal status and reason for a group ID."""
        if not GROUP_ID_PATTERN.fullmatch(group_id):
            return {"found": False, "message": "Use a fictional group ID such as ABC123."}
        return database.get_group_renewal(group_id)

    @tool("lookup_member_claims")
    def lookup_member_claims(member_id: str) -> dict:
        """Read synthetic claims already recorded for a member ID, such as M1001."""
        if not MEMBER_ID_PATTERN.fullmatch(member_id):
            return {"found": False, "message": "Use a fictional member ID such as M1001."}
        return database.get_member_claims(member_id)

    @tool("lookup_provider")
    def lookup_provider(provider_id: str) -> dict:
        """Read one synthetic provider record by provider ID, such as P1001."""
        if not PROVIDER_ID_PATTERN.fullmatch(provider_id):
            return {"found": False, "message": "Use a fictional provider ID such as P1001."}
        return database.get_provider(provider_id)

    return {
        "lookup_group": lookup_group,
        "lookup_group_renewal": lookup_group_renewal,
        "lookup_member_claims": lookup_member_claims,
        "lookup_provider": lookup_provider,
    }
