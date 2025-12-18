from typing import Any, Optional
import jwt
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from ..dependencies import (
    get_conn,
    get_user_by_username,
    get_current_user_dependency,
    oauth2_scheme,
)
from . import borrows
from ..security import (
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter()


def hash_password(password: str) -> str:
    """使用SHA256加密密码（不使用salt）"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return hash_password(plain_password) == hashed_password


# 响应模型
class LoginRequest(BaseModel):
    userName: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str  # 新增字段
    token_type: str = "bearer"
    expires_in: int = 3600


class UserInfo(BaseModel):
    userId: int
    userName: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    roles: list = ["user"]


class RefreshTokenRequest(BaseModel):
    refreshToken: str


class Refresh(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class StatisticsResponse(BaseModel):
    books: int
    users: int
    borrows: int
    total_borrows: int


# 登录接口 - 支持JSON格式请求
@router.post("/auth/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    conn=Depends(get_conn),
):
    """用户登录"""
    try:
        user = await get_user_by_username(conn, login_data.userName)
        if not user or not verify_password(
            login_data.password, user["hashed_password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="账户已被禁用"
            )

        access_token = create_access_token(
            data={"sub": user["username"], "user_id": user["id"]}
        )
        refresh_token = create_refresh_token(
            data={"sub": user["username"], "user_id": user["id"]}
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # 返回 refresh token
            token_type="bearer",
            expires_in=3600,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}",
        )


# 兼容表单登录
@router.post("/auth/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn=Depends(get_conn),
):
    """表单登录接口（兼容性）"""
    login_data = LoginRequest(userName=form_data.username, password=form_data.password)
    result = await login(login_data, conn)
    return JSONResponse(content=jsonable_encoder(result))


# 获取当前用户信息
@router.get("/auth/getUserInfo", response_model=UserInfo)
async def get_user_info(
    current_user: dict = Depends(get_current_user_dependency),
) -> UserInfo:
    """获取当前用户信息"""
    print(f"当前用户信息: {current_user}")  # 调试输出
    try:
        return UserInfo(
            userId=current_user["id"],
            userName=current_user["username"],
            email=current_user.get("email", ""),
            full_name=current_user.get("full_name", ""),
            phone=current_user.get("phone"),
            is_active=current_user.get("is_active", True),
            roles=["admin"] if current_user.get("is_admin", False) else ["user"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}",
        )


# 更新用户信息


# 刷新token
@router.post("/auth/refresh-token", response_model=LoginResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    conn=Depends(get_conn),
):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        payload = jwt.decode(
            refresh_data.refreshToken, SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")

        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
            )

        # 验证用户是否存在且激活
        user = await get_user_by_username(conn, username)
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被禁用"
            )

        # 生成新的访问令牌
        new_access_token = create_access_token(
            data={"sub": username, "user_id": user_id}
        )

        return Refresh(
            access_token=new_access_token, token_type="bearer", expires_in=3600
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌已过期"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}",
        )


# 验证用户角色的依赖函数
def require_admin():
    """需要管理员权限的依赖函数"""

    async def _require_admin(current_user: dict = Depends(get_current_user_dependency)):
        if not current_user.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
            )
        return current_user

    return _require_admin


# 登出接口（可选）
@router.post("/auth/logout")
async def logout():
    """用户登出"""
    # 由于使用JWT，服务端无状态，客户端删除token即可
    return JSONResponse(status_code=200, content={"message": "登出成功"})


# 错误处理端点
@router.post("/auth/error")
async def custom_backend_error(code: str, msg: str):
    """自定义后端错误"""
    return JSONResponse(status_code=400, content={"code": code, "message": msg})


# 兼容旧接口
@router.get("/auth/getUser")
async def get_current_user_legacy(
    current_user: dict = Depends(get_current_user_dependency),
) -> Any:
    """获取当前用户（兼容旧接口）"""
    return current_user


@router.get("/auth/refresh")
async def refresh_token_legacy(
    token: str = Depends(oauth2_scheme),
    conn=Depends(get_conn),
) -> Any:
    """刷新token（兼容旧接口）"""
    refresh_data = RefreshTokenRequest(refreshToken=token)
    result = await refresh_token(refresh_data, conn)
    return JSONResponse(content=jsonable_encoder(result))
