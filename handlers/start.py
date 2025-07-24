from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from db.database import create_user_if_not_exists

router = Router()

@router.message(Command("start"))
async def handle_start(message: Message):
    await create_user_if_not_exists(message.from_user.id, message.from_user.full_name)
    await message.answer("Привет! Я твой бот для учёта трат 💸")

