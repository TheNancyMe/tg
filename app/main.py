 
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

app = FastAPI(
    title="Note API",
    description="API для создания, получения и удаления заметок",
    version="1.0.0"
)

# CORS — на будущее, если бот будет обращаться из другого источника
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание таблиц при запуске (временно, вместо Alembic)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Зависимость для получения сессии
async def get_db():
    async with SessionLocal() as session:
        yield session

# POST /notes/ — создать заметку
@app.post("/notes/", response_model=schemas.Note)
async def create_note(note: schemas.NoteCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_note(db, note)

# GET /notes/{user_id} — получить заметки пользователя
@app.get("/notes/{user_id}", response_model=list[schemas.Note])
async def get_notes(user_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_notes_by_user(db, user_id)

# DELETE /notes/{note_id} — удалить заметку
from fastapi.responses import Response

@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_note(db, note_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return Response(status_code=204)