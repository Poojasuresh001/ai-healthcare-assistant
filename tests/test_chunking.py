"""Small standard-library tests for the Phase 4 chunking step."""

import unittest

from app.rag.chunking import split_documents, split_text
from app.rag.ingestion import load_documents


class SplitTextTests(unittest.TestCase):
    def test_chunks_respect_size_and_overlap(self) -> None:
        source = " ".join(f"word{index:03d}" for index in range(100))

        chunks = split_text(source, chunk_size=100, chunk_overlap=20)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(0 < len(chunk) <= 100 for chunk in chunks))
        self.assertTrue(set(chunks[0].split()) & set(chunks[1].split()))

    def test_rejects_invalid_overlap(self) -> None:
        with self.assertRaises(ValueError):
            split_text("some text", chunk_size=10, chunk_overlap=10)


class SplitDocumentsTests(unittest.TestCase):
    def test_preserves_source_and_section_metadata_on_chunks(self) -> None:
        chunks = split_documents(load_documents())

        self.assertGreater(len(chunks), 5)
        self.assertTrue(all(chunk.text for chunk in chunks))
        self.assertTrue(all(chunk.source_path.startswith("documents/") for chunk in chunks))
        self.assertTrue(all(chunk.metadata["section"] == chunk.section for chunk in chunks))
        self.assertEqual(len({chunk.chunk_id for chunk in chunks}), len(chunks))


if __name__ == "__main__":
    unittest.main()
