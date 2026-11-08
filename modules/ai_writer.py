from utils.openai_client import chat
from utils.prompts import WRITER_SYSTEM, WRITER_TASKS
from utils.validators import validate_text


def run_task(text: str, task: str) -> str:
    text = validate_text(text)
    if task not in WRITER_TASKS:
        raise ValueError("Unknown writing task.")
    return chat(WRITER_SYSTEM, f"{WRITER_TASKS[task]}\n\nTEXT:\n{text}", max_tokens=2000)