# Flux RAG (Retrieval-Augmented Generation)

## Vue d'ensemble du processus RAG

Le système RAG du projet SBI permet de répondre aux questions sur la CAN 2025 en combinant deux étapes:
1. **Retrieval**: Récupération de documents pertinents depuis des bases de données vectorielles
2. **Generation**: Génération de réponses basées sur le contexte récupéré

```
┌─────────────────────────┐
│  Requête utilisateur    │
│   "Qui a gagné CAN2025?"│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 1. QUERY EXPANSION                      │
│  - Reformule/améliore la requête        │
│  - Ajoute des variantes linguistiques   │
│  - Enrichit avec contexte pertinent     │
└────────────┬────────────────────────────┘
             │
             ▼
     ┌───────────────┬───────────────┐
     │               │               │
     ▼               ▼               ▼
┌───────────┐   ┌───────────┐   ┌───────────┐
│  Static   │   │  Matches  │   │ (Optional)│
│ Retriever │   │ Retriever │   │ Retriever │
│  (k=15)   │   │  (k=10)   │   │           │
└───────────┘   └───────────┘   └───────────┘
     │               │               │
     │ FAISS DB      │ FAISS DB      │
     │ Vector Search │ Vector Search │
     │               │
     └───────────┬───────────┘
                 │
     ┌───────────▼──────────┐
     │ Format Documents     │
     │ Add Metadata & Type  │
     └───────────┬──────────┘
                 │
     ┌───────────▼──────────┐
     │ Context Aggregation  │
     │ Join all docs        │
     │ with separators      │
     └───────────┬──────────┘
                 │
     ┌───────────▼──────────────────────────┐
     │ 2. PROMPT ENGINEERING                │
     │ ┌────────────────────────────────┐   │
     │ │ RAG_TEMPLATE with:             │   │
     │ │ - {context}: Retrieved docs    │   │
     │ │ - {question}: User query       │   │
     │ │ - Instructions & directives    │   │
     │ └────────────────────────────────┘   │
     └───────────┬──────────────────────────┘
                 │
     ┌───────────▼──────────────────┐
     │ 3. LLM INFERENCE             │
     │ Google Gemini 3 Pro          │
     │ - Temperature: 0 (deterministic)
     │ - Context-aware generation   │
     └───────────┬──────────────────┘
                 │
     ┌───────────▼──────────────────┐
     │ 4. OUTPUT PARSING            │
     │ StrOutputParser              │
     │ - Extraction text brut       │
     │ - Nettoyage si nécessaire    │
     └───────────┬──────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │  Response      │
        │  JSON format   │
        └────────────────┘
```

## Étapes détaillées

### 1. Query Expansion

**Fichier**: [query_expander.py](../back/app/rag/query_expander.py)

**Objectif**: Transformer la question utilisateur pour améliorer la récupération de documents.

**Processus**:
```python
def expand_query(query: str) -> str:
    # Peut inclure:
    # - Ajout d'alias d'équipes (ex: "MAR" → "Maroc")
    # - Expansion de synonymes
    # - Clarification du contexte
    # - Reformulation en variantes linguistiques
    return expanded_query
```

**Exemple**:
- Input: "Les Lions contre les Eagles en 2025"
- Output: "Maroc Nigeria match CAN 2025 score résultat Super Eagles Lions de l'Atlas"

### 2. Dual Retrieval

Le système utilise **deux retrievers indépendants**:

#### 2.1 Static Retriever
- **Source**: Base vectorielle statique des informations générales
- **Contenu**: 
  - Équipes qualifiées
  - Stades et emplacements
  - Coaches et staff
  - Règlements et informations générales
  - Squads des équipes
- **Paramètres**:
  - k=15 (retourne 15 documents les plus proches)
  - Distance métrique: Similarité cosinus
- **Modèle d'embedding**: `sentence-transformers/all-MiniLM-L6-v2`

#### 2.2 Matches Retriever
- **Source**: Base vectorielle des matchs CAN 2025
- **Contenu**:
  - Détails des matchs (score, résultat)
  - Buteurs et événements
  - Cartons (jaunes/rouges)
  - Statistiques de match
  - Historique des rencontres
- **Paramètres**:
  - k=10 (retourne 10 documents les plus proches)
  - Versioning: Symlink "current" → dernière version
- **Modèle d'embedding**: Même que static retriever

**Code**:
```python
def get_retrievers():
    static_db = FAISS.load_local(STATIC_DB_PATH, embedding_model)
    matches_db = FAISS.load_local(MATCHES_DB_PATH, embedding_model)
    
    static_retriever = static_db.as_retriever(search_kwargs={"k": 15})
    matches_retriever = matches_db.as_retriever(search_kwargs={"k": 10})
    
    return static_retriever, matches_retriever
```

### 3. Combinaison des Retrievers

**Fonction**: `combine_retrievers(query)` dans [chain.py](../back/app/rag/chain.py)

```python
def combine_retrievers(query):
    docs_static = static_retriever.invoke(query)    # 15 documents
    docs_matches = matches_retriever.invoke(query)  # 10 documents
    return format_docs(docs_static + docs_matches)  # 25 documents totaux
```

### 4. Format des Documents

**Fonction**: `format_docs(docs)` 

**Transformation**:
```python
def format_docs(docs):
    formatted = []
    for d in docs:
        dtype = d.metadata.get('doc_type', 'info')
        # Format: [Source: type] content
        content = f"[Source: {dtype}] {d.page_content}"
        formatted.append(content)
    return "\n\n".join(formatted)
```

**Résultat**: Chaîne de caractères avec documents séparés par `\n\n`

**Exemple**:
```
[Source: match] Maroc vs Cameroun: 2-1 (Buteurs: Sofiane Boufal 15', Noussair Mazraoui 67')

[Source: team_info] Maroc - Lions de l'Atlas. Coach: Walid Regragui...

[Source: squad] Maroc Squad: Yassine Bounou (gardien), Achraf Hakimi...
```

### 5. Template de Prompt

**Fichier**: [prompt.py](../back/app/rag/prompt.py)

**Structure**:
```
Tu es l'assistant technique expert de la CAN 2025.

### DIRECTIVES DE STYLE:
1. PAS D'INTRODUCTION
2. RÉPONSE DIRECTE
3. CONCIS - Réponse factuelle

### CONTEXTE:
{context}  ← Documents récupérés

### QUESTION:
{question}  ← Requête utilisateur

### RÉPONSE (en français):
```

**Objectif du prompt**:
- Forcer des réponses directes et factuelles
- Éviter les formules de politesse
- Gérer les cas d'informations manquantes
- Assurer la réponse en français

### 6. LLM Inference

**Modèle**: Google Gemini 3 Pro Preview
**Paramètres**:
- Temperature: 0 (déterministe, pas d'aléatoire)
- Mode: Génération de texte
- Token limit: Configuré par Google

**Pipeline LangChain**:
```python
rag_chain = (
    {"context": combine_retrievers, "question": RunnablePassthrough()}
    | PROMPT_TEMPLATE
    | llm
    | StrOutputParser()
)
```

**Flux**:
1. Input: `refined_query` (string)
2. `combine_retrievers`: Récupère le contexte
3. `PROMPT_TEMPLATE`: Formate contexte + question
4. `llm`: Génère la réponse
5. `StrOutputParser`: Parse la sortie en texte brut

### 7. Output Parsing

**Classe**: `StrOutputParser` (LangChain)

**Fonction**: 
- Extrait le texte brut de la réponse LLM
- Gère les formats de sortie structurés
- Nettoie la réponse si nécessaire

## Exemple complet de flux

### Entrée
```json
{
  "query": "Quel est le score du match Maroc vs Nigeria?"
}
```

### Étape 1: Query Expansion
```
Input: "Quel est le score du match Maroc vs Nigeria?"
Output: "Maroc Nigeria score résultat match CAN 2025 Super Eagles Lions de l'Atlas MAR NGA"
```

### Étape 2: Retrieval
```
Static Retriever (k=15):
- Document 1: Équipes qualifiées CAN 2025 - Maroc, Nigeria...
- Document 2: Squads Maroc: Bounou, Hakimi, En-Nesyri...
- Document 3: Squads Nigeria: Nwabali, Awoniyi...
- ... (12 autres documents)

Matches Retriever (k=10):
- Document 16: Match CAN 2025 - Maroc vs Nigeria - Phase groupe
- Document 17: Maroc vs Nigeria détails score: 2-0 (En-Nesyri 23', Mazraoui 89')
- ... (8 autres documents)
```

### Étape 3: Formatting
```
[Source: team] Maroc - Lions de l'Atlas, Entraîneur: Walid Regragui

[Source: team] Nigeria - Super Eagles, Entraîneur: Finidi George

[Source: match] Maroc 2 - 0 Nigeria
Buteurs: En-Nesyri (23'), Mazraoui (89')
Cartons: Adebayor (Nigeria, 67' - jaune)

[Source: squad] Maroc: Yassine Bounou, Achraf Hakimi, Romain Saïss...

[Source: squad] Nigeria: Stanley Nwabali, Ola Aina, William Troost-Ekong...
```

### Étape 4: LLM Generation
```
Prompt complet envoyé au LLM:
- Context: (les 25 documents formatés)
- Question: "Quel est le score du match Maroc vs Nigeria?"
- Instructions: Style, format, langue

LLM Response:
"Maroc a remporté le match contre le Nigeria 2-0 en phase de groupe de la CAN 2025.
Les buteurs marocains sont:
- Youssef En-Nesyri (23')
- Noussair Mazraoui (89')"
```

### Étape 5: Output
```json
{
  "response": "Maroc a remporté le match contre le Nigeria 2-0 en phase de groupe de la CAN 2025. Les buteurs marocains sont: - Youssef En-Nesyri (23') - Noussair Mazraoui (89')"
}
```

## Optimisations et considérations

### 1. Chunking des documents
**Voir**: [chunking.py](../back/indexing/chunking.py)
- Les documents sont découpés en chunks optimisés
- Balance entre contexte et granularité
- Métadonnées préservées dans chaque chunk

### 2. Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384 dimensions
- **Performance**: Rapide et efficace
- **Multilingual**: Supporte plusieurs langues (FR, EN, etc.)

### 3. Versioning des bases vectorielles
- Chaque version de données crée un nouvel index FAISS
- Symlink "current" pointe vers la dernière version
- Permet la mise à jour sans downtime

### 4. Gestion des erreurs
```python
@app.post("/chat")
async def chat(question: Question):
    try:
        refined_query = expand_query(question.query)
        response = rag_chain.invoke(refined_query) 
        return {"response": response}
    except Exception as e:
        return {"response": f"Erreur technique : {str(e)}"}
```

## Points de tuning possibles

1. **Nombre de documents** (k):
   - Static: k=15
   - Matches: k=10
   - Pourrait être optimisé selon les besoins

2. **Temperature du LLM**:
   - Actuellement: 0 (déterministe)
   - Pourrait augmenter pour plus de créativité

3. **Modèle d'embedding**:
   - Actuellement: all-MiniLM-L6-v2
   - Alternatives: all-mpnet-base-v2 (meilleur, mais plus lent)

4. **Stratégie de chunking**:
   - Taille actuelle: Voir chunking.py
   - Pourrait varier par type de document

5. **Prompt engineering**:
   - Directives actuelles: Concis et factuel
   - Pourrait ajouter des exemples (few-shot prompting)
