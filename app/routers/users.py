from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import aiomysql
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import hashlib
import re

from app.dependencies import get_conn, get_current_user_dependency

router = APIRouter()


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    phone: Optional[str] = None
    is_admin: Optional[bool] = False


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str

class UserResetPassword(BaseModel):
    new_password: str

class UserResponse(BaseModel):
    records: List[User]  # 改为 records
    total: int
    current: int
    size: int

class BatchDeleteUsers(BaseModel):
    user_ids: List[int]

def hash_password(password: str) -> str:
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password(password: str) -> bool:
    """密码强度验证"""
    if len(password) < 6:
        return False
    if not re.search(r'[A-Za-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True


def validate_phone(phone: str) -> bool:
    """手机号验证"""
    if not phone:
        return True  # 允许为空
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


@router.get("/users", response_model=UserResponse)
async def list_users(
    current: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量，最大100"),
    username: Optional[str] = Query(None, description="用户名搜索"),
    full_name: Optional[str] = Query(None, description="姓名搜索"),
    phone: Optional[str] = Query(None, description="手机号搜索"),
    email: Optional[str] = Query(None, description="邮箱搜索"),
    is_active: Optional[bool] = Query(None, description="用户状态筛选"),
    is_admin: Optional[bool] = Query(None, description="管理员筛选"),
    conn: aiomysql.Connection = Depends(get_conn)
):
    """获取用户列表，支持分页和分字段搜索"""
    try:
        offset = (current - 1) * size
        page = current
        page_size = size
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        # 分别处理每个搜索字段
        if username:
            where_conditions.append("username LIKE %s")
            params.append(f"%{username}%")
        
        if full_name:
            where_conditions.append("full_name LIKE %s")
            params.append(f"%{full_name}%")
        
        if phone:
            where_conditions.append("phone LIKE %s")
            params.append(f"%{phone}%")
        
        if email:
            where_conditions.append("email LIKE %s")
            params.append(f"%{email}%")
        
        if is_active is not None:
            where_conditions.append("is_active = %s")
            params.append(is_active)
        
        if is_admin is not None:
            where_conditions.append("is_admin = %s")
            params.append(is_admin)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM users WHERE {where_clause}"
            await cursor.execute(count_sql, params)
            total_result = await cursor.fetchone()
            total = total_result['total']
            
            # 查询当前页数据
            data_sql = f"""
                SELECT id, username, email, full_name, phone, is_active, is_admin, 
                       created_at, updated_at
                FROM users 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            await cursor.execute(data_sql, params + [page_size, offset])
            users = await cursor.fetchall()
            
            return UserResponse(
                records=[User(**user) for user in users],
                total=total,
                current=page,
                size=page_size
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户列表失败: {str(e)}")


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, conn: aiomysql.Connection = Depends(get_conn)):
    """获取单个用户详情"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = """
                SELECT id, username, email, full_name, phone, is_active, is_admin,
                       created_at, updated_at
                FROM users WHERE id = %s
            """
            await cursor.execute(sql, (user_id,))
            user = await cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            return User(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")


@router.post("/users", response_model=User)
async def create_user(user_data: UserCreate, conn: aiomysql.Connection = Depends(get_conn)):
    """创建新用户"""
    try:
        # 数据验证
        if not validate_password(user_data.password):
            raise HTTPException(
                status_code=400, 
                detail="密码强度不够，至少6位且包含字母和数字"
            )
        
        if user_data.phone and not validate_phone(user_data.phone):
            raise HTTPException(status_code=400, detail="手机号格式不正确")
        
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查用户名是否已存在
            await cursor.execute("SELECT id FROM users WHERE username = %s", (user_data.username,))
            if await cursor.fetchone():
                raise HTTPException(status_code=400, detail="用户名已存在")
            
            # 检查邮箱是否已存在
            await cursor.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
            if await cursor.fetchone():
                raise HTTPException(status_code=400, detail="邮箱已存在")
            
            # 创建用户
            hashed_password = hash_password(user_data.password)
            sql = """
                INSERT INTO users (username, email, hashed_password, full_name, phone, 
                                 is_admin, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            await cursor.execute(sql, (
                user_data.username, user_data.email, hashed_password,
                user_data.full_name, user_data.phone, user_data.is_admin
            ))
            
            user_id = cursor.lastrowid
            await conn.commit()
            
            # 返回创建的用户信息
            return await get_user(user_id, conn)
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@router.put("/users", response_model=User)
async def update_self(
    user_data: UserUpdate, 
    current_user: dict = Depends(get_current_user_dependency),
    conn: aiomysql.Connection = Depends(get_conn)
):
    """更新用户信息"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查用户是否存在
            await cursor.execute("SELECT id FROM users WHERE id = %s", (current_user["id"],))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="用户不存在")
            user_id = current_user["id"]
            # 构建更新语句
            update_fields = []
            params = []
            
            update_data = user_data.dict(exclude_unset=True)
            
            # 验证数据
            if 'phone' in update_data and update_data['phone'] and not validate_phone(update_data['phone']):
                raise HTTPException(status_code=400, detail="手机号格式不正确")
            
            # 检查用户名唯一性
            if 'username' in update_data:
                await cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", 
                                    (update_data['username'], user_id))
                if await cursor.fetchone():
                    raise HTTPException(status_code=400, detail="用户名已存在")
            
            # 检查邮箱唯一性
            if 'email' in update_data:
                await cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", 
                                    (update_data['email'], user_id))
                if await cursor.fetchone():
                    raise HTTPException(status_code=400, detail="邮箱已存在")
            
            for field, value in update_data.items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="没有提供要更新的字段")
            
            # 执行更新
            sql = f"UPDATE users SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"
            params.append(user_id)
            await cursor.execute(sql, params)
            await conn.commit()
            
            # 返回更新后的用户信息
            return await get_user(user_id, conn)
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int, 
    user_data: UserUpdate, 
    conn: aiomysql.Connection = Depends(get_conn)
):
    """更新用户信息"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查用户是否存在
            await cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 构建更新语句
            update_fields = []
            params = []
            
            update_data = user_data.dict(exclude_unset=True)
            
            # 验证数据
            if 'phone' in update_data and update_data['phone'] and not validate_phone(update_data['phone']):
                raise HTTPException(status_code=400, detail="手机号格式不正确")
            
            # 检查用户名唯一性
            if 'username' in update_data:
                await cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", 
                                    (update_data['username'], user_id))
                if await cursor.fetchone():
                    raise HTTPException(status_code=400, detail="用户名已存在")
            
            # 检查邮箱唯一性
            if 'email' in update_data:
                await cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", 
                                    (update_data['email'], user_id))
                if await cursor.fetchone():
                    raise HTTPException(status_code=400, detail="邮箱已存在")
            
            for field, value in update_data.items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="没有提供要更新的字段")
            
            # 执行更新
            sql = f"UPDATE users SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"
            params.append(user_id)
            await cursor.execute(sql, params)
            await conn.commit()
            
            # 返回更新后的用户信息
            return await get_user(user_id, conn)
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, conn: aiomysql.Connection = Depends(get_conn)):
    """删除用户"""
    try:
        async with conn.cursor() as cursor:
            # 检查用户是否存在
            await cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 删除用户
            await cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            await conn.commit()
            
            return JSONResponse(
                status_code=204,
                content=None
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")


@router.patch("/users/change-password")
async def change_password(
    password_data: UserChangePassword, 
    current_user: dict = Depends(get_current_user_dependency),
    conn: aiomysql.Connection = Depends(get_conn)
):
    """修改用户密码"""
    try:
        if not validate_password(password_data.new_password):
            raise HTTPException(
                status_code=400, 
                detail="新密码强度不够，至少6位且包含字母和数字"
            )
        
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 验证旧密码
            await cursor.execute("SELECT hashed_password FROM users WHERE id = %s", (current_user["id"],))
            user = await cursor.fetchone()
            user_id = current_user["id"]
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            old_password_hash = hash_password(password_data.old_password)
            if user['hashed_password'] != old_password_hash:
                raise HTTPException(status_code=400, detail="原密码错误")
            
            # 更新密码
            new_password_hash = hash_password(password_data.new_password)
            await cursor.execute(
                "UPDATE users SET hashed_password = %s, updated_at = NOW() WHERE id = %s",
                (new_password_hash, user_id)
            )
            await conn.commit()
            
            return JSONResponse(
                status_code=200,
                content={"message": "密码修改成功"}
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"修改密码失败: {str(e)}")

#管理员重置用户密码
@router.patch('/users/{user_id}/reset-password')
async def reset_user_password(
    user_id: int, 
    data: UserResetPassword, 
    current_user: dict = Depends(get_current_user_dependency),
    conn: aiomysql.Connection = Depends(get_conn)
):
    """管理员重置用户密码"""
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="需要管理员权限")

    if not validate_password(data.new_password):
        raise HTTPException(
            status_code=400, 
            detail="新密码强度不够，至少6位且包含字母和数字"
        )
    
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查用户是否存在
            await cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 更新密码
            new_password_hash = hash_password(data.new_password)
            await cursor.execute(
                "UPDATE users SET hashed_password = %s, updated_at = NOW() WHERE id = %s",
                (new_password_hash, user_id)
            )
            await conn.commit()
            
            return JSONResponse(
                status_code=200,
                content={"message": "密码重置成功"}
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"重置密码失败: {str(e)}")

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: int, conn: aiomysql.Connection = Depends(get_conn)):
    """切换用户状态（启用/禁用）"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 获取当前状态
            await cursor.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
            user = await cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            # 切换状态
            new_status = not user['is_active']
            await cursor.execute(
                "UPDATE users SET is_active = %s, updated_at = NOW() WHERE id = %s",
                (new_status, user_id)
            )
            await conn.commit()
            
            status_text = "启用" if new_status else "禁用"
            return JSONResponse(
                status_code=200,
                content={"message": f"用户已{status_text}", "is_active": new_status}
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"切换用户状态失败: {str(e)}")


@router.post("/auth/register")
async def register_user(user_data: UserCreate, conn: aiomysql.Connection = Depends(get_conn)):
    """用户注册（公开接口）"""
    # 强制设置为非管理员
    user_data.is_admin = False
    return await create_user(user_data, conn)


@router.get("/users/stats/summary")
async def get_user_stats(user: dict = Depends(get_current_user_dependency),
                         conn: aiomysql.Connection = Depends(get_conn)):
    """获取用户统计信息"""
    try:
        id= user.get("id")
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 总借阅次数
            await cursor.execute("SELECT COUNT(*) as total FROM borrows WHERE user_id = %s", (id,))
            total_borrows = (await cursor.fetchone())['total']

            # 当前借阅数
            await cursor.execute("SELECT COUNT(*) as active FROM borrows WHERE status = 'borrowed' AND user_id = %s", (id,))
            active_borrows = (await cursor.fetchone())['active']

            # 逾期借阅数
            await cursor.execute("SELECT COUNT(*) as overdue FROM borrows WHERE status = 'overdue' AND user_id = %s", (id,))
            overdue_borrows = (await cursor.fetchone())['overdue']
            
            return JSONResponse(
                status_code=200,
                content={
                    "total_borrows": total_borrows,
                    "active_borrows": active_borrows,
                    "overdue_borrows": overdue_borrows
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户统计失败: {str(e)}")

@router.get('/statistics')
# 站点统计
async def get_statistics(conn: aiomysql.Connection = Depends(get_conn)):
    """获取站点统计信息"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 用户总数
            await cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = (await cursor.fetchone())['total_users']

            # 图书总数
            await cursor.execute("SELECT COUNT(*) as total_books FROM books")
            total_books = (await cursor.fetchone())['total_books']

            # 借阅总数
            await cursor.execute("SELECT COUNT(*) as total_borrows FROM borrows")
            total_borrows = (await cursor.fetchone())['total_borrows']
            
            # 当前借阅数
            await cursor.execute("SELECT COUNT(*) as active_borrows FROM borrows WHERE status = 'borrowed'")
            active_borrows = (await cursor.fetchone())['active_borrows']

            # 逾期借阅数
            await cursor.execute("SELECT COUNT(*) as overdue_borrows FROM borrows WHERE status = 'overdue'")
            overdue_borrows = (await cursor.fetchone())['overdue_borrows']

            return JSONResponse(
                status_code=200,
                content={
                    "total_users": total_users,
                    "total_books": total_books,
                    "total_borrows": total_borrows,
                    "active_borrows": active_borrows,
                    "overdue_borrows": overdue_borrows
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取站点统计失败: {str(e)}")

@router.post('/users/batch-delete')
async def batch_delete_users(
    batch: BatchDeleteUsers, 
    current_user: dict = Depends(get_current_user_dependency),
    conn: aiomysql.Connection = Depends(get_conn)
):
    """批量删除用户"""
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    if not batch.user_ids:
        raise HTTPException(status_code=400, detail="没有提供要删除的用户ID列表")
    user_ids = batch.user_ids
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
             # 检查用户是否存在
            await cursor.execute("SELECT id FROM users WHERE id IN %s", (tuple(user_ids),))
            existing_users = await cursor.fetchall()
            existing_ids = {user['id'] for user in existing_users}
            
            if len(existing_ids) != len(user_ids):
                raise HTTPException(status_code=404, detail="部分用户不存在")
            
            # 执行批量删除
            await cursor.execute("DELETE FROM users WHERE id IN %s", (tuple(user_ids),))
            await conn.commit()
            
            return JSONResponse(
                status_code=204,
                content=None
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除用户失败: {str(e)}")