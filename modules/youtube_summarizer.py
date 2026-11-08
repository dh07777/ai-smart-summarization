import json
from urllib.parse import quote
from urllib.request import urlopen

from youtube_transcript_api import (YouTubeTranscriptApi, TranscriptsDisabled,
                                    NoTranscriptFound, VideoUnavailable,
                                    CouldNotRetrieveTranscript)

from modules.text_summarizer import condense
from utils.openai_client import chat
from utils.prompts import SUMMARY_SYSTEM, YOUTUBE_PROMPT
from utils.validators import ValidationError, extract_video_id


def get_title(url: str):
    try:
        endpoint = f"https://www.youtube.com/oembed?url={quote(url, safe='')}&format=json"
        with urlopen(endpoint, timeout=8) as r:
            return json.loads(r.read().decode()).get("title")
    except Exception:
        return None


def fetch_transcript(video_id: str) -> str:
    try:
        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id)
        try:
            tr = transcripts.find_transcript(["en", "en-US", "en-GB"])
        except NoTranscriptFound:
            tr = next(iter(transcripts))
        text = " ".join(s.text for s in tr.fetch()).strip()
    except TranscriptsDisabled:
        raise ValidationError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise ValidationError("No transcript is available for this video.")
    except VideoUnavailable:
        raise ValidationError("This video is unavailable (private, removed, or region-blocked).")
    except StopIteration:
        raise ValidationError("No transcript is available for this video.")
    except CouldNotRetrieveTranscript as e:
        raise ValidationError(
            "Could not retrieve the transcript. YouTube may be blocking requests from this "
            "server's IP (common on cloud hosts), or the video has no captions. "
            f"Details: {type(e).__name__}")
    except Exception as e:
        raise ValidationError(f"Transcript extraction failed: {type(e).__name__}")
    if not text:
        raise ValidationError("The transcript is empty, so there is nothing to summarize.")
    return text


def summarize_youtube(url: str, language: str = "English") -> dict:
    video_id = extract_video_id(url)
    if not video_id:
        raise ValidationError("That is not a valid YouTube video URL.")
    transcript = fetch_transcript(video_id)  # raises if unavailable: never fake a summary
    condensed = condense(transcript, language)
    summary = chat(SUMMARY_SYSTEM, YOUTUBE_PROMPT.format(language=language, text=condensed),
                   max_tokens=1500)
    return {"title": get_title(url), "url": url.strip(), "video_id": video_id,
            "transcript": transcript, "summary": summary}