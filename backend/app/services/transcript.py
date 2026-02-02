import re
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from fastapi import HTTPException


def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    Supports standard, shortened, and embed URLs.
    """
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return match.group(1)


def get_transcript_text(video_id: str) -> str:
    """
    Fetches the transcript for a given video ID and returns it as a single string.
    """
    try:
        # Fetch the transcript (returns a list of dicts: {'text': '...', 'start': ..., 'duration': ...})
        # Note: YouTubeTranscriptApi in this version requires instantiation
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)

        # Concatenate text parts
        full_text = " ".join([item.text for item in transcript_list])

        # Clean up whitespace
        return " ".join(full_text.split())

    except TranscriptsDisabled:
        raise HTTPException(
            status_code=400, detail="Transcripts are disabled for this video."
        )
    except NoTranscriptFound:
        raise HTTPException(
            status_code=400, detail="No transcript found for this video."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching transcript: {str(e)}"
        )
