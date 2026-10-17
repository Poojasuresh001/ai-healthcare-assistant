"""Document-index endpoint, separate from chat-time retrieval."""

import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import IngestRequest, IngestResponse
from app.rag.vector_store import index_documents


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest) -> IngestResponse:
    try:
        summary = index_documents(all_documents=request.all_documents)
    except Exception as error:
        logger.error("Document indexing failed (%s)", type(error).__name__)
        raise HTTPException(
            status_code=502,
            detail="Document indexing failed. Check the local API key, network, and logs.",
        ) from error
    return IngestResponse.model_validate(summary)
