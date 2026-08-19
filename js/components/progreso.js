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

  function fmt(value, digits) {
    if (value === null || value === undefined || Number.isNaN(value)) return "—";
    return Number(value).toLocaleString("es-ES", {
      minimumFractionDigits: 0,
      maximumFractionDigits: digits
    });
  }

  function loadRows(key) {
    try {
      var raw = localStorage.getItem(key);
      var rows = raw ? JSON.parse(raw) : [];
      return Array.isArray(rows) ? rows : [];
    } catch (ignore) {
      return [];
    }
  }

  function lastLabel(row) {
    if (!row) return "Sin simulacros";
    if (typeof row.s === "number" && Number.isFinite(row.s)) {
      var extra = row.run ? " · " + row.run : "";
      return fmt(row.s, 2) + extra;
    }
    if (typeof row.ok === "boolean") {
      var run = row.runDisplay ? " · " + row.runDisplay : "";
      return (row.ok ? "Apto" : "No apto") + run;
    }
    return "Registrado";
  }

  function bind() {
    var rootEl = $("progreso-root");
    var node = $("progreso-config");
    if (!rootEl || !node) return;
    var trackers;
    try {
      trackers = JSON.parse(node.textContent);
    } catch (ignore) {
      return;
    }
    if (!Array.isArray(trackers) || !trackers.length) return;
    var prefix = document.body.getAttribute("data-root") || "../";
    var cards = [];
    var i;
    for (i = 0; i < trackers.length; i += 1) {
      var item = trackers[i];
      var rows = loadRows(item.key);
      var last = rows.length ? rows[rows.length - 1] : null;
      var when = last && last.t
        ? new Date(last.t).toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" })
        : "Aún no hay simulacros en este navegador";
      var href = prefix + item.href + "index.html";
      var cta = item.kind === "fisicas" ? "Calcular físicas" : "Calcular nota";
      cards.push(
        '<article class="progress-card">' +
          "<h2>" + escapeHtml(item.name) + "</h2>" +
          '<p class="progress-last"><strong>' + escapeHtml(lastLabel(last)) + "</strong></p>" +
          '<p class="progress-note">' + escapeHtml(when) +
          (rows.length ? " · " + rows.length + " simulacro" + (rows.length === 1 ? "" : "s") : "") +
          "</p>" +
          '<p><a class="button button-secondary" href="' + escapeHtml(href) + '">' + cta + "</a></p>" +
        "</article>"
      );
    }
    rootEl.innerHTML = cards.join("");
  }

  root.NotaOpoProgreso = { bind: bind };
})(window);
