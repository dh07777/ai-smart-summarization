import httpx
import pytest
from openai import RateLimitError, AuthenticationError

import config
from database import db
from modules import text_summarizer, text_improver, ai_writer
from utils import openai_client
from utils.openai_client import AIError
from utils.pdf_export import text_to_pdf_bytes
from utils.text_extractor import chunk_text
from utils.validators import ValidationError, validate_text


@pytest.fixture
def fake_chat(monkeypatch):
    calls = []

    def _chat(system, user, max_tokens=1000, temperature=0.3):
        calls.append(user)
        return "MOCK RESULT"
    monkeypatch.setattr(text_summarizer, "chat", _chat)
    monkeypatch.setattr(text_improver, "chat", _chat)
    monkeypatch.setattr(ai_writer, "chat", _chat)
    return calls


def test_short_text_summary(fake_chat):
    assert text_summarizer.summarize_text("Short text to summarize.") == "MOCK RESULT"
    assert len(fake_chat) == 1


def test_long_text_summary_is_hierarchical(fake_chat, monkeypatch):
    monkeypatch.setattr(config, "CHUNK_WORDS", 50)
    text = "word " * 400
    assert text_summarizer.summarize_text(text, "Detailed", "Bullet points", "French") == "MOCK RESULT"
    assert len(fake_chat) > 2  # chunk summaries + final


def test_chunking():
    assert len(chunk_text("a " * 100, 30)) == 4


def test_empty_input():
    for bad in ["", "   ", None]:
        with pytest.raises(ValidationError):
            validate_text(bad)
    with pytest.raises(ValidationError):
        text_summarizer.summarize_text("")


def test_grammar_correction(fake_chat):
    assert text_improver.improve_text("me go store yesterday", "Grammar Correction") == "MOCK RESULT"
    assert "Fix grammar" in fake_chat[0]


def test_professional_rewrite(fake_chat):
    text_improver.improve_text("hey send report asap", "Professional Writing")
    assert "professional" in fake_chat[0].lower()


def test_writer(fake_chat):
    assert ai_writer.run_task("some text", "Extract keywords") == "MOCK RESULT"


def _resp(code):
    return httpx.Response(code, request=httpx.Request("POST", "https://api.openai.com/v1/x"))


class _FakeClient:
    def __init__(self, exc):
        self.chat = type("C", (), {"completions": type("X", (), {"create": lambda s, **k: (_ for _ in ()).throw(exc)})()})()


def test_openai_rate_limit(monkeypatch):
    exc = RateLimitError("rate", response=_resp(429), body=None)
    monkeypatch.setattr(openai_client, "OpenAI", lambda **k: _FakeClient(exc))
    with pytest.raises(AIError, match="Rate limit"):
        openai_client.chat("s", "u")


def test_openai_auth_error(monkeypatch):
    exc = AuthenticationError("bad", response=_resp(401), body=None)
    monkeypatch.setattr(openai_client, "OpenAI", lambda **k: _FakeClient(exc))
    with pytest.raises(AIError, match="Authentication"):
        openai_client.chat("s", "u")


def test_missing_key(monkeypatch):
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    with pytest.raises(AIError, match="API key"):
        openai_client.chat("s", "u")


def test_database_history(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "t.db"))
    db.init_db()
    rid = db.add_record("Text", "orig", "summary", {"length": "Short"})
    assert len(db.get_history()) == 1
    assert db.get_record(rid)["output_text"] == "summary"
    db.delete_record(rid)
    assert db.get_history().empty


def test_download_pdf_bytes():
    assert text_to_pdf_bytes("Title", "Hello **world**\n• item").startswith(b"%PDF")