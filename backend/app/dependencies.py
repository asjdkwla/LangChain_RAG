"""
全局依赖
提供数据库会话、认证依赖等可复用的 FastAPI 依赖函数
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings

# 数据库引擎与会话工厂
# create_async_engine：创建异步数据库引擎，连接 MySQL 使用 aiomysql 驱动
#   - settings.MYSQL_URL 由 settings.py 动态拼接，格式如：mysql+aiomysql://user:pass@host:port/db
#   - echo=False         表示不打印 SQL 日志（生产环境推荐；调试时可设为 True）
#   - pool_size=20       连接池保持的连接数
#   - max_overflow=10    当连接池满时可额外创建的连接数（最大总连接数 = 20 + 10 = 30）
#   - pool_pre_ping=True 每次从连接池取出连接前先发 SELECT 1 探测连接是否有效，避免使用已断开的连接
engine = create_async_engine(
    settings.MYSQL_URL,
    echo=False,               # 生产环境关闭 SQL 日志
    pool_size=20,             # 连接池大小
    max_overflow=10,          # 超出 pool_size 时可额外创建的连接数
    pool_pre_ping=False,       # 每次从池中取出连接时先 ping 测试可用性
)

# sessionmaker：创建异步会话工厂，每次调用产生一个 AsyncSession 实例
#   - expire_on_commit=False 提交后对象不会过期，允许在提交后继续访问属性（如 id 字段）
async_session_factory = sessionmaker(engine, class_ = AsyncSession, expire_on_commit = False,)


# 用于依赖注入的数据库会话工具函数
async def get_db() -> AsyncSession:
    """
    FastAPI 依赖，提供异步数据库会话
    用法：
        @router.get("/items")
        async def read_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()