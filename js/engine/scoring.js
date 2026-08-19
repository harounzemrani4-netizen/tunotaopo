/**
 * NotaOpo scoring engine — declarative, opposition-agnostic.
 * Models: net_score, scaled_score, fixed_value, pass_fail,
 * pass_fail_errors, transform, multi_stage, aggregate.
 */
(function (root) {
  "use strict";

  function isFiniteNumber(value) {
    return typeof value === "number" && Number.isFinite(value);
  }

  function toInt(value, label) {
    if (value === "" || value === null || value === undefined) {
      throw new Error("Indica " + label + ".");
    }
    if (typeof value === "string" && value.trim() === "") {
      throw new Error("Indica " + label + ".");
    }
    var n = typeof value === "number" ? value : Number(value);
    if (!Number.isFinite(n) || !Number.isInteger(n)) {
      throw new Error(label + " debe ser un número entero.");
    }
    if (n < 0) {
      throw new Error(label + " no puede ser negativo.");
    }
    return n;
  }

  function optionalNumber(value, label) {
    if (value === "" || value === null || value === undefined) return null;
    if (typeof value === "string" && value.trim() === "") return null;
    var n = typeof value === "number" ? value : Number(String(value).replace(",", "."));
    if (!Number.isFinite(n)) {
      throw new Error(label + " no es un número válido.");
    }
    return n;
  }

  function optionalInt(value, label) {
    var n = optionalNumber(value, label);
    if (n === null) return null;
    if (!Number.isInteger(n) || n < 0) {
      throw new Error(label + " debe ser un entero mayor o igual que 0.");
    }
    return n;
  }

  function roundTo(value, digits) {
    if (!isFiniteNumber(value)) return value;
    if (!isFiniteNumber(digits)) return value;
    var factor = Math.pow(10, digits);
    return Math.round((value + Number.EPSILON) * factor) / factor;
  }

  function clamp(value, min, max) {
    var out = value;
    if (isFiniteNumber(min) && out < min) out = min;
    if (isFiniteNumber(max) && out > max) out = max;
    return out;
  }

  function penaltyPerError(stage) {
    if (isFiniteNumber(stage.incorrect_penalty)) return stage.incorrect_penalty;
    var correct = isFiniteNumber(stage.correct_value) ? stage.correct_value : 1;
    var divisor = stage.incorrect_divisor;
    if (!isFiniteNumber(divisor) && isFiniteNumber(stage.options_count)) {
      divisor = stage.options_count - 1;
    }
    if (isFiniteNumber(divisor) && divisor !== 0) return correct / divisor;
    return 0;
  }

  function resolveValidQuestions(stage, inputs) {
    var key = stage.id + "_valid";
    var override = optionalInt(inputs ? inputs[key] : null, "preguntas válidas de " + stage.label);
    var fallback = isFiniteNumber(stage.valid_questions) ? stage.valid_questions : stage.questions;
    var valid = override === null ? fallback : override;
    if (!isFiniteNumber(valid) || valid < 1) {
      throw new Error(stage.label + ": las preguntas válidas deben ser al menos 1.");
    }
    var original = isFiniteNumber(stage.questions) ? stage.questions : valid;
    if (valid > original + (stage.reserve_questions || 0)) {
      throw new Error(
        stage.label + ": las preguntas válidas no pueden superar el cuestionario más la reserva."
      );
    }
    return valid;
  }

  function assertCounts(valid, hits, errors, label) {
    var blanks = valid - hits - errors;
    if (blanks < 0) {
      throw new Error(
        (label ? label + ": " : "") +
          "aciertos + errores no pueden superar " + valid + " preguntas válidas."
      );
    }
    return blanks;
  }

  function netRaw(hits, errors, blanks, stage) {
    var correct = isFiniteNumber(stage.correct_value) ? stage.correct_value : 1;
    var blankValue = isFiniteNumber(stage.blank_value) ? stage.blank_value : 0;
    return hits * correct - errors * penaltyPerError(stage) + blanks * blankValue;
  }

  function applyRoundClamp(raw, stage) {
    var min = isFiniteNumber(stage.clamp_min) ? stage.clamp_min : undefined;
    var max = isFiniteNumber(stage.clamp_max)
      ? stage.clamp_max
      : (isFiniteNumber(stage.maximum) ? stage.maximum : undefined);
    var score = clamp(raw, min, max);
    var digits = isFiniteNumber(stage.rounding) ? stage.rounding : null;
    return {
      raw: raw,
      score: score,
      rounded: digits === null ? score : roundTo(score, digits)
    };
  }

  function evaluateNetOrFixed(stage, hits, errors, valid) {
    var blanks = assertCounts(valid, hits, errors, stage.label);
    var raw = netRaw(hits, errors, blanks, stage);
    var packed = applyRoundClamp(raw, stage);
    return baseStageResult(stage, hits, errors, blanks, valid, packed, packed.rounded);
  }

  function evaluateScaled(stage, hits, errors, valid) {
    var blanks = assertCounts(valid, hits, errors, stage.label);
    var divisor = stage.incorrect_divisor;
    if (!isFiniteNumber(divisor) && isFiniteNumber(stage.options_count)) {
      divisor = stage.options_count - 1;
    }
    if (!isFiniteNumber(divisor) || divisor === 0) {
      throw new Error(stage.label + ": falta incorrect_divisor u options_count.");
    }
    var maximum = isFiniteNumber(stage.maximum) ? stage.maximum : valid;
    var raw = (maximum * (hits - errors / divisor)) / valid;
    var packed = applyRoundClamp(raw, stage);
    packed.penalty = errors / divisor;
    return baseStageResult(stage, hits, errors, blanks, valid, packed, packed.rounded);
  }

  function evaluatePassFailErrors(stage, errors) {
    var limit = isFiniteNumber(stage.questions) ? stage.questions : stage.valid_questions;
    if (isFiniteNumber(limit) && errors > limit) {
      throw new Error(stage.label + ": los errores no pueden superar " + limit + ".");
    }
    var threshold = stage.fail_if_errors_gte;
    if (!isFiniteNumber(threshold)) {
      throw new Error(stage.label + ": falta fail_if_errors_gte.");
    }
    var passed = errors < threshold;
    return {
      id: stage.id,
      label: stage.label,
      model: "pass_fail_errors",
      hits: null,
      errors: errors,
      blanks: null,
      valid_questions: limit,
      penalty: errors,
      raw: null,
      score: passed ? 1 : 0,
      rounded: null,
      verdict: passed ? "apto" : "no_apto",
      passed: passed,
      minimum: null,
      maximum: null,
      eliminatory: stage.eliminatory === true,
      source_reference: stage.source_reference || null
    };
  }

  function evaluatePassFail(stage, inputs) {
    var value = optionalNumber(inputs[stage.id + "_value"], stage.label);
    if (value === null) {
      throw new Error("Indica " + stage.label + ".");
    }
    var passed = true;
    if (isFiniteNumber(stage.minimum)) passed = passed && value >= stage.minimum;
    if (isFiniteNumber(stage.maximum)) passed = passed && value <= stage.maximum;
    return {
      id: stage.id,
      label: stage.label,
      model: "pass_fail",
      hits: null,
      errors: null,
      blanks: null,
      valid_questions: null,
      penalty: null,
      raw: value,
      score: value,
      rounded: value,
      verdict: passed ? "apto" : "no_apto",
      passed: passed,
      minimum: stage.minimum,
      maximum: stage.maximum,
      eliminatory: stage.eliminatory === true,
      source_reference: stage.source_reference || null
    };
  }

  function baseStageResult(stage, hits, errors, blanks, valid, packed, rounded) {
    var min = isFiniteNumber(stage.minimum) ? stage.minimum : null;
    var passed = min === null ? null : rounded >= min;
    return {
      id: stage.id,
      label: stage.label,
      model: stage.model,
      hits: hits,
      errors: errors,
      blanks: blanks,
      valid_questions: valid,
      penalty: packed.penalty !== undefined ? packed.penalty : errors * penaltyPerError(stage),
      raw: packed.raw,
      score: packed.score,
      rounded: rounded,
      verdict: passed === true ? "supera_minimo" : passed === false ? "no_alcanza_minimo" : null,
      passed: passed,
      minimum: min,
      maximum: isFiniteNumber(stage.maximum) ? stage.maximum : null,
      eliminatory: stage.eliminatory === true,
      source_reference: stage.source_reference || null
    };
  }

  function evaluateTransform(stage, byId) {
    var source = byId[stage.source_stage];
    if (!source || !isFiniteNumber(source.rounded)) {
      return {
        id: stage.id,
        label: stage.label,
        model: "transform",
        rounded: null,
        passed: null,
        verdict: "sin_umbral",
        source_stage: stage.source_stage,
        pd: source ? source.rounded : null,
        cut: stage.cut,
        eliminatory: stage.eliminatory === true
      };
    }
    var cut = stage.cut;
    if (!isFiniteNumber(cut)) {
      return {
        id: stage.id,
        label: stage.label,
        model: "transform",
        rounded: null,
        passed: null,
        verdict: "sin_umbral",
        source_stage: stage.source_stage,
        pd: source.rounded,
        cut: null,
        eliminatory: stage.eliminatory === true
      };
    }
    var pd = source.rounded;
    var pdMax = isFiniteNumber(stage.pd_max) ? stage.pd_max : source.maximum;
    var calMin = stage.cal_min;
    var calMax = stage.cal_max;
    if (pd < cut) {
      return {
        id: stage.id,
        label: stage.label,
        model: "transform",
        rounded: null,
        passed: false,
        verdict: "no_alcanza_minimo",
        source_stage: stage.source_stage,
        pd: pd,
        cut: cut,
        minimum: calMin,
        maximum: calMax,
        eliminatory: stage.eliminatory === true
      };
    }
    var raw = pd >= pdMax ? calMax : calMin + ((calMax - calMin) * (pd - cut)) / (pdMax - cut);
    var rounded = isFiniteNumber(stage.rounding) ? roundTo(raw, stage.rounding) : raw;
    return {
      id: stage.id,
      label: stage.label,
      model: "transform",
      rounded: rounded,
      score: rounded,
      raw: raw,
      passed: true,
      verdict: "supera_minimo",
      source_stage: stage.source_stage,
      pd: pd,
      cut: cut,
      minimum: calMin,
      maximum: calMax,
      eliminatory: stage.eliminatory === true
    };
  }

  function evaluateStage(stage, inputs, byId) {
    var model = stage.model;
    if (model === "transform") {
      var cut = optionalNumber(inputs[stage.id + "_cut"] || inputs[stage.source_stage + "_cut"], "umbral de " + stage.label);
      var clone = {};
      Object.keys(stage).forEach(function (k) { clone[k] = stage[k]; });
      clone.cut = cut;
      return evaluateTransform(clone, byId);
    }
    if (model === "pass_fail_errors") {
      return evaluatePassFailErrors(stage, toInt(inputs[stage.id + "_errors"], "errores de " + stage.label));
    }
    if (model === "pass_fail") {
      return evaluatePassFail(stage, inputs);
    }
    if (model === "aggregate" || model === "multi_stage") {
      return null;
    }
    var hits = toInt(inputs[stage.id + "_hits"], "aciertos de " + stage.label);
    var errors = toInt(inputs[stage.id + "_errors"], "errores de " + stage.label);
    var valid = resolveValidQuestions(stage, inputs);
    if (model === "scaled_score") {
      return evaluateScaled(stage, hits, errors, valid);
    }
    if (model === "net_score" || model === "fixed_value") {
      return evaluateNetOrFixed(stage, hits, errors, valid);
    }
    throw new Error("Modelo no soportado: " + model);
  }

  function sumStages(results, ids) {
    var total = 0;
    var i;
    for (i = 0; i < ids.length; i += 1) {
      var item = results[ids[i]];
      if (!item || !isFiniteNumber(item.rounded)) {
        return null;
      }
      total += item.rounded;
    }
    return total;
  }

  function evaluateAggregates(config, byId) {
    var aggregates = config.aggregates || [];
    if (config.aggregate && aggregates.length === 0) {
      aggregates = [config.aggregate];
    }
    var out = {};
    aggregates.forEach(function (agg) {
      var ids = agg.include || agg.stages || [];
      var total = sumStages(byId, ids);
      if (total !== null && isFiniteNumber(agg.rounding)) {
        total = roundTo(total, agg.rounding);
      }
      if (total !== null && isFiniteNumber(agg.maximum)) {
        total = clamp(total, isFiniteNumber(agg.minimum) ? agg.minimum : undefined, agg.maximum);
      }
      out[agg.id] = {
        id: agg.id,
        label: agg.label || agg.id,
        model: "aggregate",
        value: total,
        maximum: agg.maximum || null
      };
    });
    return out;
  }

  function evaluateMerits(config, inputs) {
    if (!config.merits) return null;
    var merits = config.merits;
    var value = optionalNumber(inputs[merits.id] || inputs.merits || inputs.concurso, merits.label || "méritos");
    if (value === null) return null;
    var min = isFiniteNumber(merits.minimum) ? merits.minimum : 0;
    var max = isFiniteNumber(merits.maximum) ? merits.maximum : undefined;
    if (value < min || (isFiniteNumber(max) && value > max)) {
      throw new Error(
        (merits.label || "Méritos") + " debe estar entre " + min + " y " + max + " puntos."
      );
    }
    var rounded = isFiniteNumber(merits.rounding) ? roundTo(value, merits.rounding) : value;
    return {
      id: merits.id || "merits",
      label: merits.label || "Méritos",
      value: rounded,
      minimum: min,
      maximum: max
    };
  }

  function requirementsMet(config, byId) {
    var reqs = config.requirements || [];
    if (!reqs.length) {
      return Object.keys(byId).every(function (id) {
        return byId[id].eliminatory !== true || byId[id].passed !== false;
      });
    }
    return reqs.every(function (req) {
      if (req.type === "all_passed" || req.type === "all_eliminatory_passed") {
        var ids = req.stages || Object.keys(byId);
        return ids.every(function (id) {
          return !byId[id] || byId[id].passed !== false;
        });
      }
      return true;
    });
  }

  function hitsNeededForScore(stage, errors, target, valid) {
    if (!isFiniteNumber(target)) return null;
    var maxHits = valid - errors;
    var a;
    for (a = 0; a <= maxHits; a += 1) {
      var trial;
      if (stage.model === "scaled_score") {
        trial = evaluateScaled(stage, a, errors, valid);
      } else if (stage.model === "net_score" || stage.model === "fixed_value") {
        trial = evaluateNetOrFixed(stage, a, errors, valid);
      } else {
        return null;
      }
      if (trial.rounded >= target) return a;
    }
    return null;
  }

  function maxErrorsForMinimum(stage, hits, valid) {
    if (!isFiniteNumber(stage.minimum)) return null;
    var keep = null;
    var e;
    for (e = 0; e <= valid - hits; e += 1) {
      var trial;
      if (stage.model === "scaled_score") {
        trial = evaluateScaled(stage, hits, e, valid);
      } else {
        trial = evaluateNetOrFixed(stage, hits, e, valid);
      }
      if (trial.rounded >= stage.minimum) keep = e;
      else break;
    }
    return keep;
  }

  function buildScenarios(config, inputs, byId, aggregates) {
    var lines = [];
    var stages = config.stages || [];
    stages.forEach(function (stage) {
      if (!isFiniteNumber(stage.minimum)) return;
      if (stage.model !== "scaled_score" && stage.model !== "net_score" && stage.model !== "fixed_value") return;
      var current = byId[stage.id];
      if (!current || !isFiniteNumber(current.hits)) return;
      var valid = current.valid_questions;
      var maxE = maxErrorsForMinimum(stage, current.hits, valid);
      if (maxE !== null) {
        lines.push({
          type: "max_errors_for_minimum",
          stage_id: stage.id,
          hits: current.hits,
          max_errors: maxE,
          minimum: stage.minimum
        });
      }
      var need = hitsNeededForScore(stage, current.errors, stage.minimum, valid);
      if (need !== null) {
        lines.push({
          type: "hits_for_minimum",
          stage_id: stage.id,
          errors: current.errors,
          hits_needed: need,
          minimum: stage.minimum
        });
      }
    });

    var target = optionalNumber(inputs.target_score, "puntuación objetivo");
    var agg = config.aggregate || (config.aggregates && config.aggregates[0]);
    if (target !== null && agg && isFiniteNumber(aggregates[agg.id] && aggregates[agg.id].value)) {
      var include = agg.include || agg.stages || [];
      include.forEach(function (id) {
        var stage = stages.filter(function (s) { return s.id === id; })[0];
        var current = byId[id];
        if (!stage || !current || !isFiniteNumber(current.rounded)) return;
        var others = include.filter(function (x) { return x !== id; }).reduce(function (sum, x) {
          return sum + (byId[x] && isFiniteNumber(byId[x].rounded) ? byId[x].rounded : 0);
        }, 0);
        var neededScore = target - others;
        var hits = hitsNeededForScore(stage, current.errors, neededScore, current.valid_questions);
        lines.push({
          type: "hits_for_target",
          stage_id: id,
          target: target,
          hits_needed: hits,
          errors: current.errors,
          possible: hits !== null
        });
      });
    }
    return lines;
  }

  function evaluate(config, inputs) {
    if (!config || !config.stages) {
      throw new Error("Falta la configuración de etapas de la convocatoria.");
    }
    inputs = inputs || {};
    var byId = {};
    var order = [];
    var i;
    var stage;
    var result;

    var pending = config.stages.slice();
    var guard = 0;
    while (pending.length && guard < 40) {
      guard += 1;
      var next = [];
      for (i = 0; i < pending.length; i += 1) {
        stage = pending[i];
        if (stage.model === "aggregate" || stage.model === "multi_stage") {
          continue;
        }
        if (stage.model === "transform" && !byId[stage.source_stage]) {
          next.push(stage);
          continue;
        }
        result = evaluateStage(stage, inputs, byId);
        if (result) {
          byId[result.id] = result;
          order.push(result.id);
        }
      }
      if (next.length === pending.length) break;
      pending = next;
    }

    var aggregates = evaluateAggregates(config, byId);
    var merits = evaluateMerits(config, inputs);
    var oppositionId = (config.aggregate && config.aggregate.id) || "oposicion";
    var opposition = aggregates[oppositionId] ? aggregates[oppositionId].value : null;
    var processTotal = opposition;
    if (merits && isFiniteNumber(opposition)) {
      var digits = config.process_rounding || (config.aggregate && config.aggregate.rounding) || 4;
      processTotal = roundTo(opposition + merits.value, digits);
    }

    var stages = order.map(function (id) { return byId[id]; });
    var scenarios = buildScenarios(config, inputs, byId, aggregates);

    return {
      slug: config.slug,
      stages: stages,
      byId: byId,
      aggregates: aggregates,
      merits: merits,
      opposition_total: opposition,
      process_total: processTotal,
      all_required_passed: requirementsMet(config, byId),
      scenarios: scenarios
    };
  }

  root.NotaOpoEngine = {
    toInt: toInt,
    optionalNumber: optionalNumber,
    roundTo: roundTo,
    clamp: clamp,
    penaltyPerError: penaltyPerError,
    evaluateStage: evaluateStage,
    hitsNeededForScore: hitsNeededForScore,
    maxErrorsForMinimum: maxErrorsForMinimum,
    evaluate: evaluate
  };
})(typeof window !== "undefined" ? window : globalThis);
