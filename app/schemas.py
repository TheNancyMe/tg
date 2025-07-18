from pydantic import BaseModel
from datetime import datetime

# Создание новой заметки
class NoteCreate(BaseModel):
    user_id: int
    title: str
    description: str | None = None

# Ответ API
class Note(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None = None
    created_at: datetime

    class Config:
        orm_mode = True
