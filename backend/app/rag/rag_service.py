"""
RAG 生成服务
使用阿里云百炼 DashScope 原生 API 完成文本生成
流程：检索 → 重排序 → 构建 Prompt → LLM 生成（支持流式）
"""
import logging
from typing import AsyncIterator, Optional
from http import HTTPStatus

from dashscope import Generation
from langchain_core.documents import Document

from app.config.settings import settings
from app.rag.retrievers.retriever import retrieve
from app.rag.reorder_service import rerank

logger = logging.getLogger(__name__)


def _format_context(docs: list[Document]) -> str:
    """将文档列表格式化为 LLM 可读的上下文字符串"""
    if not docs:
        return "未找到相关文档。"
    parts = []
    for i, doc in enumerate(docs, 1):
        parts.append(f"[文档{i}]\n{doc.page_content}")
    return "\n\n".join(parts)


def _build_prompt(query: str, context: str) -> str:
    """构建发送给 LLM 的最终提示词"""
    return f"""你是一个专业的知识问答助手。请根据以下参考文档回答用户的问题。
如果文档中找不到答案，请如实说明，不要编造信息。

## 参考文档
{context}

## 用户问题
{query}

## 回答
"""


async def generate_answer(
    query: str,
    user_id: int,
    top_k: Optional[int] = None,
    rerank_top_k: Optional[int] = None,
) -> str:
    """
    非流式生成完整答案（内部使用流式 API，但聚合后一次性返回）
    """
    docs = await retrieve(query, user_id=user_id, top_k=top_k)
    if not docs:
        return "抱歉，在您的知识库中未找到相关信息。"

    docs = await rerank(query, docs, top_k=rerank_top_k)
    context = _format_context(docs)
    prompt = _build_prompt(query, context)

    # 调用 DashScope 原生 API（非流式）
    response = Generation.call(
        model=settings.CHAT_MODEL_NAME,
        prompt=prompt,
        api_key=settings.ALIYUN_ACCESS_KEY_SECRET,
        result_format='message',   # 返回 message 格式
        stream=False,
    )
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"LLM 生成失败：{response.message}")
    # 提取回答文本
    return response.output.choices[0].message.content


async def generate_answer_stream(
    query: str,
    user_id: int,
    top_k: Optional[int] = None,
    rerank_top_k: Optional[int] = None,
) -> AsyncIterator[str]:
    """
    流式生成答案，逐 token 返回，适用于 SSE 实时推送
    """
    docs = await retrieve(query, user_id=user_id, top_k=top_k)
    if not docs:
        yield "抱歉，在您的知识库中未找到相关信息。"
        return

    docs = await rerank(query, docs, top_k=rerank_top_k)
    context = _format_context(docs)
    prompt = _build_prompt(query, context)

    # 调用 DashScope 原生流式 API
    responses = Generation.call(
        model=settings.CHAT_MODEL_NAME,
        prompt=prompt,
        api_key=settings.ALIYUN_ACCESS_KEY_SECRET,
        result_format='message',
        stream=True,
        incremental_output=True,  # 增量输出
    )
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            choice = response.output.choices[0]
            # 获取增量内容
            if hasattr(choice.message, 'content'):
                yield choice.message.content
        else:
            logger.error(f"流式生成出错：{response.message}")
            yield f"\n[生成错误：{response.message}]"
            break