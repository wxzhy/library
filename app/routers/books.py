from urllib import response
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import aiomysql
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.dependencies import get_conn

router = APIRouter()


class Book(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    publisher: str
    publish_date: str
    category: str
    price: float
    stock_quantity: int
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: str
    publish_date: str
    category: str
    price: float
    stock_quantity: int
    description: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    description: Optional[str] = None


class BookResponse(BaseModel):
    records: List[Book]
    total: int
    current: int
    size: int

class BatchDeleteBooks(BaseModel):
    book_ids: List[int]

@router.get("/books", response_model=BookResponse)
async def get_books(
    current: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    publisher: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    conn: aiomysql.Connection = Depends(get_conn)
):
    """获取图书列表，支持分页和多条件搜索"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 构建查询条件
            where_conditions = []
            params = []
            
            # 全文搜索（在标题、作者、ISBN中搜索）
            if search:
                where_conditions.append("(title LIKE %s OR author LIKE %s OR isbn LIKE %s)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])
            
            # 按标题搜索
            if title:
                where_conditions.append("title LIKE %s")
                params.append(f"%{title}%")
            
            # 按作者搜索
            if author:
                where_conditions.append("author LIKE %s")
                params.append(f"%{author}%")
            
            # 按出版社搜索
            if publisher:
                where_conditions.append("publisher LIKE %s")
                params.append(f"%{publisher}%")
            
            # 按分类精确匹配
            if category:
                where_conditions.append("category = %s")
                params.append(category)
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # 获取总数
            count_sql = f"SELECT COUNT(*) as total FROM books WHERE {where_clause}"
            await cursor.execute(count_sql, params)
            total_result = await cursor.fetchone()
            total = total_result['total']
            
            # 获取分页数据
            offset = (current - 1) * size
            data_sql = f"""
                SELECT id, title, author, isbn, publisher, publish_date, category, 
                       price, stock_quantity, description, created_at, updated_at
                FROM books 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            await cursor.execute(data_sql, params + [size, offset])
            books = await cursor.fetchall()
            
            return BookResponse(
                records=[Book(**book) for book in books],
                total=total,
                current=current,
                size=size
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图书列表失败: {str(e)}")


@router.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int, conn: aiomysql.Connection = Depends(get_conn)):
    """获取单本图书详情"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = """
                SELECT id, title, author, isbn, publisher, publish_date, category,
                       price, stock_quantity, description, created_at, updated_at
                FROM books WHERE id = %s
            """
            await cursor.execute(sql, (book_id,))
            book = await cursor.fetchone()
            
            if not book:
                raise HTTPException(status_code=404, detail="图书不存在")
            
            return Book(**book)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图书详情失败: {str(e)}")


@router.post("/books", response_model=Book)
async def create_book(book_data: BookCreate, conn: aiomysql.Connection = Depends(get_conn)):
    """创建新图书"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查ISBN是否已存在
            check_sql = "SELECT id FROM books WHERE isbn = %s"
            await cursor.execute(check_sql, (book_data.isbn,))
            if await cursor.fetchone():
                raise HTTPException(status_code=400, detail="ISBN已存在")
            
            # 插入新图书
            sql = """
                INSERT INTO books (title, author, isbn, publisher, publish_date, category,
                                 price, stock_quantity, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            await cursor.execute(sql, (
                book_data.title, book_data.author, book_data.isbn, book_data.publisher,
                book_data.publish_date, book_data.category, book_data.price,
                book_data.stock_quantity, book_data.description
            ))
            
            # 获取新创建的图书ID
            book_id = cursor.lastrowid
            await conn.commit()
            response = await get_book(book_id, conn)
            # 将响应转换为JSON格式
            # 返回创建的图书信息
            return JSONResponse(status_code=201, content=jsonable_encoder(response))
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建图书失败: {str(e)}")


@router.put("/books/{book_id}", response_model=Book)
async def update_book(
    book_id: int, 
    book_data: BookUpdate, 
    conn: aiomysql.Connection = Depends(get_conn)
):
    """更新图书信息"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查图书是否存在
            check_sql = "SELECT id FROM books WHERE id = %s"
            await cursor.execute(check_sql, (book_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="图书不存在")
            
            # 构建更新语句
            update_fields = []
            params = []
            
            for field, value in book_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(value)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="没有提供要更新的字段")
            
            # 检查ISBN唯一性（如果要更新ISBN）
            if book_data.isbn:
                isbn_check_sql = "SELECT id FROM books WHERE isbn = %s AND id != %s"
                await cursor.execute(isbn_check_sql, (book_data.isbn, book_id))
                if await cursor.fetchone():
                    raise HTTPException(status_code=400, detail="ISBN已存在")
            
            # 执行更新
            sql = f"UPDATE books SET {', '.join(update_fields)}, updated_at = NOW() WHERE id = %s"
            params.append(book_id)
            await cursor.execute(sql, params)
            await conn.commit()
            
            # 返回更新后的图书信息
            return await get_book(book_id, conn)
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新图书失败: {str(e)}")


@router.delete("/books/{book_id}")
async def delete_book(book_id: int, conn: aiomysql.Connection = Depends(get_conn)):
    """删除图书"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查图书是否存在
            check_sql = "SELECT id FROM books WHERE id = %s"
            await cursor.execute(check_sql, (book_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="图书不存在")
            
            # 删除图书
            sql = "DELETE FROM books WHERE id = %s"
            await cursor.execute(sql, (book_id,))
            await conn.commit()
            
            return JSONResponse(
                status_code=204,
                content=None
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除图书失败: {str(e)}")


@router.get("/books/categories/list")
async def get_categories(conn: aiomysql.Connection = Depends(get_conn)):
    """获取所有图书分类"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = "SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category"
            await cursor.execute(sql)
            categories = await cursor.fetchall()
            
            return JSONResponse(
                status_code=200,
                content={"categories": [cat['category'] for cat in categories]}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")


@router.get("/books/authors/list")
async def get_authors(conn: aiomysql.Connection = Depends(get_conn)):
    """获取所有作者"""
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            sql = "SELECT DISTINCT author FROM books WHERE author IS NOT NULL ORDER BY author"
            await cursor.execute(sql)
            authors = await cursor.fetchall()
            
            return JSONResponse(
                status_code=200,
                content={"authors": [author['author'] for author in authors]}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取作者列表失败: {str(e)}")
    
@router.post('/books/batch-delete')
async def batch_delete_books(
    batch: BatchDeleteBooks,
    conn: aiomysql.Connection = Depends(get_conn)
):
    """批量删除图书"""

    if not batch.book_ids:
        raise HTTPException(status_code=400, detail="没有提供要删除的图书ID列表")
    book_ids = batch.book_ids
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # 检查图书是否存在
            check_sql = "SELECT id FROM books WHERE id IN %s"
            await cursor.execute(check_sql, (tuple(book_ids),))
            existing_books = await cursor.fetchall()
            existing_ids = {book['id'] for book in existing_books}
            
            if len(existing_ids) != len(book_ids):
                raise HTTPException(status_code=404, detail="部分图书ID不存在")
            
            # 执行批量删除
            delete_sql = "DELETE FROM books WHERE id IN %s"
            await cursor.execute(delete_sql, (tuple(book_ids),))
            await conn.commit()
            
            return JSONResponse(
                status_code=204,
                content=None
            )
    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除图书失败: {str(e)}")