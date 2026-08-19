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

  function collectInputs(form) {
    var data = {};
    var elements = form.elements;
    for (var i = 0; i < elements.length; i += 1) {
      var el = elements[i];
      if (!el.name) continue;
      if (el.type === "checkbox") data[el.name] = el.checked;
      else data[el.name] = el.value;
    }
    return data;
  }

  function applyInputs(form, data) {
    Object.keys(data).forEach(function (key) {
      var el = form.elements[key];
      if (!el) return;
      if (el.type === "checkbox") {
        el.checked = data[key] === true || data[key] === "1" || data[key] === "true";
      } else {
        el.value = data[key];
      }
    });
  }

  function allowedFieldNames(form) {
    var names = {};
    var i;
    for (i = 0; i < form.elements.length; i += 1) {
      if (form.elements[i].name) names[form.elements[i].name] = true;
    }
    return names;
  }

  function isSafeParam(value) {
    return /^\d+([.,]\d+)?$/.test(String(value).trim());
  }

  function isInInputRange(el, value) {
    var number = Number(String(value).trim().replace(",", "."));
    if (!Number.isFinite(number)) return false;
    if (el.min !== "" && number < Number(el.min)) return false;
    if (el.max !== "" && number > Number(el.max)) return false;
    return true;
  }

  function keepCanonicalClean() {
    var link = document.querySelector('link[rel="canonical"]');
    if (!link) return;
    var href = link.getAttribute("href") || "";
    var clean = href.split("?")[0];
    if (clean !== href) link.setAttribute("href", clean);
  }

  function queryFromInputs(form, data) {
    var allowed = allowedFieldNames(form);
    var params = new URLSearchParams();
    Object.keys(data).forEach(function (key) {
      var value = data[key];
      if (!allowed[key]) return;
      if (value === "" || value === false || value === null || value === undefined) return;
      if (!isSafeParam(value)) return;
      params.set(key, String(value).trim());
    });
    return params.toString();
  }

  function inputsFromQuery(form) {
    var allowed = allowedFieldNames(form);
    var params = new URLSearchParams(location.search);
    var data = {};
    var rejected = false;
    params.forEach(function (value, key) {
      if (!allowed[key]) return;
      if (value === "") return;
      var field = form.elements[key];
      if (!isSafeParam(value) || (field && !isInInputRange(field, value))) {
        rejected = true;
        return;
      }
      data[key] = String(value).trim();
    });
    return { data: data, rejected: rejected };
  }

  function statusHtml(stage) {
    if (stage.verdict === "apto") return '<span class="status status-pass">✓ apto</span>';
    if (stage.verdict === "no_apto") return '<span class="status status-fail">✗ no apto</span>';
    if (stage.verdict === "supera_minimo") return '<span class="status status-pass">✓ supera mínimo</span>';
    if (stage.verdict === "no_alcanza_minimo") return '<span class="status status-fail">✗ no alcanza mínimo</span>';
    if (stage.verdict === "sin_umbral") return '<span class="status status-neutral">sin umbral oficial</span>';
    return '<span class="status status-neutral">sin mínimo oficial</span>';
  }

  function statusTone(stage) {
    if (stage.verdict === "apto" || stage.verdict === "supera_minimo") return "is-pass";
    if (stage.verdict === "no_apto" || stage.verdict === "no_alcanza_minimo") return "is-fail";
    return "is-neutral";
  }

  function displayStages(stages) {
    var scored = [];
    var rest = [];
    (stages || []).forEach(function (stage) {
      if (stage.verdict === "apto" || stage.verdict === "no_apto") rest.push(stage);
      else scored.push(stage);
    });
    return scored.concat(rest);
  }

  function stageDetail(stage) {
    var bits = [];
    if (stage.hits !== null && stage.hits !== undefined) bits.push(stage.hits + (stage.hits === 1 ? " acierto" : " aciertos"));
    if (stage.errors !== null && stage.errors !== undefined) bits.push(stage.errors + (stage.errors === 1 ? " error" : " errores"));
    if (stage.blanks !== null && stage.blanks !== undefined) bits.push(stage.blanks + (stage.blanks === 1 ? " blanco" : " blancos"));
    return bits.join(" · ");
  }

  function scoreHtml(stage) {
    if (stage.verdict === "apto" || stage.verdict === "no_apto") {
      return stage.verdict === "apto" ? "Apto" : "No apto";
    }
    if (typeof stage.rounded === "number") return fmt(stage.rounded, 4);
    return "—";
  }

  function renderBreakdown(result) {
    var rows = displayStages(result.stages).map(function (stage) {
      var max = typeof stage.maximum === "number" ? '<span class="score-max"> / ' + fmt(stage.maximum, 4) + "</span>" : "";
      var detail = stageDetail(stage);
      return (
        '<div class="score-row ' + statusTone(stage) + '">' +
        '<div class="score-row-main"><p class="score-row-label">' + escapeHtml(stage.label) + "</p>" +
        (detail ? '<p class="score-row-meta">' + detail + "</p>" : "") +
        "</div>" +
        '<p class="score-row-score">' + scoreHtml(stage) + max + "</p>" +
        '<p class="score-row-status">' + statusHtml(stage) + "</p></div>"
      );
    }).join("");
    if (result.merits) {
      rows += (
        '<div class="score-row is-neutral">' +
        '<div class="score-row-main"><p class="score-row-label">' + escapeHtml(result.merits.label || "Méritos") + "</p>" +
        '<p class="score-row-meta">puntos que has escrito tú, no un baremo automático</p></div>' +
        '<p class="score-row-score">' + fmt(result.merits.value, 3) +
        (typeof result.merits.maximum === "number" ? '<span class="score-max"> / ' + fmt(result.merits.maximum, 3) + "</span>" : "") +
        "</p>" +
        '<p class="score-row-status"><span class="status status-neutral">concurso</span></p></div>'
      );
    }
    if (typeof result.process_total === "number" && result.merits) {
      rows += (
        '<div class="score-row is-total">' +
        '<div class="score-row-main"><p class="score-row-label">TOTAL</p>' +
        '<p class="score-row-meta">oposición + méritos</p></div>' +
        '<p class="score-row-score">' + fmt(result.process_total, 4) + "</p>" +
        '<p class="score-row-status"><span class="status status-neutral">proceso</span></p></div>'
      );
    }
    return rows;
  }

  function interpretation(result) {
    if (result.all_required_passed === false) {
      return "Con estos números no llegas a todos los mínimos o al apto que esta convocatoria permite comprobar. Mira las filas en rojo: no es plaza ni un corte, es el suelo de las bases.";
    }
    if (result.all_required_passed === true) {
      return "Llegas al mínimo oficial de las pruebas que esta página puede comprobar. Eso no es plaza ni la nota de corte: el corte lo marca el resto de aspirantes cuando el tribunal publica la lista.";
    }
    return "Esta es la puntuación según la fórmula del boletín. Si una prueba no tiene mínimo en esta página, no se afirma apto ni no apto.";
  }

  function scenarioText(config, item) {
    var stage = (config.stages || []).filter(function (s) { return s.id === item.stage_id; })[0];
    var name = stage ? escapeHtml(stage.label) : escapeHtml(item.stage_id);
    if (item.type === "max_errors_for_minimum") {
      return "En " + name + ", con " + item.hits + " aciertos podrías cometer como máximo " + item.max_errors + " error(es) y seguir en el mínimo " + item.minimum + ".";
    }
    if (item.type === "hits_for_minimum") {
      return "En " + name + ", con " + item.errors + " error(es) necesitarías al menos " + item.hits_needed + " acierto(s) para el mínimo " + item.minimum + ".";
    }
    if (item.type === "hits_for_target") {
      if (!item.possible) {
        return "En " + name + ", con " + item.errors + " error(es) no es posible alcanzar " + item.target + " puntos de oposición dejando el resto igual.";
      }
      return "Para alcanzar " + item.target + " puntos de oposición, en " + name + " necesitarías " + item.hits_needed + " acierto(s) si mantienes " + item.errors + " error(es) y el resto de pruebas.";
    }
    return "";
  }

  function renderScenarios(config, result) {
    var items = (result.scenarios || []).map(function (item) {
      return scenarioText(config, item);
    }).filter(Boolean);
    if (!items.length) return "";
    return "<h3>Qué implican estos números</h3><ul>" + items.map(function (s) { return "<li>" + s + "</li>"; }).join("") + "</ul>";
  }

  function historicalScore(config, result) {
    var hist = config.historical || {};
    if (hist.metric === "process_total" && typeof result.process_total === "number") return result.process_total;
    return result.opposition_total;
  }

  function rankInList(scores, value) {
    var better = 0;
    var equal = 0;
    var i;
    for (i = 0; i < scores.length; i += 1) {
      if (scores[i] > value) better += 1;
      else if (scores[i] === value) equal += 1;
    }
    return {
      position: better + 1,
      equal: equal,
      n: scores.length,
      cut: scores.length ? scores[scores.length - 1] : null
    };
  }

  function renderHistorical(config, result) {
    var hist = config.historical;
    if (!hist) return "";
    var score = historicalScore(config, result);
    if (typeof score !== "number" || Number.isNaN(score)) return "";
    var title = escapeHtml(hist.title || "Comparación con el año pasado");
    var disc = hist.disclaimer ? "<p class=\"historical-note\">" + escapeHtml(hist.disclaimer) + "</p>" : "";
    var source = "";
    if (hist.source_url && hist.source_identifier) {
      source = '<p class="historical-source"><a href="' + escapeHtml(hist.source_url) + '">' + escapeHtml(hist.source_identifier) + "</a></p>";
    } else if (hist.source_identifier) {
      source = '<p class="historical-source">' + escapeHtml(hist.source_identifier) + "</p>";
    }
    if (hist.kind === "cut" && typeof hist.cut === "number") {
      var above = score + 1e-9 >= hist.cut;
      var gap = Math.abs(score - hist.cut);
      var verdict = above
        ? "Con " + fmt(score, 4) + " habrías superado ese corte (por " + fmt(gap, 4) + " puntos)."
        : "Con " + fmt(score, 4) + " no habrías alcanzado ese corte (te faltarían " + fmt(gap, 4) + " puntos).";
      return (
        "<h3>" + title + "</h3>" +
        "<p>" + escapeHtml(hist.what || "Corte de la convocatoria anterior") + ": <strong>" + fmt(hist.cut, 4) + "</strong>" +
        (hist.cut_label ? " (" + escapeHtml(hist.cut_label) + ")" : "") + ".</p>" +
        "<p>" + verdict + "</p>" +
        disc + source
      );
    }
    if (hist.kind === "selected_list" && hist.scores && hist.scores.length) {
      var ranked = rankInList(hist.scores, score);
      var body;
      if (score + 1e-9 < ranked.cut) {
        body = "Con un total de " + fmt(score, 4) + " no habrías entrado en esa lista. El último con plaza tuvo " + fmt(ranked.cut, 5) + " puntos.";
      } else {
        body = "Con un total de " + fmt(score, 4) + " habrías ocupado el puesto <strong>" + ranked.position + "</strong> de " + ranked.n + " propuestos a alumno en turno libre.";
        if (ranked.equal > 1) {
          body += " " + ranked.equal + " personas tuvieron exactamente esa puntuación.";
        }
      }
      return (
        "<h3>" + title + "</h3>" +
        "<p>" + escapeHtml(hist.label || "Lista oficial de quienes obtuvieron plaza") + ".</p>" +
        "<p>" + body + "</p>" +
        disc + source
      );
    }
    return "";
  }

  function resultText(config, result) {
    var lines = [config.h1, "Oposición: " + fmt(result.opposition_total, 4)];
    if (result.merits) {
      lines.push("Méritos: " + fmt(result.merits.value, 3));
      lines.push("Total: " + fmt(result.process_total, 4));
    }
    result.stages.forEach(function (stage) {
      lines.push(stage.label + ": " + scoreHtml(stage));
    });
    lines.push("Fuente: " + (config.source_identifier || config.fuente_oficial.title));
    lines.push("Cálculo orientativo. Prevalece la convocatoria oficial.");
    return lines.join("\n");
  }

  function progressKey(slug) {
    return "tunotaopo:progress:" + slug;
  }

  function targetKey(slug) {
    return "tunotaopo:target:" + slug;
  }

  function loadProgress(slug) {
    try {
      var raw = localStorage.getItem(progressKey(slug));
      var rows = raw ? JSON.parse(raw) : [];
      return Array.isArray(rows) ? rows : [];
    } catch (ignore) {
      return [];
    }
  }

  function readTarget(slug, form) {
    var targetEl = form && form.elements.target_score;
    var typed = targetEl && targetEl.value ? Number(String(targetEl.value).replace(",", ".")) : NaN;
    if (Number.isFinite(typed) && typed > 0) return typed;
    try {
      var saved = Number(localStorage.getItem(targetKey(slug)));
      return Number.isFinite(saved) && saved > 0 ? saved : NaN;
    } catch (ignore) {
      return NaN;
    }
  }

  function saveProgress(config, result) {
    var score = typeof result.process_total === "number" ? result.process_total : result.opposition_total;
    if (typeof score !== "number" || !Number.isFinite(score)) return;
    var rows = loadProgress(config.slug);
    rows.push({ t: Date.now(), s: Math.round(score * 10000) / 10000 });
    if (rows.length > 20) rows = rows.slice(-20);
    var form = $("calc-form");
    var target = readTarget(config.slug, form);
    try {
      localStorage.setItem(progressKey(config.slug), JSON.stringify(rows));
      if (Number.isFinite(target)) localStorage.setItem(targetKey(config.slug), String(target));
    } catch (ignore) {}
  }

  function renderProgress(config) {
    var panel = $("progress-panel");
    if (!panel) return;
    var rows = loadProgress(config.slug);
    if (!rows.length) {
      panel.hidden = true;
      panel.innerHTML = "";
      return;
    }
    var first = rows[0].s;
    var last = rows[rows.length - 1].s;
    var delta = Math.round((last - first) * 10000) / 10000;
    var form = $("calc-form");
    var target = readTarget(config.slug, form);
    var items = rows.slice(-8).map(function (row) {
      var label = new Date(row.t).toLocaleDateString("es-ES", { day: "numeric", month: "long" });
      return "<li><span>" + escapeHtml(label) + "</span><strong>" + fmt(row.s, 2) + "</strong></li>";
    }).join("");
    var trend = "Mejora: " + (delta >= 0 ? "+" : "") + fmt(delta, 2);
    var goal = "";
    if (Number.isFinite(target) && target > 0) {
      var left = Math.round((target - last) * 10000) / 10000;
      if (left > 0) goal = "<p>Objetivo: " + fmt(target, 2) + ". Te faltan " + fmt(left, 2) + ".</p>";
      else goal = "<p>Objetivo: " + fmt(target, 2) + ". Ya lo superas en este simulacro.</p>";
    }
    panel.hidden = false;
    panel.innerHTML =
      "<h2>Mis simulacros</h2>" +
      '<ol class="progress-list">' + items + "</ol>" +
      '<p class="progress-trend">' + trend + "</p>" +
      goal +
      '<p class="progress-note">Se guarda solo en este navegador. No hay cuenta ni servidor.</p>' +
      '<p><a href="' + (document.body.getAttribute("data-root") || "") + 'oposiciones/progreso/index.html">Ver todo mi progreso</a></p>' +
      '<p><button type="button" class="button button-secondary" id="progress-clear">Borrar historial</button></p>';
    var clear = $("progress-clear");
    if (clear) {
      clear.addEventListener("click", function () {
        try {
          localStorage.removeItem(progressKey(config.slug));
        } catch (ignore) {}
        renderProgress(config);
      });
    }
  }

  function showResult(config, result) {
    var box = $("calc-result");
    hideToast();
    clearInvalid();
    box.hidden = false;
    if ($("result-placeholder")) $("result-placeholder").hidden = true;
    $("result-kicker").textContent = "Puntuación de la oposición";
    $("result-value").textContent = fmt(result.opposition_total, 4);
    var maxOpp = config.aggregate && typeof config.aggregate.maximum === "number" ? config.aggregate.maximum : null;
    var scale = $("result-scale");
    if (scale) {
      if (maxOpp !== null) {
        scale.textContent = "sobre " + fmt(maxOpp, 0) + (result.merits ? " · total " + fmt(result.process_total, 4) : "");
      } else {
        scale.textContent = result.merits ? "total " + fmt(result.process_total, 4) : "";
      }
    }
    $("result-note").textContent = interpretation(result);
    $("result-breakdown").innerHTML = '<h3 class="score-list-title">Desglose de cada prueba</h3>' + renderBreakdown(result);
    $("result-scenarios").innerHTML = renderScenarios(config, result);
    if ($("result-historical")) $("result-historical").innerHTML = renderHistorical(config, result);
    box.dataset.text = resultText(config, result);
    saveProgress(config, result);
    renderProgress(config);
    if (typeof box.scrollIntoView === "function") {
      var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      box.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
  }

  var toastTimer = null;

  function friendlyError(message) {
    var text = String(message || "").trim();
    if (!text) return "Revisa los datos del formulario para poder calcular.";
    if (/^Indica /i.test(text)) {
      return "Falta un dato: " + text.replace(/^Indica\s+/i, "").replace(/\.$/, "") + ".";
    }
    return text;
  }

  function clearInvalid() {
    document.querySelectorAll(".is-invalid").forEach(function (el) {
      el.classList.remove("is-invalid");
      if (el.removeAttribute) el.removeAttribute("aria-invalid");
    });
  }

  function hideToast() {
    var toast = $("calc-toast");
    if (toast) toast.hidden = true;
    if (toastTimer) {
      window.clearTimeout(toastTimer);
      toastTimer = null;
    }
  }

  function fieldFromError(form, config, message) {
    var stages = (config && config.stages) || [];
    var i;
    var field;
    for (i = 0; i < stages.length; i += 1) {
      var stage = stages[i];
      var label = stage.label;
      if (message.indexOf(label) === -1) continue;
      if (message.indexOf("preguntas válidas") !== -1) field = form.elements[stage.id + "_valid"];
      else if (message.indexOf("aciertos") !== -1) field = form.elements[stage.id + "_hits"];
      else if (message.indexOf("errores") !== -1) field = form.elements[stage.id + "_errors"];
      else field = form.elements[stage.id + "_hits"] || form.elements[stage.id + "_errors"] || form.elements[stage.id + "_cut"] || form.elements[stage.id + "_value"];
      if (field) return field;
    }
    return null;
  }

  function showError(message, form, config) {
    hideToast();
    clearInvalid();
    var toast = $("calc-toast");
    var text = $("calc-toast-message");
    if (text) text.textContent = friendlyError(message);
    if (toast) toast.hidden = false;
    if ($("calc-result")) $("calc-result").hidden = true;
    if ($("result-placeholder")) $("result-placeholder").hidden = false;
    var field = form && config ? fieldFromError(form, config, String(message || "")) : null;
    if (field) {
      field.classList.add("is-invalid");
      field.setAttribute("aria-invalid", "true");
      if (field.closest) {
        var stage = field.closest(".stage");
        if (stage) stage.classList.add("is-invalid");
      }
      if (typeof field.focus === "function") field.focus();
      if (typeof field.scrollIntoView === "function") {
        var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        field.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
      }
    }
    toastTimer = window.setTimeout(hideToast, 7000);
  }

  function bind(config) {
    var form = $("calc-form");
    if (!form || !root.NotaOpoEngine) return;
    keepCanonicalClean();

    form.setAttribute("autocomplete", "off");
    try {
      var savedTarget = Number(localStorage.getItem(targetKey(config.slug)));
      if (Number.isFinite(savedTarget) && savedTarget > 0 && form.elements.target_score && !form.elements.target_score.value) {
        form.elements.target_score.value = String(savedTarget);
      }
    } catch (ignore) {}
    renderProgress(config);

    function clearSession() {
      form.reset();
      $("calc-result").hidden = true;
      hideToast();
      clearInvalid();
      if ($("result-placeholder")) $("result-placeholder").hidden = false;
      localStorage.removeItem("notaopo:" + config.slug);
    }

    var fromQuery = inputsFromQuery(form);
    if (fromQuery.rejected) {
      showError("La URL compartida contiene un parámetro no válido. Introduce los datos de nuevo.", form, config);
    } else if (Object.keys(fromQuery.data).length) {
      applyInputs(form, fromQuery.data);
    } else {
      localStorage.removeItem("notaopo:" + config.slug);
    }

    window.addEventListener("pageshow", function (event) {
      if (location.search) return;
      if (event.persisted) clearSession();
    });

    form.addEventListener("input", function (event) {
      var target = event.target;
      if (target && target.classList) {
        target.classList.remove("is-invalid");
        target.removeAttribute("aria-invalid");
        if (target.closest) {
          var stage = target.closest(".stage");
          if (stage && !stage.querySelector(".is-invalid")) stage.classList.remove("is-invalid");
        }
      }
      root.NotaOpoAnalytics.started(config.slug);
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      try {
        var inputs = collectInputs(form);
        var result = root.NotaOpoEngine.evaluate(config, inputs);
        showResult(config, result);
        root.NotaOpoAnalytics.completed(config.slug);
      } catch (error) {
        showError(error.message, form, config);
      }
    });

    form.addEventListener("reset", function () {
      $("calc-result").hidden = true;
      hideToast();
      clearInvalid();
      if ($("result-placeholder")) $("result-placeholder").hidden = false;
      localStorage.removeItem("notaopo:" + config.slug);
      history.replaceState({}, "", location.pathname);
    });

    if ($("calc-toast-close")) {
      $("calc-toast-close").addEventListener("click", hideToast);
    }

    function copyText(text) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text).catch(function () {
          return copyTextFallback(text);
        });
      }
      return copyTextFallback(text);
    }

    function copyTextFallback(text) {
      return new Promise(function (resolve, reject) {
        var area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.setAttribute("aria-hidden", "true");
        area.style.position = "fixed";
        area.style.top = "0";
        area.style.left = "0";
        area.style.width = "2em";
        area.style.height = "2em";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.focus();
        area.select();
        var ok = false;
        try {
          ok = document.execCommand("copy");
        } catch (ignore) {}
        document.body.removeChild(area);
        if (ok) resolve();
        else reject(new Error("No se pudo copiar"));
      });
    }

    function flashButton(button, label) {
      var original = button.textContent;
      button.textContent = label;
      window.setTimeout(function () {
        button.textContent = original;
      }, 2000);
    }

    $("copy-result").addEventListener("click", function () {
      var textValue = $("calc-result").dataset.text || "";
      if (!textValue) return;
      copyText(textValue).then(function () {
        flashButton($("copy-result"), "Copiado");
      }).catch(function () {
        flashButton($("copy-result"), "No se pudo copiar");
      });
    });

    $("share-result").addEventListener("click", function () {
      var query = queryFromInputs(form, collectInputs(form));
      var url = location.pathname + (query ? "?" + query : "");
      var absolute = location.origin + url;
      history.replaceState({}, "", url);
      copyText(absolute).then(function () {
        flashButton($("share-result"), "URL copiada");
        root.NotaOpoAnalytics.shared(config.slug);
      }).catch(function () {
        window.prompt("Copia esta URL:", absolute);
      });
    });

    $("print-result").addEventListener("click", function () {
      window.print();
    });

    document.querySelectorAll("[data-track='official-source']").forEach(function (link) {
      link.addEventListener("click", function () {
        root.NotaOpoAnalytics.officialSourceClicked(link.href);
      });
    });

    if (!fromQuery.rejected && Object.keys(fromQuery.data).length) {
      form.requestSubmit();
    }
    renderProgress(config);
  }

  root.NotaOpoCalculator = { bind: bind };
})(window);
