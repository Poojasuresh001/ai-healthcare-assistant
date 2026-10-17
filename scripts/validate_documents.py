"""Validate that the Phase 2 synthetic reference documents are present."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
REQUIRED_DOCUMENTS = (
    "Group_Renewal_Guide.md",
    "Plan_Setup_Guide.md",
    "Claims_Process_Guide.md",
    "Member_FAQ.md",
    "ETL_Process_Documentation.md",
)
SYNTHETIC_NOTICE = "Synthetic training material"


def main() -> int:
    """Check each expected document has metadata and the synthetic-data notice."""
    errors: list[str] = []

    for filename in REQUIRED_DOCUMENTS:
        path = DOCUMENTS_DIR / filename
        if not path.is_file():
            errors.append(f"Missing document: {filename}")
            continue

        content = path.read_text(encoding="utf-8")
        metadata_parts = content.split("---", maxsplit=2)
        if not content.startswith("---\n") or len(metadata_parts) < 3:
            errors.append(f"Missing YAML-style metadata header: {filename}")
        elif "document_type:" not in metadata_parts[1]:
            errors.append(f"Missing document_type metadata: {filename}")
        if SYNTHETIC_NOTICE not in content:
            errors.append(f"Missing synthetic-data notice: {filename}")
        if "\n# " not in content:
            errors.append(f"Missing Markdown title: {filename}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Documents checked: {len(REQUIRED_DOCUMENTS)}")
    print("Synthetic notice, metadata, and title: present in every document")
    print("Phase 2 check: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
