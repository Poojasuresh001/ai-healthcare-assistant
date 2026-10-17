"""Stateful LangGraph workflow for routing, retrieval and grounded answers."""

from collections import defaultdict
from threading import Lock, RLock
from typing import Annotated, Any, Callable, TypedDict
import json
import logging
import re
import uuid

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from app.agents.routing import classify_sources, extract_identifiers


logger = logging.getLogger(__name__)
_CITATION_PATTERN = re.compile(r"\[(D\d+|S\d+)\]")


class AssistantState(TypedDict, total=False):
    question: str
    session_id: str
    document_type: str | None
    source_types: list[str]
    identifiers: dict[str, str | None]
    retrieved_documents: list[dict[str, str]]
    database_result: dict[str, Any]
    sources: list[dict[str, Any]]
    answer: str
    messages: Annotated[list[AnyMessage], add_messages]


class AssistantService:
    """Orchestrate safe SQL tools, Chroma retrieval, Gemini and session memory."""

    def __init__(
        self,
        *,
        retriever_factory: Callable[[str | None], Any],
        database_tools: dict,
        chat_model: Any,
        checkpointer: Any | None = None,
    ) -> None:
        self.retriever_factory = retriever_factory
        self.database_tools = database_tools
        self.chat_model = chat_model
        self._session_locks: defaultdict[str, RLock] = defaultdict(RLock)
        self._lock_guard = Lock()
        self.graph = self._build_graph(checkpointer or InMemorySaver())

    def _build_graph(self, checkpointer: Any):
        builder = StateGraph(AssistantState)
        builder.add_node("route", self._route)
        builder.add_node("retrieve_documents", self._retrieve_documents)
        builder.add_node("query_database", self._query_database)
        builder.add_node("generate_answer", self._generate_answer)
        builder.add_node("validate_answer", self._validate_answer)
        builder.add_edge(START, "route")
        builder.add_conditional_edges(
            "route",
            self._first_source,
            {"document": "retrieve_documents", "database": "query_database"},
        )
        builder.add_conditional_edges(
            "retrieve_documents",
            self._next_after_documents,
            {"database": "query_database", "answer": "generate_answer"},
        )
        builder.add_edge("query_database", "generate_answer")
        builder.add_edge("generate_answer", "validate_answer")
        builder.add_edge("validate_answer", END)
        return builder.compile(checkpointer=checkpointer)

    def _route(self, state: AssistantState) -> dict:
        return {
            "source_types": classify_sources(state["question"]),
            "identifiers": extract_identifiers(state["question"]),
            "retrieved_documents": [],
            "sources": [],
        }

    @staticmethod
    def _first_source(state: AssistantState) -> str:
        return "document" if "document" in state["source_types"] else "database"

    @staticmethod
    def _next_after_documents(state: AssistantState) -> str:
        return "database" if "database" in state["source_types"] else "answer"

    def _retrieve_documents(self, state: AssistantState) -> dict:
        retriever = self.retriever_factory(state.get("document_type"))
        documents: list[Document] = retriever.invoke(state["question"])
        retrieved: list[dict[str, str]] = []
        sources: list[dict[str, Any]] = []
        for index, document in enumerate(documents, start=1):
            metadata = document.metadata
            citation_id = f"D{index}"
            title = str(metadata.get("title") or metadata.get("document_id") or "Reference document")
            section = str(metadata.get("section") or "")
            source_path = str(metadata.get("source_path") or "")
            retrieved.append(
                {
                    "id": citation_id,
                    "title": title,
                    "section": section,
                    "content": document.page_content,
                }
            )
            sources.append(
                {
                    "id": citation_id,
                    "source_type": "document",
                    "title": title,
                    "source_path": source_path or None,
                    "section": section or None,
                    "excerpt": document.page_content[:600],
                }
            )
        return {"retrieved_documents": retrieved, "sources": sources}

    def _query_database(self, state: AssistantState) -> dict:
        question = state["question"].casefold()
        identifiers = state.get("identifiers", {})
        group_id = identifiers.get("group_id")
        member_id = identifiers.get("member_id")
        provider_id = identifiers.get("provider_id")

        if member_id and "claim" in question:
            tool_name, argument = "lookup_member_claims", {"member_id": member_id}
            title = f"Synthetic claims for {member_id}"
            table = "claims / members / providers"
        elif provider_id:
            tool_name, argument = "lookup_provider", {"provider_id": provider_id}
            title = f"Synthetic provider {provider_id}"
            table = "providers"
        elif group_id and any(word in question for word in ("renew", "not renewed", "hold")):
            tool_name, argument = "lookup_group_renewal", {"group_id": group_id}
            title = f"Synthetic renewal record for {group_id}"
            table = "renewals"
        elif group_id:
            tool_name, argument = "lookup_group", {"group_id": group_id}
            title = f"Synthetic group and plans for {group_id}"
            table = "groups / plans"
        else:
            missing = "member" if "member" in question or "claim" in question else "group or provider"
            result = {
                "found": False,
                "message": f"Please include a fictional {missing} ID, such as ABC123, M1001, or P1001.",
            }
            return {"database_result": result}

        try:
            result = self.database_tools[tool_name].invoke(argument)
        except Exception as error:
            logger.error("Database tool failed (%s)", type(error).__name__)
            result = {"found": False, "message": "The synthetic database lookup failed."}

        sources = list(state.get("sources", []))
        if result.get("found"):
            sources.append(
                {
                    "id": "S1",
                    "source_type": "database",
                    "title": title,
                    "source_path": f"database:{table}",
                    "section": None,
                    "excerpt": json.dumps(result, ensure_ascii=False, sort_keys=True)[:600],
                }
            )
        return {"database_result": result, "sources": sources}

    def _generate_answer(self, state: AssistantState) -> dict:
        database_result = state.get("database_result")
        retrieved_documents = state.get("retrieved_documents", [])
        has_document_context = bool(retrieved_documents)
        has_database_context = bool(database_result and database_result.get("found"))

        if database_result and not has_database_context and not has_document_context:
            return {"answer": database_result.get("message", "No synthetic database record was found.")}
        if not has_document_context and not has_database_context:
            return {
                "answer": "I could not find supporting information in the synthetic project sources."
            }

        context_sections = []
        for document in retrieved_documents:
            context_sections.append(
                f"[{document['id']}] {document['title']} — {document['section']}\n"
                f"{document['content']}"
            )
        if has_database_context:
            context_sections.append(f"[S1] Structured database record\n{json.dumps(database_result, ensure_ascii=False)}")

        system_prompt = (
            "You are Northstar's synthetic healthcare-insurance operations assistant. "
            "Answer only from the supplied synthetic source context. Do not invent records, "
            "dates, claim outcomes, approvals, policy rules, or coverage decisions. If sources "
            "conflict, state the conflict and defer to the signed approved source; never choose "
            "a date yourself. This is fictional training data, not medical, legal, benefits, or "
            "real claims advice. Cite factual statements using the supplied labels such as [D1] "
            "or [S1]. If context does not support an answer, say so plainly."
        )
        history = state.get("messages", [])[:-1][-6:]
        current_prompt = (
            f"Question: {state['question']}\n\n"
            "Use this retrieved context only:\n\n"
            + "\n\n---\n\n".join(context_sections)
        )
        response = self.chat_model.invoke(
            [SystemMessage(content=system_prompt), *history, HumanMessage(content=current_prompt)]
        )
        answer = self._message_text(response).strip()
        if not answer:
            answer = "I could not generate a grounded answer from the retrieved sources."
        return {"answer": answer, "messages": [AIMessage(content=answer)]}

    @staticmethod
    def _message_text(message: Any) -> str:
        content = getattr(message, "content", message)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                str(item.get("text", "")) if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content)

    @staticmethod
    def _validate_answer(state: AssistantState) -> dict:
        answer = state.get("answer", "").strip()
        sources = state.get("sources", [])
        valid_ids = {source["id"] for source in sources}

        def remove_unknown_citation(match: re.Match[str]) -> str:
            return match.group(0) if match.group(1) in valid_ids else ""

        answer = _CITATION_PATTERN.sub(remove_unknown_citation, answer)
        cited_ids = {match.group(1) for match in _CITATION_PATTERN.finditer(answer)}
        if valid_ids and not cited_ids:
            answer = f"{answer}\n\nSources: " + ", ".join(f"[{source_id}]" for source_id in sorted(valid_ids))
        return {"answer": answer}

    def ask(
        self,
        question: str,
        *,
        session_id: str | None = None,
        document_type: str | None = None,
    ) -> dict:
        resolved_session = session_id or str(uuid.uuid4())
        with self._lock_guard:
            session_lock = self._session_locks[resolved_session]
        with session_lock:
            config = {"configurable": {"thread_id": resolved_session}}
            output = self.graph.invoke(
                {
                    "question": question,
                    "session_id": resolved_session,
                    "document_type": document_type,
                    "messages": [HumanMessage(content=question)],
                },
                config=config,
            )
        return {
            "answer": output["answer"],
            "sources": output.get("sources", []),
            "source_type": output.get("source_types", []),
            "session_id": resolved_session,
        }
