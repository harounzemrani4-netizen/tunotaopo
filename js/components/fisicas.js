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

  function bind() {
    var form = $("fisicas-form");
    var result = $("fisicas-result");
    var toast = $("calc-toast");
    var toastMsg = $("calc-toast-message");
    if (!form || !root.NotaOpoFisicas) return;

    function showToast(message) {
      if (!toast || !toastMsg) return;
      toastMsg.textContent = message;
      toast.hidden = false;
    }

    function hideToast() {
      if (toast) toast.hidden = true;
    }

    function toggleForce() {
      var sex = (form.elements.sex && form.elements.sex.value) || "hombres";
      var men = $("force-hombres");
      var women = $("force-mujeres");
      if (men) men.hidden = sex !== "hombres";
      if (women) women.hidden = sex !== "mujeres";
    }

    form.addEventListener("change", function (ev) {
      if (ev.target && ev.target.name === "sex") toggleForce();
    });
    toggleForce();

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      hideToast();
      var sex = form.elements.sex.value;
      var inputs = {
        sex: sex,
        circuit: form.elements.circuit.value,
        pullups: form.elements.pullups ? form.elements.pullups.value : "",
        hang: form.elements.hang ? form.elements.hang.value : "",
        run_min: form.elements.run_min.value,
        run_sec: form.elements.run_sec.value
      };
      try {
        var out = root.NotaOpoFisicas.evaluate(inputs);
        var placeholder = $("fisicas-placeholder");
        if (placeholder) placeholder.hidden = true;
        result.hidden = false;
        $("fisicas-circuit").textContent = String(out.circuit.score);
        $("fisicas-force").textContent = String(out.force.score);
        $("fisicas-run").textContent = String(out.run.score);
        $("fisicas-avg").textContent = out.average.toLocaleString("es-ES", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });
        $("fisicas-force-label").textContent = out.force.label;
        var verdict = $("fisicas-verdict");
        if (out.zeroOut) {
          verdict.textContent = "0 en un ejercicio elimina, según el anexo II. Esta media no vale para seguir.";
        } else if (out.passed) {
          verdict.textContent = "Media de 5 o más: superas el mínimo de la prueba de aptitud física. No es plaza.";
        } else {
          verdict.textContent = "Media por debajo de 5: no superas el mínimo de la prueba de aptitud física.";
        }
        if (root.NotaOpoAnalytics && root.NotaOpoAnalytics.completed) {
          root.NotaOpoAnalytics.completed("policia-nacional-fisicas-2026");
        }
        saveFisicasProgress(out.average);
        renderFisicasProgress();
      } catch (err) {
        result.hidden = true;
        showToast(err.message || "Revisa los datos.");
      }
    });

    var close = $("calc-toast-close");
    if (close) close.addEventListener("click", hideToast);
    renderFisicasProgress();
  }

  function fisicasKey() {
    return "tunotaopo:progress:policia-nacional-fisicas-2026";
  }

  function loadFisicasProgress() {
    try {
      var raw = localStorage.getItem(fisicasKey());
      var rows = raw ? JSON.parse(raw) : [];
      return Array.isArray(rows) ? rows : [];
    } catch (ignore) {
      return [];
    }
  }

  function saveFisicasProgress(average) {
    if (typeof average !== "number" || !Number.isFinite(average)) return;
    var rows = loadFisicasProgress();
    rows.push({ t: Date.now(), s: average });
    if (rows.length > 20) rows = rows.slice(-20);
    try {
      localStorage.setItem(fisicasKey(), JSON.stringify(rows));
    } catch (ignore) {}
  }

  function renderFisicasProgress() {
    var panel = $("progress-panel");
    if (!panel) return;
    var rows = loadFisicasProgress();
    if (!rows.length) {
      panel.hidden = true;
      panel.innerHTML = "";
      return;
    }
    var first = rows[0].s;
    var last = rows[rows.length - 1].s;
    var delta = Math.round((last - first) * 100) / 100;
    var items = rows.slice(-8).map(function (row) {
      var label = new Date(row.t).toLocaleDateString("es-ES", { day: "numeric", month: "long" });
      return "<li><span>" + escapeHtml(label) + "</span><strong>" + String(row.s) + "</strong></li>";
    }).join("");
    var trend = delta >= 0 ? "↗ +" + String(delta) : "↘ " + String(delta);
    panel.hidden = false;
    panel.innerHTML =
      "<h2>Mis últimas físicas</h2>" +
      '<ol class="progress-list">' + items + "</ol>" +
      '<p class="progress-trend">' + trend + " desde el primero guardado en este navegador.</p>" +
      '<p class="progress-note">Se guarda solo en este dispositivo. No hay cuenta ni servidor.</p>';
  }

  root.NotaOpoFisicasUI = { bind: bind };
})(typeof window !== "undefined" ? window : globalThis);
