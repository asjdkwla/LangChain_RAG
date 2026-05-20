"""
聊天路由
提供 SSE 流式对话接口，支持基于知识库的 RAG 问答
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.router.user import get_current_user
from app.model.user import User
from app.rag.rag_service import generate_answer_stream
from app.config.settings import settings
from pydantic import BaseModel, Field

import json
import asyncio

router = APIRouter()


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="用户问题")


async def sse_event_generator(query: str, user_id: int):
    """
    异步生成器：将流式生成的 token 包装为 SSE 事件
    """
    try:
        async for token in generate_answer_stream(query, user_id=user_id):
            # SSE 格式：data: <内容>\n\n
            yield f"data: {json.dumps({'token': token})}\n\n"
        # 发送结束标志
        yield "data: [DONE]\n\n"
    except Exception as e:
        # 发送错误事件
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    SSE 流式聊天接口
    返回 text/event-stream 格式的响应，前端可以使用 EventSource 接收
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="问题不能为空"
        )

    # 注意：这里不需要 await db 操作，因为 RAG 服务不需要直接操作数据库（通过用户 ID 隔离）
    # 如果需要多轮对话历史，可以在此处通过 db 加载历史消息并插入 prompt

    return StreamingResponse(
        sse_event_generator(request.query, current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )