import sys
import pytest
from unittest.mock import MagicMock, patch

# Define a fixture that mocks dependencies and imports the module
@pytest.fixture(scope="module")
def transcript_services():
    """
    Fixture to mock dependencies and import app.services.transcript.
    Uses patch.dict to safely mock sys.modules without permanent pollution.
    """
    # Create the mocks
    mock_fastapi = MagicMock()

    # Define the custom exception
    class MockHTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail
    mock_fastapi.HTTPException = MockHTTPException

    # Patch sys.modules
    with patch.dict(sys.modules, {
        "youtube_transcript_api": MagicMock(),
        "fastapi": mock_fastapi,
    }):
        # Ensure we re-import the module to pick up the mocks
        if "app.services.transcript" in sys.modules:
            del sys.modules["app.services.transcript"]

        import app.services.transcript
        yield app.services.transcript

        # Cleanup: remove the module so it doesn't pollute subsequent tests
        if "app.services.transcript" in sys.modules:
            del sys.modules["app.services.transcript"]

def test_extract_video_id_standard(transcript_services):
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert transcript_services.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_shortened(transcript_services):
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert transcript_services.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_embed(transcript_services):
    url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
    assert transcript_services.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_with_params(transcript_services):
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
    assert transcript_services.extract_video_id(url) == "dQw4w9WgXcQ"

def test_extract_video_id_invalid(transcript_services):
    url = "https://www.google.com"
    # We need to use the HTTPException class from the mocked module's import source
    # The module imports HTTPException from fastapi, which is our mock
    # Accessing it via sys.modules["fastapi"] works because the fixture context is active
    HTTPException = sys.modules["fastapi"].HTTPException

    with pytest.raises(HTTPException) as excinfo:
        transcript_services.extract_video_id(url)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Invalid YouTube URL"

def test_extract_video_id_empty(transcript_services):
    url = ""
    HTTPException = sys.modules["fastapi"].HTTPException

    with pytest.raises(HTTPException) as excinfo:
        transcript_services.extract_video_id(url)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Invalid YouTube URL"
