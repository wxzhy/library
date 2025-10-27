# 抓取测试数据
import aiohttp
import aiomysql
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "1Qaz@wsx",
    "db": "library_management",
    "autocommit": True,
}
import asyncio
async with aiomysql.create_pool(**DB_CONFIG) as pool:
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # 插入数据
            await cursor.execute("""
                INSERT INTO books (title, author, published_date)
                VALUES ('The Great Gatsby', 'F. Scott Fitzgerald', '1925-04-10')
            """)

            await conn.commit()