"""Requêtes HTTP communes : délai, réessais espacés, masquage des secrets.

Nommé « reseau » et pas « http » pour ne pas masquer le module standard
`http` (src/ est en tête du sys.path quand on lance src/main.py).
"""

import time

import requests

USER_AGENT = "steam-100-tracker/0.1 (outil perso)"
TIMEOUT_S = 30
# Attentes successives avant chaque nouvel essai (secondes)
ATTENTES_REESSAI = [5, 15, 45, 120]

# Valeurs à ne jamais laisser apparaître dans un message (clé API…)
_secrets = set()


def enregistrer_secret(valeur):
    """Déclare une valeur sensible à masquer dans tous les messages."""
    if valeur:
        _secrets.add(valeur)


def masquer(texte):
    """Remplace les secrets connus par *** (les exceptions requests contiennent l'URL complète)."""
    texte = str(texte)
    for s in _secrets:
        texte = texte.replace(s, "***")
    return texte


class ErreurReseau(Exception):
    """Échec définitif après tous les réessais. Le message est déjà masqué."""


_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT


def get_json(url, params=None):
    """GET avec réessais sur 429, 5xx et timeouts.

    Renvoie (code_http, json_ou_None). Les autres codes 4xx sont renvoyés
    tels quels à l'appelant, qui sait les interpréter (ex. 400 « no stats »).
    Lève ErreurReseau si tous les essais échouent.
    """
    derniere_erreur = None
    for essai in range(len(ATTENTES_REESSAI) + 1):
        if essai > 0:
            attente = ATTENTES_REESSAI[essai - 1]
            # Retry-After explicite du serveur : on le respecte s'il est plus long
            if isinstance(derniere_erreur, requests.Response):
                ra = derniere_erreur.headers.get("Retry-After", "")
                if ra.isdigit():
                    attente = max(attente, int(ra))
            print(f"    … nouvel essai dans {attente} s ({_decrire(derniere_erreur)})")
            time.sleep(attente)
        try:
            r = _session.get(url, params=params, timeout=TIMEOUT_S)
        except (requests.Timeout, requests.ConnectionError) as e:
            derniere_erreur = e
            continue
        if r.status_code == 429 or r.status_code >= 500:
            derniere_erreur = r
            continue
        try:
            donnees = r.json()
        except ValueError:
            donnees = None
        return r.status_code, donnees
    raise ErreurReseau(masquer(_decrire(derniere_erreur)))


def _decrire(erreur):
    if isinstance(erreur, requests.Response):
        return f"HTTP {erreur.status_code}"
    return masquer(f"{type(erreur).__name__}: {erreur}")
