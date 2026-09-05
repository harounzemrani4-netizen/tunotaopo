/**
 * Policía Municipal de Madrid — físicas (Anexo II, BOAM núm. 9829).
 * Marcas literales. Entre marcas: interpolación del anterior y posterior.
 * Mínimo 5 en cada prueba. La media solo vale si las cinco llegan a 5.
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

  function round2(value) {
    return Math.round((value + Number.EPSILON) * 100) / 100;
  }

  function interpolate(value, points, higherIsBetter) {
    var first = points[0];
    var last = points[points.length - 1];
    if (higherIsBetter) {
      if (value >= last.mark) return { score: last.score, passed: true, interpolated: value > last.mark ? false : value !== last.mark };
      if (value < first.mark) return { score: null, passed: false, interpolated: false };
    } else {
      if (value <= last.mark) return { score: last.score, passed: true, interpolated: value < last.mark ? false : value !== last.mark };
      if (value > first.mark) return { score: null, passed: false, interpolated: false };
    }
    var i;
    for (i = 0; i < points.length - 1; i += 1) {
      var a = points[i];
      var b = points[i + 1];
      var inRange = higherIsBetter
        ? value >= a.mark && value <= b.mark
        : value <= a.mark && value >= b.mark;
      if (!inRange) continue;
      if (value === a.mark) return { score: a.score, passed: a.score >= 5, interpolated: false };
      if (value === b.mark) return { score: b.score, passed: b.score >= 5, interpolated: false };
      var span = b.mark - a.mark;
      if (span === 0) return { score: a.score, passed: a.score >= 5, interpolated: false };
      var raw = a.score + ((value - a.mark) / span) * (b.score - a.score);
      var score = round2(raw);
      return { score: score, passed: score >= 5, interpolated: true };
    }
    return { score: null, passed: false, interpolated: false };
  }

  var TABLES = {
    run800: {
      higher: false,
      unit: "s",
      hombres: [
        { score: 5, mark: 170 },
        { score: 6, mark: 159 },
        { score: 7, mark: 148 },
        { score: 8, mark: 137 },
        { score: 9, mark: 126 },
        { score: 10, mark: 115 }
      ],
      mujeres: [
        { score: 5, mark: 210 },
        { score: 6, mark: 199 },
        { score: 7, mark: 188 },
        { score: 8, mark: 177 },
        { score: 9, mark: 166 },
        { score: 10, mark: 155 }
      ]
    },
    run60: {
      higher: false,
      unit: "s",
      hombres: [
        { score: 5, mark: 9.1 },
        { score: 6, mark: 8.68 },
        { score: 7, mark: 8.26 },
        { score: 8, mark: 7.84 },
        { score: 9, mark: 7.42 },
        { score: 10, mark: 7 }
      ],
      mujeres: [
        { score: 5, mark: 10.4 },
        { score: 6, mark: 9.98 },
        { score: 7, mark: 9.56 },
        { score: 8, mark: 9.14 },
        { score: 9, mark: 8.72 },
        { score: 10, mark: 8.3 }
      ]
    },
    ball: {
      higher: true,
      unit: "m",
      hombres: [
        { score: 5, mark: 5.5 },
        { score: 6, mark: 6.5 },
        { score: 7, mark: 7.5 },
        { score: 8, mark: 8.5 },
        { score: 9, mark: 9.5 },
        { score: 10, mark: 10.5 }
      ],
      mujeres: [
        { score: 5, mark: 5.5 },
        { score: 6, mark: 6.5 },
        { score: 7, mark: 7.5 },
        { score: 8, mark: 8.5 },
        { score: 9, mark: 9.5 },
        { score: 10, mark: 10.5 }
      ]
    },
    jump: {
      higher: true,
      unit: "m",
      hombres: [
        { score: 5, mark: 2.15 },
        { score: 6, mark: 2.35 },
        { score: 7, mark: 2.55 },
        { score: 8, mark: 2.75 },
        { score: 9, mark: 2.95 },
        { score: 10, mark: 3.15 }
      ],
      mujeres: [
        { score: 5, mark: 1.85 },
        { score: 6, mark: 2.05 },
        { score: 7, mark: 2.25 },
        { score: 8, mark: 2.45 },
        { score: 9, mark: 2.65 },
        { score: 10, mark: 2.85 }
      ]
    },
    swim: {
      higher: false,
      unit: "s",
      hombres: [
        { score: 5, mark: 24 },
        { score: 6, mark: 21.2 },
        { score: 7, mark: 18.4 },
        { score: 8, mark: 15.6 },
        { score: 9, mark: 12.8 },
        { score: 10, mark: 10 }
      ],
      mujeres: [
        { score: 5, mark: 26 },
        { score: 6, mark: 23.2 },
        { score: 7, mark: 20.4 },
        { score: 8, mark: 17.6 },
        { score: 9, mark: 14.8 },
        { score: 10, mark: 12 }
      ]
    }
  };

  function scoreEvent(table, sex, value) {
    var points = table[sex];
    if (!points) throw new Error("Indica el sexo de la tabla.");
    var packed = interpolate(value, points, table.higher);
    return {
      raw: value,
      score: packed.score,
      passed: packed.passed,
      interpolated: packed.interpolated,
      minimumMark: points[0].mark
    };
  }

  function clock(totalSec) {
    var minutes = Math.floor(totalSec / 60);
    var seconds = Math.round((totalSec - minutes * 60) * 100) / 100;
    if (seconds >= 60) {
      minutes += 1;
      seconds = 0;
    }
    var secLabel = seconds % 1 === 0 ? String(seconds) : String(seconds).replace(".", ",");
    return minutes + ":" + (seconds < 10 ? "0" : "") + secLabel;
  }

  function evaluate(inputs) {
    var sex = inputs.sex === "mujeres" ? "mujeres" : "hombres";
    var min800 = toNumber(inputs.run800_min, "minutos de los 800 m");
    var sec800 = toNumber(inputs.run800_sec, "segundos de los 800 m");
    if (sec800 >= 60) throw new Error("Los segundos de los 800 m deben ser menores de 60.");
    var run800 = min800 * 60 + sec800;
    var run60 = toNumber(inputs.run60, "tiempo de los 60 m");
    var ball = toNumber(inputs.ball, "lanzamiento de balón");
    var jump = toNumber(inputs.jump, "salto de longitud");
    var swim = toNumber(inputs.swim, "tiempo de natación");

    var events = {
      run800: scoreEvent(TABLES.run800, sex, run800),
      run60: scoreEvent(TABLES.run60, sex, run60),
      ball: scoreEvent(TABLES.ball, sex, ball),
      jump: scoreEvent(TABLES.jump, sex, jump),
      swim: scoreEvent(TABLES.swim, sex, swim)
    };
    events.run800.display = clock(run800);
    events.ball.weight = sex === "mujeres" ? "3 kg" : "5 kg";

    var ids = ["run800", "run60", "ball", "jump", "swim"];
    var allPassed = ids.every(function (id) { return events[id].passed; });
    var average = null;
    if (allPassed) {
      var sum = ids.reduce(function (total, id) { return total + events[id].score; }, 0);
      average = round2(sum / ids.length);
    }

    return {
      sex: sex,
      events: events,
      average: average,
      passed: allPassed
    };
  }

  root.NotaOpoPlFisicas = {
    evaluate: evaluate,
    TABLES: TABLES
  };
})(typeof window !== "undefined" ? window : globalThis);
