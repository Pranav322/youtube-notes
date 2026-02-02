from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.db import create_db_and_tables, get_session
from app.models import Note, NoteRead
from app.services.transcript import extract_video_id, get_transcript_text
from app.services.ai import generate_technical_notes
from pydantic import BaseModel
from typing import Optional


class NoteRequest(BaseModel):
    url: str
    force_refresh: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "YouTube Technical Note-Taker API is running"}


@app.post("/notes", response_model=NoteRead)
async def create_note(request: NoteRequest, session: Session = Depends(get_session)):
    """
    Creates a new note from a YouTube URL.
    Checks if note exists first.
    """
    # 1. Extract Video ID
    video_id = extract_video_id(request.url)

    # 2. Check DB
    statement = select(Note).where(Note.video_id == video_id)
    existing_note = session.exec(statement).first()
    if existing_note:
        if not request.force_refresh:
            return existing_note
        else:
            session.delete(existing_note)
            session.commit()

    # 3. Fetch Transcript
    transcript_text = get_transcript_text(video_id)

    # 4. Generate AI Notes
    # TODO: Make this background task if it takes too long, but for now we wait (simple architecture)
    try:
        markdown_content = await generate_technical_notes(transcript_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

    # 5. Save to DB
    # Extract title logic could be better (fetching video metadata), but we'll leave it blank or simple for now
    # We could add a simple title fetcher later.
    new_note = Note(
        video_id=video_id,
        url=request.url,
        title=f"Notes for {video_id}",  # Placeholder
        markdown_content=markdown_content,
    )
    session.add(new_note)
    session.commit()
    session.refresh(new_note)

    return new_note


@app.get("/notes/{note_id}", response_model=NoteRead)
def read_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
