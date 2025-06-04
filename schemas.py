from pydantic import BaseModel
from datetime import datetime

#созданиe новой заметки
class NoteCreate(BaseModel):
    user_id: int
    content: str
#ответ API
class Note(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True  # позволяет работать с объектами SQLAlchemy
