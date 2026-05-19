"""
FastAPI 应用入口
- 加载全局配置
- 初始化数据库引擎与表结构
- 注册路由与中间件
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.model.base import Base  # 需要提前创建 base.py（见下文）
from app.router import user, chat, knowledge_router, health
from app.dependencies import engine, get_db

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    启动时：创建所有未存在的表
    关闭时：释放数据库连接池
    """
    # 启动
    # 使用 engine.begin() 开启一个事务，通过 run_sync 在异步上下文中执行同步建表操作
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭
    await engine.dispose()


# 创建 FastAPI 实例
app = FastAPI(title="LangChain RAG Service", lifespan=lifespan)

# 中间件注册
# CORS（跨域资源共享）中间件：允许前端（可能部署在不同域名/端口）访问后端 API
#   - allow_origins=["*"]          允许所有来源（开发阶段方便，生产环境应改为具体域名如 ["https://example.com"]）
#   - allow_credentials=True       允许携带 Cookie 等凭证信息
#   - allow_methods=["*"]          允许所有 HTTP 方法（GET, POST, PUT, DELETE 等）
#   - allow_headers=["*"]          允许所有请求头
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#
# # 路由注册
# 各模块路由均以 Router 对象形式定义在对应文件中，通过 include_router 挂载到主应用
# prefix 参数为该模块下所有接口统一添加 URL 前缀
# tags 参数用于在自动生成的 API 文档（/docs）中对接口进行分组显示
app.include_router(health.router, tags=["Health"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(knowledge_router.router, prefix="/api/knowledge", tags=["Knowledge"])

# 根路径与调试信息
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "LangChain RAG Service",
        "version": "1.0.0",
        "docs": "/docs",
    }


