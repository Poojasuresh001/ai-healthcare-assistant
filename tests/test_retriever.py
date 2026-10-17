"""LangChain-Chroma retrieval and metadata-filter tests with local fake vectors."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from chromadb.api.shared_system_client import SharedSystemClient
from langchain_core.embeddings import Embeddings

from app.config import PROJECT_ROOT
from app.rag.retriever import build_langchain_retriever
from app.rag.vector_store import COLLECTION_NAME, get_chroma_collection


class FakeEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


class LangChainRetrieverTests(unittest.TestCase):
    def test_retriever_returns_langchain_documents_and_filters_metadata(self) -> None:
        with TemporaryDirectory(dir=PROJECT_ROOT) as temp_dir:
            client, collection = get_chroma_collection(
                persist_directory=Path(temp_dir),
                collection_name=COLLECTION_NAME,
            )
            try:
                collection.upsert(
                    ids=["renewal-1", "claims-1"],
                    embeddings=[[1.0, 0.0, 0.0], [0.9, 0.1, 0.0]],
                    documents=["Renewal date mismatch instructions", "Synthetic claim workflow"],
                    metadatas=[
                        {
                            "document_type": "renewal_procedure",
                            "title": "Group Renewal Guide",
                            "section": "Effective-date mismatch handling",
                            "source_path": "documents/Group_Renewal_Guide.md",
                        },
                        {
                            "document_type": "claims_workflow",
                            "title": "Claims Process Guide",
                            "section": "Sample workflow",
                            "source_path": "documents/Claims_Process_Guide.md",
                        },
                    ],
                )
                retriever = build_langchain_retriever(
                    client=client,
                    collection_name=COLLECTION_NAME,
                    embedding_function=FakeEmbeddings(),
                    k=2,
                    document_type="renewal_procedure",
                )

                results = retriever.invoke("What is the renewal date mismatch process?")

                self.assertEqual(len(results), 1)
                self.assertEqual(results[0].metadata["title"], "Group Renewal Guide")
                self.assertEqual(
                    results[0].metadata["document_type"],
                    "renewal_procedure",
                )
            finally:
                client._system.stop()
                SharedSystemClient.clear_system_cache()


if __name__ == "__main__":
    unittest.main()
