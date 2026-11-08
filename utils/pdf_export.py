from fpdf import FPDF


def _clean(s: str) -> str:
    s = s.replace("**", "").replace("•", "-").replace("’", "'").replace("“", '"').replace("”", '"')
    return s.encode("latin-1", "replace").decode("latin-1")


def text_to_pdf_bytes(title: str, text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, _clean(title), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 11)
    for line in text.splitlines():
        pdf.multi_cell(0, 6, _clean(line) or " ", new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())