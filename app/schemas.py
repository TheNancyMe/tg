from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteCreate(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    passcode: Optional[str] = None

class NoteOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    passcode: Optional[str] = None

    class Config:
        orm_mode = True
