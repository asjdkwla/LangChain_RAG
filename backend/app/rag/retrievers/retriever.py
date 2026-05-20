"""
语义检索器
根据用户输入查询，从对应用户的知识库中检索最相关的文本块
"""
from typing import List, Optional
from langchain_core.documents import Document
from app.rag.vector_store import get_vector_store
from app.config.settings import settings


async def retrieve(
    query: str,
    user_id: int,
    top_k: Optional[int] = None,
    filter: Optional[dict] = None,
) -> List[Document]:
    """
    从指定用户的知识库中检索与查询最相关的文档块
    参数:
        query: 用户输入的自然语言查询
        user_id: 用户 ID（用于隔离知识库）
        top_k: 返回的文档数量，默认使用全局配置 RETRIEVAL_TOP_K
        filter: 可选的元数据过滤条件（如 {"source": "upload.pdf"}）
    返回:
        LangChain Document 列表，每个包含 page_content 和 metadata
    """
    if top_k is None:
        top_k = settings.RETRIEVAL_TOP_K

    # 获取用户专属向量存储
    vector_store = get_vector_store(user_id)

    # 执行相似度搜索（支持过滤）
    docs = vector_store.similarity_search(
        query=query,
        k=top_k,
        filter=filter,
    )
    return docs