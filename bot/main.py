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

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить заметку")],
        [KeyboardButton(text="Список заметок")],
        [KeyboardButton(text="Удалить заметку")]
    ],
    resize_keyboard=True
)

class AddNoteState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()

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
    await message.answer("Введите текст заметки или напишите 'пропустить', чтобы оставить пустым.")
    await state.set_state(AddNoteState.waiting_for_description)

@dp.message(AddNoteState.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await message.answer("Добавление заметки отменено.", reply_markup=main_kb)
        await state.clear()
        return

    data = await state.get_data()
    title = data["title"]
    description = None if message.text.lower() == "пропустить" else message.text

    if description is None:
        await message.answer("Действительно сохранить заметку без описания? (да/нет)")
        await state.update_data(confirm_without_desc=True)
    else:
        await save_note_and_finish(message, state, title, description)

@dp.message(AddNoteState.waiting_for_description, F.text.in_(["да", "нет"]))
async def confirm_without_description(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("confirm_without_desc") and message.text.lower() == "да":
        await save_note_and_finish(message, state, data["title"], None)
    else:
        await message.answer("Добавление заметки отменено.", reply_markup=main_kb)
        await state.clear()

async def save_note_and_finish(message: Message, state: FSMContext, title: str, description: str | None):
    try:
        note = await add_note(user_id=message.from_user.id, title=title, description=description)
        await message.answer(f"Заметка добавлена:\n<b>{note['title']}</b>", reply_markup=main_kb)
    except Exception:
        await message.answer("Ошибка при сохранении заметки.", reply_markup=main_kb)
    finally:
        await state.clear()

@dp.message(F.text == "Список заметок")
async def list_notes_handler(message: Message):
    def format_datetime(iso_str: str) -> str:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return dt.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return iso_str  # если что-то пойдёт не так — покажем как есть

    user_id = message.from_user.id
    notes = await list_notes(user_id)
    if not notes:
        await message.answer("У тебя пока нет заметок.")
        return
    text = "Твои заметки:\n\n"
    for note in notes:
        formatted_time = format_datetime(note['created_at'])
        text += f"{hbold(note['id'])}: {note['title']} ({formatted_time})\n"
    text += "\nЧтобы прочитать заметку, напиши: /read id"
    await message.answer(text)

@dp.message(Command("read"))
async def cmd_read(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /read id")
        return
    note_id = int(parts[1])
    try:
        note = await get_note(note_id)
        text = f"<b>{note['title']}</b>\n\n{note['description'] or '(без описания)'}"
        await message.answer(text)
    except Exception:
        await message.answer("Заметка не найдена.")


@dp.message(F.text == "Удалить заметку")
async def delete_note_handler(message: Message):
    await message.answer("Чтобы удалить заметку, напиши:\n/delete id_заметки")


@dp.message(Command("delete"))
async def cmd_delete(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /delete id")
        return
    note_id = int(parts[1])
    success = await delete_note(note_id)
    if success:
        await message.answer("Заметка удалена.")
    else:
        await message.answer("Заметка не найдена.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
