"""Small local configuration helpers for the learning project."""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)
CHROMA_DIRECTORY = Path(os.getenv("CHROMA_DIRECTORY", PROJECT_ROOT / "chroma_db"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", PROJECT_ROOT / "data" / "synthetic_healthcare.sqlite3"))
GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.8-flash")
AUTO_INGEST_ON_STARTUP = os.getenv("AUTO_INGEST_ON_STARTUP", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def get_google_api_key() -> str | None:
    """Return the Gemini API key from the process environment or local .env."""
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
