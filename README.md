# 🏆 Architecture du Projet ASSAD CAN 2025

**ASSAD** est une application intelligente de question-réponse (QA) dédiée à la **Coupe d’Afrique des Nations 2025 (CAN 2025)**. 

Le projet repose sur une architecture **Retrieval-Augmented Generation (RAG)** avancée, conçue pour fournir des réponses précises, contextualisées et à jour, basées exclusivement sur les données réelles de la compétition.

---

## Objectifs du projet

* **Fiabilité historique :** Fournir des résumés précis des matchs déjà joués.
* **Intégrité des données :** Répondre honnêtement aux questions sur les événements à venir sans aucune hallucination.
* **Centralisation de l'information :** Regrouper toutes les données clés sur les équipes, stades, coachs, groupes et classements.
* **Pipeline Incremental :** Mettre à jour automatiquement les données via un flux de synchronisation continue.
* **Standard Production :** Appliquer les meilleures pratiques RAG orientées vers un déploiement réel.

---

##  Principe clé : RAG Multi-Retrievers

ASSAD se distingue par une séparation stratégique des flux d'informations pour garantir une précision maximale :

### 1. Données Statiques (Rarement modifiées)
* **Contenu :** Détails des équipes, infrastructures (stades), biographies des coachs, historique des qualifications et composition des groupes.
* **Stockage :** Base vectorielle dédiée.

### 2. Données Dynamiques (Fréquemment mises à jour)
* **Contenu :** Résultats des matchs en temps réel, statistiques de jeu et calendriers mis à jour.
* **Stockage :** Index vectoriel séparé pour des rafraîchissements rapides.

###  Avantages de cette architecture
* **Mises à jour ciblées :** Seul l'index dynamique est reconstruit fréquemment, économisant des ressources.
* **Performance accrue :** Recherche sémantique optimisée par catégorie de données.
* **Réduction des hallucinations :** Meilleur contrôle du contexte fourni au modèle de langage (LLM).

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend (React)                          │
│              (Requêtes de questions utilisateur)              │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          │ HTTP POST /chat
                          ▼
┌──────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Query Expansion                                      │   │
│  │ (Amélioration de la requête utilisateur)             │   │
│  └─────────────────────┬────────────────────────────────┘   │
│                        │                                      │
│  ┌─────────────────────▼────────────────────────────────┐   │
│  │ RAG Chain                                            │   │
│  │ ┌──────────────────┐         ┌──────────────────┐   │   │
│  │ │ Static Retriever │         │ Matches Retriever│   │   │
│  │ │ (FAISS DB)       │         │ (FAISS DB)       │   │   │
│  │ └──────────────────┘         └──────────────────┘   │   │
│  │           │                           │              │   │
│  │           └─────────────┬─────────────┘              │   │
│  │                         │                            │   │
│  │           ┌─────────────▼────────────┐              │   │
│  │           │ Context Formatting       │              │   │
│  │           └─────────────┬────────────┘              │   │
│  │                         │                            │   │
│  │           ┌─────────────▼────────────┐              │   │
│  │           │ Prompt Template          │              │   │
│  │           └─────────────┬────────────┘              │   │
│  │                         │                            │   │
│  │           ┌─────────────▼────────────┐              │   │
│  │           │ LLM (Gemini)             │              │   │
│  │           └─────────────┬────────────┘              │   │
│  │                         │                            │   │
│  │           ┌─────────────▼────────────┐              │   │
│  │           │ Output Parser            │              │   │
│  │           └──────────────────────────┘              │   │
│  └──────────────────────────────────────────────────────┘   │
│                        │                                      │
│                        │ Réponse structurée                   │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                          ▼
                    Frontend (Affichage)
```

## Architecture en couches

### 1. **Couche Présentation (Frontend)**
- **Technologie**: React.js
- **Responsabilités**:
  - Capture des requêtes utilisateur
  - Affichage des réponses du serveur
  - Interface utilisateur responsive (Tailwind CSS)

### 2. **Couche API (Backend)**
- **Framework**: FastAPI
- **Endpoint principal**: `POST /chat`
  - Accepte: `{"query": "string"}`
  - Retourne: `{"response": "string"}`
- **Middleware CORS**: Autorise les requêtes cross-origin

### 3. **Couche Traitement (RAG)**
- **Pipeline RAG** composé de:
  1. **Query Expander**: Améliore la requête utilisateur
  2. **Retrievers**: Récupère les documents pertinents
  3. **Prompt Formatter**: Structure le contexte pour le LLM
  4. **LLM**: Génère la réponse (Google Gemini 3 Pro)
  5. **Output Parser**: Parse la sortie du modèle

### 4. **Couche Données**
- **Vector Databases** (FAISS):
  - Base statique: Informations générales sur la CAN 2025
  - Base matches: Détails des matchs
- **Document Storage** (JSON):
  - Données brutes des matchs
  - Données statiques (équipes, stades, coaches, etc.)
  - Métadonnées de versioning

### 5. **Couche Pipeline**
- **Web Scraping**: Extraction des données depuis Wikipedia
- **Versioning**: Gestion des versions de données
- **Indexing**: Construction des index FAISS
- **Cron Jobs**: Mise à jour automatique des données

## Structure des dossiers

```
sbi/
├── front/                    # Application React
│   ├── src/
│   ├── public/
│   └── package.json
│
└── back/                     # Backend Python
    ├── app/                  # Application principale
    │   ├── main.py          # API FastAPI
    │   └── rag/             # Système RAG
    │       ├── chain.py      # Pipeline RAG
    │       ├── prompt.py     # Templates de prompts
    │       ├── retrievers.py # Récupération de documents
    │       └── query_expander.py
    │
    ├── data/                # Données du projet
    │   ├── matches/         # Données des matchs (v1, v2, etc.)
    │   ├── static/          # Données statiques (équipes, stades, etc.)
    │   └── metadata/        # Versions et métadonnées
    │
    ├── vectordb/            # Vector stores (FAISS)
    │   ├── static_db/       # Index statique
    │   └── matches/         # Index des matchs (versioning)
    │
    ├── indexing/            # Construction des index
    │   ├── build_matches_index.py
    │   ├── build_static_index.py
    │   ├── chunking.py      # Stratégie de chunking
    │   ├── embeddings.py    # Configuration des embeddings
    │   └── load_docs.py     # Chargement des documents
    │
    ├── pipeline/            # Pipeline de données
    │   ├── scrape.py        # Web scraping
    │   ├── versioning_pipeline.py
    │   └── versioning.py    # Gestion des versions
    │
    ├── scripts/             # Scripts d'automatisation
    │   ├── main_pipeline.py
    │   └── cron.sh          # Tâches planifiées
    │
    ├── tests/               # Tests unitaires
    ├── config.py            # Configuration globale
    └── .env                 # Variables d'environnement
```

## Flux de données

### Flux de requête (Utilisateur → Réponse)
1. Utilisateur pose une question via l'interface
2. FastAPI reçoit la requête POST `/chat`
3. Query Expander améliore/reformule la question
4. Retrievers récupèrent les documents pertinents des deux bases (statique + matches)
5. Documents sont formatés avec métadonnées
6. Prompt Template insère le contexte et la question
7. LLM (Gemini) génère la réponse
8. Réponse retournée au frontend

### Flux de données (Source → Index)
1. Web Scraping depuis Wikipedia
2. Extraction structurée (teams, matches, stats)
3. Sauvegarde en JSON versionnée
4. Chunking des documents pour l'embedding
5. Embeddings (sentence-transformers) calculés
6. Index FAISS créé et sauvegardé
7. Symlink "current" mis à jour vers la dernière version

## Dépendances clés

### Backend
- **FastAPI**: Framework web asynchrone
- **LangChain**: Orchestration RAG
- **FAISS**: Vector database
- **Google Generative AI**: API Gemini LLM
- **Sentence Transformers**: Modèle d'embedding

### Frontend
- **React**: Framework UI
- **Tailwind CSS**: Styling
- **Axios/Fetch**: Requêtes HTTP

## Configuration

Voir [config.py](../back/config.py) pour:
- Chemins des bases de données
- Alias des équipes
- Modèle d'embedding utilisé
- URLs et user agents

## Environnement

Fichier `.env` requis:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Points d'intégration

1. **Frontend ↔ Backend**: API REST HTTP
2. **Backend ↔ FAISS**: Chargement local des index
3. **Backend ↔ LLM**: API Google Generative AI
4. **Pipeline ↔ Sources**: Web scraping Wikipedia + JSON local
5. **Pipeline ↔ Vector DB**: FAISS save/load local
