import sys
from unittest.mock import MagicMock
import os

# Create a mock for fastapi
mock_fastapi = MagicMock()
class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
mock_fastapi.HTTPException = HTTPException
sys.modules["fastapi"] = mock_fastapi

# Create a mock for youtube_transcript_api
sys.modules["youtube_transcript_api"] = MagicMock()

# Add backend to sys.path
sys.path.append(os.getcwd())

import pytest
from app.services.transcript import extract_video_id

@pytest.mark.parametrize("url,expected_id", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=abc_123-456", "abc_123-456"), # underscores and hyphens
])
def test_extract_video_id_success(url, expected_id):
    assert extract_video_id(url) == expected_id

@pytest.mark.parametrize("url", [
    "https://google.com",
    "https://youtube.com/watch?v=short", # too short
    "not_a_url",
    "",
])
def test_extract_video_id_invalid(url):
    with pytest.raises(HTTPException) as excinfo:
        extract_video_id(url)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Invalid YouTube URL"

def test_extract_video_id_bug_case():
    # This URL has an 11-char string in the path that is NOT the video ID.
    url = "https://www.youtube.com/abc-def_ghi/watch?v=dQw4w9WgXcQ"

    # Existing behavior: returns 'abc-def_ghi'
    # Desired behavior: returns 'dQw4w9WgXcQ'
    extracted = extract_video_id(url)
    assert extracted == "dQw4w9WgXcQ", f"Expected dQw4w9WgXcQ but got {extracted}"
