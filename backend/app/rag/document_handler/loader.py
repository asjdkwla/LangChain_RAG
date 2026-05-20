"""
文档加载器
根据文件扩展名自动选择合适的解析方式，提取纯文本内容
"""
from pathlib import Path
from typing import List
from pypdf import PdfReader               # 用于 PDF 解析
from docx import Document as DocxDocument # 用于 Word 文档解析


def load_text_file(file_path: Path) -> str:
    """
    读取纯文本文件（.txt, .md）
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_pdf_file(file_path: Path) -> str:
    """
    读取 PDF 文件，提取所有页面的文本
    """
    reader = PdfReader(str(file_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def load_docx_file(file_path: Path) -> str:
    """
    读取 Word (.docx) 文件，提取段落文本
    """
    doc = DocxDocument(str(file_path))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)


def load_document(file_path: str) -> str:
    """
    根据文件扩展名自动选择加载器，返回文档的完整文本内容
    参数:
        file_path: 文件路径（字符串或 Path 对象）
    返回:
        提取到的纯文本
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in [".txt", ".md"]:
        return load_text_file(path)
    elif suffix == ".pdf":
        return load_pdf_file(path)
    elif suffix == ".docx":
        return load_docx_file(path)
    else:
        raise ValueError(f"不支持的文件类型: {suffix}")