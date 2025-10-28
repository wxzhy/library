import aiomysql
from contextlib import asynccontextmanager
from fastapi import FastAPI

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1Qaz@wsx",
    "db": "library_management",
    "autocommit": True,
}

pool: aiomysql.Pool = None


async def get_pool():
    if pool is None:
        raise RuntimeError("数据库连接池未初始化")
    return pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await aiomysql.create_pool(**DB_CONFIG)
    print("数据库连接池已创建")
    yield
    pool.close()
    await pool.wait_closed()
    print("数据库连接池已关闭")
