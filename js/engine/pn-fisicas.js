/**
 * Policía Nacional Escala Básica — aptitud física (Anexo II, BOE-A-2026-15055).
 * Tablas literales del boletín. 0 en un ejercicio elimina. Media ≥ 5 para aprobar.
 */
(function (root) {
  "use strict";

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

  function round1(value) {
    return Math.round((value + Number.EPSILON) * 10) / 10;
  }

  function scoreFromRanges(value, ranges) {
    var i;
    for (i = 0; i < ranges.length; i += 1) {
      var row = ranges[i];
      var minOk = row.min === null || value >= row.min;
      var maxOk = row.max === null || value <= row.max;
      if (minOk && maxOk) return row.score;
    }
    return 0;
  }

  /* Circuito: menos tiempo, más puntos. Tiempos en segundos (1 decimal). */
  var CIRCUIT = {
    hombres: [
      { min: 11.7, max: null, score: 0 },
      { min: 11.5, max: 11.6, score: 1 },
      { min: 11.3, max: 11.4, score: 2 },
      { min: 11.0, max: 11.2, score: 3 },
      { min: 10.6, max: 10.9, score: 4 },
      { min: 10.2, max: 10.5, score: 5 },
      { min: 9.8, max: 10.1, score: 6 },
      { min: 9.4, max: 9.7, score: 7 },
      { min: 8.9, max: 9.3, score: 8 },
      { min: 8.3, max: 8.8, score: 9 },
      { min: null, max: 8.2, score: 10 }
    ],
    mujeres: [
      { min: 12.8, max: null, score: 0 },
      { min: 12.6, max: 12.7, score: 1 },
      { min: 12.4, max: 12.5, score: 2 },
      { min: 12.1, max: 12.3, score: 3 },
      { min: 11.7, max: 12.0, score: 4 },
      { min: 11.3, max: 11.6, score: 5 },
      { min: 10.9, max: 11.2, score: 6 },
      { min: 10.4, max: 10.8, score: 7 },
      { min: 9.9, max: 10.3, score: 8 },
      { min: 9.4, max: 9.8, score: 9 },
      { min: null, max: 9.3, score: 10 }
    ]
  };

  var PULLUPS_MEN = [
    { min: 0, max: 4, score: 0 },
    { min: 5, max: 5, score: 1 },
    { min: 6, max: 6, score: 2 },
    { min: 7, max: 7, score: 3 },
    { min: 8, max: 9, score: 4 },
    { min: 10, max: 11, score: 5 },
    { min: 12, max: 13, score: 6 },
    { min: 14, max: 14, score: 7 },
    { min: 15, max: 15, score: 8 },
    { min: 16, max: 16, score: 9 },
    { min: 17, max: null, score: 10 }
  ];

  var HANG_WOMEN = [
    { min: null, max: 35, score: 0 },
    { min: 36, max: 40, score: 1 },
    { min: 41, max: 45, score: 2 },
    { min: 46, max: 51, score: 3 },
    { min: 52, max: 56, score: 4 },
    { min: 57, max: 62, score: 5 },
    { min: 63, max: 69, score: 6 },
    { min: 70, max: 77, score: 7 },
    { min: 78, max: 85, score: 8 },
    { min: 86, max: 94, score: 9 },
    { min: 95, max: null, score: 10 }
  ];

  /* 1000 m: más tiempo, menos puntos. Valor en segundos. */
  var RUN = {
    hombres: [
      { min: 229, max: null, score: 0 },
      { min: 223, max: 228, score: 1 },
      { min: 217, max: 222, score: 2 },
      { min: 211, max: 216, score: 3 },
      { min: 205, max: 210, score: 4 },
      { min: 199, max: 204, score: 5 },
      { min: 193, max: 198, score: 6 },
      { min: 187, max: 192, score: 7 },
      { min: 181, max: 186, score: 8 },
      { min: 175, max: 180, score: 9 },
      { min: null, max: 174, score: 10 }
    ],
    mujeres: [
      { min: 286, max: null, score: 0 },
      { min: 277, max: 285, score: 1 },
      { min: 268, max: 276, score: 2 },
      { min: 259, max: 267, score: 3 },
      { min: 250, max: 258, score: 4 },
      { min: 241, max: 249, score: 5 },
      { min: 232, max: 240, score: 6 },
      { min: 223, max: 231, score: 7 },
      { min: 214, max: 222, score: 8 },
      { min: 205, max: 213, score: 9 },
      { min: null, max: 204, score: 10 }
    ]
  };

  function sexOf(value) {
    var s = String(value || "").toLowerCase();
    if (s === "hombres" || s === "hombre" || s === "m") return "hombres";
    if (s === "mujeres" || s === "mujer" || s === "f") return "mujeres";
    throw new Error("Indica si haces la tabla de hombres o de mujeres.");
  }

  function evaluate(inputs) {
    var sex = sexOf(inputs.sex);
    var circuit = round1(toNumber(inputs.circuit, "tiempo del circuito"));
    var runMin = toInt(inputs.run_min, "minutos de los 1.000 m");
    var runSec = toInt(inputs.run_sec, "segundos de los 1.000 m");
    if (runSec > 59) {
      throw new Error("Los segundos de la carrera no pueden superar 59.");
    }
    var runTotal = runMin * 60 + runSec;
    var forceScore;
    var forceLabel;
    var forceRaw;
    if (sex === "hombres") {
      forceRaw = toInt(inputs.pullups, "dominadas");
      forceScore = scoreFromRanges(forceRaw, PULLUPS_MEN);
      forceLabel = "Dominadas";
    } else {
      forceRaw = toInt(inputs.hang, "segundos de suspensión");
      forceScore = scoreFromRanges(forceRaw, HANG_WOMEN);
      forceLabel = "Suspensión en barra";
    }
    var circuitScore = scoreFromRanges(circuit, CIRCUIT[sex]);
    var runScore = scoreFromRanges(runTotal, RUN[sex]);
    var zeroOut = circuitScore === 0 || forceScore === 0 || runScore === 0;
    var average = Math.round(((circuitScore + forceScore + runScore) / 3 + Number.EPSILON) * 100) / 100;
    var passed = !zeroOut && average >= 5;
    return {
      sex: sex,
      circuit: { raw: circuit, score: circuitScore, label: "Circuito de agilidad" },
      force: { raw: forceRaw, score: forceScore, label: forceLabel },
      run: { raw: runTotal, display: runMin + " min " + runSec + " s", score: runScore, label: "1.000 metros" },
      average: average,
      zeroOut: zeroOut,
      passed: passed,
      source: "Anexo II, BOE-A-2026-15055"
    };
  }

  root.NotaOpoFisicas = {
    evaluate: evaluate,
    scoreFromRanges: scoreFromRanges,
    tables: { CIRCUIT: CIRCUIT, PULLUPS_MEN: PULLUPS_MEN, HANG_WOMEN: HANG_WOMEN, RUN: RUN }
  };
})(typeof window !== "undefined" ? window : globalThis);
