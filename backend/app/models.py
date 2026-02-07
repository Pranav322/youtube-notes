from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class NoteBase(SQLModel):
    video_id: str = Field(index=True)
    url: str
    title: Optional[str] = None
    content_detailed: Optional[str] = None
    # Cost tracking
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    generation_cost: Optional[float] = None  # USD


class Note(NoteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_ip: Optional[str] = Field(default=None)


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: int
    created_at: datetime
