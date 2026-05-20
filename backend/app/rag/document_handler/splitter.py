"""
文本分割器
使用 LangChain 的递归字符分割器，按配置的 chunk_size / chunk_overlap 进行切分
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.settings import settings


def create_splitter() -> RecursiveCharacterTextSplitter:
    """
    根据全局配置创建一个文本分割器实例
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],  # 中文友好的分隔符
    )


def split_text(text: str) -> list[str]:
    """
    将输入的文本分割为多个块 (chunks)
    参数:
        text: 待分割的完整文本
    返回:
        分割后的文本块列表
    """
    splitter = create_splitter()
    return splitter.split_text(text)