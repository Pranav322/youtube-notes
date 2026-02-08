from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app, get_session
from app.models import Note
import pytest
import os

# Use an in-memory SQLite database for testing with StaticPool to share data
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session_override():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

@pytest.fixture(name="session")
def session_fixture():
    create_db_and_tables()
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@patch("app.main.extract_video_id")
@patch("app.main.get_raw_transcript")
@patch("app.main.generate_notes_map_reduce")
def test_limit_enforcement(mock_generate, mock_transcript, mock_extract, session):
    # Mock return values
    mock_extract.side_effect = lambda url: url.split("/")[-1]
    mock_transcript.return_value = [{"text": "foo", "start": 0, "duration": 1}]
    mock_generate.return_value = ("Detailed content", {"cost": 0.01, "input_tokens": 100, "output_tokens": 50})

    # User IP to test
    user_ip = "1.2.3.4"

    # Simulate headers for IP
    headers = {"X-Forwarded-For": user_ip}

    # Create 1st note
    response = client.post("/notes", json={"url": "http://youtube.com/vid1"}, headers=headers)
    assert response.status_code == 200

    # Create 2nd note
    response = client.post("/notes", json={"url": "http://youtube.com/vid2"}, headers=headers)
    assert response.status_code == 200

    # Create 3rd note - should fail
    response = client.post("/notes", json={"url": "http://youtube.com/vid3"}, headers=headers)
    assert response.status_code == 429
    assert "You've reached the limit of 2 videos." in response.json()["detail"]["message"]

@patch("app.main.extract_video_id")
@patch("app.main.get_raw_transcript")
@patch("app.main.generate_notes_map_reduce")
def test_admin_bypass(mock_generate, mock_transcript, mock_extract, session):
    # Mock return values
    mock_extract.side_effect = lambda url: url.split("/")[-1]
    mock_transcript.return_value = [{"text": "foo", "start": 0, "duration": 1}]
    mock_generate.return_value = ("Detailed content", {"cost": 0.01, "input_tokens": 100, "output_tokens": 50})

    # Admin IP
    admin_ip = "10.0.0.1"
    os.environ["ADMIN_IPS"] = admin_ip

    # Simulate headers for IP
    headers = {"X-Forwarded-For": admin_ip}

    # Create 1st note
    response = client.post("/notes", json={"url": "http://youtube.com/vid1"}, headers=headers)
    assert response.status_code == 200

    # Create 2nd note
    response = client.post("/notes", json={"url": "http://youtube.com/vid2"}, headers=headers)
    assert response.status_code == 200

    # Create 3rd note - should succeed for admin
    response = client.post("/notes", json={"url": "http://youtube.com/vid3"}, headers=headers)
    assert response.status_code == 200
