# Steam 100 % Tracker

## Objectif

Outil perso qui me dit **combien de temps il me reste pour atteindre le 100 % des succès** sur chacun de mes jeux Steam, et qui me permet de **trier ma bibliothèque par temps restant**.

Contexte : plus de 1 500 jeux dans la bibliothèque. Completionist.me affiche déjà des données de complétion par jeu, mais ne permet pas de trier par temps restant vers le 100 %. C'est ce manque que cet outil comble.

## Livrable

1. Un **script Python** qui récupère les données, les met en cache et calcule les estimations.
2. Un **fichier HTML autonome** généré par le script : tableau triable et filtrable, ouvrable directement dans le navigateur, sans serveur.

Pas d'appli web avec backend : le script fait le travail lourd, la page n'est que l'affichage.

## Pourquoi un script et pas une page seule

- Hypothèse (à vérifier dans le code) : l'API Web Steam n'est pas appelable directement depuis un navigateur (CORS).
- 1 500+ jeux = beaucoup de requêtes (succès par jeu, temps de complétion par jeu) : il faut un cache, des reprises sur erreur et des délais entre requêtes.

## Sources de données

- **API officielle Steam** : liste des jeux possédés, temps de jeu, succès débloqués par jeu, % global de déblocage. Clé API et SteamID lus depuis des variables d'environnement (voir plus bas).
- **SteamHunters** (source préférée pour le temps de complétion) : temps de complétion les plus rapides et médians, % de joueurs ayant fait le 100 %, DLC payant requis, succès non obtenables ou cassés. Son API publique alimente une extension navigateur ; à vérifier : endpoints exacts, limites de débit, conditions d'utilisation.
- **HowLongToBeat** (source de secours) : durée « Completionist ». Attention, ce n'est pas basé sur les succès Steam mais sur des temps déclarés par les joueurs.
- Completionist.me expose aussi des temps moyens/médians de complétion par jeu, mais je n'ai pas vérifié s'il existe une API exploitable.

## Calcul du temps restant

Idée de départ, à affiner :

- `temps_restant = temps_complétion_estimé − temps_déjà_joué`, borné à 0 minimum.
- Alternative plus fine : pondérer par la proportion de succès restants (`succès_restants / succès_total`), en gardant le calcul simple et explicable.
- Toujours afficher **la source et la méthode** utilisées pour chaque jeu (SteamHunters médian, HLTB, etc.), car ce sont des estimations communautaires.
- Les jeux sans estimation fiable vont dans une catégorie **« inconnu »**, jamais ignorés silencieusement et jamais comptés comme 0 h.

## Cas particuliers à gérer

- Jeux sans aucun succès : exclus du tri principal, listés à part.
- Jeux déjà à 100 % : marqués « terminé », exclus du tri par défaut.
- Jeux sans donnée de temps de complétion : « inconnu ».
- Jeux où le 100 % est impossible ou cassé (succès non obtenables, serveurs fermés, DLC requis) : afficher un avertissement, ne pas fausser le total.
- Jeux multijoueur ou sans fin (type Counter-Strike) : le temps estimé n'a pas de sens, prévoir un marqueur.
- Jeux de stratégie très longs (type Paradox) : le « 100 % » est trompeur, ne pas se fier aveuglément à l'estimation.

## Architecture proposée

```
steam-100/
  CLAUDE.md
  .env.example          # variables attendues, sans valeurs réelles
  .gitignore            # ignore .env et le cache
  src/
    steam_api.py        # appels API Steam
    completion_sources.py  # SteamHunters, HLTB (une fonction par source)
    cache.py            # SQLite
    compute.py          # calcul du temps restant
    report.py           # génération du HTML
    main.py             # point d'entrée en ligne de commande
  output/
    rapport.html        # généré, non versionné
```

## Cache

- SQLite local, un fichier.
- Première exécution lente (normal), les suivantes ne mettent à jour que ce qui a changé ou expiré.
- Durée de validité distincte : succès du joueur (courte), temps de complétion communautaires (longue).
- Reprise après interruption : on ne refait jamais ce qui est déjà en cache.

## Contraintes techniques

- **Délai entre requêtes** et gestion des erreurs 429 / timeouts avec réessais espacés.
- Sortie console de progression lisible (par exemple « 412/1537 jeux traités »).
- Une erreur sur un jeu ne doit jamais arrêter tout le traitement : on la note et on continue.
- Le profil Steam doit être public (au moins la section détails des jeux).

## Secrets et confidentialité

- Clé API Steam et SteamID dans des **variables d'environnement** (`STEAM_API_KEY`, `STEAM_ID`), jamais en dur dans le code, jamais dans le dépôt.
- Fournir `.env.example` avec des valeurs factices.
- Ne jamais afficher la clé API dans les logs.

## Page HTML

Autonome (CSS et JS inline, aucune dépendance externe), avec :

- Tableau triable par colonne, **tri par défaut : temps restant croissant**.
- Colonnes : jeu, temps joué, succès débloqués / total, % de succès, estimation du temps de complétion, **temps restant estimé**, source de l'estimation, avertissements.
- Filtres : jeux avec succès restants uniquement, temps restant maximum, masquer les « inconnu », recherche par nom.
- Total global en tête : nombre de jeux terminés, restants, somme des heures estimées.
- Lisible sur mobile.

## Commandes prévues

À adapter selon ce qui sera réellement codé :

```
python src/main.py sync      # récupère les données et remplit le cache
python src/main.py report    # génère output/rapport.html depuis le cache
python src/main.py all       # sync puis report
```

## Conventions

- Python 3, code simple et commenté en français.
- Dépendances minimales, listées dans `requirements.txt`.
- Chaque source de données est isolée dans sa propre fonction, pour pouvoir la remplacer facilement.
- Quand une hypothèse n'est pas vérifiée (endpoint, format de réponse, limite de débit), le dire explicitement dans le code ou dans la réponse plutôt que d'inventer.

## Ordre de travail suggéré

1. Vérifier les endpoints réels de l'API Steam et de SteamHunters sur 5 à 10 jeux, avant tout code complet.
2. Mettre en place le cache et la récupération des succès.
3. Brancher la source de temps de complétion, puis la source de secours.
4. Écrire le calcul du temps restant.
5. Générer la page HTML.
6. Tester sur la bibliothèque complète, puis traiter les cas particuliers rencontrés.

## Style de réponse attendu de Claude Code

- Expliquer chaque commande de terminal donnée, une par une.
- Dire clairement ce qui est vérifié et ce qui est supposé ou inventé.
- Ton sympa et direct, pas de blabla.
