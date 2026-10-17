"""HTTP request/response validation tests; no Gemini calls are made."""

import unittest
from unittest.mock import patch

from pydantic import ValidationError

from app.main import app
from app.main import health
from app.models.schemas import ChatRequest, IngestRequest
from app.routes.chat import chat
from app.routes.ingest import ingest


class FakeChatService:
    def ask(self, question: str, *, session_id=None, document_type=None) -> dict:
        return {
            "answer": "The sample renewal process uses a second-person review [D1].",
            "sources": [
                {
                    "id": "D1",
                    "source_type": "document",
                    "title": "Group Renewal Guide",
                    "source_path": "documents/Group_Renewal_Guide.md",
                    "section": "Completion checks",
                    "excerpt": "A second reviewer records the validation result.",
                }
            ],
            "source_type": ["document"],
            "session_id": session_id or "test-session",
        }


class ApiTests(unittest.TestCase):
    def test_routes_are_registered_in_openapi(self) -> None:
        paths = app.openapi()["paths"]

        self.assertEqual(set(paths), {"/chat", "/health", "/ingest"})
        self.assertIn("post", paths["/chat"])
        self.assertIn("post", paths["/ingest"])
        self.assertIn("get", paths["/health"])

    def test_health_handler_returns_healthy_status(self) -> None:
        response = health()

        self.assertEqual(response.status, "ok")
        self.assertEqual(response.service, "synthetic-healthcare-assistant")

    def test_chat_response_is_validated_and_contains_sources(self) -> None:
        response = chat(
            ChatRequest(question="What is the renewal process?", session_id="api-test"),
            service=FakeChatService(),
        )

        self.assertEqual(response.source_type, ["document"])
        self.assertEqual(response.sources[0].id, "D1")
        self.assertEqual(response.session_id, "api-test")

    def test_chat_rejects_empty_or_invalid_document_filter(self) -> None:
        with self.assertRaises(ValidationError):
            ChatRequest(question=" ")
        with self.assertRaises(ValidationError):
            ChatRequest(question="Find renewal guidance", document_type="private_table")

    def test_ingest_response_model(self) -> None:
        with patch(
            "app.routes.ingest.index_documents",
            return_value={
                "collection": "northstar_healthcare_docs",
                "indexed_this_run": 35,
                "collection_count": 35,
                "persist_directory": "chroma_db",
            },
        ):
            response = ingest(IngestRequest(all_documents=True))

        self.assertEqual(response.collection_count, 35)


if __name__ == "__main__":
    unittest.main()
