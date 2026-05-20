import asyncio
from app.rag.retrievers.retriever import retrieve

async def test():
    docs = await retrieve("测试查询", user_id=1, top_k=2)
    for d in docs:
        print(d.page_content)
        print("---")

asyncio.run(test())