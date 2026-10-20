"""Appels à l'API Web officielle de Steam.

Vérifié le 2026-10-20 :
  - l'API ne renvoie pas d'en-tête CORS (Access-Control-Allow-Origin absent),
    donc elle n'est pas lisible depuis une page web : d'où ce script.
Non encore vérifié avec une vraie clé (formats tirés de la doc Valve / usage connu,
à confirmer au premier lancement) :
  - GetOwnedGames : {"response": {"game_count": N, "games": [...]}} ;
    {"response": {}} si le profil ou les détails de jeux sont privés.
  - GetPlayerAchievements : HTTP 400 + "Requested app has no stats" pour un jeu
    sans succès ; HTTP 403 + "Profile is not public" si profil privé.
"""

import reseau

BASE = "https://api.steampowered.com"


class ProfilPrive(Exception):
    pass


def jeux_possedes(cle, steam_id):
    """Liste des jeux possédés : [{appid, name, playtime_forever (min), ...}]."""
    code, donnees = reseau.get_json(
        f"{BASE}/IPlayerService/GetOwnedGames/v1/",
        {
            "key": cle,
            "steamid": steam_id,
            "include_appinfo": 1,
            "include_played_free_games": 1,
            "format": "json",
        },
    )
    if code == 401 or code == 403:
        raise ProfilPrive(f"HTTP {code} : clé API invalide ou profil inaccessible")
    if code != 200 or not isinstance(donnees, dict):
        raise reseau.ErreurReseau(f"GetOwnedGames : réponse inattendue (HTTP {code})")
    reponse = donnees.get("response") or {}
    if "games" not in reponse:
        # Réponse vide = détails de jeux privés (cas connu, pas une erreur réseau)
        raise ProfilPrive(
            "Steam ne renvoie aucun jeu : passe « Détails des jeux » en public "
            "dans les paramètres de confidentialité du profil."
        )
    return reponse["games"]


def succes_joueur(cle, steam_id, appid):
    """Succès du joueur pour un jeu.

    Renvoie un dict :
      {"statut": "ok", "debloques": n, "total": m}
      {"statut": "sans_succes"}            jeu sans succès / sans stats
      {"statut": "prive"}                  jeu marqué privé : succès invisibles
      {"statut": "erreur", "message": ...}  à réessayer au prochain sync
    """
    code, donnees = reseau.get_json(
        f"{BASE}/ISteamUserStats/GetPlayerAchievements/v1/",
        {"key": cle, "steamid": steam_id, "appid": appid},
    )
    stats = (donnees or {}).get("playerstats") or {}
    if code == 200 and stats.get("success"):
        liste = stats.get("achievements") or []
        return {
            "statut": "ok",
            "debloques": sum(1 for a in liste if a.get("achieved") == 1),
            "total": len(liste),
        }
    message = stats.get("error") or f"HTTP {code}"
    if "no stats" in message.lower():
        return {"statut": "sans_succes"}
    if code == 403 or "not public" in message.lower():
        # Jeu marqué privé sur Steam (constaté avec Cookie Clicker : HTTP 403
        # « Profile is not public » alors que le profil est public), ou profil
        # entier privé : main.py abandonne si ça touche tous les premiers jeux
        return {"statut": "prive", "prive": True}
    return {"statut": "erreur", "message": reseau.masquer(message)}
