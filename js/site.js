document.addEventListener("DOMContentLoaded", function () {
  if (window.NotaOpoAnalytics) {
    window.NotaOpoAnalytics.pageView();
  }
  var node = document.getElementById("oposicion-config");
  if (node && window.NotaOpoCalculator) {
    window.NotaOpoCalculator.bind(JSON.parse(node.textContent));
  }
  if (document.getElementById("fisicas-form") && window.NotaOpoFisicasUI) {
    window.NotaOpoFisicasUI.bind();
  }
  if (document.getElementById("gc-fisicas-form") && window.NotaOpoGcFisicasUI) {
    window.NotaOpoGcFisicasUI.bind();
  }
  if (document.getElementById("gc-baremo-form") && window.NotaOpoGcBaremoUI) {
    window.NotaOpoGcBaremoUI.bind();
  }
  if (document.getElementById("progreso-root") && window.NotaOpoProgreso) {
    window.NotaOpoProgreso.bind();
  }
  if (window.NotaOpoTools) {
    window.NotaOpoTools.bindClassroom();
    window.NotaOpoTools.bindShare();
  }
  var search = document.getElementById("opo-search");
  var catalog = document.getElementById("opo-catalog");
  function normalize(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }
  function filterCatalog() {
    if (!catalog) return;
    var q = "";
    if (search && search.value) q = search.value;
    else q = String(new URLSearchParams(window.location.search).get("q") || "");
    if (search && !search.value && q) search.value = q;
    var needle = normalize(q).trim();
    var cards = catalog.querySelectorAll(".catalog-card");
    var i;
    var visible = 0;
    for (i = 0; i < cards.length; i += 1) {
      var text = normalize(cards[i].textContent);
      var aliases = normalize(cards[i].getAttribute("data-aliases") || "");
      var match = !needle || text.indexOf(needle) !== -1 || aliases.indexOf(needle) !== -1;
      cards[i].hidden = !match;
      if (match) visible += 1;
    }
    var empty = document.getElementById("opo-search-empty");
    if (empty) empty.hidden = !needle || visible > 0;
  }
  if (search) {
    search.addEventListener("input", filterCatalog);
    search.form && search.form.addEventListener("submit", function (ev) {
      if (catalog) {
        ev.preventDefault();
        filterCatalog();
      }
    });
  }
  filterCatalog();
});
