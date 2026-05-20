from app.rag.document_handler.loader import load_document
from app.rag.document_handler.splitter import split_text

text = load_document("test.pdf")          # 替换为实际文件路径
chunks = split_text(text)
print(f"共 {len(chunks)} 个文本块")
print(chunks[0][:200])