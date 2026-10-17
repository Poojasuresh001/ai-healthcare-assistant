"""Gemini chat-model construction kept separate from request routing."""

from app.config import GEMINI_CHAT_MODEL, get_google_api_key


def create_gemini_chat_model():
    """Create the configured LangChain Gemini chat model without exposing secrets."""
    api_key = get_google_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key is missing. Set GOOGLE_API_KEY in your local .env.")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as error:
        raise RuntimeError("Install the dependencies listed in requirements.txt.") from error

    return ChatGoogleGenerativeAI(
        model=GEMINI_CHAT_MODEL,
        temperature=0,
        api_key=api_key,
    )
