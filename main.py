import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import start
from db.database import init_db

load_dotenv()

bot = Bot(token=os.getenv("MONEYBOT_TOKEN"))
dp = Dispatcher()

async def main():
    await init_db()

    dp.include_router(start.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

