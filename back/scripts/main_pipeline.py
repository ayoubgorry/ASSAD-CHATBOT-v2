from pipeline.versioning_pipeline import run as run_scraping
from indexing.build_matches_index import build_from_metadata

def start_pipeline():
    print("---  Démarrage du Pipeline Intégré ---")

    run_scraping() 

    build_from_metadata()

    print("---  Pipeline terminé avec succès ---")

if __name__ == "__main__":
    start_pipeline()