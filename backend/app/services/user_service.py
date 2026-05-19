"""
用户服务
- 提供用户相关的数据库操作（注册、查询等）
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.model.user import User
from app.services.auth_service import hash_password, verify_password


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    根据用户名查询用户
    参数:
        db: 异步数据库会话
        username: 用户名
    返回:
        User 对象或 None
    """
    # 使用 select 语句异步查询
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    根据用户 ID 查询用户
    参数:
        db: 异步数据库会话
        user_id: 用户 ID
    返回:
        User 对象或 None
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, password: str, email: Optional[str] = None) -> User:
    """
    创建新用户（注册）
    参数:
        db: 异步数据库会话
        username: 用户名
        password: 明文密码（将在本函数内进行哈希处理）
        email: 邮箱（可选）
    返回:
        新创建的 User 对象（已包含自动生成的 ID、时间戳等）
    """
    # 对密码进行哈希
    hashed_pw = hash_password(password)

    # 构造用户对象（尚未持久化）
    new_user = User(
        username=username,
        hashed_password=hashed_pw,
        email=email,
    )

    # 添加到会话并刷新以获取数据库自动生成的字段（如 id、created_at）
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    验证用户凭据（用于登录）
    参数:
        db: 异步数据库会话
        username: 用户名
        password: 明文密码
    返回:
        User 对象（凭据有效）或 None（用户名不存在或密码错误）
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user