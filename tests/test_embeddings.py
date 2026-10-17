"""Offline unit tests for Gemini embedding orchestration and validation."""

import unittest

from app.rag.chunking import split_documents
from app.rag.embeddings import EmbeddingError, embed_chunks
from app.rag.ingestion import load_documents


class FakeEmbeddingClient:
    """A deterministic local stand-in; it never calls an external service."""

    def __init__(self) -> None:
        self.batch_sizes: list[int] = []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self.batch_sizes.append(len(texts))
        return [[float(len(text)), 1.0] for text in texts]


class BadEmbeddingClient:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return []


class EmbeddingTests(unittest.TestCase):
    def test_embeds_chunks_in_batches_and_retains_sources(self) -> None:
        chunks = split_documents(load_documents())[:5]
        fake_client = FakeEmbeddingClient()

        embedded = embed_chunks(chunks, embedding_client=fake_client, batch_size=2)

        self.assertEqual(fake_client.batch_sizes, [2, 2, 1])
        self.assertEqual(len(embedded), len(chunks))
        self.assertEqual(embedded[0].chunk.source_path, chunks[0].source_path)
        self.assertEqual(len(embedded[0].vector), 2)

    def test_rejects_a_response_with_the_wrong_vector_count(self) -> None:
        chunks = split_documents(load_documents())[:1]

        with self.assertRaises(EmbeddingError):
            embed_chunks(chunks, embedding_client=BadEmbeddingClient())

    def test_empty_input_does_not_create_or_call_an_api_client(self) -> None:
        self.assertEqual(embed_chunks([]), [])


if __name__ == "__main__":
    unittest.main()
