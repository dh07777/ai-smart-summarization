from openai import (OpenAI, AuthenticationError, RateLimitError, APIConnectionError,
                    APITimeoutError, APIStatusError, BadRequestError)

import config


class AIError(Exception):
    """User-friendly error from the AI layer."""


def _runtime(name: str, default):
    try:
        import streamlit as st
        return st.session_state.get(name) or default
    except Exception:
        return default


def chat(system: str, user: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
    api_key = _runtime("api_key", config.OPENAI_API_KEY)
    model = _runtime("model", config.DEFAULT_MODEL)
    if not api_key:
        raise AIError("No OpenAI API key found. Add OPENAI_API_KEY to your .env file "
                      "(or Streamlit secrets), or enter it in Settings.")
    client = OpenAI(api_key=api_key, timeout=60, max_retries=2)
    try:
        resp = client.chat.completions.create(
            model=model, max_tokens=max_tokens, temperature=temperature,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}])
    except AuthenticationError:
        raise AIError("Authentication failed: your OpenAI API key is invalid or revoked.")
    except RateLimitError as e:
        if "insufficient_quota" in str(e):
            raise AIError("OpenAI quota exceeded. Check your plan and billing at platform.openai.com.")
        raise AIError("Rate limit reached. Please wait a moment and try again.")
    except APITimeoutError:
        raise AIError("The request to OpenAI timed out. Please try again.")
    except APIConnectionError:
        raise AIError("Could not connect to OpenAI. Check your internet connection.")
    except BadRequestError as e:
        raise AIError(f"OpenAI rejected the request (model or input problem): {e}")
    except APIStatusError as e:
        raise AIError(f"OpenAI API error ({e.status_code}). Please try again later.")
    content = (resp.choices[0].message.content or "").strip()
    if not content:
        raise AIError("OpenAI returned an empty response. Please try again.")
    return content