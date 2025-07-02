import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.markdown import hbold

from config import BOT_TOKEN
from utils import add_note, list_notes, delete_note

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Reply клавиатура с понятными кнопками
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить заметку")],
        [KeyboardButton(text="Список заметок")],
        [KeyboardButton(text="Удалить заметку")]
    ],
    resize_keyboard=True
)

from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="add", description="Добавить заметку"),
        BotCommand(command="list", description="Список заметок"),
        BotCommand(command="delete", description="Удалить заметку"),
        BotCommand(command="start", description="Перезапустить бота"),
    ]
    await bot.set_my_commands(commands)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Выбери действие:", reply_markup=main_kb)

# Обработка нажатия кнопки "Добавить заметку"
@dp.message(F.text == "Добавить заметку")
async def add_note_handler(message: Message):
    await message.answer("Напиши текст заметки в формате:\n/add Текст заметки")

# Обработка команды добавления заметки
@dp.message(Command("add"))
async def cmd_add(message: Message):
    user_id = message.from_user.id
    content = message.text.replace("/add", "", 1).strip()

    if not content:
        await message.answer("Использование: /add текст заметки")
        return

    note = await add_note(user_id=user_id, content=content)
    await message.answer(f"Заметка добавлена:\n{note['content']}")

# Обработка нажатия кнопки "Список заметок"
@dp.message(F.text == "Список заметок")
async def list_notes_handler(message: Message):
    user_id = message.from_user.id
    notes = await list_notes(user_id)

    if not notes:
        await message.answer("У тебя пока нет заметок.")
        return

    text = "Твои заметки:\n\n"
    for note in notes:
        text += f"{hbold(note['id'])}: {note['content']}\n"

    await message.answer(text)

# Обработка нажатия кнопки "Удалить заметку"
@dp.message(F.text == "Удалить заметку")
async def delete_note_handler(message: Message):
    await message.answer("Чтобы удалить заметку, напиши:\n/delete id_заметки")

# Обработка команды удаления заметки
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
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
