import config
from utils.openai_client import chat
from utils.prompts import (SUMMARY_SYSTEM, LENGTH_GUIDE, summary_prompt, chunk_prompt)
from utils.text_extractor import chunk_text
from utils.validators import validate_text


def condense(text: str, language: str) -> str:
    """Hierarchical reduction: summarize chunks, merge, repeat until it fits one chunk."""
    chunks = chunk_text(text, config.CHUNK_WORDS)
    rounds = 0
    while len(chunks) > 1 and rounds < 5:
        notes = [chat(SUMMARY_SYSTEM, chunk_prompt(c, language), max_tokens=700) for c in chunks]
        chunks = chunk_text("\n\n".join(notes), config.CHUNK_WORDS)
        rounds += 1
    return "\n\n".join(chunks)


def summarize_long(text: str, length: str, fmt: str, language: str) -> str:
    condensed = condense(text, language)
    return chat(SUMMARY_SYSTEM, summary_prompt(condensed, length, fmt, language),
                max_tokens=LENGTH_GUIDE[length]["tokens"])


def summarize_text(text: str, length: str = "Medium", fmt: str = "Paragraph",
                   language: str = "English") -> str:
    text = validate_text(text)
    return summarize_long(text, length, fmt, language)