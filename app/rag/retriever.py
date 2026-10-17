"""LangChain retriever over the persistent Chroma collection."""

from typing import Any

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever

from app.rag.embeddings import (
    DOCUMENT_TASK_TYPE,
    QUERY_TASK_TYPE,
    create_gemini_embeddings,
)
from app.rag.vector_store import COLLECTION_NAME, get_chroma_collection


class GeminiRetrievalEmbeddings(Embeddings):
    """Use document and query task types appropriate to semantic retrieval."""

    def __init__(self, document_client: Any = None, query_client: Any = None) -> None:
        self.document_client = document_client or create_gemini_embeddings(
            task_type=DOCUMENT_TASK_TYPE
        )
        self.query_client = query_client or create_gemini_embeddings(task_type=QUERY_TASK_TYPE)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.document_client.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.query_client.embed_query(text)


class EmptyVectorStoreError(RuntimeError):
    """Raised when queries are attempted before any document chunks are indexed."""


def build_langchain_retriever(
    *,
    client: Any,
    embedding_function: Embeddings,
    collection_name: str = COLLECTION_NAME,
    k: int = 4,
    document_type: str | None = None,
) -> BaseRetriever:
    """Wrap an existing Chroma collection as a LangChain retriever."""
    search_kwargs: dict[str, Any] = {"k": k}
    if document_type:
        search_kwargs["filter"] = {"document_type": document_type}

    vector_store = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_function,
        create_collection_if_not_exists=False,
    )
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )


def create_langchain_retriever(
    document_type: str | None = None,
    *,
    embedding_function: Embeddings | None = None,
    k: int = 4,
) -> BaseRetriever:
    """Open the persisted store and return a filtered similarity retriever."""
    client, collection = get_chroma_collection()
    if collection.count() == 0:
        raise EmptyVectorStoreError(
            "The Chroma collection is empty. Run POST /ingest before document queries."
        )
    return build_langchain_retriever(
        client=client,
        embedding_function=embedding_function or GeminiRetrievalEmbeddings(),
        k=k,
        document_type=document_type,
    )
