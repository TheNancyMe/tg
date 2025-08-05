import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.markdown import hbold
from config import BOT_TOKEN
from utils import add_note, list_notes, get_note, delete_note
from datetime import datetime

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить заметку➕")],
        [KeyboardButton(text="Список заметок📋")],
        [KeyboardButton(text="Удалить заметку🗑")]
    ],
    resize_keyboard=True
)

class AddNoteState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_passcode = State()

class ReadNoteState(StatesGroup):
    waiting_for_passcode = State()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Выбери действие:", reply_markup=main_kb)

@dp.message(F.text == "Добавить заметку")
async def add_note_start(message: Message, state: FSMContext):
    await message.answer("Введите заголовок заметки или напишите 'отмена' для выхода.")
    await state.set_state(AddNoteState.waiting_for_title)

@dp.message(AddNoteState.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer("Добавление заметки отменено.", reply_markup=main_kb)
        await state.clear()
        return
    await state.update_data(title=message.text)
    await message.answer("Введите описание или 'пропустить':")
    await state.set_state(AddNoteState.waiting_for_description)

@dp.message(AddNoteState.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание или 'пропустить':")
    await state.set_state(AddNoteState.waiting_for_description)

@dp.message(AddNoteState.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    description = None if message.text.lower() == "пропустить" else message.text
    await state.update_data(description=description)
    await message.answer("Введите код доступа или 'без кода':")
    await state.set_state(AddNoteState.waiting_for_passcode)

@dp.message(AddNoteState.waiting_for_passcode)
async def process_passcode(message: Message, state: FSMContext):
    data = await state.get_data()
    passcode = None if message.text.lower() == "без кода" else message.text
    try:
        note = await add_note(
            user_id=message.from_user.id,
            title=data["title"],
            description=data.get("description"),
            passcode=passcode
        )
        await message.answer(f"Заметка добавлена:\n<b>{note['title']}</b>", reply_markup=main_kb)
    except Exception as e:
        await message.answer(f"Ошибка при сохранении заметки: {e}")
    finally:
        await state.clear()

@dp.message(F.text == "Список заметок")
async def list_notes_handler(message: Message):
    notes = await list_notes(message.from_user.id)
    if not notes:
        await message.answer("У тебя нет заметок.")
        return
    text = "Твои заметки:\n\n"
    for note in notes:
        dt = datetime.fromisoformat(note['created_at'].replace("Z", "+00:00"))
        lock = "🔒" if note.get("passcode") else ""
        text += f"{hbold(note['id'])}: {note['title']} {lock} ({dt.strftime('%d.%m.%Y %H:%M')})\n"
    text += "\nЧтобы прочитать: /read ID\nЧтобы удалить: /delete ID"
    await message.answer(text)

@dp.message(Command("read"))
async def cmd_read(message: Message, state: FSMContext):
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Формат: /read ID")
        return
    await state.update_data(note_id=int(parts[1]))
    await message.answer("Введите код доступа или 'нет':")
    await state.set_state(ReadNoteState.waiting_for_passcode)

@dp.message(ReadNoteState.waiting_for_passcode)
async def process_read_passcode(message: Message, state: FSMContext):
    data = await state.get_data()
    note_id = data["note_id"]
    passcode = None if message.text.lower() == "нет" else message.text
    try:
        note = await get_note(note_id, passcode=passcode)
        await message.answer(f"<b>{note['title']}</b>\n\n{note['description'] or '(без описания)'}")
    except PermissionError:
        await message.answer("Неверный код доступа.")
    except Exception:
        await message.answer("Заметка не найдена.")
    finally:
        await state.clear()

@dp.message(Command("delete"))
async def cmd_delete(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Формат: /delete ID")
        return
    note_id = int(parts[1])
    success = await delete_note(note_id)
    await message.answer("Удалена." if success else "Не найдена.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
