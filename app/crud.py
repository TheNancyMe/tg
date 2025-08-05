from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from .models import Note
from .schemas import NoteCreate

async def create_note(session: AsyncSession, note: NoteCreate) -> Note:
    new_note = Note(**note.dict())
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return new_note

async def get_notes_by_user(session: AsyncSession, user_id: int):
    result = await session.execute(select(Note).where(Note.user_id == user_id))
    return result.scalars().all()

async def get_note_by_id(session: AsyncSession, note_id: int) -> Note:
    result = await session.execute(select(Note).where(Note.id == note_id))
    return result.scalar_one()

async def delete_note_by_id(session: AsyncSession, note_id: int) -> bool:
    note = await get_note_by_id(session, note_id)
    if note:
        await session.delete(note)
        await session.commit()
        return True
    return False
