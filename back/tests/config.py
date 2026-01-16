import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_MATCHES_DIR = os.path.join(DATA_DIR, "matches") # Contient v1, v2...
DATA_STATIC_DIR = os.path.join(DATA_DIR, "static")
DATA_METADATA_DIR = os.path.join(DATA_DIR, "metadata")

DB_DIR = os.path.join(BASE_DIR, "vectordb")
STATIC_DB_PATH = os.path.join(DB_DIR, "static_db", "faiss")
MATCHES_DB_ROOT = os.path.join(DB_DIR, "matches")
REGISTRY_PATH = os.path.join(DB_DIR, "registry.json")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TEAM_ALIASES = {
    "Maroc": ["Maroc", "Morocco", "MAR", "Lions de l'Atlas", "Al Maghrib"],
    "Burkina Faso": ["Burkina Faso", "Burkina", "BFA", "Étalons"],
    "Cameroun": ["Cameroun", "Cameroon", "CMR", "Lions Indomptables"],
    "Algérie": ["Algérie", "Algeria", "ALG", "Fennecs"],
    "RD Congo": ["RD Congo", "RDC", "DR Congo", "Congo DR", "COD", "Léopards"],
    "Sénégal": ["Sénégal", "Senegal", "SEN", "Lions de la Teranga"],
    "Égypte": ["Égypte", "Egypt", "EGY", "Pharaons"],
    "Angola": ["Angola", "ANG", "Palancas Negras"],
    "Guinée équatoriale": ["Guinée équatoriale", "Equatorial Guinea", "GEQ", "EQG", "Nzalang Nacional"],
    "Côte d'Ivoire": ["Côte d'Ivoire", "Ivory Coast", "CIV", "Éléphants"],
    "Gabon": ["Gabon", "GAB", "Panthères"],
    "Ouganda": ["Ouganda", "Uganda", "UGA", "Cranes"],
    "Afrique du Sud": ["Afrique du Sud", "South Africa", "RSA", "Bafana Bafana"],
    "Tunisie": ["Tunisie", "Tunisia", "TUN", "Aigles de Carthage"],
    "Nigeria": ["Nigeria", "NGA", "Super Eagles"],
    "Mali": ["Mali", "MLI", "Aigles du Mali"],
    "Zambie": ["Zambie", "Zambia", "ZAM", "Chipolopolo"],
    "Zimbabwe": ["Zimbabwe", "ZIM", "Warriors"],
    "Comores": ["Comores", "Comoros", "COM", "Cœlacanthes"],
    "Soudan": ["Soudan", "Sudan", "SDN", "Faucons de Jediane"],
    "Bénin": ["Bénin", "Benin", "BEN", "Guépards"],
    "Tanzanie": ["Tanzanie", "Tanzania", "TAN", "Taifa Stars"],
    "Botswana": ["Botswana", "BOT", "Zebras"],
    "Mozambique": ["Mozambique", "MOZ", "Mambas"]
}