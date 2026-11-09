"""Génération de la page HTML autonome (CSS et JS inline, aucune dépendance externe).

Les données sont injectées en JSON dans la page ; tout le tri et le filtrage
se font dans le navigateur, sans serveur.
"""

import json
from datetime import datetime
from pathlib import Path

CHEMIN_DEFAUT = Path(__file__).resolve().parent.parent / "output" / "rapport.html"


def generer(lignes, resume, tags, definitions_tags, chemin=CHEMIN_DEFAUT):
    """tags : contenu de tags.json (voir tags.py) ; definitions_tags : tags.TAGS."""
    donnees = {
        "lignes": lignes,
        "resume": resume,
        "tags": tags,
        "definitions_tags": definitions_tags,
        "genere_le": datetime.now().strftime("%d/%m/%Y à %H:%M"),
    }
    # « </ » échappé pour ne pas fermer la balise <script> par accident
    blob = json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")
    html = MODELE.replace("__DONNEES__", blob)
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    Path(chemin).write_text(html, encoding="utf-8")
    return chemin


MODELE = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Steam 100 %</title>
<style>
:root {
  --fond: #f6f7f9; --carte: #ffffff; --texte: #1b1f24; --doux: #5d6670;
  --ligne: #e3e6ea; --accent: #2f6fde; --ok: #1f8a4c; --alerte: #b26a00;
  --bloque: #c0392b; --survol: #eef3fc;
}
@media (prefers-color-scheme: dark) {
  :root {
    --fond: #121418; --carte: #1b1e24; --texte: #e6e8eb; --doux: #9aa3ad;
    --ligne: #2c313a; --accent: #6ea0ff; --ok: #4cc27f; --alerte: #f0a63a;
    --bloque: #ff6b5b; --survol: #232a36;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--fond); color: var(--texte);
  font: 15px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
main { max-width: 1280px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 1.6rem; margin: 0 0 2px; }
.sous-titre { color: var(--doux); margin: 0 0 20px; font-size: .9rem; }
.tuiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px; margin-bottom: 20px; }
.tuile { background: var(--carte); border: 1px solid var(--ligne); border-radius: 10px; padding: 12px 14px; }
.tuile b { display: block; font-size: 1.5rem; font-variant-numeric: tabular-nums; }
.tuile span { color: var(--doux); font-size: .85rem; }
.tuile.principale b { color: var(--accent); }
.filtres { display: flex; flex-wrap: wrap; gap: 10px 18px; align-items: center;
  background: var(--carte); border: 1px solid var(--ligne); border-radius: 10px;
  padding: 12px 14px; margin-bottom: 12px; }
.filtres label { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }
.filtres input[type=search] { flex: 1 1 220px; min-width: 0; }
.filtres input[type=search], .filtres input[type=number] {
  font: inherit; color: inherit; background: var(--fond); border: 1px solid var(--ligne);
  border-radius: 6px; padding: 6px 8px; }
.filtres input[type=number] { width: 80px; }
.compteur { color: var(--doux); font-size: .9rem; margin: 0 0 8px; }
table { width: 100%; border-collapse: collapse; background: var(--carte);
  border: 1px solid var(--ligne); border-radius: 10px; overflow: hidden; }
th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid var(--ligne); vertical-align: top; }
th { font-size: .8rem; text-transform: uppercase; letter-spacing: .03em; color: var(--doux);
  cursor: pointer; user-select: none; white-space: nowrap; background: var(--carte);
  position: sticky; top: 0; }
th[aria-sort=ascending]::after { content: " ▲"; }
th[aria-sort=descending]::after { content: " ▼"; }
tbody tr:hover { background: var(--survol); }
td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
td.restant { font-weight: 600; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.barre { height: 4px; background: var(--ligne); border-radius: 2px; margin-top: 4px; }
.barre i { display: block; height: 100%; background: var(--ok); border-radius: 2px; }
.badge { display: inline-block; font-size: .75rem; padding: 1px 7px; border-radius: 999px;
  border: 1px solid currentColor; margin: 1px 3px 1px 0; color: var(--alerte); cursor: help; white-space: nowrap; }
.badge.bloquant { color: var(--bloque); }
.statut-termine { color: var(--ok); font-weight: 600; }
.inconnu { color: var(--doux); font-style: italic; }
.source { color: var(--doux); font-size: .85rem; }
.note.haute, .note.haute a { color: var(--ok); }
.note.basse, .note.basse a { color: var(--bloque); }
details { background: var(--carte); border: 1px solid var(--ligne); border-radius: 10px;
  padding: 10px 14px; margin-top: 16px; }
summary { cursor: pointer; font-weight: 600; }
details ul { columns: 3 240px; margin: 10px 0 0; padding-left: 18px; }
details p { color: var(--doux); }
code { font-size: .85em; }
/* Mobile : chaque ligne devient une carte */
@media (max-width: 760px) {
  thead { display: none; }
  table, tbody, tr, td { display: block; width: 100%; }
  table { border: none; background: none; }
  tr { background: var(--carte); border: 1px solid var(--ligne); border-radius: 10px;
    margin-bottom: 10px; padding: 6px 0; }
  td { border: none; padding: 3px 12px; text-align: left !important; }
  td[data-label]::before { content: attr(data-label) " : "; color: var(--doux); font-size: .85rem; }
  td.nom { font-weight: 600; font-size: 1.02rem; }
  .tri-mobile { display: flex !important; }
}
/* Tags perso */
.barre-tags { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center;
  background: var(--carte); border: 1px solid var(--ligne); border-radius: 10px;
  padding: 10px 14px; margin-bottom: 12px; }
.compteur-jamais { font-weight: 600; flex: 1 1 100%; }
.etat-export { color: var(--doux); font-size: .85rem; flex: 1 1 220px; }
.bouton { font: inherit; font-size: .9rem; color: inherit; background: var(--fond);
  border: 1px solid var(--ligne); border-radius: 6px; padding: 5px 10px; cursor: pointer; }
.bouton:hover { border-color: var(--accent); }
.bouton.a-exporter { border-color: var(--accent); color: var(--accent); font-weight: 600; }
.tag { font: inherit; font-size: .75rem; padding: 1px 8px; border-radius: 999px; cursor: pointer;
  background: none; color: var(--doux); border: 1px dashed var(--ligne); white-space: nowrap; }
.tag:hover { border-color: var(--doux); }
.tag[aria-pressed=true] { background: var(--doux); color: var(--carte); border: 1px solid var(--doux); }
tr.tague-jamais td:not(.tags), li.tague-jamais span { opacity: .5; }
#sans-succes li { margin-bottom: 3px; }
#sans-succes li .tag { margin-left: 6px; }
.message { position: relative; background: var(--carte); border: 1px solid var(--ligne);
  border-left: 4px solid var(--alerte); border-radius: 10px; padding: 10px 40px 10px 14px; margin-bottom: 12px; }
.message p { margin: 4px 0; }
.message .fermer { position: absolute; top: 6px; right: 8px; font-size: 1.2rem; line-height: 1;
  background: none; border: none; color: var(--doux); cursor: pointer; padding: 4px; }
.tri-mobile { display: none; gap: 8px; align-items: center; margin-bottom: 10px; }
.tri-mobile select { font: inherit; color: inherit; background: var(--carte);
  border: 1px solid var(--ligne); border-radius: 6px; padding: 6px; }
</style>
</head>
<body>
<main>
  <h1>Steam 100 %</h1>
  <p class="sous-titre">Temps restant estimé vers le 100 % des succès · généré le <span id="date"></span></p>

  <div class="tuiles" id="tuiles"></div>

  <div class="message" id="message-tags" role="status" hidden>
    <div id="message-texte"></div>
    <button type="button" class="fermer" id="fermer-message" aria-label="Fermer le message">×</button>
  </div>

  <div class="barre-tags">
    <span class="compteur-jamais" id="compteur-jamais"></span>
    <span class="etat-export" id="etat-export"></span>
    <button type="button" class="bouton" id="exporter">Exporter les tags</button>
    <button type="button" class="bouton" id="importer">Importer les tags</button>
    <input type="file" id="fichier-import" accept=".json,application/json" hidden>
  </div>

  <div class="filtres" id="filtres">
    <input type="search" id="recherche" placeholder="Rechercher un jeu…" aria-label="Rechercher un jeu">
    <label><input type="checkbox" id="f-restants" checked> Succès restants uniquement</label>
    <label><input type="checkbox" id="f-inconnus"> Masquer les « inconnu »</label>
    <label>Temps restant max <input type="number" id="f-max" min="0" step="1" placeholder="∞"> h</label>
    <label>Note Steam min <input type="number" id="f-note" min="0" max="100" step="5" placeholder="0"> %</label>
  </div>

  <div class="tri-mobile">
    <label for="tri-select">Trier par</label>
    <select id="tri-select"></select>
  </div>

  <p class="compteur" id="compteur"></p>

  <table>
    <thead><tr id="entetes"></tr></thead>
    <tbody id="corps"></tbody>
  </table>

  <details id="sans-succes"><summary></summary><ul></ul></details>

  <details>
    <summary>Méthode de calcul</summary>
    <p><b>E</b> = estimation du temps pour faire le 100 % : médiane SteamHunters
    (temps de jeu des joueurs ayant tout fini), sinon durée « Completionist » de HowLongToBeat
    (temps déclarés, non basés sur les succès Steam).</p>
    <p><b>Temps restant</b> = max(E − temps joué ; E × succès restants / succès total).
    Le maximum est l'option prudente : il évite qu'un jeu « idlé » sans succès paraisse presque fini.</p>
    <p>Le total en tête n'inclut que les jeux ayant une estimation et sans avertissement bloquant
    (rouge : 100 % impossible, multijoueur/sans fin, estimation > 1 000 h, données Steam manquantes).
    Les jeux sans estimation sont « inconnu », jamais comptés comme 0 h.</p>
    <p><b>Notes</b> (information seulement, n'entrent dans aucun calcul) : « Note Steam » = note SteamDB,
    calculée à partir des avis des joueurs Steam (fournie par SteamHunters) ; « Metacritic » = note de la presse,
    lue sur la fiche Steam du jeu, absente pour beaucoup de petits jeux.</p>
    <p><b>Tags</b> : un jeu marqué « jamais » est masqué et retiré des totaux en tête.
    Les tags posés ici sont gardés dans ce navigateur. Pour les rendre durables :
    « Exporter les tags », placer le fichier téléchargé à la racine du projet (<code>tags.json</code>),
    puis relancer <code>python src/main.py report</code>. À l'ouverture, si un tag diffère entre
    le navigateur et <code>tags.json</code>, la modification la plus récente l'emporte et un message le signale.</p>
  </details>
</main>

<script id="donnees" type="application/json">__DONNEES__</script>
<script>
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("donnees").textContent);
  var $ = function (id) { return document.getElementById(id); };

  // Libellés courts des badges d'avertissement
  var BADGES = { impossible: "impossible", multi: "multi", strategie: "stratégie",
    dlc: "DLC", retire: "retiré", restreint: "restreint", peu_donnees: "peu de données",
    hltb_nom: "nom HLTB", hltb: "HLTB", tres_long: "très long", erreur: "erreur", prive: "privé" };

  function heures(h) {
    if (h === null || h === undefined) return "";
    if (h >= 100) return Math.round(h).toLocaleString("fr-FR") + " h";
    return h.toLocaleString("fr-FR", { maximumFractionDigits: 1 }) + " h";
  }
  function echapper(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  $("date").textContent = D.genere_le;

  // ===========================================================================
  // Tags perso (« jamais » pour l'instant). La logique est générique : ajouter
  // un tag dans TAGS (src/tags.py) suffit pour avoir son bouton et son filtre.
  //
  // Référence : tags.json, injecté dans la page par le script au moment du report.
  // Changements faits ici : gardés dans le localStorage en attendant un export.
  // Un état = { appid: { tag: { actif: bool, modifie_le: "date ISO UTC" } } }
  // ===========================================================================
  var DEF_TAGS = D.definitions_tags;
  var LISTE_TAGS = Object.keys(DEF_TAGS);
  var CLE_TAGS = "howlongto100:tags", CLE_EXPORT = "howlongto100:dernier_export";
  var NOMS = {};
  D.lignes.forEach(function (l) { NOMS[l.appid] = l.nom; });

  function nomJeu(appid) {
    return NOMS[appid] || (D.tags[appid] && D.tags[appid].nom) || "App " + appid;
  }
  function libelleTag(t) { return DEF_TAGS[t] ? DEF_TAGS[t].libelle : t; }
  function union(a, b) {
    var vu = {};
    return a.concat(b).filter(function (k) { return vu[k] ? false : (vu[k] = true); });
  }

  // Le localStorage peut être indisponible (navigation privée, fichiers locaux bloqués…)
  var stockageOk = true;
  function lireStockage(cle) {
    try { return localStorage.getItem(cle); } catch (e) { stockageOk = false; return null; }
  }
  function ecrireStockage(cle, valeur) {
    try { localStorage.setItem(cle, valeur); } catch (e) { stockageOk = false; }
  }

  // « jeux » de tags.json -> état ; les entrées malformées sont ignorées
  function normaliser(jeux) {
    var res = {};
    Object.keys(jeux || {}).forEach(function (appid) {
      if (!/^\d+$/.test(appid)) return;
      var t = (jeux[appid] || {}).tags || {};
      Object.keys(t).forEach(function (tag) {
        var e = t[tag];
        if (!e || typeof e.actif !== "boolean") return;
        (res[appid] = res[appid] || {})[tag] = { actif: e.actif, modifie_le: String(e.modifie_le || "") };
      });
    });
    return res;
  }

  // État -> « jeux » de tags.json, trié par appid ; le nom rend le fichier lisible
  function enJeux(etatTags, avecNoms) {
    var jeux = {};
    Object.keys(etatTags).sort(function (a, b) { return a - b; }).forEach(function (appid) {
      jeux[appid] = avecNoms ? { nom: nomJeu(appid), tags: etatTags[appid] } : { tags: etatTags[appid] };
    });
    return jeux;
  }

  // Fusion tag par tag : la modification la plus récente l'emporte (égalité : le fichier).
  //   gardes    = changements du navigateur plus récents que le fichier, conservés
  //   remplaces = tags du fichier plus récents, qui écrasent ceux du navigateur
  function fusionner(navigateur, fichierTags) {
    var res = {}, gardes = [], remplaces = [];
    union(Object.keys(navigateur), Object.keys(fichierTags)).forEach(function (appid) {
      var n = navigateur[appid] || {}, f = fichierTags[appid] || {};
      union(Object.keys(n), Object.keys(f)).forEach(function (tag) {
        var en = n[tag], ef = f[tag], gagnant = ef;
        if (en && (!ef || en.modifie_le > ef.modifie_le)) {
          gagnant = en;
          if (en.actif !== (ef ? ef.actif : false)) gardes.push({ appid: appid, tag: tag, actif: en.actif });
        } else if (en && en.actif !== ef.actif) {
          remplaces.push({ appid: appid, tag: tag, actif: ef.actif });
        }
        (res[appid] = res[appid] || {})[tag] = { actif: gagnant.actif, modifie_le: gagnant.modifie_le };
      });
    });
    return { etat: res, gardes: gardes, remplaces: remplaces };
  }

  function aTag(appid, tag) { var e = (etat[appid] || {})[tag]; return !!(e && e.actif); }
  function nbTags(appid) { return LISTE_TAGS.filter(function (t) { return aTag(appid, t); }).length; }
  // Écarté = porte un tag masqué par défaut (« jamais ») : hors des totaux en tête
  function ecarte(l) {
    return LISTE_TAGS.some(function (t) { return DEF_TAGS[t].masque_par_defaut && aTag(l.appid, t); });
  }
  // Masqué = écarté et le filtre « Afficher les … » correspondant n'est pas coché
  function masque(l) {
    return LISTE_TAGS.some(function (t) {
      return DEF_TAGS[t].masque_par_defaut && aTag(l.appid, t) && !$("f-tag-" + t).checked;
    });
  }
  function sauver() {
    ecrireStockage(CLE_TAGS, JSON.stringify({ version: 1, jeux: enJeux(etat, false) }));
  }

  // --- Messages ---
  function decrire(c) {
    return nomJeu(c.appid) + " (« " + libelleTag(c.tag) + " » " + (c.actif ? "ajouté" : "retiré") + ")";
  }
  function resumeListe(liste) {
    var txt = liste.slice(0, 10).map(decrire).join(", ");
    return liste.length > 10 ? txt + " et " + (liste.length - 10) + " autre(s)" : txt;
  }
  function annoncer(paragraphes) {
    if (!paragraphes.length) return;
    $("message-texte").innerHTML = paragraphes.map(function (p) { return "<p>" + p + "</p>"; }).join("");
    $("message-tags").hidden = false;
  }
  // source : texte déjà échappé (« tags.json » ou le nom du fichier importé)
  function messagesFusion(r, source) {
    var p = [];
    if (r.gardes.length) p.push("<b>" + r.gardes.length + " changement(s) fait(s) dans ce navigateur, plus récent(s) que " +
      source + ", ont été conservés</b> : " + echapper(resumeListe(r.gardes)) +
      ". Clique « Exporter les tags » pour mettre tags.json à jour.");
    if (r.remplaces.length) p.push("<b>" + r.remplaces.length + " tag(s) de " + source +
      ", plus récent(s), ont remplacé ceux de ce navigateur</b> : " + echapper(resumeListe(r.remplaces)) + ".");
    return p;
  }
  $("fermer-message").addEventListener("click", function () { $("message-tags").hidden = true; });

  // --- Chargement : tags.json (injecté) fusionné avec le localStorage ---
  var fichier = normaliser(D.tags);   // contenu de tags.json, ou du dernier fichier importé
  var avertissementsTags = [];
  var navigateur = {}, brut = lireStockage(CLE_TAGS);
  if (brut) {
    try { navigateur = normaliser(JSON.parse(brut).jeux); }
    catch (e) { avertissementsTags.push("Les tags gardés dans ce navigateur étaient illisibles : ignorés, tags.json fait foi."); }
  }
  var fusion = fusionner(navigateur, fichier);
  var etat = fusion.etat;
  var dernierExport = lireStockage(CLE_EXPORT) || "";
  sauver();
  if (!stockageOk) avertissementsTags.push("<b>Ce navigateur bloque le stockage local</b> : les tags posés ici " +
    "seront perdus à la fermeture de la page. Exporte-les avant de partir.");
  annoncer(messagesFusion(fusion, "tags.json").concat(avertissementsTags));

  function basculer(appid, tag) {
    (etat[appid] = etat[appid] || {})[tag] = { actif: !aTag(appid, tag), modifie_le: new Date().toISOString() };
    sauver();
    afficher();
    // Le tableau est redessiné : on rend le focus au bouton s'il est toujours visible
    var b = document.querySelector('button.tag[data-appid="' + appid + '"][data-tag="' + tag + '"]');
    if (b) b.focus();
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("button.tag[data-tag]");
    if (b) basculer(b.getAttribute("data-appid"), b.getAttribute("data-tag"));
  });

  function boutonsTags(appid) {
    return LISTE_TAGS.map(function (t) {
      var actif = aTag(appid, t), d = DEF_TAGS[t];
      var aide = (actif ? "Retirer le tag « " : "Marquer « ") + d.libelle + " » : " + d.description;
      return '<button type="button" class="tag" data-appid="' + appid + '" data-tag="' + t +
        '" aria-pressed="' + actif + '" title="' + echapper(aide) + '">' + echapper(d.libelle) + "</button>";
    }).join("");
  }
  function classesTags(appid) {
    return LISTE_TAGS.filter(function (t) { return aTag(appid, t); })
      .map(function (t) { return "tague-" + t; }).join(" ");
  }

  // --- Export / import de tags.json ---
  // Changements par rapport au fichier de référence ; renvoie leurs dates
  function differences() {
    var dates = [];
    union(Object.keys(etat), Object.keys(fichier)).forEach(function (appid) {
      var e = etat[appid] || {}, f = fichier[appid] || {};
      union(Object.keys(e), Object.keys(f)).forEach(function (tag) {
        if ((e[tag] ? e[tag].actif : false) !== (f[tag] ? f[tag].actif : false)) {
          dates.push(e[tag] ? e[tag].modifie_le : "");
        }
      });
    });
    return dates;
  }
  function majEtatExport() {
    var dates = differences();
    var nonExportes = dates.filter(function (d) { return d > dernierExport; }).length;
    $("etat-export").textContent = !dates.length ? "tags.json à jour." :
      nonExportes ? nonExportes + " changement(s) pas encore exporté(s)." :
      "Exporté : place le fichier téléchargé à la racine du projet (tags.json), puis relance « report ».";
    $("exporter").classList.toggle("a-exporter", nonExportes > 0);
  }

  $("exporter").addEventListener("click", function () {
    var texte = JSON.stringify({ version: 1, jeux: enJeux(etat, true) }, null, 2) + "\n";
    var url = URL.createObjectURL(new Blob([texte], { type: "application/json" }));
    var a = document.createElement("a");
    a.href = url; a.download = "tags.json";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    dernierExport = new Date().toISOString();
    ecrireStockage(CLE_EXPORT, dernierExport);
    majEtatExport();
  });

  $("importer").addEventListener("click", function () { $("fichier-import").click(); });
  $("fichier-import").addEventListener("change", function () {
    var choisi = this.files[0], champ = this;
    if (!choisi) return;
    var nom = "« " + echapper(choisi.name) + " »";
    var lecteur = new FileReader();
    lecteur.onload = function () {
      var contenu = null;
      try { contenu = JSON.parse(lecteur.result); } catch (e) { /* traité juste en dessous */ }
      if (!contenu || !contenu.jeux || typeof contenu.jeux !== "object") {
        annoncer(["<b>Import impossible</b> : " + nom + " n'est pas un tags.json valide (clé « jeux » absente)."]);
        return;
      }
      fichier = normaliser(contenu.jeux);
      var avant = etat, r = fusionner(etat, fichier);
      etat = r.etat;
      sauver();
      afficher();
      // Tags dont l'état a changé dans la page (y compris ceux sans conflit)
      var modifies = 0;
      Object.keys(etat).forEach(function (appid) {
        Object.keys(etat[appid]).forEach(function (tag) {
          var e = (avant[appid] || {})[tag];
          if ((e ? e.actif : false) !== etat[appid][tag].actif) modifies++;
        });
      });
      annoncer(["Import de " + nom + " : " + modifies + " tag(s) modifié(s) dans la page."]
        .concat(messagesFusion(r, nom)));
    };
    lecteur.onerror = function () { annoncer(["<b>Import impossible</b> : lecture de " + nom + " refusée."]); };
    lecteur.readAsText(choisi);
    champ.value = "";   // permet de réimporter le même fichier
  });

  // Un filtre « Afficher les … » par tag masqué par défaut
  LISTE_TAGS.forEach(function (t) {
    if (!DEF_TAGS[t].masque_par_defaut) return;
    var label = document.createElement("label");
    label.innerHTML = '<input type="checkbox" id="f-tag-' + t + '"> Afficher les « ' + echapper(DEF_TAGS[t].libelle) + " »";
    $("filtres").appendChild(label);
    label.firstChild.addEventListener("change", afficher);
  });

  // --- Compteur « jamais » et tuiles du résumé (hors jeux écartés) ---
  function majCompteurs() {
    var jamaisTouches = D.lignes.filter(function (l) { return l.joue_min === 0; });
    var ecartes = jamaisTouches.filter(function (l) { return aTag(l.appid, "jamais"); }).length;
    var lances = D.lignes.filter(function (l) { return l.joue_min > 0 && aTag(l.appid, "jamais"); }).length;
    $("compteur-jamais").textContent = jamaisTouches.length + " jeux jamais touchés, dont " + ecartes +
      " écartés, reste " + (jamaisTouches.length - ecartes) +
      (lances ? " · + " + lances + " jeu(x) déjà lancé(s) marqué(s) « jamais »" : "");

    var gardes = D.lignes.filter(function (l) { return !ecarte(l); });
    var nb = function (st) { return gardes.filter(function (l) { return l.statut === st; }).length; };
    var h = gardes.reduce(function (s, l) { return s + (l.compte ? l.restant_h : 0); }, 0);
    var horsJamais = gardes.length < D.lignes.length ? ", hors « jamais »" : "";
    var tuiles = [
      [heures(Math.round(h * 10) / 10), "estimées pour tout finir" + horsJamais, true],
      [nb("a_faire"), "jeux à finir (estimés)"],
      [nb("inconnu"), "jeux « inconnu »"],
      [nb("termine"), "jeux terminés"],
      [nb("sans_succes"), "jeux sans succès"],
      [gardes.filter(function (l) { return l.statut === "a_faire" && !l.compte; }).length, "estimés mais exclus du total"]
    ];
    $("tuiles").innerHTML = tuiles.map(function (t) {
      return '<div class="tuile' + (t[2] ? " principale" : "") + '"><b>' + echapper(t[0]) +
        "</b><span>" + echapper(t[1]) + "</span></div>";
    }).join("");
  }

  // --- Colonnes ---
  var COLONNES = [
    { cle: "nom", titre: "Jeu" },
    { cle: "joue_h", titre: "Joué", num: true },
    { cle: "succes", titre: "Succès", num: true, val: function (l) { return l.debloques; } },
    { cle: "pct", titre: "%", num: true },
    { cle: "estimation_h", titre: "Estim. 100 %", num: true },
    { cle: "restant_h", titre: "Restant", num: true },
    { cle: "note_steam", titre: "Note Steam", num: true },
    { cle: "metacritic", titre: "Metacritic", num: true },
    { cle: "source", titre: "Source" },
    { cle: "avert", titre: "Avertissements", val: function (l) { return l.avert.length; } },
    { cle: "tags", titre: "Tags", val: function (l) { return nbTags(l.appid); } }
  ];
  var tri = { cle: "restant_h", sens: 1 };

  function valeur(l, col) { return col.val ? col.val(l) : l[col.cle]; }

  function comparer(a, b) {
    var col = COLONNES.filter(function (c) { return c.cle === tri.cle; })[0];
    var va = valeur(a, col), vb = valeur(b, col);
    // Les valeurs manquantes (« inconnu ») restent toujours en bas
    var na = va === null || va === undefined, nb = vb === null || vb === undefined;
    if (na || nb) return na === nb ? a.nom.localeCompare(b.nom, "fr") : (na ? 1 : -1);
    var r = typeof va === "string" ? va.localeCompare(vb, "fr", { sensitivity: "base" }) : va - vb;
    return r * tri.sens || a.nom.localeCompare(b.nom, "fr");
  }

  $("entetes").innerHTML = COLONNES.map(function (c) {
    return '<th data-cle="' + c.cle + '"' + (c.num ? ' style="text-align:right"' : "") + ">" + c.titre + "</th>";
  }).join("");
  $("entetes").addEventListener("click", function (e) {
    var th = e.target.closest("th"); if (!th) return;
    var cle = th.getAttribute("data-cle");
    tri = { cle: cle, sens: tri.cle === cle ? -tri.sens : 1 };
    $("tri-select").value = tri.cle + ":" + tri.sens;
    afficher();
  });

  // Sélecteur de tri pour mobile (les en-têtes sont masqués)
  $("tri-select").innerHTML = COLONNES.map(function (c) {
    return '<option value="' + c.cle + ':1">' + c.titre + " ↑</option>" +
           '<option value="' + c.cle + ':-1">' + c.titre + " ↓</option>";
  }).join("");
  $("tri-select").value = "restant_h:1";
  $("tri-select").addEventListener("change", function () {
    var p = this.value.split(":"); tri = { cle: p[0], sens: +p[1] }; afficher();
  });

  // Note sur 100, colorée : ≥ 75 bonne, < 50 mauvaise ; lien optionnel
  function note(valeur, unite, aide, lien) {
    if (valeur === null || valeur === undefined) return "";
    var classe = valeur >= 75 ? "note haute" : valeur < 50 ? "note basse" : "note";
    var texte = valeur.toLocaleString("fr-FR", { maximumFractionDigits: 1 }) + unite;
    var contenu = lien ? '<a href="' + echapper(lien) + '" target="_blank" rel="noopener">' + texte + "</a>" : texte;
    return '<span class="' + classe + '" title="' + echapper(aide) + '">' + contenu + "</span>";
  }

  function cellules(l) {
    var succes = l.total ? l.debloques + " / " + l.total : "";
    var pct = l.pct === null ? "" : l.pct.toLocaleString("fr-FR") + " %" +
      '<div class="barre"><i style="width:' + l.pct + '%"></i></div>';
    var restant = l.statut === "termine" ? '<span class="statut-termine">terminé</span>' :
      l.statut === "inconnu" ? '<span class="inconnu">inconnu</span>' : heures(l.restant_h);
    var badges = l.avert.map(function (a) {
      return '<span class="badge' + (a.bloquant ? " bloquant" : "") + '" title="' + echapper(a.texte) + '">' +
        echapper(BADGES[a.code] || a.code) + "</span>";
    }).join("");
    var source = l.source ? '<span class="source" title="' + echapper(l.methode || "") + '">' + echapper(l.source) + "</span>" : "";
    return [
      '<td class="nom"><a href="https://steamhunters.com/apps/' + l.appid + '" target="_blank" rel="noopener">' + echapper(l.nom) + "</a></td>",
      '<td class="num" data-label="Joué">' + heures(l.joue_h) + "</td>",
      '<td class="num" data-label="Succès">' + succes + "</td>",
      '<td class="num" data-label="%">' + pct + "</td>",
      '<td class="num" data-label="Estim. 100 %">' + heures(l.estimation_h) + "</td>",
      '<td class="num restant" data-label="Restant">' + restant + "</td>",
      '<td class="num" data-label="Note Steam">' + note(l.note_steam, " %",
        "Note SteamDB, calculée à partir des avis des joueurs Steam") + "</td>",
      '<td class="num" data-label="Metacritic">' + note(l.metacritic, "", "Note Metacritic (presse)",
        l.metacritic_url) + "</td>",
      '<td data-label="Source">' + source + "</td>",
      "<td" + (badges ? ' data-label="Avert."' : "") + ">" + badges + "</td>",
      '<td class="tags" data-label="Tags">' + boutonsTags(l.appid) + "</td>"
    ].join("");
  }

  var principales = D.lignes.filter(function (l) { return l.statut !== "sans_succes"; });

  function afficher() {
    var q = $("recherche").value.trim().toLowerCase();
    var restants = $("f-restants").checked, sansInconnus = $("f-inconnus").checked;
    var max = parseFloat($("f-max").value);
    var noteMin = parseFloat($("f-note").value);
    var caches = 0;   // jeux qui passeraient les filtres mais sont masqués par un tag
    var liste = principales.filter(function (l) {
      if (restants && l.statut === "termine") return false;
      if (sansInconnus && l.statut === "inconnu") return false;
      if (!isNaN(max) && (l.restant_h === null || l.restant_h > max)) return false;
      if (!isNaN(noteMin) && (l.note_steam === null || l.note_steam < noteMin)) return false;
      if (q && l.nom.toLowerCase().indexOf(q) === -1) return false;
      if (masque(l)) { caches++; return false; }
      return true;
    }).sort(comparer);

    var somme = liste.reduce(function (s, l) { return s + (l.compte ? l.restant_h : 0); }, 0);
    $("compteur").textContent = liste.length + " jeu(x) affiché(s) · " + heures(Math.round(somme * 10) / 10) +
      " restantes sur la sélection (hors exclus du total)" +
      (caches ? " · " + caches + " « jamais » masqué(s)" : "");

    Array.prototype.forEach.call($("entetes").children, function (th) {
      var actif = th.getAttribute("data-cle") === tri.cle;
      if (actif) th.setAttribute("aria-sort", tri.sens > 0 ? "ascending" : "descending");
      else th.removeAttribute("aria-sort");
    });
    $("corps").innerHTML = liste.map(function (l) {
      return '<tr class="' + classesTags(l.appid) + '">' + cellules(l) + "</tr>";
    }).join("");
    afficherSansSucces();
    majCompteurs();
    majEtatExport();
  }

  ["recherche", "f-max", "f-note"].forEach(function (id) { $(id).addEventListener("input", afficher); });
  ["f-restants", "f-inconnus"].forEach(function (id) { $(id).addEventListener("change", afficher); });

  // --- Jeux sans succès, listés à part (taggables aussi) ---
  var sans = D.lignes.filter(function (l) { return l.statut === "sans_succes"; })
    .sort(function (a, b) { return a.nom.localeCompare(b.nom, "fr"); });
  function afficherSansSucces() {
    var visibles = sans.filter(function (l) { return !masque(l); });
    var nbCaches = sans.length - visibles.length;
    $("sans-succes").querySelector("summary").textContent = "Jeux sans succès (" + visibles.length +
      (nbCaches ? ", + " + nbCaches + " « jamais » masqué(s)" : "") + ")";
    $("sans-succes").querySelector("ul").innerHTML = visibles.map(function (l) {
      return '<li class="' + classesTags(l.appid) + '"><span>' + echapper(l.nom) + "</span>" +
        boutonsTags(l.appid) + "</li>";
    }).join("");
  }

  afficher();
})();
</script>
</body>
</html>
"""
