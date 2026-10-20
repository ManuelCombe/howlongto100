"""Génération de la page HTML autonome (CSS et JS inline, aucune dépendance externe).

Les données sont injectées en JSON dans la page ; tout le tri et le filtrage
se font dans le navigateur, sans serveur.
"""

import json
from datetime import datetime
from pathlib import Path

CHEMIN_DEFAUT = Path(__file__).resolve().parent.parent / "output" / "rapport.html"


def generer(lignes, resume, chemin=CHEMIN_DEFAUT):
    donnees = {
        "lignes": lignes,
        "resume": resume,
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

  <div class="filtres">
    <input type="search" id="recherche" placeholder="Rechercher un jeu…" aria-label="Rechercher un jeu">
    <label><input type="checkbox" id="f-restants" checked> Succès restants uniquement</label>
    <label><input type="checkbox" id="f-inconnus"> Masquer les « inconnu »</label>
    <label>Temps restant max <input type="number" id="f-max" min="0" step="1" placeholder="∞"> h</label>
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
  </details>
</main>

<script id="donnees" type="application/json">__DONNEES__</script>
<script>
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("donnees").textContent);
  var R = D.resume;
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

  // --- Tuiles du résumé ---
  var tuiles = [
    [heures(R.heures_restantes), "estimées pour tout finir", true],
    [R.a_faire, "jeux à finir (estimés)"],
    [R.inconnus, "jeux « inconnu »"],
    [R.termines, "jeux terminés"],
    [R.sans_succes, "jeux sans succès"],
    [R.exclus_du_total, "estimés mais exclus du total"]
  ];
  $("tuiles").innerHTML = tuiles.map(function (t) {
    return '<div class="tuile' + (t[2] ? " principale" : "") + '"><b>' + echapper(t[0]) +
      "</b><span>" + echapper(t[1]) + "</span></div>";
  }).join("");

  // --- Colonnes ---
  var COLONNES = [
    { cle: "nom", titre: "Jeu" },
    { cle: "joue_h", titre: "Joué", num: true },
    { cle: "succes", titre: "Succès", num: true, val: function (l) { return l.debloques; } },
    { cle: "pct", titre: "%", num: true },
    { cle: "estimation_h", titre: "Estim. 100 %", num: true },
    { cle: "restant_h", titre: "Restant", num: true },
    { cle: "source", titre: "Source" },
    { cle: "avert", titre: "Avertissements", val: function (l) { return l.avert.length; } }
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
      '<td data-label="Source">' + source + "</td>",
      "<td" + (badges ? ' data-label="Avert."' : "") + ">" + badges + "</td>"
    ].join("");
  }

  var principales = D.lignes.filter(function (l) { return l.statut !== "sans_succes"; });

  function afficher() {
    var q = $("recherche").value.trim().toLowerCase();
    var restants = $("f-restants").checked, sansInconnus = $("f-inconnus").checked;
    var max = parseFloat($("f-max").value);
    var liste = principales.filter(function (l) {
      if (restants && l.statut === "termine") return false;
      if (sansInconnus && l.statut === "inconnu") return false;
      if (!isNaN(max) && (l.restant_h === null || l.restant_h > max)) return false;
      if (q && l.nom.toLowerCase().indexOf(q) === -1) return false;
      return true;
    }).sort(comparer);

    var somme = liste.reduce(function (s, l) { return s + (l.compte ? l.restant_h : 0); }, 0);
    $("compteur").textContent = liste.length + " jeu(x) affiché(s) · " + heures(Math.round(somme * 10) / 10) +
      " restantes sur la sélection (hors exclus du total)";

    Array.prototype.forEach.call($("entetes").children, function (th) {
      var actif = th.getAttribute("data-cle") === tri.cle;
      if (actif) th.setAttribute("aria-sort", tri.sens > 0 ? "ascending" : "descending");
      else th.removeAttribute("aria-sort");
    });
    $("corps").innerHTML = liste.map(function (l) { return "<tr>" + cellules(l) + "</tr>"; }).join("");
  }

  ["recherche", "f-max"].forEach(function (id) { $(id).addEventListener("input", afficher); });
  ["f-restants", "f-inconnus"].forEach(function (id) { $(id).addEventListener("change", afficher); });

  // --- Jeux sans succès, listés à part ---
  var sans = D.lignes.filter(function (l) { return l.statut === "sans_succes"; })
    .sort(function (a, b) { return a.nom.localeCompare(b.nom, "fr"); });
  $("sans-succes").querySelector("summary").textContent = "Jeux sans succès (" + sans.length + ")";
  $("sans-succes").querySelector("ul").innerHTML = sans.map(function (l) {
    return "<li>" + echapper(l.nom) + "</li>";
  }).join("");

  afficher();
})();
</script>
</body>
</html>
"""
