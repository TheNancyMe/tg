from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.markdown import hbold

from config import BOT_TOKEN
from utils import add_note, list_notes, delete_note

import asyncio

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для заметок.\nДоступные команды:\n/add [текст]\n/list\n/delete [id]")


@dp.message(Command("add"))
async def cmd_add(message: Message):
    user_id = message.from_user.id
    content = message.text.replace("/add", "", 1).strip()

    if not content:
        await message.answer("Использование: /add [текст заметки]")
        return

    note = await add_note(user_id=user_id, content=content)
    await message.answer(f"Заметка добавлена:\n{note['content']}")


@dp.message(Command("list"))
async def cmd_list(message: Message):
    user_id = message.from_user.id
    notes = await list_notes(user_id)

    if not notes:
        await message.answer("У тебя пока нет заметок.")
        return

    text = "Твои заметки:\n\n"
    for note in notes:
        text += f"{hbold(note['id'])}: {note['content']}\n"

    await message.answer(text)


@dp.message(Command("delete"))
async def cmd_delete(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /delete [id]")
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