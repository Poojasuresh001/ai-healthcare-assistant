"""Persist generated chunk embeddings in a local Chroma collection."""

import argparse
from pathlib import Path
import sys

import chromadb
from chromadb.config import Settings

from app.config import CHROMA_DIRECTORY
from app.rag.chunking import split_documents
from app.rag.embeddings import embed_chunks
from app.rag.ingestion import load_documents


COLLECTION_NAME = "northstar_healthcare_docs"


def get_chroma_collection(
    persist_directory: Path = CHROMA_DIRECTORY,
    collection_name: str = COLLECTION_NAME,
):
    """Open or create the persistent local collection, with telemetry disabled."""
    persist_directory.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(persist_directory),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Synthetic healthcare insurance reference chunks"},
    )
    return client, collection


def upsert_embedded_chunks(collection, embedded_chunks) -> int:
    """Insert or update chunks using stable IDs so reruns do not duplicate them."""
    if not embedded_chunks:
        return 0

    collection.upsert(
        ids=[item.chunk.chunk_id for item in embedded_chunks],
        embeddings=[item.vector for item in embedded_chunks],
        documents=[item.chunk.text for item in embedded_chunks],
        metadatas=[dict(item.chunk.metadata) for item in embedded_chunks],
    )
    return len(embedded_chunks)


def index_documents(
    *,
    all_documents: bool = True,
    db_path: Path = CHROMA_DIRECTORY,
    embedding_client=None,
) -> dict[str, int | str]:
    """Chunk, embed, and upsert synthetic documents into the persistent collection."""
    chunks = split_documents(load_documents())
    selected_chunks = chunks if all_documents else chunks[:1]
    if not selected_chunks:
        raise ValueError("No document chunks are available to index.")

    embedded_chunks = embed_chunks(selected_chunks, embedding_client=embedding_client)
    _, collection = get_chroma_collection(persist_directory=db_path)
    indexed_count = upsert_embedded_chunks(collection, embedded_chunks)
    return {
        "collection": COLLECTION_NAME,
        "indexed_this_run": indexed_count,
        "collection_count": collection.count(),
        "persist_directory": str(db_path.resolve()),
    }


def main() -> int:
    """Embed one chunk by default and persist it; --all indexes the whole corpus."""
    parser = argparse.ArgumentParser(description="Index synthetic chunks in local ChromaDB.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Embed and index every chunk. By default only one smoke-test chunk is indexed.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=CHROMA_DIRECTORY,
        help="Local directory for Chroma persistence (default: chroma_db).",
    )
    args = parser.parse_args()

    try:
        summary = index_documents(all_documents=args.all, db_path=args.db_path)
    except Exception as error:
        print(f"Chroma indexing failed ({type(error).__name__}): {error}", file=sys.stderr)
        return 1

    print(f"Collection: {summary['collection']}")
    print(f"Persist directory: {summary['persist_directory']}")
    print(f"Chunks indexed this run: {summary['indexed_this_run']}")
    print(f"Chunks in collection: {summary['collection_count']}")
    print("Phase 6 check: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
