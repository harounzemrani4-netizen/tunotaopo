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

  function showResult(config, result) {
    var box = $("calc-result");
    var err = $("calc-error");
    err.hidden = true;
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
    box.dataset.text = resultText(config, result);
    if (typeof box.scrollIntoView === "function") {
      var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      box.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
  }

  function showError(message) {
    $("calc-result").hidden = true;
    var err = $("calc-error");
    err.hidden = false;
    err.textContent = message;
    if ($("result-placeholder")) $("result-placeholder").hidden = true;
  }

  function bind(config) {
    var form = $("calc-form");
    if (!form || !root.NotaOpoEngine) return;
    keepCanonicalClean();

    form.setAttribute("autocomplete", "off");

    function clearSession() {
      form.reset();
      $("calc-result").hidden = true;
      $("calc-error").hidden = true;
      if ($("result-placeholder")) $("result-placeholder").hidden = false;
      localStorage.removeItem("notaopo:" + config.slug);
    }

    var fromQuery = inputsFromQuery(form);
    if (fromQuery.rejected) {
      showError("La URL compartida contiene un parámetro no válido. Introduce los datos de nuevo.");
    } else if (Object.keys(fromQuery.data).length) {
      applyInputs(form, fromQuery.data);
    } else {
      localStorage.removeItem("notaopo:" + config.slug);
    }

    window.addEventListener("pageshow", function (event) {
      if (location.search) return;
      if (event.persisted) clearSession();
    });

    form.addEventListener("input", function () {
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
        showError(error.message);
      }
    });

    form.addEventListener("reset", function () {
      $("calc-result").hidden = true;
      $("calc-error").hidden = true;
      if ($("result-placeholder")) $("result-placeholder").hidden = false;
      localStorage.removeItem("notaopo:" + config.slug);
      history.replaceState({}, "", location.pathname);
    });

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
  }

  root.NotaOpoCalculator = { bind: bind };
})(window);
