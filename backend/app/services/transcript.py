import re
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from fastapi import HTTPException


VIDEO_ID_REGEX = re.compile(r"(?:v=|\/live\/|\/shorts\/|\/embed\/|\/v\/|youtu\.be\/)([0-9A-Za-z_-]{11})")


def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    Supports standard, shortened, and embed URLs.
    """
    match = VIDEO_ID_REGEX.search(url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return match.group(1)


def get_raw_transcript(video_id: str) -> list[dict]:
    """
    Fetches the transcript for a given video ID and returns the raw list of segments.
    Each segment is a dict: {'text': '...', 'start': ..., 'duration': ...}
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        # Convert FetchedTranscriptSnippet objects to dicts
        return [{"text": item.text, "start": item.start, "duration": item.duration} for item in transcript_list]
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
