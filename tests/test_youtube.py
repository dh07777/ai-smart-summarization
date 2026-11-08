import pytest
from youtube_transcript_api import TranscriptsDisabled

from modules import youtube_summarizer as ys
from utils.validators import ValidationError, extract_video_id


def test_url_parsing():
    vid = "dQw4w9WgXcQ"
    assert extract_video_id(f"https://www.youtube.com/watch?v={vid}") == vid
    assert extract_video_id(f"https://youtu.be/{vid}") == vid
    assert extract_video_id(f"https://www.youtube.com/shorts/{vid}") == vid


def test_invalid_urls():
    for bad in ["", "https://example.com/watch?v=dQw4w9WgXcQ", "not a url",
                "https://www.youtube.com/watch?v=short"]:
        assert extract_video_id(bad) is None
    with pytest.raises(ValidationError):
        ys.summarize_youtube("https://example.com")


def test_transcript_disabled(monkeypatch):
    class Fake:
        def list(self, vid):
            raise TranscriptsDisabled(vid)
    monkeypatch.setattr(ys, "YouTubeTranscriptApi", Fake)
    with pytest.raises(ValidationError, match="disabled"):
        ys.summarize_youtube("https://youtu.be/dQw4w9WgXcQ")


def test_summary_with_mocked_transcript(monkeypatch):
    monkeypatch.setattr(ys, "fetch_transcript", lambda v: "hello transcript text")
    monkeypatch.setattr(ys, "get_title", lambda u: "Test Video")
    monkeypatch.setattr(ys, "chat", lambda *a, **k: "## Summary\nOK")
    monkeypatch.setattr(ys, "condense", lambda t, l: t)
    res = ys.summarize_youtube("https://youtu.be/dQw4w9WgXcQ")
    assert res["title"] == "Test Video" and "Summary" in res["summary"]