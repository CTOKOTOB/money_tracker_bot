import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("MONEYBOT_DATABASE_URL")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def create_user_if_not_exists(self, telegram_id: int, name: str = None):
        query = """
        INSERT INTO app.users (telegram_id, name)
        VALUES ($1, $2)
        ON CONFLICT (telegram_id) DO NOTHING;
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, telegram_id, name)

db = Database()

async def init_db():
    await db.connect()

