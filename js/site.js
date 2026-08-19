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
  var search = document.getElementById("opo-search");
  var catalog = document.getElementById("opo-catalog");
  function filterCatalog() {
    if (!catalog) return;
    var q = "";
    if (search && search.value) q = search.value.toLowerCase();
    else q = String(new URLSearchParams(window.location.search).get("q") || "").toLowerCase();
    if (search && !search.value && q) search.value = q;
    var cards = catalog.querySelectorAll(".catalog-card");
    var i;
    for (i = 0; i < cards.length; i += 1) {
      var text = cards[i].textContent.toLowerCase();
      cards[i].hidden = Boolean(q) && text.indexOf(q) === -1;
    }
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
