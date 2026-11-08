import pymupdf as fitz

import config
from utils.validators import ValidationError


def word_count(text: str) -> int:
    return len((text or "").split())


def chunk_text(text: str, chunk_words: int = None) -> list:
    chunk_words = chunk_words or config.CHUNK_WORDS
    words = text.split()
    if not words:
        return []
    return [" ".join(words[i:i + chunk_words]) for i in range(0, len(words), chunk_words)]


def extract_pdf_text(data: bytes):
    """Return (text, page_count). Raises ValidationError for bad/scanned/encrypted PDFs."""
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception:
        raise ValidationError("This PDF is corrupted or could not be opened.")
    try:
        if doc.needs_pass:
            raise ValidationError("This PDF is password-protected and cannot be read.")
        if doc.page_count == 0:
            raise ValidationError("This PDF has no pages.")
        if doc.page_count > config.MAX_PDF_PAGES:
            raise ValidationError(f"PDF has too many pages (max {config.MAX_PDF_PAGES}).")
        pages = [page.get_text() for page in doc]
        count = doc.page_count
    finally:
        doc.close()
    text = "\n\n".join(pages).strip()
    if len(text) < 20:
        raise ValidationError(
            "No readable text found. This looks like a scanned/image-only PDF, and OCR is "
            "not available in this app. Please upload a text-based PDF.")
    return text, count