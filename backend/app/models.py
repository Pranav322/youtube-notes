from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class NoteBase(SQLModel):
    video_id: str = Field(index=True)
    url: str
    title: Optional[str] = None
    markdown_content: Optional[str] = None


class Note(NoteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: int
    created_at: datetime
