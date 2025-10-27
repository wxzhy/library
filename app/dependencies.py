from typing import AsyncGenerator
from aiomysql import Connection, DictCursor
from app.database import get_pool
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.security import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_conn() -> AsyncGenerator[Connection, None]:
    # print("获取数据库连接", await get_pool())
    async with (await get_pool()).acquire() as conn:
        # print(await get_pool(), conn)
        yield conn


async def get_user_by_username(conn, username: str) -> dict:
    async with conn.cursor(DictCursor) as cur:
        await cur.execute(
            "SELECT id, username, hashed_password, email,phone,full_name,is_admin, is_active FROM users WHERE username = %s",
            (username,),
        )
        return await cur.fetchone()

async def get_current_user(conn, user_id: int) -> dict:
    async with conn.cursor(DictCursor) as cur:
        await cur.execute(
            "SELECT id, username, hashed_password, is_admin, is_active FROM users WHERE id = %s",
            (user_id,),
        )
        return await cur.fetchone()


# 用户认证依赖函数 - 移到前面定义
async def get_current_user_dependency(
    token: str = Depends(oauth2_scheme),
    conn = Depends(get_conn),
) -> dict:
    """获取当前用户依赖函数"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userName: str = payload.get("sub")
        userId: int = payload.get("user_id")

        if not userName:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的访问令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="访问令牌已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_username(conn, userName)
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    return user

