from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.db import create_db_and_tables, get_session
from app.models import Note, NoteRead
from app.services.transcript import extract_video_id, get_raw_transcript
from app.services.ai import generate_notes_map_reduce
from pydantic import BaseModel, HttpUrl
from typing import Optional


class NoteRequest(BaseModel):
    url: HttpUrl
    force_refresh: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "YouTube Technical Note-Taker API is running"}


@app.post("/notes", response_model=NoteRead)
async def create_note(
    request: NoteRequest, req: Request, session: Session = Depends(get_session)
):
    """
    Creates a new note from a YouTube URL.
    Checks if note exists first.
    Enforces a limit of 2 videos per user (IP address).
    Admin IPs are exempt from this limit.
    """
    # Whitelisted IPs that bypass the 2-video limit
    # Load from ADMIN_IPS env var (comma-separated) or use defaults
    import os
    admin_ips_env = os.getenv("ADMIN_IPS", "")
    ADMIN_IPS = set(ip.strip() for ip in admin_ips_env.split(",") if ip.strip())
    
    # Get real client IP (Cloudflare sends it in headers)
    # Priority: CF-Connecting-IP > X-Forwarded-For > req.client.host
    cf_ip = req.headers.get("cf-connecting-ip")
    forwarded_for = req.headers.get("x-forwarded-for")
    
    if cf_ip:
        user_ip = cf_ip
    elif forwarded_for:
        # X-Forwarded-For can have multiple IPs, first one is the client
        user_ip = forwarded_for.split(",")[0].strip()
    else:
        user_ip = req.client.host if req.client else "unknown"
    
    is_admin = user_ip in ADMIN_IPS

    # 1. Extract Video ID
    video_id = extract_video_id(str(request.url))

    # 2. Check DB
    statement = select(Note).where(Note.video_id == video_id)
    existing_note = session.exec(statement).first()

    if existing_note:
        if not request.force_refresh:
            return existing_note
        else:
            # Check limit before deleting/recreating
            user_notes_stmt = select(Note).where(Note.user_ip == user_ip)
            user_notes = session.exec(user_notes_stmt).all()

            is_own_note = existing_note.user_ip == user_ip

            # If refreshing someone else's note, we are adding to our count
            if not is_admin and not is_own_note and len(user_notes) >= 2:
                raise HTTPException(
                    status_code=403, detail="Limit of 2 videos reached per user."
                )

            session.delete(existing_note)
            session.commit()

    else:
        # Check limit for new note
        user_notes_stmt = select(Note).where(Note.user_ip == user_ip)
        user_notes = session.exec(user_notes_stmt).all()
        if not is_admin and len(user_notes) >= 2:
            raise HTTPException(
                status_code=403, detail="Limit of 2 videos reached per user."
            )

    # 3. Fetch Transcript
    transcript_segments = get_raw_transcript(video_id)

    # 4. Generate AI Notes (Map-Reduce only)
    try:
        content_detailed, cost_stats = await generate_notes_map_reduce(transcript_segments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

    # 5. Save to DB (including cost tracking)
    new_note = Note(
        video_id=video_id,
        url=str(request.url),
        title=f"Notes for {video_id}",
        content_detailed=content_detailed,
        input_tokens=cost_stats.get("input_tokens"),
        output_tokens=cost_stats.get("output_tokens"),
        generation_cost=cost_stats.get("cost"),
        user_ip=user_ip,
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
