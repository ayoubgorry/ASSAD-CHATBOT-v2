import os
from langchain_community.vectorstores import FAISS
from indexing.embeddings import embedding_model
from config import STATIC_DB_PATH, MATCHES_DB_ROOT

def get_retrievers():
    static_db = FAISS.load_local(
        STATIC_DB_PATH, 
        embedding_model, 
        allow_dangerous_deserialization=True
    )
    
    current_matches_path = os.path.join(MATCHES_DB_ROOT, "current")
    matches_db = FAISS.load_local(
        current_matches_path, 
        embedding_model, 
        allow_dangerous_deserialization=True
    )

    static_retriever = static_db.as_retriever(search_kwargs={"k": 15})
    matches_retriever = matches_db.as_retriever(search_kwargs={"k": 10})
    
    return static_retriever, matches_retriever

def format_docs(docs):
    formatted = []
    for d in docs:
        dtype = d.metadata.get('doc_type', 'info')
        content = f"[Source: {dtype}] {d.page_content}"
        formatted.append(content)
    return "\n\n".join(formatted)