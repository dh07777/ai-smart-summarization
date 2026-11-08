from utils.openai_client import chat
from utils.prompts import IMPROVE_SYSTEM, IMPROVE_MODES
from utils.validators import validate_text


def improve_text(text: str, mode: str = "Grammar Correction") -> str:
    text = validate_text(text)
    if mode not in IMPROVE_MODES:
        raise ValueError("Unknown improvement mode.")
    prompt = f"{IMPROVE_MODES[mode]}\n\nTEXT:\n{text}"
    return chat(IMPROVE_SYSTEM, prompt, max_tokens=2000, temperature=0.2)