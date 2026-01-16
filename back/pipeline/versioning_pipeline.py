import os
import json
from datetime import datetime
from pipeline.scrape import parse_events,parse_cards , get_afcon_data, slugify
from pipeline.versioning import get_next_version_path, update_version_metadata, create_latest_link

def run():
    print(f" Début du pipeline CAN 2025...")
    
    data = get_afcon_data()
    if not data:
        print(" Erreur : aucune donnée trouvée.")
        return

    v_name, v_path = get_next_version_path()
    os.makedirs(v_path, exist_ok=True)
    
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    for m in data:
        tds1, tds2, tds3 = m.pop("raw_tds")
        m["last_update"] = now
        m["buteurs_domicile"] = parse_events(tds2[1])
        m["buteurs_exterieur"] = parse_events(tds2[3])
        m["cartons_domicile"] = parse_cards(tds3[0]) if tds3 else []
        m["cartons_exterieur"] = parse_cards(tds3[2]) if tds3 and len(tds3) > 2 else []

        fname = f"match_{slugify(m['match_n'])}_{slugify(m['equipe_domicile'])}_vs_{slugify(m['equipe_exterieur'])}.json"
        
        with open(os.path.join(v_path, fname), "w", encoding="utf-8") as f:
            json.dump(m, f, indent=4, ensure_ascii=False)

    update_version_metadata(v_name)
    create_latest_link(v_name)
    
    print(f" Version {v_name} créée avec succès dans '{v_path}'.")

if __name__ == "__main__":
    run()