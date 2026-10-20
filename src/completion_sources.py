"""Sources de temps de complétion. Une fonction par source, interchangeables.

Chaque fonction renvoie des dicts « bruts » qui sont mis en cache tels quels ;
l'interprétation (choix de la source, avertissements) est faite dans compute.py.
"""

import re

import reseau

# ---------------------------------------------------------------------------
# SteamHunters (source préférée)
# ---------------------------------------------------------------------------
# Vérifié le 2026-10-20 sur une dizaine de jeux :
#   - GET https://steamhunters.com/api/apps/{appid}  → un objet JSON (ou null)
#   - GET https://steamhunters.com/api/apps?appIds=1,2,3  → liste ; les appids
#     inconnus sont simplement absents. Testé avec 100 ids en une requête (0,4 s).
#   - pas de clé, pas d'en-tête CORS.
# Supposé, non documenté :
#   - medianCompletionTime / fastestCompletionTime sont en MINUTES (cohérent :
#     Portal 2 → 2010 = 33,5 h, médiane ; record 152 = 2,5 h). Il s'agit
#     probablement du temps de jeu Steam total des joueurs ayant fini le jeu,
#     donc une estimation plutôt haute.
#   - aucune limite de débit ni conditions d'utilisation publiées trouvées :
#     on reste poli (lots de 100, une requête par seconde).
SH_URL = "https://steamhunters.com/api/apps"
SH_TAILLE_LOT = 100

# Champs gardés en cache (le reste de la réponse ne sert pas)
SH_CHAMPS = [
    "name", "achievementCount", "unobtainableAchievementCount",
    "fastestCompletionTime", "medianCompletionTime",
    "playersPerfectedCount", "playersCompletedCount", "playersStartedCount",
    "hasPaidDlc", "isRemoved", "isRestricted", "isFree", "tags",
]


def steamhunters_lot(appids):
    """Données SteamHunters pour un lot d'appids (≤ 100).

    Renvoie {appid: dict}. Un appid inconnu de SteamHunters reçoit
    {"trouve": False} pour qu'on ne le redemande pas à chaque sync.
    """
    code, donnees = reseau.get_json(
        SH_URL, {"appIds": ",".join(str(a) for a in appids)}
    )
    if code != 200 or not isinstance(donnees, list):
        raise reseau.ErreurReseau(f"SteamHunters : réponse inattendue (HTTP {code})")
    resultat = {a: {"trouve": False} for a in appids}
    for app in donnees:
        d = {k: app.get(k) for k in SH_CHAMPS}
        d["tags"] = [t.get("name") for t in (app.get("tags") or [])]
        d["trouve"] = True
        resultat[app["appId"]] = d
    return resultat


# ---------------------------------------------------------------------------
# HowLongToBeat (source de secours)
# ---------------------------------------------------------------------------
# Pas d'API officielle : on passe par la bibliothèque communautaire
# howlongtobeatpy, qui imite le site et peut casser si HLTB change.
# Vérifié le 2026-10-20 (v1.0.24) : Portal 2 → 22,9 h, Hollow Knight → 65,7 h.
# Limites :
#   - durée « Completionist » déclarée par les joueurs, PAS basée sur les succès ;
#   - pas d'appid Steam dans les résultats : appariement par NOM uniquement
#     (risque de faux positif, d'où un seuil de similarité et un avertissement).
HLTB_SIMILARITE_MIN = 0.8


def _nettoyer_nom(nom):
    """Retire ™ ® © et les espaces multiples, qui gênent la recherche HLTB."""
    nom = re.sub(r"[™®©]", "", nom)
    return re.sub(r"\s+", " ", nom).strip()


def hltb_par_nom(nom):
    """Cherche un jeu sur HLTB par son nom.

    Renvoie {"trouve": True, "heures": float, "nom_hltb": str,
             "similarite": float, "nb_mesures": int}
    ou {"trouve": False}. Lève une exception en cas de panne (à réessayer).
    """
    # Import ici : si la bibliothèque manque ou casse, le reste fonctionne
    from howlongtobeatpy import HowLongToBeat

    resultats = HowLongToBeat().search(_nettoyer_nom(nom))
    if not resultats:
        return {"trouve": False}
    meilleur = max(resultats, key=lambda r: r.similarity)
    if meilleur.similarity < HLTB_SIMILARITE_MIN or not meilleur.completionist:
        return {"trouve": False, "meilleur_candidat": meilleur.game_name}
    return {
        "trouve": True,
        "heures": float(meilleur.completionist),
        "nom_hltb": meilleur.game_name,
        "similarite": round(float(meilleur.similarity), 3),
        "nb_mesures": int(meilleur.json_content.get("comp_100_count") or 0),
    }
