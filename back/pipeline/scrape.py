import requests
from bs4 import BeautifulSoup
import re
import config

def slugify(text):
    text = text.lower().replace(" ", "_")
    return re.sub(r'[^\w\s-]', '', text)

def parse_events(td_cell):
    if not td_cell: return []
    text = td_cell.get_text(" ", strip=True).replace("\xa0", " ")
    pattern = re.compile(r"(?:\(\s*([^)]+?)\s*\)\s*)?([A-Za-zÀ-ÿ\s\-\.]+?)\s+(\d+(?:\+\d+)?)\s*e|(\d+(?:\+\d+)?)\s*e\s*(?:\(\s*(pen\.|csc)\s*\))?\s*([A-Za-zÀ-ÿ\s\-\.]+)")
    events = []
    for m in pattern.finditer(text):
        res = m.groups()
        scorer = (res[1] or res[5] or "").strip()
        if not scorer: continue
        events.append({
            "joueur": scorer,
            "minute": res[2] or res[3],
            "type": "penalty" if "pen" in str(res[4]).lower() or "pen" in text.lower() else "normal"
        })
    return events

def parse_cards(td_cell):
    if not td_cell: return []
    cards = []
    text = td_cell.get_text(" ", strip=True)
    pattern = re.compile(r"([A-Za-zÀ-ÿ\s\-\.]+?)\s+(\d+(?:\+\d+)?)\s*e")
    for match in pattern.finditer(text):
        name = match.group(1).strip()
        if name in ["Rapport", "pen.", "csc"]: continue
        cards.append({"joueur": name, "minute": match.group(2), "type": "jaune"})
    return cards

def get_afcon_data():
    response = requests.get(config.URL_WIKIPEDIA, headers=config.HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    matches = []
    c_phase, c_step = "Phase de groupes", "Groupe A"

    for el in soup.find_all(['h3', 'h4', 'table']):
        if el.name == 'h3': c_phase = el.get_text(strip=True).split('[')[0]
        elif el.name == 'h4': c_step = el.get_text(strip=True).split('[')[0]
        elif el.name == 'table' and "border-spacing:0px 2px" in str(el.get("style")):
            try:
                rows = el.find_all("tr")
                tds1, tds2 = rows[0].find_all("td"), rows[1].find_all("td")
                tds3 = rows[2].find_all("td") if len(rows) > 2 else None
                
                score_raw = tds1[2].get_text(strip=True)
                status = "played" if re.search(r'\d\s*[-–]\s*\d', score_raw) else "scheduled"
                meta_text = tds2[-1].get_text(" ", strip=True)
                
                matches.append({
                    "phase": c_phase, "etape": c_step,
                    "match_n": tds1[0].get_text(strip=True),
                    "equipe_domicile": tds1[1].get_text(strip=True),
                    "score": score_raw,
                    "equipe_exterieur": tds1[3].get_text(strip=True),
                    "stade": tds1[4].get_text(strip=True),
                    "status": status,
                    "affluence": re.search(r"Spectateurs\s*:\s*([\d\s]+)", meta_text).group(1).replace(" ", "") if re.search(r"Spectateurs\s*:\s*([\d\s]+)", meta_text) else "N/C",
                    "arbitre": re.search(r"Arbitrage\s*:\s*([^:]+)", meta_text).group(1).strip() if re.search(r"Arbitrage\s*:\s*([^:]+)", meta_text) else "Inconnu",
                    "raw_tds": (tds1, tds2, tds3)
                })
            except: continue
    return matches