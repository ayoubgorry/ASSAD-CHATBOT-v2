import os
from langchain_community.vectorstores import FAISS
from indexing.load_docs import get_static_loaders, create_synth_doc
from indexing.chunking import squad_splitter, process_docs
from indexing.embeddings import embedding_model
from config import STATIC_DB_PATH

def build_static():
    loaders = get_static_loaders()
    docs = []
    for name, loader in loaders.items():
        docs.extend(loader.load())
    
    docs = process_docs(docs)
    
    squad_docs = [d for d in docs if d.metadata["doc_type"] == "squad"]
    other_docs = [d for d in docs if d.metadata["doc_type"] != "squad"]
    
    final_docs = squad_splitter.split_documents(squad_docs) + other_docs + [create_synth_doc()]
    
    os.makedirs(os.path.dirname(STATIC_DB_PATH), exist_ok=True)
    
    vector_db = FAISS.from_documents(final_docs, embedding_model)
    vector_db.save_local(STATIC_DB_PATH)
    print(f"Index statique sauvegardé dans : {STATIC_DB_PATH}")

if __name__ == "__main__":
    build_static()