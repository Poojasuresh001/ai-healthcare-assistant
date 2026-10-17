"""Lazy singleton factories used by FastAPI routes."""

from functools import lru_cache

from app.agents.graph import AssistantService
from app.database.service import HealthcareDatabase
from app.rag.retriever import create_langchain_retriever
from app.services.llm import create_gemini_chat_model
from app.tools.database_tools import build_database_tools


@lru_cache(maxsize=1)
def get_chat_service() -> AssistantService:
    """Build the graph once; database and vector operations stay lazy per route."""
    database = HealthcareDatabase()
    return AssistantService(
        retriever_factory=create_langchain_retriever,
        database_tools=build_database_tools(database),
        chat_model=create_gemini_chat_model(),
    )
