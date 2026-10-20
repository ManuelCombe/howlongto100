"""Point d'entrée : python src/main.py {sync,report,all} [--limite N]

  sync    récupère les données et remplit le cache (reprend là où il s'était arrêté)
  report  génère output/rapport.html depuis le cache, sans aucune requête réseau
  all     sync puis report
"""

import argparse
import os
import sys
import time
from pathlib import Path

import cache as cache_mod
import completion_sources
import compute
import report
import reseau
import steam_api

RACINE = Path(__file__).resolve().parent.parent

# Délais entre requêtes (secondes). Valeurs prudentes, pas des limites officielles.
DELAI_STEAM = 0.4
DELAI_STEAMHUNTERS = 1.0
DELAI_HLTB = 1.5


def charger_env():
    """Lit .env (format CLE=valeur) sans écraser les variables déjà définies."""
    fichier = RACINE / ".env"
    if fichier.exists():
        for ligne in fichier.read_text(encoding="utf-8").splitlines():
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#") and "=" in ligne:
                cle, valeur = ligne.split("=", 1)
                os.environ.setdefault(cle.strip(), valeur.strip().strip("\"'"))
    cle, steam_id = os.environ.get("STEAM_API_KEY"), os.environ.get("STEAM_ID")
    if not cle or not steam_id:
        sys.exit("STEAM_API_KEY et STEAM_ID doivent être définis (voir .env.example).")
    reseau.enregistrer_secret(cle)
    return cle, steam_id


def jeux_cibles(c, limite):
    """Jeux possédés depuis le cache ; avec --limite, les N plus joués (pour tester)."""
    jeux = c.lire("steam_jeux", 0)[0] or []
    if limite:
        jeux = sorted(jeux, key=lambda j: -(j.get("playtime_forever") or 0))[:limite]
    return jeux


# ---------------------------------------------------------------------------
# Étapes du sync
# ---------------------------------------------------------------------------

def sync_jeux(c, cle, steam_id):
    print("1/4  Liste des jeux possédés (Steam)…")
    try:
        jeux = steam_api.jeux_possedes(cle, steam_id)
    except steam_api.ProfilPrive as e:
        sys.exit(f"     ✗ {e}")
    except reseau.ErreurReseau as e:
        if c.lire("steam_jeux", 0)[0]:
            print(f"     ✗ {e} — on continue avec la liste en cache")
            return
        sys.exit(f"     ✗ {e}")
    c.ecrire("steam_jeux", 0, jeux)
    print(f"     {len(jeux)} jeux")


def sync_steamhunters(c, jeux, erreurs):
    a_faire = [j["appid"] for j in jeux if not c.est_frais("steamhunters", j["appid"])]
    print(f"2/4  SteamHunters : {len(a_faire)} jeu(x) à mettre à jour, "
          f"{len(jeux) - len(a_faire)} déjà en cache")
    lots = [a_faire[i:i + completion_sources.SH_TAILLE_LOT]
            for i in range(0, len(a_faire), completion_sources.SH_TAILLE_LOT)]
    for n, lot in enumerate(lots, 1):
        try:
            for appid, donnees in completion_sources.steamhunters_lot(lot).items():
                c.ecrire("steamhunters", appid, donnees)
        except reseau.ErreurReseau as e:
            erreurs.append(f"SteamHunters lot {n} : {e}")
        print(f"     lot {n}/{len(lots)}")
        time.sleep(DELAI_STEAMHUNTERS)


def sync_succes(c, cle, steam_id, jeux, erreurs):
    sh = c.lire_tout("steamhunters")
    a_faire = []
    for j in jeux:
        appid, joue = j["appid"], j.get("playtime_forever") or 0
        d_sh = sh.get(appid) or {}
        # SteamHunters dit « aucun succès » : inutile d'interroger Steam
        if d_sh.get("trouve") and d_sh.get("achievementCount") == 0:
            continue
        en_cache, _ = c.lire("steam_succes", appid)
        if (en_cache and en_cache.get("statut") != "erreur"
                and en_cache.get("joue_min") == joue
                and c.est_frais("steam_succes", appid)):
            continue  # rien n'a bougé depuis la dernière fois
        a_faire.append((appid, joue))

    print(f"3/4  Succès du joueur (Steam) : {len(a_faire)} jeu(x) à interroger")
    prives = 0
    for i, (appid, joue) in enumerate(a_faire, 1):
        try:
            r = steam_api.succes_joueur(cle, steam_id, appid)
        except reseau.ErreurReseau as e:
            r = {"statut": "erreur", "message": str(e)}
        if r.get("prive"):
            prives += 1
            # Tous les premiers jeux refusés : c'est le profil, pas le jeu
            if prives == i and i >= 5:
                sys.exit("     ✗ Steam refuse l'accès aux succès : passe « Détails des jeux » en public.")
        if r["statut"] == "erreur":
            erreurs.append(f"Succès appid {appid} : {r['message']}")
        r["joue_min"] = joue
        c.ecrire("steam_succes", appid, r)
        if i % 25 == 0 or i == len(a_faire):
            print(f"     {i}/{len(a_faire)} jeux traités")
        time.sleep(DELAI_STEAM)
    if prives:
        print(f"     {prives} jeu(x) marqué(s) privé(s) sur Steam : « inconnu » dans le rapport")


def sync_hltb(c, jeux, erreurs):
    """HLTB seulement pour les jeux non terminés sans médiane SteamHunters."""
    sh = c.lire_tout("steamhunters")
    succes = c.lire_tout("steam_succes")
    a_faire = []
    for j in jeux:
        s, d_sh = succes.get(j["appid"]) or {}, sh.get(j["appid"]) or {}
        if s.get("statut") != "ok" or s["debloques"] >= s["total"]:
            continue
        if d_sh.get("medianCompletionTime"):
            continue
        if not c.est_frais("hltb", j["appid"]):
            a_faire.append(j)

    print(f"4/4  HowLongToBeat (secours) : {len(a_faire)} jeu(x) à chercher")
    for i, j in enumerate(a_faire, 1):
        try:
            c.ecrire("hltb", j["appid"], completion_sources.hltb_par_nom(j.get("name") or ""))
        except ImportError:
            erreurs.append("HLTB ignoré : bibliothèque howlongtobeatpy absente (pip install -r requirements.txt)")
            return
        except Exception as e:  # la bibliothèque peut lever n'importe quoi si HLTB change
            erreurs.append(f"HLTB « {j.get('name')} » : {type(e).__name__}: {reseau.masquer(e)}")
        if i % 10 == 0 or i == len(a_faire):
            print(f"     {i}/{len(a_faire)} jeux traités")
        time.sleep(DELAI_HLTB)


def sync(c, limite):
    cle, steam_id = charger_env()
    erreurs = []
    sync_jeux(c, cle, steam_id)
    jeux = jeux_cibles(c, limite)
    if limite:
        print(f"     --limite : on ne traite que les {len(jeux)} jeux les plus joués")
    sync_steamhunters(c, jeux, erreurs)
    sync_succes(c, cle, steam_id, jeux, erreurs)
    sync_hltb(c, jeux, erreurs)
    print(f"Sync terminé, {len(erreurs)} erreur(s).")
    for e in erreurs[:30]:
        print(f"  - {e}")
    if len(erreurs) > 30:
        print(f"  … et {len(erreurs) - 30} autres (relancer sync les réessaie)")


def generer_rapport(c, limite):
    jeux = jeux_cibles(c, limite)
    if not jeux:
        sys.exit("Cache vide : lance d'abord « python src/main.py sync ».")
    lignes, resume = compute.calculer(
        jeux, c.lire_tout("steam_succes"), c.lire_tout("steamhunters"), c.lire_tout("hltb")
    )
    chemin = report.generer(lignes, resume)
    print(f"Rapport : {chemin}")
    print(f"  {resume['a_faire']} à finir (≈ {resume['heures_restantes']} h, hors "
          f"{resume['exclus_du_total']} exclus), {resume['inconnus']} inconnu(s), "
          f"{resume['termines']} terminé(s), {resume['sans_succes']} sans succès")


def main():
    p = argparse.ArgumentParser(description="Temps restant vers le 100 % des succès Steam")
    p.add_argument("commande", choices=["sync", "report", "all"])
    p.add_argument("--limite", type=int, help="ne traiter que les N jeux les plus joués (test)")
    args = p.parse_args()
    c = cache_mod.Cache()
    try:
        if args.commande in ("sync", "all"):
            sync(c, args.limite)
        if args.commande in ("report", "all"):
            generer_rapport(c, args.limite)
    except KeyboardInterrupt:
        sys.exit("\nInterrompu. Tout ce qui a été récupéré est en cache, relance pour reprendre.")


if __name__ == "__main__":
    main()
