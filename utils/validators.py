import re
from urllib.parse import urlparse, parse_qs

import config


class ValidationError(ValueError):
    """Raised for invalid user input."""


def validate_text(text: str, name: str = "Text") -> str:
    text = (text or "").strip()
    if not text:
        raise ValidationError(f"{name} is empty. Please enter some text.")
    if len(text) > config.MAX_INPUT_CHARS:
        raise ValidationError(f"{name} is too long (max {config.MAX_INPUT_CHARS:,} characters).")
    return text


def validate_pdf(filename: str, data: bytes) -> bytes:
    if not filename or not filename.lower().endswith(".pdf"):
        raise ValidationError("Only .pdf files are supported.")
    if not data:
        raise ValidationError("The uploaded file is empty.")
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise ValidationError(f"File is too large (max {config.MAX_UPLOAD_MB} MB).")
    if not data.lstrip()[:5] == b"%PDF-":
        raise ValidationError("This file is not a valid PDF.")
    return data


_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com",
          "youtu.be", "www.youtu.be"}


def extract_video_id(url: str):
    """Return the 11-char video ID, or None if the URL is not a valid YouTube video URL."""
    url = (url or "").strip()
    if not url:
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        p = urlparse(url)
    except ValueError:
        return None
    host = (p.hostname or "").lower()
    if host not in _HOSTS:
        return None
    vid = None
    if host.endswith("youtu.be"):
        vid = p.path.strip("/").split("/")[0]
    elif p.path == "/watch":
        vid = parse_qs(p.query).get("v", [None])[0]
    else:
        parts = [x for x in p.path.split("/") if x]
        if len(parts) >= 2 and parts[0] in ("shorts", "embed", "live", "v"):
            vid = parts[1]
    return vid if vid and _ID_RE.match(vid) else None