"""
知识库业务服务
处理文档上传、列表、删除等逻辑
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.config.settings import settings
from app.rag.document_handler.loader import load_document
from app.rag.document_handler.splitter import split_text
from app.rag.vector_store import add_documents_to_store, delete_user_collection


def save_upload_file(file_content: bytes, original_filename: str) -> str:
    """
    保存上传文件到本地磁盘，返回文件路径
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 用 UUID 重命名，防止文件名冲突
    ext = Path(original_filename).suffix
    saved_name = f"{uuid.uuid4().hex}{ext}"
    file_path = upload_dir / saved_name

    with open(file_path, "wb") as f:
        f.write(file_content)

    return str(file_path)


def process_document(file_path: str, user_id: int) -> int:
    """
    处理单个文档：加载 → 分割 → 向量化
    返回向量化的文本块数量
    """
    # 1. 提取文本
    text = load_document(file_path)

    # 2. 分割
    chunks = split_text(text)
    if not chunks:
        return 0

    # 3. 构造元数据（记录来源文件）
    metadatas = [{"source": os.path.basename(file_path)} for _ in chunks]

    # 4. 存入向量库
    add_documents_to_store(user_id=user_id, texts=chunks, metadatas=metadatas)

    return len(chunks)


def delete_user_knowledge(user_id: int):
    """
    清空指定用户的所有知识库文档
    """
    delete_user_collection(user_id)