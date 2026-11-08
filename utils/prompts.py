SUMMARY_SYSTEM = (
    "You are a precise summarization assistant. Use only the information in the provided "
    "text. Never invent facts, names, numbers or quotes. Do not add commentary.")

LENGTH_GUIDE = {
    "Short": {"para": "2-3 sentences", "bullets": "3-4 bullet points", "tokens": 300},
    "Medium": {"para": "one solid paragraph (5-8 sentences)", "bullets": "6-8 bullet points", "tokens": 700},
    "Detailed": {"para": "3-5 well-organized paragraphs", "bullets": "12-15 bullet points, grouped logically", "tokens": 1500},
}


def summary_prompt(text, length, fmt, language):
    g = LENGTH_GUIDE[length]
    style = g["bullets"] if fmt == "Bullet points" else g["para"]
    return (f"Summarize the text below in {language}.\nLength/format: {style}.\n"
            f"Output only the summary.\n\nTEXT:\n{text}")


def chunk_prompt(text, language):
    return (f"Write concise but information-dense notes in {language} covering all key facts "
            f"and ideas in this section. Output only the notes.\n\nSECTION:\n{text}")


YOUTUBE_PROMPT = (
    "Using ONLY the transcript below, write in {language} with exactly these markdown sections:\n"
    "## Summary\n(a short paragraph)\n## Key Points\n(bullets)\n## Important Topics\n(bullets)\n"
    "## Conclusions\n(bullets)\nDo not invent anything not in the transcript.\n\n"
    "TRANSCRIPT:\n{text}")

IMPROVE_SYSTEM = (
    "You are an expert editor. Preserve the user's original meaning exactly. Never invent "
    "facts, names, dates or details, and never change the intended message. Output only the "
    "improved text, with no explanations.")

IMPROVE_MODES = {
    "Grammar Correction": "Fix grammar, spelling and punctuation. Keep wording and tone as close to the original as possible.",
    "Professional Writing": "Rewrite in a clear, professional tone with correct grammar and good sentence structure.",
    "Simple English": "Rewrite in simple, easy-to-understand English with short sentences and common words.",
    "Formal Email": "Rewrite as a polished formal email with greeting, clear body paragraphs and closing. Use [Name] placeholders only if names are not given.",
    "Academic Writing": "Rewrite in a formal academic style with precise vocabulary and logical flow. Do not add citations or claims.",
    "Paragraph Rewriting": "Reorganize and rewrite into clear, well-structured paragraphs with improved readability.",
    "Sentence Improvement": "Improve each sentence for clarity, flow and correctness while keeping each sentence's meaning.",
}

WRITER_SYSTEM = (
    "You are a helpful writing assistant. Stay faithful to the provided text and do not "
    "invent facts. Output only the result.")

WRITER_TASKS = {
    "Rewrite text": "Rewrite the text to be clearer and better written, keeping the meaning.",
    "Expand short content": "Expand this into a fuller, well-developed version without adding made-up facts; elaborate only on what is implied.",
    "Simplify complex sentences": "Simplify complex sentences so they are easy to read, keeping all meaning.",
    "Paragraphs to bullet points": "Convert the text into clear bullet points.",
    "Bullet points to paragraphs": "Convert the bullet points into flowing, well-written paragraphs.",
    "Generate headings": "Suggest a main title plus 5 alternative headings and suitable subheadings for this content.",
    "Extract keywords": "Extract the 10-15 most important keywords/key phrases as a comma-separated list.",
    "Generate questions and answers": "Generate 5-8 important questions and answers based only on this text. Format as Q: / A:.",
}