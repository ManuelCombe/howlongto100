"""Cache SQLite : une seule table clé/valeur, une ligne par (source, appid).

Chaque résultat est enregistré (commit) dès qu'il arrive : si le script est
interrompu, la reprise ne refait jamais ce qui est déjà en cache.
"""

import json
import sqlite3
import time
from pathlib import Path

CHEMIN_DEFAUT = Path(__file__).resolve().parent.parent / "cache" / "cache.sqlite"

# Durées de validité (secondes)
JOUR = 86400
TTL = {
    # Succès du joueur : courte. En plus, on rafraîchit dès que le temps de jeu
    # a bougé (voir main.py), donc ce TTL ne sert qu'à rattraper les cas rares
    # (succès ajoutés par une mise à jour du jeu sans que j'y aie rejoué).
    "steam_succes": 14 * JOUR,
    # Temps de complétion communautaires : longue
    "steamhunters": 30 * JOUR,
    "hltb": 90 * JOUR,
}


class Cache:
    def __init__(self, chemin=CHEMIN_DEFAUT):
        Path(chemin).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(chemin)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS cache (
                   source     TEXT    NOT NULL,
                   appid      INTEGER NOT NULL,
                   donnees    TEXT    NOT NULL,   -- JSON
                   recupere_le REAL   NOT NULL,   -- timestamp Unix
                   PRIMARY KEY (source, appid)
               )"""
        )
        self.db.commit()

    def lire(self, source, appid):
        """Renvoie (donnees, age_en_secondes) ou (None, None) si absent."""
        ligne = self.db.execute(
            "SELECT donnees, recupere_le FROM cache WHERE source = ? AND appid = ?",
            (source, appid),
        ).fetchone()
        if ligne is None:
            return None, None
        return json.loads(ligne[0]), time.time() - ligne[1]

    def lire_tout(self, source):
        """Dictionnaire {appid: donnees} pour une source."""
        lignes = self.db.execute(
            "SELECT appid, donnees FROM cache WHERE source = ?", (source,)
        )
        return {appid: json.loads(d) for appid, d in lignes}

    def est_frais(self, source, appid):
        """Vrai si une entrée existe et n'a pas dépassé sa durée de validité."""
        _, age = self.lire(source, appid)
        return age is not None and age < TTL.get(source, 0)

    def ecrire(self, source, appid, donnees):
        self.db.execute(
            "INSERT OR REPLACE INTO cache (source, appid, donnees, recupere_le) VALUES (?, ?, ?, ?)",
            (source, appid, json.dumps(donnees, ensure_ascii=False), time.time()),
        )
        self.db.commit()
