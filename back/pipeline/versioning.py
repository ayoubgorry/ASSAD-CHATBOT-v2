import os
import re
import json
import shutil
from datetime import datetime
import config

def get_versions_metadata():
    if os.path.exists(config.VERSION_FILE):
        with open(config.VERSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_matches_version": None, "last_update": None}

def update_version_metadata(new_version):
    os.makedirs(config.METADATA_DIR, exist_ok=True)
    metadata = {
        "current_matches_version": new_version,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(config.VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def get_next_version_path():
    if not os.path.exists(config.MATCHS_DIR):
        os.makedirs(config.MATCHS_DIR, exist_ok=True)
        return "v1", os.path.join(config.MATCHS_DIR, "v1")
    
    versions = [int(d[1:]) for d in os.listdir(config.MATCHS_DIR) 
                if os.path.isdir(os.path.join(config.MATCHS_DIR, d)) and re.match(r'^v\d+$', d)]
    
    next_v_num = max(versions) + 1 if versions else 1
    next_v_str = f"v{next_v_num}"
    return next_v_str, os.path.join(config.MATCHS_DIR, next_v_str)

def create_latest_link(version_name):
    latest_path = os.path.join(config.MATCHS_DIR, config.LATEST_LINK_NAME)
    version_path = os.path.join(config.MATCHS_DIR, version_name)

    if os.path.exists(latest_path) or os.path.islink(latest_path):
        try:
            if os.path.islink(latest_path):
                os.unlink(latest_path) 
            elif os.path.isdir(latest_path):
                shutil.rmtree(latest_path) 
            else:
                os.remove(latest_path) 
        except Exception as e:
            print(f" Nettoyage du lien 'latest' impossible : {e}")

    try:
        os.symlink(version_path, latest_path)
        print(f" Lien symbolique mis à jour : {latest_path} -> {version_name}")
    except OSError as e:
        print(f" Erreur lors de la création du lien : {e}")
        print(f" Astuce : Copie manuelle en cours...")
        if os.path.exists(latest_path): shutil.rmtree(latest_path)
        shutil.copytree(version_path, latest_path)