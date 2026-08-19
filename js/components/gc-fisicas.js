(function (root) {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function key() {
    return "tunotaopo:progress:guardia-civil-fisicas-2026";
  }

  function loadProgress() {
    try {
      var raw = localStorage.getItem(key());
      var rows = raw ? JSON.parse(raw) : [];
      return Array.isArray(rows) ? rows : [];
    } catch (ignore) {
      return [];
    }
  }

  function saveProgress(out) {
    var rows = loadProgress();
    rows.push({
      t: Date.now(),
      ok: out.passed,
      run: out.runTotal,
      runDisplay: out.runDisplay
    });
    if (rows.length > 20) rows = rows.slice(-20);
    try {
      localStorage.setItem(key(), JSON.stringify(rows));
    } catch (ignore) {}
  }

  function renderProgress() {
    var panel = $("progress-panel");
    if (!panel) return;
    var rows = loadProgress();
    if (!rows.length) {
      panel.hidden = true;
      panel.innerHTML = "";
      return;
    }
    var first = rows[0].run;
    var last = rows[rows.length - 1].run;
    var delta = first - last;
    var items = rows.slice(-8).map(function (row) {
      var label = new Date(row.t).toLocaleDateString("es-ES", { day: "numeric", month: "long" });
      var mark = row.ok ? "apto" : "no apto";
      return (
        "<li><span>" +
        escapeHtml(label) +
        "</span><strong>" +
        escapeHtml(row.runDisplay || "") +
        " · " +
        mark +
        "</strong></li>"
      );
    }).join("");
    var trend = "";
    if (typeof first === "number" && typeof last === "number") {
      var sec = Math.round(delta);
      if (sec > 0) trend = "↗ " + sec + " segundos de mejora en los 2.000 m.";
      else if (sec < 0) trend = "↘ " + Math.abs(sec) + " segundos más lentos en los 2.000 m.";
      else trend = "Mismo tiempo de 2.000 m que en el primer registro de este navegador.";
    }
    panel.hidden = false;
    panel.innerHTML =
      "<h2>Mis 2.000 metros</h2>" +
      '<ol class="progress-list">' +
      items +
      "</ol>" +
      '<p class="progress-trend">' +
      trend +
      "</p>" +
      '<p class="progress-note">Se guarda solo en este dispositivo. No hay cuenta ni servidor.</p>' +
      '<p><a href="' + (document.body.getAttribute("data-root") || "") + 'oposiciones/progreso/index.html">Ver todo mi progreso</a></p>' +
      '<p><button type="button" class="button button-secondary" id="progress-clear">Borrar historial</button></p>';
    var clear = $("progress-clear");
    if (clear) {
      clear.addEventListener("click", function () {
        try {
          localStorage.removeItem(key());
        } catch (ignore) {}
        renderProgress();
      });
    }
  }

  function bind() {
    var form = $("gc-fisicas-form");
    var result = $("gc-fisicas-result");
    var toast = $("calc-toast");
    var toastMsg = $("calc-toast-message");
    if (!form || !root.NotaOpoGcFisicas) return;

    function showToast(message) {
      if (!toast || !toastMsg) return;
      toastMsg.textContent = message;
      toast.hidden = false;
    }

    function hideToast() {
      if (toast) toast.hidden = true;
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      hideToast();
      var inputs = {
        sex: form.elements.sex.value,
        band: form.elements.band.value,
        run_min: form.elements.run_min.value,
        run_sec: form.elements.run_sec.value,
        circuit: form.elements.circuit.value,
        pushups: form.elements.pushups.value,
        swim: form.elements.swim.value
      };
      try {
        var out = root.NotaOpoGcFisicas.evaluate(inputs);
        var placeholder = $("gc-fisicas-placeholder");
        if (placeholder) placeholder.hidden = true;
        result.hidden = false;
        $("gc-fisicas-verdict").textContent = out.passed
          ? "Apto en las cuatro pruebas, según los mínimos de tu sexo y tramo de edad. No es plaza."
          : "No apto: alguna prueba no llega al mínimo del apéndice II. Todas son eliminatorias.";
        $("gc-fisicas-list").innerHTML = out.tests
          .map(function (row) {
            var cls = row.passed ? "status-pass" : "status-fail";
            var mark = row.passed ? "apto" : "no apto";
            return (
              "<div><span>" +
              escapeHtml(row.label) +
              "</span><strong>" +
              escapeHtml(row.display) +
              ' <span class="status ' +
              cls +
              '">' +
              mark +
              "</span></strong><p>" +
              escapeHtml(row.detail) +
              "</p></div>"
            );
          })
          .join("");
        if (root.NotaOpoAnalytics && root.NotaOpoAnalytics.completed) {
          root.NotaOpoAnalytics.completed("guardia-civil-fisicas-2026");
        }
        saveProgress(out);
        renderProgress();
      } catch (err) {
        result.hidden = true;
        showToast(err.message || "Revisa los datos.");
      }
    });

    var close = $("calc-toast-close");
    if (close) close.addEventListener("click", hideToast);
    renderProgress();
  }

  root.NotaOpoGcFisicasUI = { bind: bind };
})(typeof window !== "undefined" ? window : globalThis);
