"""Split ingested documents into section-aware, overlapping text chunks."""

from dataclasses import dataclass
import re
import sys

from app.rag.ingestion import IngestedDocument, load_documents


DEFAULT_CHUNK_SIZE = 1_000
DEFAULT_CHUNK_OVERLAP = 150
BOUNDARY_SEPARATORS = ("\n\n", "\n", ". ", " ")
HEADING_PATTERN = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")


@dataclass
class DocumentChunk:
    """A text segment with its source and document metadata attached."""

    chunk_id: str
    document_id: str
    source_path: str
    title: str
    section: str
    chunk_index: int
    metadata: dict[str, str]
    text: str


def _find_chunk_end(text: str, start: int, chunk_size: int) -> int:
    """Prefer a natural text boundary near the size limit when one is available."""
    target = min(start + chunk_size, len(text))
    if target == len(text):
        return target

    earliest_boundary = start + max(1, chunk_size // 2)
    for separator in BOUNDARY_SEPARATORS:
        boundary = text.rfind(separator, earliest_boundary, target)
        if boundary >= earliest_boundary:
            return boundary + len(separator)
    return target


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Split text into bounded windows, preferring paragraph and word boundaries."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be between zero and chunk_size - 1")

    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = _find_chunk_end(text, start, chunk_size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break

        next_start = max(start + 1, end - chunk_overlap)
        # Avoid beginning the next chunk in the middle of a word. This makes
        # the actual overlap approximate, while keeping every chunk readable.
        while next_start < end and not text[next_start].isspace():
            next_start += 1
        start = next_start if next_start < end else end

    return chunks


def _iter_sections(markdown_text: str):
    """Yield Markdown heading sections and their body text in document order."""
    section_title = "Introduction"
    section_lines: list[str] = []

    for line in markdown_text.splitlines():
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            section_body = "\n".join(section_lines).strip()
            if section_body:
                yield section_title, section_body
            section_title = heading_match.group(1).strip()
            section_lines = []
        else:
            section_lines.append(line)

    final_body = "\n".join(section_lines).strip()
    if final_body:
        yield section_title, final_body


def split_document(
    document: IngestedDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """Split one document by section, retaining metadata and a stable chunk ID."""
    chunks: list[DocumentChunk] = []

    for section, section_text in _iter_sections(document.content):
        section_chunks = split_text(section_text, chunk_size, chunk_overlap)
        for text in section_chunks:
            chunk_index = len(chunks)
            chunk_metadata = {
                **document.metadata,
                "document_id": document.document_id,
                "source_path": document.source_path,
                "section": section,
                "chunk_index": str(chunk_index),
            }
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{document.document_id}::{chunk_index:04d}",
                    document_id=document.document_id,
                    source_path=document.source_path,
                    title=document.title,
                    section=section,
                    chunk_index=chunk_index,
                    metadata=chunk_metadata,
                    text=text,
                )
            )

    return chunks


def split_documents(
    documents: list[IngestedDocument],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    """Split a collection of ingested documents into chunks."""
    return [
        chunk
        for document in documents
        for chunk in split_document(document, chunk_size, chunk_overlap)
    ]


def main() -> int:
    """Load the corpus, split it, and print chunk statistics."""
    try:
        documents = load_documents()
        chunks = split_documents(documents)
    except (OSError, ValueError) as error:
        print(f"Chunking failed: {error}", file=sys.stderr)
        return 1

    print(f"Documents processed: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")
    print(f"Chunk size: {DEFAULT_CHUNK_SIZE} characters; overlap: {DEFAULT_CHUNK_OVERLAP} characters")
    for document in documents:
        document_chunks = [chunk for chunk in chunks if chunk.document_id == document.document_id]
        largest_chunk = max((len(chunk.text) for chunk in document_chunks), default=0)
        print(f"- {document.title}: {len(document_chunks)} chunks; largest {largest_chunk} characters")

    print("Phase 4 check: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
