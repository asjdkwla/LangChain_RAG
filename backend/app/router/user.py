"""
用户路由
提供用户注册、登录、获取当前用户信息的 API 接口
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, field_validator, field_serializer

from app.dependencies import get_db
from app.config.settings import settings
from app.services.user_service import (
    create_user, authenticate_user, get_user_by_username, get_user_by_id,
)
from app.services.auth_service import create_access_token, decode_access_token

router = APIRouter()

# 使用标准的 HTTPBearer 提取 Token（更可靠）
security = HTTPBearer()

# ── Pydantic 模型 ──
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = Field(None, max_length=100)

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("用户名不能包含空格")
        return v

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserInfoResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()

    model_config = {"from_attributes": True}

# ── 认证依赖 ──
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 中缺少 sub")
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户 ID 格式错误")
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    return user

# ── 接口 ──
@router.post("/register", response_model=UserInfoResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user = await create_user(db=db, username=request.username, password=request.password, email=request.email)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    access_token = create_access_token(data={"sub": str(user.id)})
    expires_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    print("生成的 Token 长度:", len(access_token))
    print("Token 前 50 字符:", access_token[:50])
    return TokenResponse(access_token=access_token, expires_in=expires_seconds)

@router.get("/me", response_model=UserInfoResponse)
async def get_me(current_user = Depends(get_current_user)):
    return current_user

