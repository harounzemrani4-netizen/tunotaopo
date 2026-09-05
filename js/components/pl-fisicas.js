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

  function fmt(value) {
    if (value === null || value === undefined) return "menos de 5";
    return Number(value).toLocaleString("es-ES", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    });
  }

  function bind() {
    var form = $("pl-fisicas-form");
    var result = $("pl-fisicas-result");
    var toast = $("calc-toast");
    var toastMsg = $("calc-toast-message");
    if (!form || !root.NotaOpoPlFisicas) return;

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
        run800_min: form.elements.run800_min.value,
        run800_sec: form.elements.run800_sec.value,
        run60: form.elements.run60.value,
        ball: form.elements.ball.value,
        jump: form.elements.jump.value,
        swim: form.elements.swim.value
      };
      try {
        var out = root.NotaOpoPlFisicas.evaluate(inputs);
        var placeholder = $("pl-fisicas-placeholder");
        if (placeholder) placeholder.hidden = true;
        result.hidden = false;
        $("pl-fisicas-800").textContent = fmt(out.events.run800.score);
        $("pl-fisicas-60").textContent = fmt(out.events.run60.score);
        $("pl-fisicas-ball").textContent = fmt(out.events.ball.score);
        $("pl-fisicas-jump").textContent = fmt(out.events.jump.score);
        $("pl-fisicas-swim").textContent = fmt(out.events.swim.score);
        $("pl-fisicas-avg").textContent = out.average === null ? "—" : fmt(out.average);
        var verdict = $("pl-fisicas-verdict");
        if (!out.passed) {
          verdict.textContent = "Alguna prueba no llega a 5. En las bases no se hace la siguiente y no hay media oficial.";
        } else {
          verdict.textContent = "Las cinco llegan a 5. Esta media es la nota de las físicas, no plaza. En la oposición vale el 40 %.";
        }
        if (root.NotaOpoAnalytics && root.NotaOpoAnalytics.completed) {
          root.NotaOpoAnalytics.completed("policia-local-madrid-fisicas-2026");
        }
        result._last = out;
        var saveBtn = $("save-progress");
        if (saveBtn) {
          saveBtn.hidden = false;
          saveBtn.textContent = "Guardar en Mi progreso";
        }
        renderProgress();
      } catch (err) {
        result.hidden = true;
        showToast(err.message || "Revisa los datos.");
      }
    });

    var close = $("calc-toast-close");
    if (close) close.addEventListener("click", hideToast);
    var saveBtn = $("save-progress");
    if (saveBtn) {
      saveBtn.addEventListener("click", function () {
        var out = result._last;
        if (!out) return;
        saveProgress(out);
        saveBtn.textContent = "Guardado";
        renderProgress();
      });
    }
    renderProgress();
  }

  function progressKey() {
    return "tunotaopo:progress:policia-local-madrid-fisicas-2026";
  }

  function loadProgress() {
    try {
      var raw = localStorage.getItem(progressKey());
      var rows = raw ? JSON.parse(raw) : [];
      return Array.isArray(rows) ? rows : [];
    } catch (ignore) {
      return [];
    }
  }

  function saveProgress(out) {
    if (!out) return;
    var rows = loadProgress();
    rows.push({
      t: Date.now(),
      s: typeof out.average === "number" ? out.average : null,
      ok: out.passed === true,
      run: out.events && out.events.run800 ? out.events.run800.display : ""
    });
    if (rows.length > 20) rows = rows.slice(-20);
    try {
      localStorage.setItem(progressKey(), JSON.stringify(rows));
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
    var items = rows.slice(-8).map(function (row) {
      var label = new Date(row.t).toLocaleDateString("es-ES", { day: "numeric", month: "long" });
      var extra = row.run ? " · 800 m " + row.run : "";
      var score = row.ok && typeof row.s === "number" ? "media " + String(row.s) : "no apto";
      return "<li><span>" + escapeHtml(label) + "</span><strong>" + escapeHtml(score + extra) + "</strong></li>";
    }).join("");
    panel.hidden = false;
    panel.innerHTML =
      "<h2>Mis físicas de Madrid</h2>" +
      '<ol class="progress-list">' + items + "</ol>" +
      '<p class="progress-note">Se guarda solo en este navegador. No hay cuenta ni servidor.</p>' +
      '<p><a href="/oposiciones/progreso/index.html">Ver todo mi progreso</a></p>' +
      '<p><button type="button" class="button button-secondary" id="progress-clear">Borrar historial</button></p>';
    var clear = $("progress-clear");
    if (clear) {
      clear.addEventListener("click", function () {
        try {
          localStorage.removeItem(progressKey());
        } catch (ignore) {}
        renderProgress();
      });
    }
  }

  root.NotaOpoPlFisicasUI = { bind: bind };
})(typeof window !== "undefined" ? window : globalThis);
