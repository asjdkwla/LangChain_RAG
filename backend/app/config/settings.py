"""
应用全局配置
基于 pydantic-settings 加载 .env 环境变量
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ==============================================
    # LLM 大模型配置
    # ==============================================
    LLM_TYPE: str = Field(default="ALIYUN", description="LLM类型：ALIYUN | OLLAMA")

    # Ollama 配置（仅 LLM_TYPE=OLLAMA 时生效）
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL_NAME: str = Field(default="qwen3.5:0.8b")

    # 阿里云百炼配置（仅 LLM_TYPE=ALIYUN 时生效）
    ALIYUN_ACCESS_KEY_SECRET: str = Field(default="your_api_key", description="阿里云 DashScope API Key")
    ALIYUN_BASE_URL: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    CHAT_MODEL_NAME: str = Field(default="qwen3-max")

    # ==============================================
    # 向量嵌入模型配置
    # ==============================================
    EMBED_MODEL_TYPE: str = Field(default="ALIYUN", description="嵌入模型类型：OLLAMA | ALIYUN")
    TEXT_EMBEDDING_MODEL_NAME: str = Field(default="qwen3-embedding:0.6b", description="Ollama 嵌入模型")
    ALIYUN_EMBED_MODEL_NAME: str = Field(default="text-embedding-v4", description="阿里云百炼嵌入模型")

    # ==============================================
    # 数据库配置
    # ==============================================
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str = Field(default="root")
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_DATABASE: str = Field(default="chat_history")

    @property
    def MYSQL_URL(self) -> str:
        """构造异步 MySQL 连接 URL"""
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    # ==============================================
    # Redis 配置
    # ==============================================
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    # ==============================================
    # JWT 身份验证配置（替代原 Django 用户服务）
    # ==============================================
    SECRET_KEY: str = Field(default="your-super-secret-jwt-key")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)

    # ==============================================
    # Skills 技能系统配置
    # ==============================================
    SKILLS_ROOT: str = Field(default="./skills", description="技能定义文件根目录")
    SKILL_DEFAULT_SELECT_STRATEGY: str = Field(default="llm", description="技能选择策略：keyword | llm")

    # ==============================================
    # LangSmith 调试追踪
    # ==============================================
    LANGCHAIN_TRACING_V2: bool = Field(default=False)
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None)
    LANGCHAIN_PROJECT: Optional[str] = Field(default="fastapi-langchain-project")

    # ==============================================
    # 重排序模型配置
    # ==============================================
    RERANK_MODEL_NAME: str = Field(default="qwen3-rerank", description="阿里云百炼重排序模型名称")

    # ==============================================
    # RAG 核心参数
    # ==============================================
    RETRIEVAL_TOP_K: int = Field(default=5, description="检索时返回的最大文档数")
    CHUNK_SIZE: int = Field(default=200, description="文档切块大小（字符数）")
    CHUNK_OVERLAP: int = Field(default=20, description="文档块重叠大小")
    RERANK_TOP_K: int = Field(default=3, description="重排序后保留的文档数")
    UPLOAD_DIR: str = Field(default="./uploads", description="文件上传目录")
    MAX_UPLOAD_SIZE_MB: int = Field(default=50, description="最大上传文件大小（MB）")
    ALLOWED_EXTENSIONS: str = Field(default="txt,pdf,md,docx", description="允许上传的文件扩展名，逗号分隔")

    @property
    def allowed_extension_list(self) -> List[str]:
        """将逗号分隔的扩展名字符串转换为列表"""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略未定义的环境变量


# 全局单例
settings = Settings()