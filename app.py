import streamlit as st

import config
from database import db
from modules import text_summarizer, pdf_summarizer, youtube_summarizer, text_improver, ai_writer
from utils.openai_client import AIError
from utils.pdf_export import text_to_pdf_bytes
from utils.prompts import IMPROVE_MODES, WRITER_TASKS
from utils.text_extractor import word_count
from utils.validators import ValidationError

st.set_page_config(page_title="AI Smart Summarizer", page_icon="📝", layout="wide")
db.init_db()

st.markdown("""<style>
.card{padding:1.1rem 1.3rem;border-radius:14px;background:rgba(128,128,128,.09);
border:1px solid rgba(128,128,128,.25);margin-bottom:.8rem}
.card h4{margin:0 0 .3rem 0}
</style>""", unsafe_allow_html=True)

PAGES = ["🏠 Home", "📝 Text Summarizer", "📄 PDF Summarizer", "▶️ YouTube Summarizer",
         "✨ Text Improver", "🤖 AI Writing Assistant", "🕘 Summary History", "⚙️ Settings / About"]

st.session_state.setdefault("save_history", True)
st.session_state.setdefault("api_key", "")
st.session_state.setdefault("model", config.DEFAULT_MODEL)
st.session_state.setdefault("page", PAGES[0])


# ---------- helpers ----------
def guarded(fn, *args, **kwargs):
    try:
        with st.spinner("Working with OpenAI, please wait..."):
            return fn(*args, **kwargs)
    except (ValidationError, AIError) as e:
        st.error(str(e))
    except ValueError as e:
        st.error(str(e))
    except Exception as e:  # last resort
        st.error(f"Unexpected error: {type(e).__name__}: {e}")
    return None


def save(input_type, original, output, settings):
    if st.session_state.save_history:
        db.add_record(input_type, original, output, settings)


def set_result(key, output, source, **extra):
    st.session_state[key] = {"output": output, "source": source, **extra}


def show_result(key, title, filename):
    r = st.session_state.get(key)
    if not r:
        return
    out, src = r["output"], r["source"]
    st.success("Done!")
    c1, c2 = st.columns(2)
    c1.metric("Words before", word_count(src))
    c2.metric("Words after", word_count(out))
    st.markdown(out)
    with st.expander("📋 Copy text (use the copy icon at top-right of the box)"):
        st.code(out, language=None, wrap_lines=True)
    d1, d2 = st.columns(2)
    d1.download_button("⬇️ Download .txt", out, f"{filename}.txt", "text/plain", key=f"{key}_txt")
    try:
        d2.download_button("⬇️ Download PDF", text_to_pdf_bytes(title, out), f"{filename}.pdf",
                           "application/pdf", key=f"{key}_pdf")
    except Exception:
        d2.caption("PDF export unavailable for this text. Use the .txt download.")


def summary_options(prefix):
    c1, c2, c3 = st.columns(3)
    length = c1.selectbox("Length", ["Short", "Medium", "Detailed"], index=1, key=f"{prefix}_len")
    fmt = c2.selectbox("Format", ["Paragraph", "Bullet points"], key=f"{prefix}_fmt")
    lang = c3.selectbox("Language", config.LANGUAGES, key=f"{prefix}_lang")
    return length, fmt, lang


# ---------- pages ----------
def page_home():
    st.title("📝 AI Smart Summarizer & Text Improver")
    st.caption("Summarize text, PDFs and YouTube videos. Turn rough writing into polished English.")
    df = db.get_history(1000)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total items in history", len(df))
    m2.metric("Active model", st.session_state.model)
    m3.metric("API key", "Configured ✅" if (st.session_state.api_key or config.OPENAI_API_KEY) else "Missing ❌")
    cards = [("📝 Text Summarizer", "Short, medium or detailed summaries in any language."),
             ("📄 PDF Summarizer", "Multi-page PDFs with hierarchical summarization."),
             ("▶️ YouTube Summarizer", "Key points, topics and conclusions from transcripts."),
             ("✨ Text Improver", "Fix grammar, go professional, write formal emails."),
             ("🤖 AI Writing Assistant", "Rewrite, expand, simplify, keywords, Q&A."),
             ("🕘 Summary History", "Review and delete saved results.")]
    cols = st.columns(3)
    for i, (name, desc) in enumerate(cards):
        with cols[i % 3]:
            st.markdown(f'<div class="card"><h4>{name}</h4>{desc}</div>', unsafe_allow_html=True)
            st.button("Open", key=f"open_{i}",
                      on_click=lambda n=name: st.session_state.update(page=next(p for p in PAGES if n in p)))
    if not (st.session_state.api_key or config.OPENAI_API_KEY):
        st.warning("Add your OpenAI API key in `.env` or under Settings to get started.")


def page_text():
    st.header("📝 Text Summarizer")
    text = st.text_area("Paste your text", height=250, key="ts_in")
    st.caption(f"Words: {word_count(text)}")
    length, fmt, lang = summary_options("ts")
    if st.button("Summarize", type="primary", key="ts_btn"):
        out = guarded(text_summarizer.summarize_text, text, length, fmt, lang)
        if out:
            set_result("ts_res", out, text)
            save("Text", text, out, {"length": length, "format": fmt, "language": lang,
                                     "model": st.session_state.model})
    show_result("ts_res", "Text Summary", "text_summary")


def page_pdf():
    st.header("📄 PDF Summarizer")
    f = st.file_uploader("Upload a PDF (max 10 MB)", type=["pdf"], key="pdf_up")
    length, fmt, lang = summary_options("pdf")
    if st.button("Extract & Summarize", type="primary", key="pdf_btn"):
        if f is None:
            st.error("Please upload a PDF file first.")
        else:
            data = f.getvalue()
            ext = guarded(pdf_summarizer.extract, f.name, data)
            if ext:
                text, pages = ext
                out = guarded(pdf_summarizer.summarize_pdf_text, text, length, fmt, lang)
                if out:
                    set_result("pdf_res", out, text, pages=pages, name=f.name)
                    save("PDF", text, out, {"file": f.name, "pages": pages, "length": length,
                                            "format": fmt, "language": lang,
                                            "model": st.session_state.model})
    r = st.session_state.get("pdf_res")
    if r:
        st.info(f"File: {r['name']} · Pages: {r['pages']}")
        with st.expander("Extracted text"):
            st.text_area("Extracted", r["source"][:50000], height=250, key="pdf_ext_view")
    show_result("pdf_res", "PDF Summary", "pdf_summary")


def page_youtube():
    st.header("▶️ YouTube Summarizer")
    url = st.text_input("YouTube video URL", key="yt_url")
    lang = st.selectbox("Summary language", config.LANGUAGES, key="yt_lang")
    if st.button("Summarize Video", type="primary", key="yt_btn"):
        res = guarded(youtube_summarizer.summarize_youtube, url, lang)
        if res:
            set_result("yt_res", res["summary"], res["transcript"], title=res["title"], url=res["url"])
            save("YouTube", res["transcript"], res["summary"],
                 {"url": res["url"], "title": res["title"], "language": lang,
                  "model": st.session_state.model})
    r = st.session_state.get("yt_res")
    if r:
        st.subheader(r.get("title") or "Title not available")
        st.write(f"Source: {r['url']}")
        with st.expander("Transcript"):
            st.text_area("Transcript", r["source"][:50000], height=250, key="yt_tr_view")
    show_result("yt_res", r.get("title") or "YouTube Summary" if r else "", "youtube_summary")


def page_improve():
    st.header("✨ Text Improver")
    text = st.text_area("Enter rough, informal or incorrect text", height=220, key="ti_in")
    mode = st.selectbox("Improvement mode", list(IMPROVE_MODES), key="ti_mode")
    if st.button("Improve Text", type="primary", key="ti_btn"):
        out = guarded(text_improver.improve_text, text, mode)
        if out:
            set_result("ti_res", out, text)
            save("Text Improver", text, out, {"mode": mode, "model": st.session_state.model})
    show_result("ti_res", "Improved Text", "improved_text")


def page_writer():
    st.header("🤖 AI Writing Assistant")
    text = st.text_area("Your text", height=220, key="aw_in")
    task = st.selectbox("What should I do?", list(WRITER_TASKS), key="aw_task")
    if st.button("Run", type="primary", key="aw_btn"):
        out = guarded(ai_writer.run_task, text, task)
        if out:
            set_result("aw_res", out, text)
            save("Writing Assistant", text, out, {"task": task, "model": st.session_state.model})
    show_result("aw_res", task, "writing_result")


def page_history():
    st.header("🕘 Summary History")
    df = db.get_history()
    if df.empty:
        st.info("No history yet.")
        return
    st.dataframe(df[["id", "input_type", "created_at", "settings"]], use_container_width=True, hide_index=True)
    rid = st.selectbox("Select record ID", df["id"].tolist(), key="hist_id")
    rec = db.get_record(int(rid))
    if rec:
        with st.expander("Original text"):
            st.text(rec["original_text"] or "")
        st.markdown("**Output**")
        st.markdown(rec["output_text"])
        st.code(rec["output_text"], language=None, wrap_lines=True)
        st.download_button("⬇️ Download .txt", rec["output_text"], f"record_{rid}.txt", key="hist_dl")
    c1, c2 = st.columns(2)
    if c1.button("🗑️ Delete selected", key="hist_del"):
        db.delete_record(int(rid))
        st.rerun()
    if c2.button("⚠️ Clear ALL history", key="hist_clear"):
        db.clear_history()
        st.rerun()


def page_settings():
    st.header("⚙️ Settings / About")
    st.session_state.model = st.selectbox(
        "OpenAI model", config.AVAILABLE_MODELS,
        index=config.AVAILABLE_MODELS.index(st.session_state.model)
        if st.session_state.model in config.AVAILABLE_MODELS else 0)
    st.session_state.api_key = st.text_input(
        "OpenAI API key (this session only, never saved)", type="password",
        value=st.session_state.api_key, help="Leave empty to use the key from .env / secrets.")
    st.session_state.save_history = st.toggle("Save results to history (local SQLite)",
                                              value=st.session_state.save_history)
    st.markdown("**Theme:** open the ⋮ menu (top right) → Settings → Theme for light/dark.")
    st.markdown("---\n**About:** AI Smart Summarizer & Text Improver, built with Streamlit, "
                "the OpenAI Python SDK, PyMuPDF and youtube-transcript-api. AI output can contain "
                "mistakes, so please review important results.")


with st.sidebar:
    st.title("📝 AI Summarizer")
    st.radio("Navigation", PAGES, key="page", label_visibility="collapsed")

{"🏠": page_home, "📝": page_text, "📄": page_pdf, "▶️": page_youtube,
 "✨": page_improve, "🤖": page_writer, "🕘": page_history, "⚙️": page_settings
 }[st.session_state.page.split(" ")[0]]()