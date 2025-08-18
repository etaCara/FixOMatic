import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

# Environment variables
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DB = os.getenv("DB")
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 3306))

# Connection pool
pool = None

async def init_db_pool():
    global pool
    if pool is None:
        pool = await aiomysql.create_pool(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            db=DB,
            autocommit=True,
        )

async def close_db_pool():
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        pool = None

async def get_connection():
    global pool
    if pool is None:
        await init_db_pool()
    conn = await pool.acquire()
    return conn
