import os
import time
import json
from config import STATIC_DB_PATH, MATCHES_DB_ROOT, REGISTRY_PATH
from indexing.build_static_index import build_static
from indexing.build_matches_index import build_versioned_matches

def test_full_indexing_pipeline():
    print("🚀 Démarrage du test d'indexation...")

    # 1. Tester l'index Statique
    print("\n--- Test Index Statique ---")
    build_static()
    if os.path.exists(os.path.join(STATIC_DB_PATH, "index.faiss")):
        print("✅ Index statique créé avec succès.")
    else:
        print("❌ Échec de la création de l'index statique.")

    # 2. Tester l'index des Matchs (Version 1)
    print("\n--- Test Index Matchs V1 ---")
    build_versioned_matches()
    
    with open(REGISTRY_PATH, "r") as f:
        reg_v1 = json.load(f)
    v1_name = reg_v1["current_version"]
    print(f"✅ V1 créée : {v1_name}")

    # Petite pause pour garantir un timestamp différent
    print("Attente de 2 secondes...")
    time.sleep(2)

    # 3. Tester l'index des Matchs (Version 2 - Mise à jour)
    print("\n--- Test Index Matchs V2 (Mise à jour) ---")
    build_versioned_matches()
    
    with open(REGISTRY_PATH, "r") as f:
        reg_v2 = json.load(f)
    v2_name = reg_v2["current_version"]
    print(f"✅ V2 créée : {v2_name}")

    # 4. Vérification des liens et dossiers
    print("\n--- Vérifications Finales ---")
    
    # Vérifier que V1 et V2 existent physiquement
    path_v1 = os.path.join(MATCHES_DB_ROOT, v1_name)
    path_v2 = os.path.join(MATCHES_DB_ROOT, v2_name)
    
    print(f"Dossier V1 présent : {os.path.exists(path_v1)}")
    print(f"Dossier V2 présent : {os.path.exists(path_v2)}")

    # Vérifier le lien symbolique 'current'
    current_path = os.path.join(MATCHES_DB_ROOT, "current")
    if os.path.islink(current_path):
        target = os.readlink(current_path)
        print(f"🔗 Lien 'current' pointe vers : {target}")
        if target == v2_name:
            print("✅ Le lien symbolique pointe bien vers la version la plus récente.")
        else:
            print("❌ Erreur : Le lien pointe vers une ancienne version.")
    else:
        print("❌ Erreur : Le lien symbolique 'current' n'a pas été trouvé.")

if __name__ == "__main__":
    # Assurez-vous d'être à la racine du projet pour les imports
    test_full_indexing_pipeline()