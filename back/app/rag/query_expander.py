from config import TEAM_ALIASES

def expand_query(query: str) -> str:
    expanded_query = query
    for official_name, aliases in TEAM_ALIASES.items():
        for alias in aliases:
            if alias.lower() in query.lower():
                if alias.lower() != official_name.lower():
                    expanded_query += f" ({official_name})"
                break 
    return expanded_query