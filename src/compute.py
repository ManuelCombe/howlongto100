"""Calcul du temps restant vers le 100 % et des avertissements, à partir du cache.

Méthode (volontairement simple et explicable) :
    E        = estimation du temps pour faire le 100 % (SteamHunters, sinon HLTB)
    par_temps      = max(0, E − temps_joué)
    par_proportion = E × succès_restants / succès_total
    restant  = max(par_temps, par_proportion)

Pourquoi le max des deux :
  - par_temps seul est faussé par le temps « idle » (cartes à échanger…) :
    2 h d'idle sur un jeu de 3 h sans aucun succès donnerait 1 h restante ;
  - par_proportion seule ignore que j'ai peut-être déjà beaucoup joué.
  Le max est l'option prudente : on préfère surestimer que sous-estimer.
"""

# Tags SteamHunters (ce sont les 5 premiers tags Steam du jeu) qui signalent
# un jeu multijoueur / sans fin. Liste volontairement stricte : « Multiplayer »
# seul n'y est pas, sinon Terraria ou Portal 2 seraient marqués.
TAGS_MULTI = {
    "Massively Multiplayer", "MMORPG", "MMO", "MOBA", "eSports",
    "Competitive", "PvP", "Battle Royale", "Hero Shooter",
}
TAGS_STRATEGIE_LONGUE = {"Grand Strategy", "4X"}
SEUIL_TRES_LONG_H = 300      # au-delà, on prévient que l'estimation est fragile
SEUIL_DEMESURE_H = 1000      # au-delà, exclu du total (ex. Garry's Mod : 8 900 h)
SEUIL_PEU_DE_DONNEES = 10    # nb de joueurs ayant fini le jeu (SteamHunters)
SEUIL_PEU_DE_MESURES_HLTB = 5


def _avert(code, texte, bloquant=False):
    """bloquant = le jeu est exclu de la somme globale des heures."""
    return {"code": code, "texte": texte, "bloquant": bloquant}


def estimation(sh, hltb):
    """Choisit l'estimation E (heures) et sa source. Renvoie (E, source, avertissements)."""
    avert = []
    if sh and sh.get("trouve") and sh.get("medianCompletionTime"):
        heures = sh["medianCompletionTime"] / 60
        finis = sh.get("playersCompletedCount") or 0
        if finis < SEUIL_PEU_DE_DONNEES:
            avert.append(_avert("peu_donnees", f"seulement {finis} joueur(s) ont fini ce jeu sur SteamHunters"))
        return heures, "SteamHunters (médiane)", avert
    if hltb and hltb.get("trouve"):
        if hltb.get("similarite", 1) < 1:
            avert.append(_avert("hltb_nom", f"HLTB apparié par nom : « {hltb['nom_hltb']} »"))
        if (hltb.get("nb_mesures") or 0) < SEUIL_PEU_DE_MESURES_HLTB:
            avert.append(_avert("peu_donnees", f"seulement {hltb.get('nb_mesures', 0)} mesure(s) HLTB"))
        avert.append(_avert("hltb", "HLTB « Completionist » : temps déclarés, pas basés sur les succès Steam"))
        return hltb["heures"], "HLTB (Completionist)", avert
    return None, None, avert


def avertissements_jeu(sh):
    """Avertissements liés au jeu lui-même (données SteamHunters)."""
    if not sh or not sh.get("trouve"):
        return []
    avert = []
    tags = set(sh.get("tags") or [])
    if (sh.get("unobtainableAchievementCount") or 0) > 0:
        avert.append(_avert(
            "impossible",
            f"{sh['unobtainableAchievementCount']} succès non obtenable(s) : 100 % impossible",
            bloquant=True,
        ))
    if tags & TAGS_MULTI:
        avert.append(_avert(
            "multi",
            "multijoueur / sans fin (" + ", ".join(sorted(tags & TAGS_MULTI)) + ") : estimation peu pertinente",
            bloquant=True,
        ))
    if tags & TAGS_STRATEGIE_LONGUE:
        avert.append(_avert("strategie", "stratégie très longue : « 100 % » trompeur, estimation à prendre avec recul"))
    if sh.get("hasPaidDlc"):
        avert.append(_avert("dlc", "a des DLC payants (peut-être requis pour certains succès)"))
    if sh.get("isRemoved"):
        avert.append(_avert("retire", "retiré du Steam Store (serveurs / succès peut-être cassés)"))
    if sh.get("isRestricted"):
        # Sens exact du drapeau non vérifié dans la doc SteamHunters
        avert.append(_avert("restreint", "marqué « restreint » sur SteamHunters"))
    return avert


def calculer(jeux, steam_succes, sh, hltb):
    """Construit une ligne par jeu possédé. Renvoie (lignes, resume)."""
    lignes = []
    for jeu in jeux:
        appid = jeu["appid"]
        s = steam_succes.get(appid)
        d_sh = sh.get(appid)
        d_hltb = hltb.get(appid)
        ligne = {
            "appid": appid,
            "nom": jeu.get("name") or (d_sh or {}).get("name") or f"App {appid}",
            "joue_h": round((jeu.get("playtime_forever") or 0) / 60, 1),
            "debloques": None, "total": None, "pct": None,
            "estimation_h": None, "source": None, "methode": None,
            "restant_h": None, "statut": None, "avert": [],
        }
        avert = avertissements_jeu(d_sh)

        # 1. Succès : Steam en priorité, SteamHunters pour savoir s'il y en a
        if s and s.get("statut") == "ok":
            ligne["debloques"], ligne["total"] = s["debloques"], s["total"]
        elif (s and s.get("statut") == "sans_succes") or (
            d_sh and d_sh.get("trouve") and d_sh.get("achievementCount") == 0
        ):
            ligne["total"] = 0
        elif s and s.get("statut") == "prive":
            avert.append(_avert("prive", "jeu marqué privé sur Steam : succès invisibles pour l'API", bloquant=True))
        elif s and s.get("statut") == "erreur":
            avert.append(_avert("erreur", f"succès Steam indisponibles : {s.get('message')}", bloquant=True))
        else:
            avert.append(_avert("erreur", "succès Steam pas encore récupérés (relancer sync)", bloquant=True))

        # 2. Statut
        if ligne["total"] == 0:
            ligne["statut"] = "sans_succes"
            avert = []  # les avertissements n'ont pas d'intérêt ici
        elif ligne["total"] is None:
            ligne["statut"] = "inconnu"
        else:
            ligne["pct"] = round(100 * ligne["debloques"] / ligne["total"], 1)
            if ligne["debloques"] >= ligne["total"]:
                ligne["statut"] = "termine"
                ligne["restant_h"] = 0
                avert = [a for a in avert if a["code"] != "impossible"]
            else:
                E, source, avert_estim = estimation(d_sh, d_hltb)
                avert += avert_estim
                if E is None:
                    ligne["statut"] = "inconnu"
                else:
                    ligne["statut"] = "a_faire"
                    restants = ligne["total"] - ligne["debloques"]
                    par_temps = max(0.0, E - ligne["joue_h"])
                    par_proportion = E * restants / ligne["total"]
                    ligne["estimation_h"] = round(E, 1)
                    ligne["restant_h"] = round(max(par_temps, par_proportion), 1)
                    ligne["source"] = source
                    ligne["methode"] = (
                        f"max(E − joué = {par_temps:.1f} h ; "
                        f"E × {restants}/{ligne['total']} = {par_proportion:.1f} h)"
                    )
                    if E > SEUIL_DEMESURE_H:
                        avert.append(_avert(
                            "tres_long", f"estimation > {SEUIL_DEMESURE_H} h : démesurée, exclue du total",
                            bloquant=True,
                        ))
                    elif E > SEUIL_TRES_LONG_H:
                        avert.append(_avert("tres_long", f"estimation > {SEUIL_TRES_LONG_H} h, fiabilité faible"))

        ligne["avert"] = avert
        # Compte dans la somme globale : estimation dispo et aucun avertissement bloquant
        ligne["compte"] = ligne["statut"] == "a_faire" and not any(a["bloquant"] for a in avert)
        lignes.append(ligne)

    resume = {
        "total_jeux": len(lignes),
        "termines": sum(l["statut"] == "termine" for l in lignes),
        "a_faire": sum(l["statut"] == "a_faire" for l in lignes),
        "inconnus": sum(l["statut"] == "inconnu" for l in lignes),
        "sans_succes": sum(l["statut"] == "sans_succes" for l in lignes),
        "heures_restantes": round(sum(l["restant_h"] for l in lignes if l["compte"]), 1),
        "exclus_du_total": sum(l["statut"] == "a_faire" and not l["compte"] for l in lignes),
    }
    return lignes, resume
