# pyright: ignore[reportMissingImports]
import os
import psycopg
from psycopg_pool import AsyncConnectionPool

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "sslmode": "require"
    }
)


async def init_db():
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    is_subscribed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)


async def add_user(telegram_id: int):
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO users (telegram_id)
                VALUES (%s)
                ON CONFLICT (telegram_id) DO NOTHING;
            """, (telegram_id,))


async def activate_subscription(telegram_id: int):
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                UPDATE users
                SET is_subscribed = TRUE
                WHERE telegram_id = %s;
            """, (telegram_id,))


async def get_user(telegram_id: int):
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT * FROM users
                WHERE telegram_id = %s;
            """, (telegram_id,))
            return await cur.fetchone()