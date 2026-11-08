from modules.text_summarizer import summarize_long
from utils.text_extractor import extract_pdf_text
from utils.validators import validate_pdf


def extract(filename: str, data: bytes):
    validate_pdf(filename, data)
    return extract_pdf_text(data)  # (text, pages)


def summarize_pdf_text(text: str, length="Medium", fmt="Paragraph", language="English") -> str:
    return summarize_long(text, length, fmt, language)