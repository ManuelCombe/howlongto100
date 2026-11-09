"""Tags perso posés sur les jeux (« jamais » pour l'instant), stockés dans tags.json.

Le script ne fait que LIRE tags.json. C'est la page HTML qui le produit (bouton
« Exporter les tags ») : une page statique ne peut pas écrire sur le disque, elle
garde donc les changements dans le localStorage du navigateur en attendant.

Format de tags.json (versionné dans le dépôt) :

    {
      "version": 1,
      "jeux": {
        "730": {
          "nom": "Counter-Strike 2",
          "tags": {
            "jamais": {"actif": true, "modifie_le": "2026-11-09T14:32:05.123Z"}
          }
        }
      }
    }

- Les clés de « jeux » sont les appid Steam (en texte, contrainte du JSON).
- « nom » sert seulement à rendre le fichier lisible dans un diff ; il est ignoré à la lecture.
- Un tag retiré reste présent avec "actif": false. Sa date permet, lors de la
  fusion avec le navigateur, de savoir quelle version est la plus récente.
- Les dates sont en ISO 8601 UTC (format de Date.toISOString() en JS) :
  comparer les textes suffit pour savoir lequel est le plus récent.
"""

import json
from pathlib import Path

CHEMIN_DEFAUT = Path(__file__).resolve().parent.parent / "tags.json"
VERSION = 1

# Tags connus de la page HTML : un bouton par tag sur chaque ligne.
# Pour en ajouter un plus tard, une entrée ici suffit pour le bouton et le filtre.
# Prévus (non implémentés) : "deck", "court", "cleo" (« à faire avec Cléo »).
TAGS = {
    "jamais": {
        "libelle": "jamais",
        "description": "jeu que je ne jouerai pas, écarté sans le désinstaller",
        # Masqué du tableau et des totaux tant que le filtre « Afficher » n'est pas coché
        "masque_par_defaut": True,
    },
}


def lire(chemin=CHEMIN_DEFAUT):
    """Renvoie (jeux, problèmes). Ne lève jamais d'exception.

    Fichier absent : aucun tag, sans message. Fichier illisible : aucun tag pour
    ce rapport, avec un message ; le fichier n'est jamais modifié par le script.
    Les tags inconnus sont conservés tels quels (la page les ré-exporte sans y toucher).
    """
    chemin = Path(chemin)
    if not chemin.exists():
        return {}, []
    try:
        brut = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {}, [f"illisible ({e}) : ignoré pour ce rapport, fichier laissé tel quel"]
    if not isinstance(brut, dict) or not isinstance(brut.get("jeux"), dict):
        return {}, ["clé « jeux » absente ou invalide : ignoré pour ce rapport"]

    problemes = []
    if brut.get("version") != VERSION:
        problemes.append(f"version {brut.get('version')!r} inattendue (attendu {VERSION}), lecture tentée quand même")

    jeux, ignores = {}, 0
    for appid, entree in brut["jeux"].items():
        if not str(appid).isdigit() or not isinstance(entree, dict) or not isinstance(entree.get("tags"), dict):
            ignores += 1
            continue
        tags = {}
        for tag, e in entree["tags"].items():
            if isinstance(e, dict) and isinstance(e.get("actif"), bool):
                tags[tag] = {"actif": e["actif"], "modifie_le": str(e.get("modifie_le") or "")}
            else:
                ignores += 1
        if tags:
            jeux[str(appid)] = {"nom": entree.get("nom"), "tags": tags}

    if ignores:
        problemes.append(f"{ignores} entrée(s) malformée(s) ignorée(s)")
    inconnus = {t for j in jeux.values() for t in j["tags"]} - TAGS.keys()
    if inconnus:
        problemes.append("tag(s) inconnu(s) conservé(s) sans bouton : " + ", ".join(sorted(inconnus)))
    return jeux, problemes


def compter(jeux, tag):
    """Nombre de jeux ayant ce tag actif."""
    return sum(1 for j in jeux.values() if (j["tags"].get(tag) or {}).get("actif"))
