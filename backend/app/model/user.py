"""
用户模型
对应数据库中的 users 表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.model.base import Base


class User(Base):
    """
    用户表
    字段：
        id              - 主键，自增
        username        - 用户名，唯一，不可为空
        hashed_password - 经过 bcrypt 哈希后的密码
        email           - 电子邮箱（可选）
        created_at      - 账户创建时间
    """
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")

    # 用户名（唯一约束，最大长度 50）
    username = Column(String(50), unique=True, nullable=False, comment="用户名")

    # 加密后的密码（存储 bcrypt 哈希结果，长度设为 255 足够）
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")

    # 邮箱（可选，最大长度 100）
    email = Column(String(100), nullable=True, comment="电子邮箱")

    # 创建时间（默认当前时间）
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        """开发者友好的字符串表示"""
        return f"<User(id={self.id}, username='{self.username}')>"