"""
重排序服务（阿里云百炼 DashScope API 版本）
使用 dashscope.TextReRank 对检索结果进行语义重排序，返回最相关文档子集
"""
import asyncio
from typing import List
import dashscope
from dashscope import TextReRank
from langchain_core.documents import Document

from app.config.settings import settings

# 全局配置阿里云 DashScope API Key
dashscope.api_key = settings.ALIYUN_ACCESS_KEY_SECRET


def _sync_rerank(query: str, documents: List[str], top_n: int) -> List[int]:
    """
    同步调用重排序 API（正确参数格式）
    参数:
        query: 用户查询文本
        documents: 待排序的文档文本列表
        top_n: 返回的最相关文档数量
    返回:
        按相关性降序排列的文档索引列表
    """
    response = TextReRank.call(
        model=settings.RERANK_MODEL_NAME,
        query=query,                    # 直接传顶层参数，而非 input 字典
        documents=documents,
        top_n=top_n,
        return_documents=False,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"重排序 API 调用失败，状态码：{response.status_code}，"
            f"信息：{response.message}"
        )

    # 返回排序后的索引（已按相关性降序）
    return [result.index for result in response.output.results]


async def rerank(
    query: str,
    docs: List[Document],
    top_k: int = None,
) -> List[Document]:
    """
    异步重排序：通过线程池调用同步 API，避免阻塞事件循环
    参数:
        query: 用户原始查询
        docs: 检索器返回的候选文档列表
        top_k: 重排序后保留的文档数，默认使用全局配置 RERANK_TOP_K
    返回:
        按相关性降序排列的 top_k 个文档
    """
    if top_k is None:
        top_k = settings.RERANK_TOP_K

    if not docs:
        return []

    # 提取文档文本
    doc_texts = [doc.page_content for doc in docs]

    try:
        # 在线程池中执行同步 API 调用（asyncio.to_thread 是 Python 3.9+ 的特性）
        sorted_indices = await asyncio.to_thread(
            _sync_rerank,
            query=query,
            documents=doc_texts,
            top_n=top_k,
        )

        # 根据返回的索引重新排列文档
        return [docs[idx] for idx in sorted_indices]

    except Exception as e:
        # 降级：返回原始文档的前 top_k 个
        print(f"[警告] 重排序失败，使用原始排序：{e}")
        return docs[:top_k]