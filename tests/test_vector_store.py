"""Offline tests for persistent Chroma storage using deterministic fake vectors."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from chromadb.api.shared_system_client import SharedSystemClient

from app.config import PROJECT_ROOT
from app.rag.chunking import split_documents
from app.rag.embeddings import embed_chunks
from app.rag.ingestion import load_documents
from app.rag.vector_store import get_chroma_collection, upsert_embedded_chunks


class FakeEmbeddingClient:
    """Small deterministic embedding stand-in; never calls Gemini."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, float(len(text) % 17), 0.5] for text in texts]


class ChromaPersistenceTests(unittest.TestCase):
    def test_upserts_are_idempotent_and_metadata_filters_work(self) -> None:
        all_chunks = split_documents(load_documents())
        selected_chunks = [
            chunk
            for chunk in all_chunks
            if chunk.metadata["document_type"] in {"renewal_procedure", "claims_workflow"}
        ][:4]
        embedded_chunks = embed_chunks(selected_chunks, embedding_client=FakeEmbeddingClient())

        with TemporaryDirectory(dir=PROJECT_ROOT) as temp_dir:
            client, collection = get_chroma_collection(
                persist_directory=Path(temp_dir),
                collection_name="phase6_test_collection",
            )
            try:
                first_write_count = upsert_embedded_chunks(collection, embedded_chunks)
                second_write_count = upsert_embedded_chunks(collection, embedded_chunks)
                results = collection.get(
                    where={"document_type": "claims_workflow"},
                    include=["documents", "metadatas"],
                )

                self.assertEqual(first_write_count, len(embedded_chunks))
                self.assertEqual(second_write_count, len(embedded_chunks))
                self.assertEqual(collection.count(), len(embedded_chunks))
                self.assertGreater(len(results["ids"]), 0)
                self.assertTrue(
                    all(metadata["document_type"] == "claims_workflow" for metadata in results["metadatas"])
                )

                client._system.stop()
                SharedSystemClient.clear_system_cache()
                client, collection = get_chroma_collection(
                    persist_directory=Path(temp_dir),
                    collection_name="phase6_test_collection",
                )
                self.assertEqual(collection.count(), len(embedded_chunks))
            finally:
                client._system.stop()
                SharedSystemClient.clear_system_cache()


if __name__ == "__main__":
    unittest.main()
