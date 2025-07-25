import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from db.database import init_db

from handlers import start, expense, income, delete_income, report, report_detail

load_dotenv()

bot = Bot(token=os.getenv("MONEYBOT_TOKEN"))
dp = Dispatcher()

async def main():
    await init_db()

    dp.include_router(start.router)
    dp.include_router(expense.router)
    dp.include_router(income.router)
    dp.include_router(delete_income.router)
    dp.include_router(report.router)
    dp.include_router(report_detail.router)

    try:
        print("🚀 Бот запущен")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("🛑 Бот остановлен вручную")
    finally:
        await bot.session.close()
        print("✅ Сессия бота закрыта")

if __name__ == "__main__":
    asyncio.run(main())
