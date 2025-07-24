from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db.database import db

router = Router()

@router.message(Command("start"))
async def handle_start(message: Message):
    await db.create_user_if_not_exists(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name
    )
    await message.answer("👋 Привет! Я помогу тебе отслеживать расходы.")

