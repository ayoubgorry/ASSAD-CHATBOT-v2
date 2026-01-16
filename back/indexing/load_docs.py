from langchain_community.document_loaders import JSONLoader, DirectoryLoader
from langchain_core.documents import Document 
import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import TEAM_ALIASES,DATA_MATCHES_DIR,DATA_STATIC_DIR,DATA_METADATA_DIR

def match_metadata_func(record: dict, metadata: dict) -> dict:
    metadata["doc_type"] = "match"
    metadata["phase"] = record.get("phase")
    metadata["etape"] = record.get("etape")
    metadata["date"] = record.get("date")
    metadata["stade"] = record.get("stade")
    metadata["equipe_domicile"] = record.get("equipe_domicile")
    metadata["equipe_exterieur"] = record.get("equipe_exterieur")
    metadata["score"] = record.get("score")
    metadata["arbitre"] = record.get("arbitre")
    metadata["affluence"] = record.get("affluence")
    metadata["status"] = record.get("status")
    
    metadata["aliases_domicile"] = TEAM_ALIASES.get(metadata["equipe_domicile"], [metadata["equipe_domicile"]])
    metadata["aliases_exterieur"] = TEAM_ALIASES.get(metadata["equipe_exterieur"], [metadata["equipe_exterieur"]])

    buteurs_dom = record.get("buteurs_domicile", [])
    buteurs_ext = record.get("buteurs_exterieur", [])

    def format_buteurs(buteurs):
        if not buteurs:
            return "Aucun but"
        return ", ".join(
            f"{b['joueur']} ({b['minute']}')"
            for b in buteurs
        )

    cartons_dom = record.get("cartons_domicile", [])
    cartons_ext = record.get("cartons_exterieur", [])

    def format_cartons(cartons):
        if not cartons:
            return "Aucun carton"
        return ", ".join(
            f"{c['joueur']} ({c['type']} à {c['minute']}')"
            for c in cartons
        )
    status_label = "joué" if metadata["status"] == "played" else "programmé"

    metadata["page_content"] = (
        f"Statut : {status_label}. "
        f"{metadata['phase']} – {metadata['etape']}. "
        f"{record.get('match_n')}, joué le {metadata['date']} au {metadata['stade']}. "
        f"Match opposant {metadata['equipe_domicile']} à {metadata['equipe_exterieur']}. "
        f"Score final : {metadata['score']}. "
        f"Buteurs {metadata['equipe_domicile']} : {format_buteurs(buteurs_dom)}. "
        f"Buteurs {metadata['equipe_exterieur']} : {format_buteurs(buteurs_ext)}. "
        f"Cartons {metadata['equipe_domicile']} : {format_cartons(cartons_dom)}. "
        f"Cartons {metadata['equipe_exterieur']} : {format_cartons(cartons_ext)}. "
        f"Affluence : {metadata['affluence']} spectateurs. "
        f"Arbitre : {metadata['arbitre']}."
    )

    return metadata


def qualification_metadata_func(record: dict, metadata: dict) -> dict:
    metadata["doc_type"] = "qualification"
    metadata["equipe"] = record.get("Equipe")
    metadata["meilleur_resultat"] = record.get("Meilleur_resultat")
    metadata["participation"] = record.get("Participation")
    metadata["date_qualification"] = record.get("Date_qualification")

    metadata["aliases"] = TEAM_ALIASES.get(metadata["equipe"], [metadata["equipe"]])

    metadata["page_content"] = (
        f"{metadata['equipe']} est qualifiée pour la compétition. "
        f"Méthode de qualification : {record.get('Methode_qualification')}. "
        f"Date de qualification : {record.get('Date_qualification')}. "
        f"Nombre de participations : {record.get('Participation')}. "
        f"Première participation : {record.get('Premiere_participation')}. "
        f"Dernière participation : {record.get('Derniere_participation')}. "
        f"Meilleur résultat historique : {record.get('Meilleur_resultat')}. "
        f"Participations précédentes : {record.get('Apparitions_precedentes')}."
    )

    return metadata


def squad_metadata_func(record: dict, metadata: dict) -> dict:
    metadata["doc_type"] = "squad"
    metadata["equipe"] = record.get("team")

    squad = record.get("squad", {})

    metadata["aliases"] = TEAM_ALIASES.get(metadata["equipe"], [metadata["equipe"]])


    def format_players(players):
        if not players:
            return "Aucun joueur"
        return ", ".join(f"{p['name']} ({p['club']})" for p in players)

    goalkeepers = squad.get("goalkeepers", [])
    defenders = squad.get("defenders", [])
    midfielders = squad.get("midfielders", [])
    forwards = squad.get("forwards", [])

    metadata["page_content"] = (
        f"L'équipe nationale de {metadata['equipe']} pour la compétition comprend les joueurs suivants. "
        f"Gardiens de but : {format_players(goalkeepers)}. "
        f"Défenseurs : {format_players(defenders)}. "
        f"Milieux de terrain : {format_players(midfielders)}. "
        f"Attaquants : {format_players(forwards)}."
    )

    return metadata


def stade_metadata_func(record: dict, metadata: dict) -> dict:
    metadata["doc_type"] = "stade"
    metadata["ville"] = record.get("Ville")
    metadata["stade"] = record.get("Stade")
    metadata["capacite"] = record.get("Capacité")

    metadata["page_content"] = (
        f"Le stade {metadata['stade']} est situé à {metadata['ville']}. "
        f"Il a une capacité de {metadata['capacite']} places."
    )
    return metadata


def coach_metadata_func(record: dict, metadata: dict) -> dict:
    metadata["doc_type"] = "coach"
    metadata["equipe"] = record.get("pays")
    metadata["coach"] = record.get("selectionneur")

    metadata["aliases"] = TEAM_ALIASES.get(metadata["equipe"], [metadata["equipe"]])


    metadata["page_content"] = (
        f"L'entraîneur de l'équipe nationale de {metadata['equipe']} "
        f"est {metadata['coach']}."
    )
    return metadata


def classement_metadata_func(record: dict, metadata: dict) -> dict:
    metadata["doc_type"] = "classement"
    metadata["group"] = record.get("Nom_Groupe")

    classement = record.get("Classement", [])

    def format_ligne(ligne):
        return (
            f"{ligne['Rang']}. {ligne['Equipe']} – "
            f"{ligne['Pts']} points, "
            f"{ligne['Gagnes']} victoires, "
            f"{ligne['Nuls']} nuls, "
            f"{ligne['Perdus']} défaites, "
            f"buts pour {ligne['Buts_pour']}, "
            f"buts contre {ligne['Buts_contre']} "
            f"(différence {ligne['Diff']})"
        )

    metadata["page_content"] = (
        f"Classement du {metadata['group']} après la phase de groupes. "
        + " ".join(format_ligne(ligne) for ligne in classement)
    )

    return metadata

def get_static_loaders():
    return {
        "stades": JSONLoader(
            file_path=os.path.join(DATA_STATIC_DIR, "stades.json"), 
            jq_schema=".[]", 
            metadata_func=stade_metadata_func, 
            text_content=False
        ),
        "classement": JSONLoader(
            file_path=os.path.join(DATA_STATIC_DIR, "classement_phase_groupe.json"), 
            jq_schema=".[]", 
            metadata_func=classement_metadata_func, 
            text_content=False
        ),
        "coaches": JSONLoader(
            file_path=os.path.join(DATA_STATIC_DIR, "coach.json"), 
            jq_schema=".[]", 
            metadata_func=coach_metadata_func, 
            text_content=False
        ),
        "squads": DirectoryLoader(
            path=os.path.join(DATA_STATIC_DIR, "squads"), 
            glob="*.json", 
            loader_cls=JSONLoader, 
            loader_kwargs={"jq_schema": ".", "metadata_func": squad_metadata_func, "text_content": False}
        ),
        "qualif": JSONLoader(
            file_path=os.path.join(DATA_STATIC_DIR, "equipes_qualifiees.json"), 
            jq_schema=".[]", 
            metadata_func=qualification_metadata_func, 
            text_content=False
        )
    }
def get_match_loader(version="v1"):
    path = os.path.join(DATA_MATCHES_DIR, version)
    return DirectoryLoader(
        path=path,
        glob="*.json",
        loader_cls=JSONLoader,
        loader_kwargs={
            "jq_schema": ".",
            "metadata_func": match_metadata_func,
            "text_content": False
        }
    )
def create_synth_doc():
    path = os.path.join(DATA_STATIC_DIR, "equipes_qualifiees.json")
    with open(path, 'r', encoding='utf-8') as f:
        equipes_data = json.load(f)
    liste_noms = [e.get('Equipe') for e in equipes_data]
    all_aliases = []
    for e in liste_noms:
        all_aliases.extend(TEAM_ALIASES.get(e, [e]))
    return Document(
        page_content=f"Les équipes qualifiées sont : {', '.join(liste_noms)}.",
        metadata={"title": "Liste officielle", "doc_type": "synthese", "aliases": list(set(all_aliases))}
    )