"""FastAPI entry point for the synthetic healthcare-insurance assistant."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.models.schemas import HealthResponse
from app.routes.chat import router as chat_router
from app.routes.ingest import router as ingest_router


app = FastAPI(
    title="Enterprise Healthcare Insurance AI Assistant",
    description="A learning demo using only fictional documents and synthetic database rows.",
    version="0.1.0",
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
