"""
认证服务（使用 bcrypt 原生 API）
- 密码哈希与验证
- JWT 令牌创建与解析
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

import bcrypt
from jose import JWTError, jwt

from app.config.settings import settings


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行哈希加密，返回可直接存储的字符串
    """
    # 将密码转为字节，使用 bcrypt 生成哈希
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(data: Dict, expires_minutes: Optional[int] = None) -> str:
    """
    创建 JWT 访问令牌
    """
    to_encode = data.copy()
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict]:
    """
    解码 JWT 令牌
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None