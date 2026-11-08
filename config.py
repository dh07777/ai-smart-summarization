import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        return str(st.secrets.get(key, default))
    except Exception:
        return default


OPENAI_API_KEY = get_secret("OPENAI_API_KEY")
DEFAULT_MODEL = get_secret("OPENAI_MODEL", "gpt-4o-mini")
AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"]

MAX_UPLOAD_MB = 10
MAX_PDF_PAGES = 300
MAX_INPUT_CHARS = 300_000
CHUNK_WORDS = 2500
DB_PATH = os.getenv("DB_PATH", "history.db")

LANGUAGES = ["English", "Spanish", "French", "German", "Portuguese", "Italian",
             "Hindi", "Urdu", "Arabic", "Chinese", "Japanese", "Korean", "Russian"]