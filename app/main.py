"""FastAPI entry point for the synthetic healthcare-insurance assistant."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.config import AUTO_INGEST_ON_STARTUP
from app.models.schemas import HealthResponse
from app.rag.vector_store import get_chroma_collection, index_documents
from app.routes.chat import router as chat_router
from app.routes.ingest import router as ingest_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Recreate the temporary free-host vector index when a service starts."""
    if AUTO_INGEST_ON_STARTUP:
        try:
            _, collection = get_chroma_collection()
            if collection.count() == 0:
                summary = index_documents(all_documents=True)
                logger.info(
                    "Startup document index created with %s chunks.",
                    summary["collection_count"],
                )
            else:
                logger.info("Startup document index already has %s chunks.", collection.count())
        except Exception as error:
            # Keep the UI and health endpoint available; /ingest can retry indexing.
            logger.error(
                "Startup document indexing failed (%s). Document questions may be unavailable "
                "until POST /ingest succeeds.",
                type(error).__name__,
            )
    yield


app = FastAPI(
    title="Enterprise Healthcare Insurance AI Assistant",
    description="A learning demo using only fictional documents and synthetic database rows.",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(chat_router)
app.include_router(ingest_router)

FRONTEND_FILE = Path(__file__).resolve().parent / "static" / "index.html"


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    """Serve the lightweight browser chat interface."""
    return FileResponse(FRONTEND_FILE)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return process health without making external Gemini or database calls."""
    return HealthResponse(status="ok", service="synthetic-healthcare-assistant")
