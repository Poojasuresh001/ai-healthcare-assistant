"""LangGraph orchestration tests with local fake retrieval and Gemini clients."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from app.agents.graph import AssistantService
from app.config import PROJECT_ROOT
from app.database.service import HealthcareDatabase
from app.tools.database_tools import build_database_tools


class FakeRetriever:
    def invoke(self, question: str) -> list[Document]:
        return [
            Document(
                page_content=(
                    "If requested and signed renewal dates differ, pause configuration and "
                    "route the discrepancy for written resolution."
                ),
                metadata={
                    "title": "Group Renewal Guide",
                    "source_path": "documents/Group_Renewal_Guide.md",
                    "section": "Effective-date mismatch handling",
                },
            )
        ]


class FakeChatModel:
    def __init__(self) -> None:
        self.calls: list[list] = []

    def invoke(self, messages: list) -> AIMessage:
        self.calls.append(messages)
        return AIMessage(
            content="Pause configuration until the dates are resolved in writing [D1] [S1]."
        )


class AssistantGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory(dir=PROJECT_ROOT)
        database = HealthcareDatabase(Path(self.temp_dir.name) / "graph.sqlite3")
        self.model = FakeChatModel()
        self.service = AssistantService(
            retriever_factory=lambda document_type: FakeRetriever(),
            database_tools=build_database_tools(database),
            chat_model=self.model,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_combined_question_uses_documents_and_database_with_valid_citations(self) -> None:
        result = self.service.ask(
            "According to the renewal policy, why is group ABC123 on hold?",
            session_id="test-combined",
        )

        self.assertEqual(result["source_type"], ["document", "database"])
        self.assertEqual([source["id"] for source in result["sources"]], ["D1", "S1"])
        self.assertIn("[D1]", result["answer"])
        self.assertIn("[S1]", result["answer"])
        self.assertIn("NEEDS_RECONCILIATION", result["sources"][1]["excerpt"])

    def test_database_only_question_does_not_open_the_vector_store(self) -> None:
        result = self.service.ask("Show claims for member M1001", session_id="test-claims")

        self.assertEqual(result["source_type"], ["database"])
        self.assertEqual(result["sources"][0]["source_type"], "database")
        self.assertIn("[S1]", result["answer"])

    def test_same_session_keeps_bounded_conversation_context(self) -> None:
        self.service.ask("What is the renewal process?", session_id="test-memory")
        self.service.ask("What must happen before configuration resumes?", session_id="test-memory")

        self.assertEqual(len(self.model.calls), 2)
        self.assertGreater(len(self.model.calls[1]), 2)


if __name__ == "__main__":
    unittest.main()
