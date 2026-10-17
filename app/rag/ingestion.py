"""Read synthetic Markdown references into normalized document records.

This phase handles file discovery, text reading, and simple front-matter
metadata. Chunking, embedding, and vector-store writes are separate phases.
"""

from dataclasses import dataclass
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"


@dataclass
class IngestedDocument:
    """One complete source document, before it is split into chunks."""

    document_id: str
    source_path: str
    title: str
    metadata: dict[str, str]
    content: str


def parse_markdown_document(text: str, source_name: str) -> tuple[dict[str, str], str]:
    """Extract scalar metadata and body text from a Markdown front-matter file.

    The project uses a deliberately small ``key: value`` header format, so
    this parser does not need an external YAML dependency.
    """
    if not text.startswith("---\n"):
        raise ValueError(f"{source_name}: expected a metadata header starting with ---")

    parts = text.split("---", maxsplit=2)
    if len(parts) != 3:
        raise ValueError(f"{source_name}: metadata header is not closed with ---")

    metadata: dict[str, str] = {}
    for line_number, line in enumerate(parts[1].splitlines(), start=2):
        stripped_line = line.strip()
        if not stripped_line:
            continue

        key, separator, value = stripped_line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValueError(f"{source_name}:{line_number}: expected a non-empty key: value")
        normalized_key = key.strip()
        if normalized_key in metadata:
            raise ValueError(f"{source_name}:{line_number}: duplicate metadata key {normalized_key!r}")
        metadata[normalized_key] = value.strip()

    required_fields = ("title", "document_type", "classification")
    missing_fields = [field for field in required_fields if not metadata.get(field)]
    if missing_fields:
        raise ValueError(f"{source_name}: missing metadata fields: {', '.join(missing_fields)}")

    content = parts[2].strip()
    if not content:
        raise ValueError(f"{source_name}: document body is empty")

    return metadata, content


def load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[IngestedDocument]:
    """Load every top-level Markdown file in the documents directory."""
    if not documents_dir.is_dir():
        raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

    markdown_paths = sorted(documents_dir.glob("*.md"))
    if not markdown_paths:
        raise FileNotFoundError(f"No Markdown documents found in: {documents_dir}")

    loaded_documents: list[IngestedDocument] = []
    for path in markdown_paths:
        text = path.read_text(encoding="utf-8")
        metadata, content = parse_markdown_document(text, path.name)
        try:
            source_path = path.resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            source_path = path.name

        loaded_documents.append(
            IngestedDocument(
                document_id=path.stem,
                source_path=source_path,
                title=metadata["title"],
                metadata=metadata,
                content=content,
            )
        )

    return loaded_documents


def main() -> int:
    """Run ingestion and print a compact report without dumping document text."""
    try:
        documents = load_documents()
    except (OSError, ValueError) as error:
        print(f"Ingestion failed: {error}", file=sys.stderr)
        return 1

    print(f"Documents ingested: {len(documents)}")
    for document in documents:
        document_type = document.metadata["document_type"]
        print(
            f"- {document.title} [{document_type}] "
            f"({len(document.content):,} characters) — {document.source_path}"
        )
    print("Phase 3 check: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
