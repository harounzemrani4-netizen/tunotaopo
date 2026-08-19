document.addEventListener("DOMContentLoaded", function () {
  if (window.NotaOpoAnalytics) {
    window.NotaOpoAnalytics.pageView();
  }
  var node = document.getElementById("oposicion-config");
  if (node && window.NotaOpoCalculator) {
    window.NotaOpoCalculator.bind(JSON.parse(node.textContent));
  }
});
