# howlongto100

Combien de temps me reste-t-il pour faire le **100 % des succès** de chacun de mes jeux Steam ?

Un script Python récupère ta bibliothèque Steam, tes succès et des temps de complétion communautaires, puis génère une **page HTML autonome** : un tableau triable par temps restant, filtrable, lisible sur mobile, qui s'ouvre directement dans le navigateur (aucun serveur, aucune dépendance externe).

Testé sur une bibliothèque de ~1 800 jeux.

## Sources de données

| Source | Utilisée pour | Remarques |
|---|---|---|
| [API Web Steam](https://steamcommunity.com/dev) | jeux possédés, temps joué, succès débloqués | clé API requise |
| [SteamHunters](https://steamhunters.com) | temps médian de complétion à 100 %, succès non obtenables, DLC, tags | source préférée, API publique non documentée |
| [HowLongToBeat](https://howlongtobeat.com) | durée « Completionist » | secours uniquement, via [`howlongtobeatpy`](https://pypi.org/project/howlongtobeatpy/) ; temps déclarés, **pas** basés sur les succès Steam ; appariement par nom |

Ces APIs ne renvoient pas d'en-tête CORS : elles ne sont pas lisibles depuis une page web, d'où le script.

## Installation

Python 3 (testé avec 3.14).

```bash
git clone https://github.com/ManuelCombe/howlongto100.git
cd howlongto100
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Puis remplis `.env` :

- `STEAM_API_KEY` : ta clé, à créer sur <https://steamcommunity.com/dev/apikey> ;
- `STEAM_ID` : ton SteamID64 (17 chiffres, par ex. via <https://steamid.io>).

Ton profil Steam doit être public, au moins la section **Détails des jeux**.

## Utilisation

```bash
.venv/bin/python src/main.py sync      # récupère les données et remplit le cache
.venv/bin/python src/main.py report    # génère output/rapport.html depuis le cache
.venv/bin/python src/main.py all       # sync puis report
```

Option `--limite N` : ne traiter que les N jeux les plus joués (pratique pour un premier essai).

- La première synchronisation est lente (une requête Steam par jeu, ~20 min pour 1 500 jeux). Les suivantes ne redemandent que ce qui a changé (temps de jeu modifié) ou expiré.
- Ctrl+C à tout moment : tout est enregistré au fil de l'eau dans `cache/cache.sqlite`, la relance reprend où elle s'était arrêtée.
- Une erreur sur un jeu n'arrête jamais le traitement : elle est listée en fin de sync et le jeu sera réessayé la fois suivante.

## Calcul du temps restant

```
E               = temps estimé pour le 100 % (médiane SteamHunters, sinon HLTB Completionist)
par_temps       = max(0, E − temps joué)
par_proportion  = E × succès restants / succès total
temps restant   = max(par_temps, par_proportion)
```

Le maximum des deux est l'option prudente : il évite qu'un jeu « idlé » (cartes à échanger) sans aucun succès paraisse presque fini. La source et le détail du calcul sont affichés pour chaque jeu (survol de la colonne Source).

## Cas particuliers

| Cas | Traitement |
|---|---|
| Jeu sans succès | listé à part, hors tableau principal |
| Jeu à 100 % | « terminé », masqué par défaut |
| Pas d'estimation disponible | « inconnu », jamais compté comme 0 h |
| Succès non obtenables | badge rouge, exclu du total |
| Multijoueur / sans fin (tags MOBA, Competitive, MMO…) | badge rouge, exclu du total |
| Estimation > 1 000 h | badge rouge, exclu du total |
| Jeu marqué privé sur Steam | « inconnu », badge « privé » |
| Grande stratégie / 4X, DLC payant, peu de données, > 300 h | badge orange, reste dans le total |

Les seuils et listes de tags sont en tête de `src/compute.py`.

## Limites connues

- Toutes les estimations sont **communautaires** : à prendre comme un ordre de grandeur.
- L'API SteamHunters n'est pas documentée. Les temps sont supposés en minutes (cohérent sur tous les jeux testés) et correspondent probablement au temps de jeu total des joueurs ayant fini, donc plutôt hauts. Aucune limite de débit publiée : le script fait des lots de 100 jeux, une requête par seconde.
- HLTB n'a pas d'API officielle ; `howlongtobeatpy` peut casser si le site change.

## Structure

```
src/
  main.py               point d'entrée (sync / report / all)
  steam_api.py          appels à l'API Steam
  completion_sources.py SteamHunters et HLTB (une fonction par source)
  cache.py              cache SQLite
  compute.py            calcul du temps restant et avertissements
  report.py             génération de la page HTML
  reseau.py             requêtes HTTP : délais, réessais, masquage de la clé
```

## Confidentialité

La clé API et le SteamID ne sont lus que depuis `.env` ou les variables d'environnement, jamais écrits dans le code ni dans les logs. `.env`, le cache et le rapport généré sont exclus du dépôt.

## Licence

[MIT](LICENSE)
