from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import aiomysql
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from enum import Enum

from app.dependencies import get_conn, get_current_user_dependency

router = APIRouter()


class BorrowStatus(str, Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"
    RENEWED = "renewed"


class Borrow(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: BorrowStatus
    renewal_count: int = 0
    fine_amount: float = 0.0
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BorrowWithDetails(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    book_id: int
    book_title: str
    book_author: str
    book_isbn: str
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: BorrowStatus
    renewal_count: int = 0
    fine_amount: float = 0.0
    notes: Optional[str] = None
    days_overdue: Optional[int] = None


class BorrowCreate(BaseModel):
    user_id: Optional[int] = None  # 如果是管理员，可以指定用户ID
    book_id: int
    borrow_days: int = 30
    notes: Optional[str] = None


class BorrowReturn(BaseModel):
    notes: Optional[str] = None


class BorrowRenewal(BaseModel):
    renewal_days: int = 30
    notes: Optional[str] = None


class BorrowResponse(BaseModel):
    records: List[BorrowWithDetails]
    total: int
    current: int
    size: int


@router.get("/borrows", response_model=BorrowResponse)
async def get_borrows(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    book_id: Optional[int] = Query(None),
    status: Optional[BorrowStatus] = Query(None),
    search: Optional[str] = Query(None, description="搜索用户名、图书标题或作者"),
    overdue_only: bool = Query(False, description="只显示逾期记录"),
    conn: aiomysql.Connection = Depends(get_conn),
    current_user: dict = Depends(get_current_user_dependency),
):
    """获取借阅记录列表"""
    try:
        offset = (page - 1) * page_size
        
        # 构建查询条件
        where_conditions = ["1=1"]
        params = []
        if current_user.get("is_admin", True):
            if user_id:
                where_conditions.append("b.user_id = %s")
                params.append(user_id)
        else:
            where_conditions.append("b.user_id = %s")
            params.append(current_user["id"])
        if book_id:
            where_conditions.append("b.book_id = %s")
            params.append(book_id)
        
        if status:
            where_conditions.append("b.status = %s")
            params.append(status.value)
        
        if search:
            where_conditions.append(
                "(u.username LIKE %s OR bk.title LIKE %s OR bk.author LIKE %s)"
            )
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if overdue_only:
            where_conditions.append("b.due_date < NOW() AND b.status = 'borrowed'")
        
        where_clause = " AND ".join(where_conditions)
        
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 查询总数
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM borrows b
                JOIN users u ON b.user_id = u.id
                JOIN books bk ON b.book_id = bk.id
                WHERE {where_clause}
            """
            await cursor.execute(count_sql, params)
            total = (await cursor.fetchone())['total']
            
            # 查询数据
            data_sql = f"""
                SELECT b.id, b.user_id, u.username as user_name, u.email as user_email,
                       b.book_id, bk.title as book_title, bk.author as book_author, bk.isbn as book_isbn,
                       b.borrow_date, b.due_date, b.return_date, b.status, b.renewal_count,
                       b.fine_amount, b.notes,
                       CASE 
                           WHEN b.due_date < NOW() AND b.status = 'borrowed' 
                           THEN DATEDIFF(NOW(), b.due_date)
                           ELSE NULL 
                       END as days_overdue
                FROM borrows b
                JOIN users u ON b.user_id = u.id
                JOIN books bk ON b.book_id = bk.id
                WHERE {where_clause}
                ORDER BY b.borrow_date DESC
                LIMIT %s OFFSET %s
            """
            await cursor.execute(data_sql, params + [page_size, offset])
            borrows = await cursor.fetchall()
            
            return BorrowResponse(
                records=[BorrowWithDetails(**borrow) for borrow in borrows],
                total=total,
                current=page,
                size=page_size
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取借阅记录失败: {str(e)}")


@router.get("/borrows/{borrow_id}", response_model=BorrowWithDetails)
async def get_borrow(borrow_id: int, conn: aiomysql.Connection = Depends(get_conn)):
    """获取单条借阅记录详情"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = """
                SELECT b.id, b.user_id, u.username as user_name, u.email as user_email,
                       b.book_id, bk.title as book_title, bk.author as book_author, bk.isbn as book_isbn,
                       b.borrow_date, b.due_date, b.return_date, b.status, b.renewal_count,
                       b.fine_amount, b.notes,
                       CASE 
                           WHEN b.due_date < NOW() AND b.status = 'borrowed' 
                           THEN DATEDIFF(NOW(), b.due_date)
                           ELSE NULL 
                       END as days_overdue
                FROM borrows b
                JOIN users u ON b.user_id = u.id
                JOIN books bk ON b.book_id = bk.id
                WHERE b.id = %s
            """
            await cursor.execute(sql, (borrow_id,))
            borrow = await cursor.fetchone()
            
            if not borrow:
                raise HTTPException(status_code=404, detail="借阅记录不存在")
            
            return BorrowWithDetails(**borrow)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取借阅记录失败: {str(e)}")


@router.post("/borrows/borrow")
async def borrow_book(
    borrow_data: BorrowCreate, 
    conn: aiomysql.Connection = Depends(get_conn),
    current_user: dict = Depends(get_current_user_dependency)
    ):
    """借书"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            if not borrow_data.user_id:
                # 如果是普通用户，使用当前用户ID
                borrow_data.user_id = current_user['id']
            # 检查用户是否存在且可用
            await cursor.execute("SELECT id, is_active FROM users WHERE id = %s", (borrow_data.user_id,))
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            if not user['is_active']:
                raise HTTPException(status_code=400, detail="用户账户已被禁用")
            
            # 检查图书是否存在且有库存
            await cursor.execute("SELECT id, title, stock_quantity FROM books WHERE id = %s", (borrow_data.book_id,))
            book = await cursor.fetchone()
            if not book:
                raise HTTPException(status_code=404, detail="图书不存在")
            if book['stock_quantity'] <= 0:
                raise HTTPException(status_code=400, detail="图书库存不足")
            
            # 检查用户是否已借阅此书且未归还
            await cursor.execute(
                "SELECT id FROM borrows WHERE user_id = %s AND book_id = %s AND status = 'borrowed'",
                (borrow_data.user_id, borrow_data.book_id)
            )
            if await cursor.fetchone():
                raise HTTPException(status_code=400, detail="用户已借阅此书，请先归还")
            
            # 检查用户当前借阅数量（限制为5本）
            await cursor.execute(
                "SELECT COUNT(*) as count FROM borrows WHERE user_id = %s AND status = 'borrowed'",
                (borrow_data.user_id,)
            )
            current_borrows = (await cursor.fetchone())['count']
            if current_borrows >= 5:
                raise HTTPException(status_code=400, detail="借阅数量已达上限（5本）")
            
            # 创建借阅记录
            borrow_date = datetime.now()
            due_date = borrow_date + timedelta(days=borrow_data.borrow_days)
            
            await cursor.execute("""
                INSERT INTO borrows (user_id, book_id, borrow_date, due_date, status, notes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, 'borrowed', %s, NOW(), NOW())
            """, (borrow_data.user_id, borrow_data.book_id, borrow_date, due_date, borrow_data.notes))
            
            borrow_id = cursor.lastrowid
            
            # 减少图书库存
            # await cursor.execute(
            #     "UPDATE books SET stock_quantity = stock_quantity - 1 WHERE id = %s",
            #     (borrow_data.book_id,)
            # )
            
            await conn.commit()
            
            return JSONResponse(
                status_code=201,
                content={
                    "message": "借书成功",
                    "borrow_id": borrow_id,
                    "due_date": due_date.isoformat()
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"借书失败: {str(e)}")


@router.post("/borrows/{borrow_id}/return")
async def return_book(
    borrow_id: int, 
    return_data: BorrowReturn, 
    conn: aiomysql.Connection = Depends(get_conn)
):
    """还书"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 获取借阅记录
            await cursor.execute(
                "SELECT * FROM borrows WHERE id = %s AND status = 'borrowed'",
                (borrow_id,)
            )
            borrow = await cursor.fetchone()
            
            if not borrow:
                raise HTTPException(status_code=404, detail="借阅记录不存在或已归还")
            
            # 计算罚金（逾期每天1元）
            return_date = datetime.now()
            fine_amount = 0.0
            
            if return_date > borrow['due_date']:
                overdue_days = (return_date - borrow['due_date']).days
                fine_amount = overdue_days * 1.0  # 每天1元罚金
            
            # 更新借阅记录
            await cursor.execute("""
                UPDATE borrows 
                SET return_date = %s, status = 'returned', fine_amount = %s, 
                    notes = CONCAT(IFNULL(notes, ''), %s), updated_at = NOW()
                WHERE id = %s
            """, (return_date, fine_amount, f" [归还备注: {return_data.notes}]" if return_data.notes else "", borrow_id))
            
            # 增加图书库存
            # await cursor.execute(
            #     "UPDATE books SET stock_quantity = stock_quantity + 1 WHERE id = %s",
            #     (borrow['book_id'],)
            # )
            
            await conn.commit()
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "还书成功",
                    "return_date": return_date.isoformat(),
                    "fine_amount": fine_amount
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"还书失败: {str(e)}")


@router.post("/borrows/{borrow_id}/renew")
async def renew_book(
    borrow_id: int, 
    renewal_data: BorrowRenewal, 
    conn: aiomysql.Connection = Depends(get_conn)
):
    """续借"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 获取借阅记录
            await cursor.execute(
                "SELECT * FROM borrows WHERE id = %s AND status = 'borrowed'",
                (borrow_id,)
            )
            borrow = await cursor.fetchone()
            
            if not borrow:
                raise HTTPException(status_code=404, detail="借阅记录不存在或已归还")
            
            # 检查续借次数限制（最多续借2次）
            if borrow['renewal_count'] >= 2:
                raise HTTPException(status_code=400, detail="续借次数已达上限（2次）")
            
            # 检查是否逾期（逾期不能续借）
            if datetime.now() > borrow['due_date']:
                raise HTTPException(status_code=400, detail="图书已逾期，不能续借，请先归还")
            
            # 更新到期时间和续借次数
            new_due_date = borrow['due_date'] + timedelta(days=renewal_data.renewal_days)
            
            await cursor.execute("""
                UPDATE borrows 
                SET due_date = %s, renewal_count = renewal_count + 1,
                    notes = CONCAT(IFNULL(notes, ''), %s), updated_at = NOW()
                WHERE id = %s
            """, (new_due_date, f" [续借备注: {renewal_data.notes}]" if renewal_data.notes else "", borrow_id))
            
            await conn.commit()
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "续借成功",
                    "new_due_date": new_due_date.isoformat(),
                    "renewal_count": borrow['renewal_count'] + 1
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"续借失败: {str(e)}")


@router.get("/borrows/user/{user_id}")
async def get_user_borrows(
    user_id: int,
    status: Optional[BorrowStatus] = Query(None),
    conn: aiomysql.Connection = Depends(get_conn)
):
    """获取用户的借阅记录"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            where_clause = "b.user_id = %s"
            params = [user_id]
            
            if status:
                where_clause += " AND b.status = %s"
                params.append(status.value)
            
            sql = f"""
                SELECT b.id, b.book_id, bk.title as book_title, bk.author as book_author,
                       b.borrow_date, b.due_date, b.return_date, b.status, b.renewal_count,
                       b.fine_amount, b.notes,
                       CASE 
                           WHEN b.due_date < NOW() AND b.status = 'borrowed' 
                           THEN DATEDIFF(NOW(), b.due_date)
                           ELSE NULL 
                       END as days_overdue
                FROM borrows b
                JOIN books bk ON b.book_id = bk.id
                WHERE {where_clause}
                ORDER BY b.borrow_date DESC
            """
            await cursor.execute(sql, params)
            borrows = await cursor.fetchall()
            
            return JSONResponse(
                status_code=200,
                content={"borrows": borrows}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户借阅记录失败: {str(e)}")


@router.get("/borrows/stats/summary")
async def get_borrow_stats(conn: aiomysql.Connection = Depends(get_conn)):
    """获取借阅统计信息"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 当前借阅中的图书数量
            await cursor.execute("SELECT COUNT(*) as count FROM borrows WHERE status = 'borrowed'")
            current_borrows = (await cursor.fetchone())['count']
            
            # 逾期图书数量
            await cursor.execute(
                "SELECT COUNT(*) as count FROM borrows WHERE status = 'borrowed' AND due_date < NOW()"
            )
            overdue_borrows = (await cursor.fetchone())['count']
            
            # 今日借阅数量
            await cursor.execute(
                "SELECT COUNT(*) as count FROM borrows WHERE DATE(borrow_date) = CURDATE()"
            )
            today_borrows = (await cursor.fetchone())['count']
            
            # 今日归还数量
            await cursor.execute(
                "SELECT COUNT(*) as count FROM borrows WHERE DATE(return_date) = CURDATE()"
            )
            today_returns = (await cursor.fetchone())['count']
            
            # 总罚金
            await cursor.execute(
                "SELECT IFNULL(SUM(fine_amount), 0) as total FROM borrows WHERE fine_amount > 0"
            )
            total_fines = (await cursor.fetchone())['total']
            
            return JSONResponse(
                status_code=200,
                content={
                    "current_borrows": current_borrows,
                    "overdue_borrows": overdue_borrows,
                    "today_borrows": today_borrows,
                    "today_returns": today_returns,
                    "total_fines": float(total_fines)
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取借阅统计失败: {str(e)}")


@router.get("/borrows/overdue/list")
async def get_overdue_borrows(conn: aiomysql.Connection = Depends(get_conn)):
    """获取逾期借阅列表"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = """
                SELECT b.id, b.user_id, u.username, u.email, u.phone,
                       b.book_id, bk.title as book_title, bk.author as book_author,
                       b.borrow_date, b.due_date, b.renewal_count,
                       DATEDIFF(NOW(), b.due_date) as days_overdue
                FROM borrows b
                JOIN users u ON b.user_id = u.id
                JOIN books bk ON b.book_id = bk.id
                WHERE b.status = 'borrowed' AND b.due_date < NOW()
                ORDER BY b.due_date ASC
            """
            await cursor.execute(sql)
            overdue_borrows = await cursor.fetchall()
            
            return JSONResponse(
                status_code=200,
                content={"overdue_borrows": overdue_borrows}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取逾期列表失败: {str(e)}")
