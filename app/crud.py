 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from . import models, schemas

# Создание заметки
async def create_note(db: AsyncSession, note: schemas.NoteCreate):
    new_note = models.Note(**note.dict())
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

# Получение всех заметок пользователя
async def get_notes_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Note).where(models.Note.user_id == user_id))
    return result.scalars().all()

# Удаление заметки по id
async def delete_note(db: AsyncSession, note_id: int):
    result = await db.execute(delete(models.Note).where(models.Note.id == note_id))
    await db.commit()
    return result.rowcount  # сколько строк удалено