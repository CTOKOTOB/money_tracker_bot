import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("MONEYBOT_DATABASE_URL")

_db_pool = None

async def init_db():
    global _db_pool
    _db_pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    print("✅ DB pool initialized")

def get_db_pool():
    if _db_pool is None:
        raise RuntimeError("DB pool is not initialized. Call init_db() first.")
    return _db_pool

async def create_user_if_not_exists(telegram_id: int, name: str = None):
    query = """
    INSERT INTO app.users (telegram_id, name)
    VALUES ($1, $2)
    ON CONFLICT (telegram_id) DO NOTHING;
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(query, telegram_id, name)
