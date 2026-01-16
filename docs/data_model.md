# Modèle de Données

## Vue d'ensemble

Le projet utilise une architecture de données multi-sources avec versioning pour la CAN 2025:
- **Données brutes** (JSON): Fichiers sources provenant du scraping
- **Données structurées**: Format unifié pour les matchs et infos statiques
- **Données vectorialisées** (FAISS): Index pour la recherche sémantique
- **Métadonnées**: Gestion des versions et références

## Structure de répertoires des données

```
data/
├── matches/              # Données des matchs (versionnées)
│   ├── v1/              # Version 1 des données
│   │   ├── match_1.json
│   │   ├── match_2.json
│   │   └── ... (jusqu'à match_64.json)
│   ├── v2/              # Version 2 des données
│   └── ...
│
├── static/              # Données statiques (immuables)
│   ├── equipes_qualifiees.json
│   ├── classement_phase_groupe.json
│   ├── classement_meilleurs_trois.json
│   ├── coach.json
│   ├── stades.json
│   └── squads/
│       ├── algeria.json
│       ├── cameroon.json
│       └── ... (une par équipe)
│
└── metadata/            # Métadonnées système
    └── versions.json
```

## Données des Matchs

### Structure d'un document Match

**Fichier exemple**: `match_match_1_match_douverture_maroc_vs_comores.json`

```json
{
  "match_n": "1",
  "date": "2025-01-14",
  "heure": "21:00",
  "stade": "Stade Moulay Abdellah, Rabat",
  "equipe_domicile": "Maroc",
  "equipe_exterieur": "Comores",
  "score_domicile": 2,
  "score_exterieur": 1,
  "statut": "Terminé",
  "phase": "Phase de groupe",
  "groupe": "A",
  
  "buteurs_domicile": [
    {
      "joueur": "Sofiane Boufal",
      "minute": "15",
      "assist": null
    },
    {
      "joueur": "Noussair Mazraoui",
      "minute": "67",
      "assist": "Hakimi"
    }
  ],
  
  "buteurs_exterieur": [
    {
      "joueur": "Sanda Ali Seif",
      "minute": "42",
      "assist": null
    }
  ],
  
  "cartons_domicile": [
    {
      "joueur": "Romain Saïss",
      "type": "jaune",
      "minute": "35"
    }
  ],
  
  "cartons_exterieur": [],
  
  "spectateurs": 55000,
  "arbitre": "Referee Name",
  "last_update": "15/01/2025 10:30:45"
}
```

### Schéma des données de match

| Champ | Type | Description |
|-------|------|-------------|
| `match_n` | string | Numéro du match (1-64) |
| `date` | string | Format ISO (YYYY-MM-DD) |
| `heure` | string | Heure de départ (HH:MM) |
| `stade` | string | Nom et localisation du stade |
| `equipe_domicile` | string | Nom de l'équipe à domicile |
| `equipe_exterieur` | string | Nom de l'équipe à l'extérieur |
| `score_domicile` | integer | Nombre de buts marqués |
| `score_exterieur` | integer | Nombre de buts marqués |
| `statut` | string | "Terminé", "En cours", "Programmé" |
| `phase` | string | "Phase de groupe", "Quarts", "Demi-finales", "Finale" |
| `groupe` | string | "A", "B", "C", "D", "E", "F" |
| `buteurs_domicile` | array | Liste des buteurs |
| `buteurs_exterieur` | array | Liste des buteurs |
| `cartons_domicile` | array | Liste des cartons |
| `cartons_exterieur` | array | Liste des cartons |
| `spectateurs` | integer | Nombre de spectateurs |
| `arbitre` | string | Nom de l'arbitre |
| `last_update` | string | Date/heure dernière mise à jour |

### Sous-schéma: Buteur

```json
{
  "joueur": "string",      // Nom du joueur
  "minute": "string",      // Minute du but (peut inclure "90+2")
  "assist": "string|null"  // Nom du passeur (optionnel)
}
```

### Sous-schéma: Carton

```json
{
  "joueur": "string",      // Nom du joueur
  "type": "jaune|rouge",   // Type de carton
  "minute": "string"       // Minute du carton
}
```

## Données Statiques

### 1. Équipes Qualifiées

**Fichier**: `static/equipes_qualifiees.json`

```json
{
  "equipes": [
    {
      "nom": "Maroc",
      "alias": ["MAR", "Morocco", "Lions de l'Atlas", "Al Maghrib"],
      "groupe": "A",
      "drapeau": "🇲🇦",
      "confederation": "CAF"
    },
    {
      "nom": "Cameroun",
      "alias": ["CMR", "Cameroon", "Lions Indomptables"],
      "groupe": "A",
      "drapeau": "🇨🇲",
      "confederation": "CAF"
    }
    // ... 32 équipes total
  ]
}
```

### 2. Squads des équipes

**Fichier**: `static/squads/algeria.json` (exemple)

```json
{
  "equipe": "Algérie",
  "coach": "Jean Beausejour",
  "effectif": [
    {
      "numero": 1,
      "nom": "Ahmed Mandi",
      "position": "Gardien",
      "club": "Al-Nassr (Arabie Saoudite)",
      "date_naissance": "1990-02-01",
      "caps": 45
    },
    {
      "numero": 2,
      "nom": "Achraf Bensaïd",
      "position": "Défenseur",
      "club": "ES Sétif",
      "date_naissance": "1995-06-15",
      "caps": 28
    }
    // ... liste complète des joueurs
  ]
}
```

### 3. Stades

**Fichier**: `static/stades.json`

```json
{
  "stades": [
    {
      "nom": "Stade Moulay Abdellah",
      "localisation": "Rabat, Maroc",
      "capacite": 55000,
      "surface": "Gazon naturel",
      "matches_prevus": 3
    },
    {
      "nom": "Stade Roi Fahd",
      "localisation": "Casablanca, Maroc",
      "capacite": 45000,
      "surface": "Gazon naturel",
      "matches_prevus": 4
    }
    // ... tous les stades CAN 2025
  ]
}
```

### 4. Coaches

**Fichier**: `static/coach.json`

```json
{
  "coaches": [
    {
      "equipe": "Maroc",
      "nom": "Walid Regragui",
      "nationalite": "Français/Marocain",
      "date_naissance": "1975-01-23",
      "experiences": [
        {
          "club": "AS Monaco",
          "debut": "2020",
          "fin": "2021"
        },
        {
          "club": "Equipe de France",
          "type": "assistant",
          "periode": "2012-2016"
        }
      ]
    }
    // ... tous les coaches
  ]
}
```

### 5. Classements

**Fichier**: `static/classement_phase_groupe.json`

```json
{
  "groupe": "A",
  "matches_joues": 3,
  "equipes": [
    {
      "rang": 1,
      "equipe": "Maroc",
      "matches": 3,
      "victoires": 2,
      "nuls": 1,
      "defaites": 0,
      "buts_pour": 5,
      "buts_contre": 1,
      "difference": 4,
      "points": 7
    },
    {
      "rang": 2,
      "equipe": "Cameroun",
      "matches": 3,
      "victoires": 1,
      "nuls": 2,
      "defaites": 0,
      "buts_pour": 4,
      "buts_contre": 2,
      "difference": 2,
      "points": 5
    }
    // ... autres équipes du groupe
  ]
}
```

## Métadonnées de Versioning

### Fichier: `metadata/versions.json`

```json
{
  "current_matches_version": "v1",
  "current_static_version": "v1",
  "versions": [
    {
      "version": "v1",
      "date_creation": "2025-01-10T10:30:00Z",
      "nombre_matches": 64,
      "nombre_mises_a_jour": 5,
      "source": "scrape_wikipedia",
      "checksum": "abc123def456..."
    },
    {
      "version": "v2",
      "date_creation": "2025-01-15T14:00:00Z",
      "nombre_matches": 64,
      "nombre_mises_a_jour": 12,
      "source": "scrape_wikipedia",
      "checksum": "xyz789uvw456..."
    }
  ]
}
```

## Données Vectorialisées (FAISS)

### Structure des index FAISS

```
vectordb/
├── static_db/
│   └── faiss/                    # Index statique
│       ├── index.faiss           # Fichier principal de l'index
│       ├── index.pkl             # Métadonnées sérialisées
│       └── docstore/
│           └── 0                 # Chunks des documents
│
└── matches/
    ├── faiss_v1/                 # Index version 1
    │   ├── index.faiss
    │   ├── index.pkl
    │   └── docstore/
    ├── faiss_v2/                 # Index version 2
    │   └── ...
    └── current -> faiss_v1/      # Symlink vers version actuelle
```

### Contenu des chunks vectorisés

**Static Index chunks**:
```
Chunk 1: "Équipes qualifiées CAN 2025: Maroc, Cameroun, Égypte..."
Chunk 2: "Maroc - Lions de l'Atlas. Groupe A. Coach: Walid Regragui"
Chunk 3: "Effectif Maroc: Yassine Bounou (gardien), Achraf Hakimi..."
...
```

**Matches Index chunks**:
```
Chunk 1: "Match 1: Maroc vs Comores, 2-1, Buteurs: Boufal, Mazraoui"
Chunk 2: "Maroc vs Cameroun score 0-0, phase groupe groupe A"
...
```

### Embedding

- **Modèle**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384 dimensions
- **Distance**: Similarité cosinus
- **Normalisation**: Les vecteurs sont normalisés

## Alias des équipes

**Configuration**: [config.py](../back/config.py) - `TEAM_ALIASES`

Permet la reconnaissance de variantes:

```python
TEAM_ALIASES = {
    "Maroc": ["Maroc", "Morocco", "MAR", "Lions de l'Atlas", "Al Maghrib"],
    "Nigeria": ["Nigeria", "NGA", "Super Eagles", "Aigles du Nigeria"],
    "Égypte": ["Égypte", "Egypt", "EGY", "Pharaons"],
    "Algérie": ["Algérie", "Algeria", "ALG", "Fennecs"],
    # ... etc pour les 32 équipes
}
```

## Cycle de vie des données

```
Wikipedia CAN 2025
        │
        ▼
    Web Scraping (scrape.py)
        │
        ├─→ Extraction structurée
        │   - Teams, matches, scores
        │   - Stats, cartons, buteurs
        │
        ▼
    Sauvegarde JSON versionnée (v1, v2, ...)
        │
        ├─→ data/matches/v1/match_*.json
        └─→ data/matches/v2/match_*.json
        │
        ▼
    Versioning Pipeline (versioning_pipeline.py)
        │
        ├─→ Mise à jour metadata/versions.json
        └─→ Création symlink "current"
        │
        ▼
    Indexing Pipeline (build_matches_index.py)
        │
        ├─→ Chunking des documents
        ├─→ Embedding vectoriel
        └─→ Construction FAISS
        │
        ▼
    Sauvegarde Vector DB (vectordb/matches/faiss_v1)
        │
        ├─→ index.faiss (vecteurs)
        ├─→ index.pkl (métadonnées)
        └─→ docstore/ (chunks)
        │
        ▼
    Production RAG (runtime)
        │
        ├─→ FAISS retrieval
        ├─→ LLM generation
        └─→ API response
```

## Flux de mise à jour des données

### 1. Scraping
- **Source**: Wikipedia CAN 2025
- **Fréquence**: Chaque jour (cron.sh)
- **Sortie**: Données JSON brutes dans `data/matches/vN/`

### 2. Versioning
- **Détection** des changements
- **Création** nouvelle version (v1 → v2, etc.)
- **Mise à jour** `metadata/versions.json`
- **Symlink** `current` pointé vers nouvelle version

### 3. Indexing
- **Chunking**: Division des documents pour embedding
- **Embeddings**: Calcul des vecteurs (sentence-transformers)
- **FAISS Index**: Création de l'index vectoriel
- **Sauvegarde**: `vectordb/matches/faiss_vN/`

### 4. Activation
- **Symlink** `vectordb/matches/current` → version active
- **Retriever** charge automatiquement la version actuelle

## Gestion des métadonnées

### Lors de la création d'index

```python
info_payload = {
    "current_version": "faiss_v2",
    "last_updated": "2025-01-16T10:30:45.123456",
    "absolute_path": "/path/to/vectordb/matches/faiss_v2"
}
```

**Stocké dans**: `vectordb/registry.json`

### Lors du chargement en runtime

```python
current_matches_path = os.path.join(MATCHES_DB_ROOT, "current")
matches_db = FAISS.load_local(
    current_matches_path,
    embedding_model,
    allow_dangerous_deserialization=True
)
```

Le symlink `current` assure le chargement de la bonne version.

## Considerations de performance

### Optimisations
1. **Chunking intelligent**: Chunks de taille optimisée pour embedding
2. **Caching FAISS**: Index pré-calculés en cache mémoire
3. **Lazy loading**: Index chargés à la demande en runtime
4. **Versioning**: Pas de recalcul complet, seulement les changements

### Limitations
- FAISS n'est optimisé que pour recherche locale (pas distribué)
- Chaque version crée un nouvel index (consommation disque)
- Embeddings figés une fois l'index créé

## Intégrité des données

- **Checksums**: Vérification lors de la création d'index
- **Métadonnées**: Versioning complet avec timestamps
- **Backup**: Chaque version conservée sur disque
- **Rollback**: Possibilité de revenir à version antérieure via symlink
