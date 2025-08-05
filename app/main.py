from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas, crud
from .database import engine, Base, get_session
from typing import List, Optional

app = FastAPI()

origins = ["*"]  # или настрой по желанию

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/notes/", response_model=schemas.NoteOut)
async def create_note(note: schemas.NoteCreate, session: AsyncSession = Depends(get_session)):
    return await crud.create_note(session, note)

@app.get("/notes/{user_id}", response_model=List[schemas.NoteOut])
async def get_notes(user_id: int, session: AsyncSession = Depends(get_session)):
    return await crud.get_notes_by_user(session, user_id)

@app.get("/note/{note_id}", response_model=schemas.NoteOut)
async def get_note(note_id: int, passcode: Optional[str] = Query(None), session: AsyncSession = Depends(get_session)):
    note = await crud.get_note_by_id(session, note_id)
    if note.passcode and note.passcode != passcode:
        raise HTTPException(status_code=403, detail="Неверный код доступа")
    return note

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, session: AsyncSession = Depends(get_session)):
    success = await crud.delete_note_by_id(session, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return {"status": "deleted"}
