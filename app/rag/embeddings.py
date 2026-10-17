"""Create Gemini embeddings for the project's document chunks."""

import argparse
from dataclasses import dataclass
import math
import sys
from typing import Protocol

from app.config import get_google_api_key
from app.rag.chunking import DocumentChunk, split_documents
from app.rag.ingestion import load_documents


EMBEDDING_MODEL = "gemini-embedding-001"
DOCUMENT_TASK_TYPE = "RETRIEVAL_DOCUMENT"
QUERY_TASK_TYPE = "RETRIEVAL_QUERY"
MAX_BATCH_SIZE = 100


class EmbeddingClient(Protocol):
    """The small part of LangChain's embedding interface used by this module."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector for each text, preserving input order."""


@dataclass
class EmbeddedChunk:
    """A source chunk paired with its numeric embedding vector."""

    chunk: DocumentChunk
    vector: list[float]


class EmbeddingError(RuntimeError):
    """Raised when an embedding response cannot be safely paired to its chunks."""


def create_gemini_embeddings(
    api_key: str | None = None,
    task_type: str = DOCUMENT_TASK_TYPE,
) -> EmbeddingClient:
    """Create the LangChain Gemini embedding client without exposing its key."""
    resolved_api_key = api_key or get_google_api_key()
    if not resolved_api_key:
        raise RuntimeError(
            "Gemini API key is missing. Copy .env.example to .env and set GOOGLE_API_KEY."
        )

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
    except ImportError as error:
        raise RuntimeError(
            "Gemini embedding dependency is missing. Install requirements.txt in the project environment."
        ) from error

    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        task_type=task_type,
        google_api_key=resolved_api_key,
    )


def embed_chunks(
    chunks: list[DocumentChunk],
    embedding_client: EmbeddingClient | None = None,
    batch_size: int = MAX_BATCH_SIZE,
) -> list[EmbeddedChunk]:
    """Embed chunks in bounded batches and validate the returned vectors."""
    if not chunks:
        return []
    if not 1 <= batch_size <= MAX_BATCH_SIZE:
        raise ValueError(f"batch_size must be between 1 and {MAX_BATCH_SIZE}")

    client = embedding_client or create_gemini_embeddings()
    results: list[EmbeddedChunk] = []
    expected_dimensions: int | None = None

    for batch_start in range(0, len(chunks), batch_size):
        batch = chunks[batch_start : batch_start + batch_size]
        try:
            vectors = client.embed_documents([chunk.text for chunk in batch])
        except Exception as error:
            # Keep provider diagnostics and secrets out of console output/logs.
            raise EmbeddingError(
                f"Gemini embedding request failed ({type(error).__name__}). "
                "Check the API key, network, quota, and model access."
            ) from error

        if len(vectors) != len(batch):
            raise EmbeddingError(
                f"Provider returned {len(vectors)} vectors for {len(batch)} chunks."
            )

        for chunk, raw_vector in zip(batch, vectors, strict=True):
            vector = [float(value) for value in raw_vector]
            if not vector:
                raise EmbeddingError(f"Provider returned an empty vector for {chunk.chunk_id}.")
            if not all(math.isfinite(value) for value in vector):
                raise EmbeddingError(f"Provider returned a non-finite value for {chunk.chunk_id}.")
            if expected_dimensions is None:
                expected_dimensions = len(vector)
            elif len(vector) != expected_dimensions:
                raise EmbeddingError("Provider returned vectors with inconsistent dimensions.")
            results.append(EmbeddedChunk(chunk=chunk, vector=vector))

    return results


def main() -> int:
    """Run a one-chunk smoke test by default; --all opts into the full corpus."""
    parser = argparse.ArgumentParser(description="Embed synthetic document chunks with Gemini.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Embed every chunk. By default only the first chunk is sent as a smoke test.",
    )
    args = parser.parse_args()

    try:
        chunks = split_documents(load_documents())
        selected_chunks = chunks if args.all else chunks[:1]
        if not selected_chunks:
            raise ValueError("No document chunks are available to embed.")
        embedded_chunks = embed_chunks(selected_chunks)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Embedding failed: {error}", file=sys.stderr)
        return 1

    dimensions = len(embedded_chunks[0].vector)
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Chunks embedded: {len(embedded_chunks)}")
    print(f"Vector dimensions: {dimensions}")
    print(f"Example chunk ID: {embedded_chunks[0].chunk.chunk_id}")
    print("Phase 5 check: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
