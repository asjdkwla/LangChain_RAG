from app.rag.vector_store import add_documents_to_store

user_id = 1
docs = [
    "苹果是一种常见的水果，富含维生素C。",
    "北京是中国的首都，拥有故宫、长城等著名景点。",
    "爱因斯坦提出了相对论，对现代物理学有深远影响。",
    "Python 是一种广泛使用的高级编程语言，适合人工智能开发。",
]
add_documents_to_store(user_id, docs)
print("测试文档已存入向量库。")