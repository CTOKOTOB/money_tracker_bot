import os
import asyncpg
from dotenv import load_dotenv
from datetime import datetime, date

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

async def add_benefit(telegram_id: int, amount: float, description: str = None):
    query_get_user_id = """
    SELECT id FROM app.users WHERE telegram_id = $1
    """
    insert_benefit = """
    INSERT INTO app.benefits (user_id, amount, description)
    VALUES ($1, $2, $3)
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow(query_get_user_id, telegram_id)
        if user_row is None:
            raise ValueError(f"❌ Пользователь с telegram_id={telegram_id} не найден")
        user_id = user_row["id"]
        await conn.execute(insert_benefit, user_id, amount, description)

async def delete_last_benefit(telegram_id: int):
    query_get_user_id = "SELECT id FROM app.users WHERE telegram_id = $1"
    query_delete_last_benefit = """
    DELETE FROM app.benefits
    WHERE id = (
        SELECT id FROM app.benefits
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 1
    )
    RETURNING amount, description, created_at
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        user_row = await conn.fetchrow(query_get_user_id, telegram_id)
        if not user_row:
            raise ValueError("Пользователь не найден")
        user_id = user_row["id"]
        deleted = await conn.fetchrow(query_delete_last_benefit, user_id)
        return deleted

async def get_last_benefit_for_user(telegram_id: int):
    query = """
    SELECT b.id, b.amount, b.description, b.created_at
    FROM app.benefits b
    JOIN app.users u ON u.id = b.user_id
    WHERE u.telegram_id = $1
    ORDER BY b.created_at DESC
    LIMIT 1
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, telegram_id)

async def get_monthly_benefits_report(telegram_id: int, year: int, month: int):
    """
    Возвращает список (день, сумма доходов) за указанный месяц и год.
    """
    query = """
    SELECT
        EXTRACT(DAY FROM b.created_at) AS day,
        SUM(b.amount) AS total_amount
    FROM app.benefits b
    JOIN app.users u ON u.id = b.user_id
    WHERE u.telegram_id = $1
      AND EXTRACT(YEAR FROM b.created_at) = $2
      AND EXTRACT(MONTH FROM b.created_at) = $3
    GROUP BY day
    ORDER BY day
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, telegram_id, year, month)


async def get_monthly_expenses_report(telegram_id: int, year: int, month: int):
    """
    Возвращает сумму расходов по категориям за указанный месяц и год.
    """
    query = """
    SELECT
        c.name AS category_name,
        SUM(e.amount) AS total_amount
    FROM app.expenses e
    JOIN app.categories c ON c.id = e.category_id
    JOIN app.users u ON u.id = e.user_id
    WHERE u.telegram_id = $1
      AND EXTRACT(YEAR FROM e.created_at) = $2
      AND EXTRACT(MONTH FROM e.created_at) = $3
    GROUP BY c.name
    ORDER BY total_amount DESC
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, telegram_id, year, month)

async def get_monthly_benefits_full(telegram_id: int, year: int, month: int):
    """
    Возвращает список всех доходов с датой, суммой и описанием.
    """
    query = """
    SELECT b.amount, b.description, b.created_at
    FROM app.benefits b
    JOIN app.users u ON u.id = b.user_id
    WHERE u.telegram_id = $1
      AND EXTRACT(YEAR FROM b.created_at) = $2
      AND EXTRACT(MONTH FROM b.created_at) = $3
    ORDER BY b.created_at
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, telegram_id, year, month)

async def get_user_categories(telegram_id: int):
    query = """
    SELECT c.id, c.name
    FROM app.categories c
    JOIN app.users u ON c.user_id = u.id
    WHERE u.telegram_id = $1
    ORDER BY c.name
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, telegram_id)

async def get_category_name(telegram_id: int, category_id: int):
    query = """
    SELECT c.name
    FROM app.categories c
    JOIN app.users u ON c.user_id = u.id
    WHERE u.telegram_id = $1 AND c.id = $2
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, telegram_id, category_id)
        return row["name"] if row else None

async def get_detailed_category_expenses(telegram_id: int, category_id: int, year: int, month: int):
    query = """
    SELECT e.amount, e.description, e.created_at
    FROM app.expenses e
    JOIN app.categories c ON c.id = e.category_id
    JOIN app.users u ON u.id = e.user_id
    WHERE u.telegram_id = $1
      AND e.category_id = $2
      AND EXTRACT(YEAR FROM e.created_at) = $3
      AND EXTRACT(MONTH FROM e.created_at) = $4
    ORDER BY e.created_at
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(query, telegram_id, category_id, year, month)

async def get_available_years_for_category(telegram_id: int, category_id: int):
    query = """
    SELECT DISTINCT EXTRACT(YEAR FROM e.created_at)::int AS year
    FROM app.expenses e
    JOIN app.users u ON u.id = e.user_id
    WHERE u.telegram_id = $1
      AND e.category_id = $2
    ORDER BY year DESC
    """
    pool = get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, telegram_id, category_id)
        return [row["year"] for row in rows]
