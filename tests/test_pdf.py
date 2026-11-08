import pymupdf as fitz
import pytest

from modules import pdf_summarizer
from utils.validators import ValidationError, validate_pdf


def make_pdf(pages=1, text="Hello world. " * 20):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i + 1}. {text}")
    data = doc.tobytes()
    doc.close()
    return data


def test_pdf_extraction():
    text, pages = pdf_summarizer.extract("a.pdf", make_pdf(1))
    assert pages == 1 and "Hello world" in text


def test_multi_page_pdf():
    text, pages = pdf_summarizer.extract("multi.pdf", make_pdf(3))
    assert pages == 3 and "Page 3" in text


def test_invalid_pdf():
    with pytest.raises(ValidationError):
        pdf_summarizer.extract("fake.pdf", b"this is not a pdf")
    with pytest.raises(ValidationError):
        pdf_summarizer.extract("a.txt", make_pdf())
    with pytest.raises(ValidationError):
        validate_pdf("a.pdf", b"")


def test_scanned_pdf_message():
    doc = fitz.open()
    doc.new_page()  # blank page, no text
    data = doc.tobytes()
    with pytest.raises(ValidationError, match="OCR"):
        pdf_summarizer.extract("scan.pdf", data)


def test_pdf_summary_uses_ai(monkeypatch):
    from modules import text_summarizer
    monkeypatch.setattr(text_summarizer, "chat", lambda *a, **k: "PDF SUMMARY")
    assert pdf_summarizer.summarize_pdf_text("some extracted text") == "PDF SUMMARY"