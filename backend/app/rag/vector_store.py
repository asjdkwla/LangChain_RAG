"""
向量存储服务
使用阿里云百炼嵌入模型将文本块向量化，并存入 ChromaDB
"""
import os
from typing import List, Optional, Dict
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

from app.config.settings import settings

# ── 全局单例：嵌入模型 ──
# 根据 .env 中的 EMBED_MODEL_TYPE 决定使用哪个嵌入服务
if settings.EMBED_MODEL_TYPE.upper() == "ALIYUN":
    embedding_model = DashScopeEmbeddings(
        model=settings.ALIYUN_EMBED_MODEL_NAME,
        dashscope_api_key=settings.ALIYUN_ACCESS_KEY_SECRET,
    )
else:
    # 预留 Ollama 等其他嵌入模型扩展
    from langchain_community.embeddings import OllamaEmbeddings
    embedding_model = OllamaEmbeddings(
        model=settings.TEXT_EMBEDDING_MODEL_NAME,
        base_url=settings.OLLAMA_BASE_URL,
    )

# ── ChromaDB 客户端 ──
_chroma_client = chromadb.PersistentClient(
    path="./chroma_db",   # 向量数据持久化目录
    settings=ChromaSettings(anonymized_telemetry=False),
)


def get_collection_name(user_id: int) -> str:
    """
    为每个用户生成独立的 collection 名称，实现知识库隔离
    """
    return f"user_{user_id}_docs"


def get_vector_store(user_id: int) -> Chroma:
    """
    获取用户专属的向量存储对象
    参数:
        user_id: 当前用户 ID
    返回:
        配置好嵌入函数的 Chroma 实例
    """
    return Chroma(
        collection_name=get_collection_name(user_id),
        embedding_function=embedding_model,
        client=_chroma_client,
    )


def add_documents_to_store(user_id: int, texts: List[str], metadatas: Optional[List[Dict]] = None) -> List[str]:
    """
    将多个文本块向量化并存入 ChromaDB
    参数:
        user_id: 用户 ID
        texts: 文本块列表
        metadatas: 与文本块一一对应的元数据列表（如文档名、页码等）
    返回:
        生成的文档 ID 列表
    """
    if not texts:
        return []
    vector_store = get_vector_store(user_id)
    ids = vector_store.add_texts(texts=texts, metadatas=metadatas)
    return ids


def delete_user_collection(user_id: int):
    """
    删除指定用户的整个向量集合（例如清空知识库时使用）
    """
    collection_name = get_collection_name(user_id)
    try:
        _chroma_client.delete_collection(collection_name)
    except ValueError:
        # 集合不存在则忽略
        pass


def get_retriever(user_id: int, top_k: Optional[int] = None):
    """
    获取用户专属的检索器，可直接用于 LangChain 的 retrieval 链
    """
    if top_k is None:
        top_k = settings.RETRIEVAL_TOP_K
    vector_store = get_vector_store(user_id)
    return vector_store.as_retriever(search_kwargs={"k": top_k})