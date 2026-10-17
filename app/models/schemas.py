"""Validated HTTP request and response shapes for the local assistant API."""

from typing import Literal

from pydantic import BaseModel, Field


DocumentType = Literal[
    "renewal_procedure",
    "plan_configuration",
    "claims_workflow",
    "frequently_asked_questions",
    "etl_runbook",
]


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    session_id: str | None = Field(default=None, min_length=1, max_length=100)
    document_type: DocumentType | None = None


class SourceReference(BaseModel):
    id: str
    source_type: Literal["document", "database"]
    title: str
    source_path: str | None = None
    section: str | None = None
    excerpt: str = Field(max_length=600)


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    source_type: list[Literal["document", "database"]]
    session_id: str


class IngestRequest(BaseModel):
    all_documents: bool = True


class IngestResponse(BaseModel):
    collection: str
    indexed_this_run: int
    collection_count: int
    persist_directory: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
