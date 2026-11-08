# AI Smart Summarizer & Text Improver

## Install
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env    # then add OPENAI_API_KEY

## Run
    streamlit run app.py

## Test
    pytest -v

## API key
Create a key at https://platform.openai.com/api-keys (billing required). Put it in `.env`.
On Streamlit Cloud, add it under App settings → Secrets.