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

  function sparkline(rows) {
    var scores = rows.map(function (row) { return row.s; }).filter(function (n) {
      return typeof n === "number" && Number.isFinite(n);
    });
    if (scores.length < 2) return "";
    var min = Math.min.apply(null, scores);
    var max = Math.max.apply(null, scores);
    var span = max - min || 1;
    var w = 220;
    var h = 40;
    var pts = scores.map(function (score, i) {
      var x = (i / (scores.length - 1)) * (w - 8) + 4;
      var y = h - 6 - ((score - min) / span) * (h - 12);
      return x.toFixed(1) + "," + y.toFixed(1);
    }).join(" ");
    return (
      '<svg class="progress-chart" viewBox="0 0 ' + w + " " + h + '" width="220" height="40" role="img" aria-label="Evolución">' +
      '<polyline fill="none" stroke="currentColor" stroke-width="2" points="' + pts + '"/></svg>'
    );
  }

  function numericRows(rows) {
    return rows.filter(function (row) {
      return typeof row.s === "number" && Number.isFinite(row.s);
    });
  }

  function compareBox(rows) {
    var scores = numericRows(rows);
    if (scores.length < 2) return "";
    var prev = scores[scores.length - 2];
    var last = scores[scores.length - 1];
    var step = Math.round((last.s - prev.s) * 10000) / 10000;
    return (
      '<div class="progress-compare" aria-label="Comparar los dos últimos simulacros">' +
      "<div><span>Anterior</span><strong>" + fmt(prev.s, 2) + "</strong></div>" +
      "<div><span>Último</span><strong>" + fmt(last.s, 2) + "</strong><p>" +
      (step >= 0 ? "+" : "") + fmt(step, 2) + " respecto al anterior</p></div></div>"
    );
  }

  function collectBackup() {
    var keys = {};
    var i;
    for (i = 0; i < localStorage.length; i += 1) {
      var key = localStorage.key(i);
      if (key && key.indexOf("tunotaopo:") === 0) {
        keys[key] = localStorage.getItem(key);
      }
    }
    return {
      app: "tunotaopo",
      exported_at: new Date().toISOString(),
      keys: keys
    };
  }

  function applyBackup(data) {
    if (!data || data.app !== "tunotaopo" || !data.keys || typeof data.keys !== "object") {
      return "El archivo no es una exportación de TuNotaOpo.";
    }
    var key;
    for (key in data.keys) {
      if (!Object.prototype.hasOwnProperty.call(data.keys, key)) continue;
      if (key.indexOf("tunotaopo:") !== 0) continue;
      localStorage.setItem(key, String(data.keys[key]));
    }
    return "";
  }

  function note(message) {
    var node = $("progress-backup-note");
    if (!node) return;
    node.hidden = !message;
    node.textContent = message || "";
  }

  function bindBackup(onChange) {
    var exp = $("progress-export");
    var inp = $("progress-import");
    if (exp) {
      exp.addEventListener("click", function () {
        var blob = new Blob([JSON.stringify(collectBackup(), null, 2)], { type: "application/json" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = "tunotaopo-progreso.json";
        a.click();
        URL.revokeObjectURL(url);
        note("Exportado. El archivo solo tiene lo guardado en este navegador.");
      });
    }
    if (inp) {
      inp.addEventListener("change", function () {
        var file = inp.files && inp.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function () {
          try {
            var err = applyBackup(JSON.parse(String(reader.result || "")));
            note(err || "Importado. Revisa las tarjetas.");
            if (!err) onChange();
          } catch (ignore) {
            note("No se pudo leer el JSON.");
          }
          inp.value = "";
        };
        reader.readAsText(file);
      });
    }
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

    function renderUsage() {
      var box = $("usage-local");
      if (!box || !root.NotaOpoAnalytics || !root.NotaOpoAnalytics.summary) return;
      var info = root.NotaOpoAnalytics.summary();
      if (!info.total) {
        box.hidden = true;
        return;
      }
      box.hidden = false;
      box.textContent =
        "En este navegador se han registrado " +
        info.total +
        " eventos locales (páginas y cálculos). No salen de este dispositivo.";
    }

    function render() {
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
        var cta = "Calcular nota";
        if (item.kind === "fisicas") cta = "Calcular físicas";
        else if (item.kind === "baremo") cta = "Calcular baremo";
        var list = "";
        var trend = "";
        if (rows.length) {
          list = '<ol class="progress-list">' + rows.slice(-8).map(function (row) {
            var day = new Date(row.t).toLocaleDateString("es-ES", { day: "numeric", month: "short" });
            return "<li><span>" + escapeHtml(day) + "</span><strong>" + escapeHtml(lastLabel(row)) + "</strong></li>";
          }).join("") + "</ol>";
          if (typeof rows[0].s === "number" && typeof rows[rows.length - 1].s === "number") {
            var delta = Math.round((rows[rows.length - 1].s - rows[0].s) * 10000) / 10000;
            trend = '<p class="progress-trend">Evolución: ' + (delta >= 0 ? "+" : "") + fmt(delta, 2) + " puntos</p>";
          } else if (typeof rows[0].run === "number" && typeof rows[rows.length - 1].run === "number") {
            var sec = Math.round(rows[0].run - rows[rows.length - 1].run);
            if (sec > 0) trend = '<p class="progress-trend">Mejora: ' + sec + " s</p>";
            else if (sec < 0) trend = '<p class="progress-trend">' + Math.abs(sec) + " s más lento</p>";
          }
        }
        var goal = "";
        try {
          var slug = item.key.replace("tunotaopo:progress:", "");
          var target = Number(localStorage.getItem("tunotaopo:target:" + slug));
          if (item.kind === "nota" && Number.isFinite(target) && target > 0 && last && typeof last.s === "number") {
            var left = Math.round((target - last.s) * 10000) / 10000;
            goal = left > 0
              ? "<p>Objetivo: " + fmt(target, 2) + ". Te faltan " + fmt(left, 2) + ".</p>"
              : "<p>Objetivo: " + fmt(target, 2) + ". Ya lo superas.</p>";
          }
        } catch (ignore) {}
        cards.push(
          '<article class="progress-card">' +
            "<h2>" + escapeHtml(item.name) + "</h2>" +
            '<p class="progress-last"><strong>' + escapeHtml(lastLabel(last)) + "</strong></p>" +
            '<p class="progress-note">' + escapeHtml(when) +
            (rows.length ? " · " + rows.length + " simulacro" + (rows.length === 1 ? "" : "s") : "") +
            "</p>" +
            sparkline(rows) +
            compareBox(rows) +
            list +
            trend +
            goal +
            '<p class="progress-card-actions"><a class="button button-secondary" href="' + escapeHtml(href) + '">' + cta + "</a>" +
            (rows.length
              ? ' <button type="button" class="button button-ghost progress-wipe" data-key="' + escapeHtml(item.key) + '">Borrar historial</button>'
              : "") +
            "</p>" +
          "</article>"
        );
      }
      rootEl.innerHTML = cards.join("");
      rootEl.querySelectorAll(".progress-wipe").forEach(function (btn) {
        btn.addEventListener("click", function () {
          try {
            localStorage.removeItem(btn.getAttribute("data-key"));
          } catch (ignore) {}
          render();
        });
      });
      renderUsage();
    }

    bindBackup(render);
    render();
  }

  root.NotaOpoProgreso = { bind: bind };
})(window);
