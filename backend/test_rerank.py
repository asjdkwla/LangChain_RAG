import asyncio
from langchain_core.documents import Document
from app.rag.reorder_service import rerank

async def test():
    docs = [
        Document(page_content="苹果是一种常见的水果"),
        Document(page_content="北京是中国的首都"),
        Document(page_content="我喜欢吃苹果"),
    ]
    result = await rerank("苹果是什么？", docs, top_k=2)
    for doc in result:
        print(doc.page_content)

asyncio.run(test())