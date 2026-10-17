"""Deterministic source and entity routing for synthetic questions."""

import re


GROUP_PATTERN = re.compile(r"\b[A-Z]{3}\d{3}\b", re.IGNORECASE)
MEMBER_PATTERN = re.compile(r"\bM\d{4}\b", re.IGNORECASE)
PROVIDER_PATTERN = re.compile(r"\bP\d{4}\b", re.IGNORECASE)

DOCUMENT_CUES = (
    "policy",
    "according to",
    "procedure",
    "process",
    "guide",
    "sop",
    "required documents",
    "documents are required",
    "what documents",
    "effective-date mismatch",
    "effective date does not match",
)

DATABASE_CUES = (
    "claim",
    "member record",
    "provider record",
    "plan effective date",
    "renewal status",
    "renewal reason",
    "group status",
)


def classify_sources(question: str) -> list[str]:
    """Select document, database, or both using visible intent and fake IDs."""
    normalized = question.casefold()
    has_identifier = any(
        pattern.search(question)
        for pattern in (GROUP_PATTERN, MEMBER_PATTERN, PROVIDER_PATTERN)
    )
    wants_database = has_identifier or any(cue in normalized for cue in DATABASE_CUES)
    wants_documents = any(cue in normalized for cue in DOCUMENT_CUES)

    if wants_database and wants_documents:
        return ["document", "database"]
    if wants_database:
        return ["database"]
    return ["document"]


def extract_identifiers(question: str) -> dict[str, str | None]:
    """Return only well-formed synthetic IDs; never interpret arbitrary SQL text."""
    group = GROUP_PATTERN.search(question)
    member = MEMBER_PATTERN.search(question)
    provider = PROVIDER_PATTERN.search(question)
    return {
        "group_id": group.group(0).upper() if group else None,
        "member_id": member.group(0).upper() if member else None,
        "provider_id": provider.group(0).upper() if provider else None,
    }
