"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    import chromadb
    from pathlib import Path
    import streamlit as st
    from sentence_transformers import SentenceTransformer

    @st.cache_resource
    def get_model():
        return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    model = get_model()
    query_embedding = model.encode(query).tolist()

    db_path = str(Path(__file__).parent.parent / "chroma_db")
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name="DrugLawDocs")
    except Exception:
        # Collection might not exist yet if Task 4 hasn't run
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    if not results['documents'] or not results['documents'][0]:
        return []

    output = []
    for i in range(len(results['documents'][0])):
        output.append({
            "content": results['documents'][0][i],
            "score": 1 - results['distances'][0][i],
            "metadata": results['metadatas'][0][i]
        })
    return output


if __name__ == "__main__":
    # Test
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
