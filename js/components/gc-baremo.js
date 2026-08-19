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

  function fmt(n) {
    return n.toLocaleString("es-ES", { minimumFractionDigits: 3, maximumFractionDigits: 3 });
  }

  function progressKey() {
    return "tunotaopo:progress:guardia-civil-baremo-2026";
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
    if (!out || typeof out.total !== "number" || !Number.isFinite(out.total)) return;
    var rows = loadProgress();
    rows.push({ t: Date.now(), s: out.total });
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
      return "<li><span>" + escapeHtml(label) + "</span><strong>" + fmt(row.s) + "</strong></li>";
    }).join("");
    panel.hidden = false;
    panel.innerHTML =
      "<h2>Mis simulacros</h2>" +
      '<ol class="progress-list">' +
      items +
      "</ol>" +
      '<p class="progress-note">Se guarda solo en este navegador si pulsas Guardar. No hay cuenta ni servidor.</p>' +
      '<p><a href="/oposiciones/progreso/index.html">Ver todo mi progreso</a></p>';
  }

  function toggleTurno(form) {
    var turno = (form.elements.turno && form.elements.turno.value) || "libre";
    var tropa = $("baremo-tropa");
    var libre = $("baremo-libre");
    if (tropa) tropa.hidden = turno !== "tropa";
    if (libre) libre.hidden = turno === "tropa";
  }

  function toggleAcademic(form) {
    var kind = (form.elements.academic && form.elements.academic.value) || "none";
    var wrap = $("baremo-degree-lang");
    if (wrap) wrap.hidden = kind !== "filologia";
  }

  function collectLanguages(form) {
    var langs = [];
    var nodes = form.querySelectorAll("[data-lang]");
    var i;
    for (i = 0; i < nodes.length; i += 1) {
      var row = nodes[i];
      var lang = row.getAttribute("data-lang");
      var level = row.querySelector('select[name$="_level"]');
      var via = row.querySelector('select[name$="_via"]');
      if (!level || !level.value || level.value === "none") continue;
      langs.push({
        lang: lang,
        level: level.value,
        via: via ? via.value : "otro"
      });
    }
    return langs;
  }

  function bind() {
    var form = $("gc-baremo-form");
    var result = $("gc-baremo-result");
    var toast = $("calc-toast");
    var toastMsg = $("calc-toast-message");
    if (!form || !root.NotaOpoGcBaremo) return;

    function showToast(message) {
      if (!toast || !toastMsg) return;
      toastMsg.textContent = message;
      toast.hidden = false;
    }

    function hideToast() {
      if (toast) toast.hidden = true;
    }

    form.addEventListener("change", function (ev) {
      if (!ev.target) return;
      if (ev.target.name === "turno") toggleTurno(form);
      if (ev.target.name === "academic") toggleAcademic(form);
    });
    toggleTurno(form);
    toggleAcademic(form);

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      hideToast();
      var input = {
        turno: form.elements.turno.value,
        tropa_years: form.elements.tropa_years ? form.elements.tropa_years.value : "",
        tropa_rank: form.elements.tropa_rank ? form.elements.tropa_rank.value : "none",
        age_years: form.elements.age_years ? form.elements.age_years.value : "",
        reservist_months: form.elements.reservist_months ? form.elements.reservist_months.value : "",
        academic: form.elements.academic.value,
        degree_lang: form.elements.degree_lang ? form.elements.degree_lang.value : "",
        fas: Boolean(form.elements.fas && form.elements.fas.checked),
        languages: collectLanguages(form),
        perm_a: Boolean(form.elements.perm_a && form.elements.perm_a.checked),
        perm_ce: Boolean(form.elements.perm_ce && form.elements.perm_ce.checked),
        perm_c: Boolean(form.elements.perm_c && form.elements.perm_c.checked),
        dan_group: form.elements.dan_group ? form.elements.dan_group.value : "none",
        dan_years: form.elements.dan_years ? form.elements.dan_years.value : ""
      };
      try {
        var out = root.NotaOpoGcBaremo.evaluate(input);
        var placeholder = $("gc-baremo-placeholder");
        if (placeholder) placeholder.hidden = true;
        result.hidden = false;
        $("gc-baremo-total").textContent = fmt(out.total);
        $("gc-baremo-note").textContent = out.capped
          ? "El apéndice fija un máximo de 45. Se ha recortado el total."
          : "Total del concurso según el apéndice I. Cópialo en la calculadora de nota si quieres el proceso completo.";
        function block(title, group) {
          var lines = (group.items || [])
            .map(function (row) {
              return "<div><span>" + escapeHtml(row.label) + "</span><strong>" + fmt(row.points) + "</strong></div>";
            })
            .join("");
          var capNote =
            group.raw > group.cap
              ? " (tope " + fmt(group.cap) + "; suma bruta " + fmt(group.raw) + ")"
              : "";
          return (
            "<h3>" +
            escapeHtml(title) +
            " · " +
            fmt(group.points) +
            capNote +
            "</h3>" +
            '<div class="score-list">' +
            (lines || "<div><span>Sin méritos en este apartado</span><strong>0,000</strong></div>") +
            "</div>"
          );
        }
        $("gc-baremo-breakdown").innerHTML =
          block("Méritos profesionales", out.professional) +
          block("Méritos académicos", out.academic) +
          block("Otros méritos", out.other);
        result._last = out;
        var saveBtn = $("save-progress");
        if (saveBtn) {
          saveBtn.hidden = false;
          saveBtn.textContent = "Guardar en Mi progreso";
        }
        if (root.NotaOpoAnalytics && root.NotaOpoAnalytics.completed) {
          root.NotaOpoAnalytics.completed("guardia-civil-baremo-2026");
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

  root.NotaOpoGcBaremoUI = { bind: bind };
})(typeof window !== "undefined" ? window : globalThis);
