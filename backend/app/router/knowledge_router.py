"""
知识库管理路由
POST /api/knowledge/upload    上传文档
GET  /api/knowledge/list     列出已上传文档
DELETE /api/knowledge/clear   清空知识库
"""
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.router.user import get_current_user    # 复用之前定义的认证依赖
from app.model.user import User
from app.router.knowledge_service import (
    save_upload_file,
    process_document,
    delete_user_knowledge,
)
from app.config.settings import settings

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    上传文档，自动分割并向量化到用户专属知识库
    """
    # 检查文件扩展名
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.allowed_extension_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型：.{ext}，仅支持：{settings.allowed_extension_list}"
        )

    # 检查文件大小
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制（{settings.MAX_UPLOAD_SIZE_MB}MB）"
        )

    # 保存文件
    file_path = save_upload_file(content, file.filename)

    try:
        # 处理文档（提取、分割、向量化）
        chunk_count = process_document(file_path, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档处理失败：{str(e)}"
        )

    return {
        "filename": file.filename,
        "chunks": chunk_count,
        "message": f"文档已成功处理，共生成 {chunk_count} 个文本块。"
    }


@router.get("/list")
async def list_documents(current_user: User = Depends(get_current_user)):
    """
    列出用户知识库中的文档列表（简化版，直接返回文件列表）
    可通过扫描 uploads 目录实现，此处为示例
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    if not upload_dir.exists():
        return {"files": []}

    files = [f.name for f in upload_dir.iterdir() if f.is_file()]
    return {"files": files, "total": len(files)}


@router.delete("/clear")
async def clear_knowledge(current_user: User = Depends(get_current_user)):
    """
    清空当前用户的所有知识库文档
    """
    delete_user_knowledge(current_user.id)
    return {"message": "知识库已清空。"}