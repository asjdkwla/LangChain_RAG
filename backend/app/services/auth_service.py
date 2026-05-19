"""
认证服务
- 密码哈希与验证（使用 passlib + bcrypt）
- JWT 令牌创建与解析（使用 python-jose）
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import settings


# 密码哈希上下文
# CryptContext 封装了密码哈希算法的配置
#   - schemes=["bcrypt"]   使用 bcrypt 算法进行哈希
#   - deprecated="auto"    自动处理过时的哈希方案
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    对明文密码进行哈希加密
    参数:
        plain_password: 用户输入的明文密码
    返回:
        加密后的哈希字符串（可直接存储到数据库）
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码是否与已存储的哈希密码匹配
    参数:
        plain_password: 用户输入的明文密码
        hashed_password: 数据库中存储的哈希密码
    返回:
        True 表示匹配，False 表示不匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

# JWT 令牌服务
def create_access_token(data: Dict, expires_minutes: Optional[int] = None) -> str:
    """
    创建 JWT 访问令牌
    参数:
        data: 要编码到令牌中的声明（至少包含 "sub" 字段，如用户 ID）
        expires_minutes: 令牌过期时间（分钟），若未指定则使用全局配置
    返回:
        编码后的 JWT 字符串
    """
    # 复制一份数据，避免修改原始字典
    to_encode = data.copy()

    # 计算过期时间
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    # 添加过期时间声明
    to_encode.update({"exp": expire})

    # 签发 JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict]:
    """
    解码 JWT 访问令牌，验证签名与过期时间
    参数:
        token: 客户端提交的 JWT 字符串
    返回:
        解码后的声明字典（若令牌有效），None（若令牌无效或已过期）
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # JWTError 涵盖了签名错误、过期、格式错误等所有异常
        return None