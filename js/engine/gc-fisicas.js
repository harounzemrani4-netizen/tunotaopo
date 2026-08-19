/**
 * Guardia Civil — pruebas físicas (Apéndice II, BOE-A-2026-9982).
 * Cuatro ejercicios eliminatorios. Apto / no apto. No usa las tablas de Policía Nacional.
 * Tramos: menor de 35; 35 a 39; 40 o más. Tiempos máximos: no superiores. Extensiones: no inferiores.
 */
(function (root) {
  "use strict";

  var BANDS = ["lt35", "a35", "ge40"];

  var LIMITS = {
    run: {
      hombres: { lt35: 9 * 60 + 25, a35: 9 * 60 + 48, ge40: 10 * 60 + 33 },
      mujeres: { lt35: 11 * 60 + 14, a35: 11 * 60 + 35, ge40: 12 * 60 + 49 }
    },
    circuit: {
      hombres: { lt35: 14.0, a35: 14.4, ge40: 15.1 },
      mujeres: { lt35: 16.0, a35: 16.4, ge40: 17.9 }
    },
    pushups: {
      hombres: { lt35: 16, a35: 16, ge40: 14 },
      mujeres: { lt35: 11, a35: 11, ge40: 9 }
    },
    swim: {
      hombres: { lt35: 70, a35: 71, ge40: 73 },
      mujeres: { lt35: 81, a35: 83, ge40: 88 }
    }
  };

  function toNumber(value, label) {
    if (value === "" || value === null || value === undefined) {
      throw new Error("Indica " + label + ".");
    }
    var n = typeof value === "number" ? value : Number(String(value).trim().replace(",", "."));
    if (!Number.isFinite(n) || n < 0) {
      throw new Error(label + " no es un número válido.");
    }
    return n;
  }

  function toInt(value, label) {
    var n = toNumber(value, label);
    if (!Number.isInteger(n)) {
      throw new Error(label + " debe ser un número entero.");
    }
    return n;
  }

  function sexOf(value) {
    var s = String(value || "").toLowerCase();
    if (s === "hombres" || s === "hombre" || s === "h") return "hombres";
    if (s === "mujeres" || s === "mujer" || s === "m") return "mujeres";
    throw new Error("Indica si haces la tabla de hombres o de mujeres.");
  }

  function bandOf(value) {
    var s = String(value || "");
    if (BANDS.indexOf(s) !== -1) return s;
    throw new Error("Indica tu tramo de edad de la tabla oficial.");
  }

  function timeParts(total) {
    var min = Math.floor(total / 60);
    var sec = Math.round(total - min * 60);
    if (sec === 60) {
      min += 1;
      sec = 0;
    }
    return min + " min " + sec + " s";
  }

  function checkTime(raw, limit, label) {
    var passed = raw <= limit;
    return {
      label: label,
      raw: raw,
      limit: limit,
      passed: passed,
      kind: "max",
      detail: passed
        ? "Dentro del máximo (" + timeParts(limit) + ")."
        : "Superas el máximo de " + timeParts(limit) + "."
    };
  }

  function checkSeconds(raw, limit, label) {
    var passed = raw <= limit;
    var shown = limit.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " s";
    return {
      label: label,
      raw: raw,
      limit: limit,
      passed: passed,
      kind: "max",
      detail: passed ? "Dentro del máximo (" + shown + ")." : "Superas el máximo de " + shown + "."
    };
  }

  function checkMin(raw, limit, label) {
    var passed = raw >= limit;
    return {
      label: label,
      raw: raw,
      limit: limit,
      passed: passed,
      kind: "min",
      detail: passed
        ? "Alcanzas el mínimo (" + limit + ")."
        : "No llegas al mínimo de " + limit + "."
    };
  }

  function evaluate(inputs) {
    var sex = sexOf(inputs.sex);
    var band = bandOf(inputs.band);
    var runMin = toInt(inputs.run_min, "minutos de los 2.000 m");
    var runSec = toInt(inputs.run_sec, "segundos de los 2.000 m");
    if (runSec > 59) {
      throw new Error("Los segundos de la carrera no pueden superar 59.");
    }
    var runTotal = runMin * 60 + runSec;
    var circuit = Math.round((toNumber(inputs.circuit, "tiempo del circuito") + Number.EPSILON) * 100) / 100;
    var pushups = toInt(inputs.pushups, "extensiones de brazos");
    var swim = Math.round((toNumber(inputs.swim, "tiempo de los 50 m") + Number.EPSILON) * 100) / 100;

    var tests = [
      checkTime(runTotal, LIMITS.run[sex][band], "Resistencia 2.000 m (R2)"),
      checkSeconds(circuit, LIMITS.circuit[sex][band], "Circuito de agilidad (C1)"),
      checkMin(pushups, LIMITS.pushups[sex][band], "Extensiones de brazos (P3)"),
      checkSeconds(swim, LIMITS.swim[sex][band], "Natación 50 m (O1)")
    ];
    tests[0].display = timeParts(runTotal);
    tests[1].display = circuit.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " s";
    tests[2].display = String(pushups);
    tests[3].display = swim.toLocaleString("es-ES", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " s";

    var passed = tests.every(function (row) {
      return row.passed;
    });
    return {
      sex: sex,
      band: band,
      tests: tests,
      passed: passed,
      runTotal: runTotal,
      runDisplay: timeParts(runTotal),
      source: "Apéndice II, BOE-A-2026-9982"
    };
  }

  root.NotaOpoGcFisicas = {
    evaluate: evaluate,
    LIMITS: LIMITS
  };
})(typeof window !== "undefined" ? window : globalThis);
