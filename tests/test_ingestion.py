"""Small standard-library tests for the Phase 3 ingestion step."""

import unittest

from app.rag.ingestion import load_documents, parse_markdown_document


class ParseMarkdownDocumentTests(unittest.TestCase):
    def test_extracts_metadata_and_body_without_front_matter(self) -> None:
        sample = "---\ntitle: Example\ndocument_type: example\nclassification: synthetic\n---\n\n# Example\n\nBody text.\n"

        metadata, content = parse_markdown_document(sample, "example.md")

        self.assertEqual(metadata["title"], "Example")
        self.assertEqual(metadata["document_type"], "example")
        self.assertTrue(content.startswith("# Example"))
        self.assertNotIn("document_type:", content)

    def test_rejects_a_file_without_a_closed_metadata_header(self) -> None:
        with self.assertRaises(ValueError):
            parse_markdown_document("# No metadata\n\nText", "invalid.md")


class LoadDocumentsTests(unittest.TestCase):
    def test_loads_all_five_synthetic_reference_documents(self) -> None:
        documents = load_documents()
        document_ids = {document.document_id for document in documents}

        self.assertEqual(len(documents), 5)
        self.assertIn("Group_Renewal_Guide", document_ids)
        self.assertTrue(all(document.metadata["classification"] == "fictional_training_material" for document in documents))
        self.assertTrue(all("Synthetic training material." in document.content for document in documents))


if __name__ == "__main__":
    unittest.main()
