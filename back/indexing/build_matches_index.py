import json
import os
from datetime import datetime # Missing import added
from langchain_community.vectorstores import FAISS
from indexing.load_docs import get_match_loader
from indexing.embeddings import embedding_model
from config import DATA_METADATA_DIR, MATCHES_DB_ROOT, REGISTRY_PATH

def build_from_metadata():
    metadata_path = os.path.join(DATA_METADATA_DIR, "versions.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        ver_info = json.load(f)
    
    current_v = ver_info["current_matches_version"]
    print(f"Indexation de la version de données : {current_v}")

    loader = get_match_loader(version=current_v)
    docs = loader.load()
    
    version_db_folder = f"faiss_{current_v}"
    version_db_path = os.path.join(MATCHES_DB_ROOT, version_db_folder)
    
    vector_db = FAISS.from_documents(docs, embedding_model)
    vector_db.save_local(version_db_path)

    info_payload = {
        "current_version": f"faiss_{current_v}", 
        "last_updated": datetime.now().isoformat(),
        "absolute_path": os.path.abspath(version_db_path)
    }

    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(info_payload, f, indent=4)
    
    print(f"Infos de version sauvegardées dans : {REGISTRY_PATH}")

    current_link = os.path.join(MATCHES_DB_ROOT, "current")
    
    # Check if a link or folder exists and remove it
    if os.path.islink(current_link) or os.path.exists(current_link):
        if os.path.isdir(current_link) and not os.path.islink(current_link):
            import shutil
            shutil.rmtree(current_link) # Remove if it's a real directory
        else:
            os.remove(current_link) # Remove if it's a link or file

    # Create the symlink (pointing to the folder name, not absolute path, for portability)
    os.symlink(version_db_folder, current_link)
    
    print(f"Index FAISS mis à jour vers {current_v}")

if __name__ == "__main__":
    build_from_metadata()