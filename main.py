 
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with SessionLocal() as session:
        yield session


@app.post("/notes/", response_model=schemas.Note)
async def create_note(note: schemas.NoteCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_note(db, note)


@app.get("/notes/{user_id}", response_model=list[schemas.Note])
async def get_notes(user_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_notes_by_user(db, user_id)


@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_note(db, note_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}
