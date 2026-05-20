import asyncio
from app.rag.rag_service import generate_answer

async def test():
    answer = await generate_answer("什么是苹果", user_id=1)
    print(answer)

asyncio.run(test())