from app.rag.vector_store import add_documents_to_store, get_vector_store

user_id = 1
test_texts = ["这是第一条测试文档。", "这是第二条测试内容，包含更多信息。"]
ids = add_documents_to_store(user_id, test_texts)
print(f"已存储文档，ID: {ids}")

# 验证检索
retriever = get_vector_store(user_id).as_retriever(search_kwargs={"k": 2})
results = retriever.invoke("测试")
for doc in results:
    print(doc.page_content)