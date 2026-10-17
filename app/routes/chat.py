"""Chat endpoint with validated inputs and sanitized service errors."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.agents.graph import AssistantService
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.retriever import EmptyVectorStoreError
from app.services.dependencies import get_chat_service


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    service: AssistantService = Depends(get_chat_service),
) -> ChatResponse:
    try:
        result = service.ask(
            request.question,
            session_id=request.session_id,
            document_type=request.document_type,
        )
    except EmptyVectorStoreError as error:
        logger.info("Chat unavailable: document index is empty")
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        logger.error("Chat configuration failed (%s)", type(error).__name__)
        raise HTTPException(
            status_code=503,
            detail="Assistant configuration is incomplete. Check the local setup and API key.",
        ) from error
    except Exception as error:
        logger.error("Chat request failed (%s)", type(error).__name__)
        raise HTTPException(
            status_code=502,
            detail="The assistant could not complete this request. Please try again.",
        ) from error
    return ChatResponse.model_validate(result)
