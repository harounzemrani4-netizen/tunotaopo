/**
 * Guardia Civil — concurso (Apéndice I, BOE-A-2026-9982).
 * Topes: profesionales 13,5 · académicos 27 · otros 4,5 · total 45.
 * Solo méritos del apéndice. No inventa puntos de títulos no listados.
 */
(function (root) {
  "use strict";

  var LANGS = ["aleman", "arabe", "frances", "ingles", "italiano", "portugues", "ruso"];
  var LEVEL_PTS = { b2: 5, c1: 7, c2: 9 };
  var DAN_PTS = { A: 0.35, B: 0.25, C: 0.2 };

  function round3(value) {
    return Math.round((value + Number.EPSILON) * 1000) / 1000;
  }

  function toNumber(value, label, allowEmpty) {
    if (value === "" || value === null || value === undefined) {
      if (allowEmpty) return 0;
      throw new Error("Indica " + label + ".");
    }
    var n = typeof value === "number" ? value : Number(String(value).trim().replace(",", "."));
    if (!Number.isFinite(n) || n < 0) {
      throw new Error(label + " no es un número válido.");
    }
    return n;
  }

  function toInt(value, label, allowEmpty) {
    var n = toNumber(value, label, allowEmpty);
    if (n === 0 && allowEmpty && (value === "" || value === null || value === undefined)) return 0;
    if (!Number.isInteger(n)) {
      throw new Error(label + " debe ser un número entero.");
    }
    return n;
  }

  function cap(value, maximum) {
    return value > maximum ? maximum : value;
  }

  function professional(input) {
    var turno = String(input.turno || "");
    var items = [];
    var raw = 0;
    if (turno === "tropa") {
      var years = toInt(input.tropa_years, "años como tropa y marinería", true);
      var tropaPts = cap(years * 0.9, 9);
      raw += tropaPts;
      items.push({
        id: "tropa_years",
        label: "Años de tropa y marinería (0,90 / año, tope 9)",
        points: round3(tropaPts)
      });
      var rank = String(input.tropa_rank || "none");
      var rankPts = 0;
      var rankLabel = "Sin empleo de cabo";
      if (rank === "cabo") {
        rankPts = 2.4;
        rankLabel = "Cabo";
      } else if (rank === "cabo1") {
        rankPts = 3.6;
        rankLabel = "Cabo 1.º";
      }
      raw += rankPts;
      items.push({ id: "tropa_rank", label: "Empleo máximo (" + rankLabel + ")", points: rankPts });
    } else if (turno === "libre" || turno === "colegio") {
      var ageYears = toInt(input.age_years, "años en la AGE (incluido el tiempo militar)", true);
      var agePts = ageYears * 0.9;
      raw += agePts;
      items.push({
        id: "age_years",
        label: "Años en la AGE, incluido el tiempo militar (0,90 / año)",
        points: round3(agePts)
      });
      var months = toInt(input.reservist_months, "meses como reservista voluntario", true);
      var resPts = months * 0.025;
      raw += resPts;
      items.push({
        id: "reservist",
        label: "Reservista voluntario (0,025 / mes)",
        points: round3(resPts)
      });
    } else {
      throw new Error("Indica el turno: libre, tropa o Colegio de Guardias Jóvenes.");
    }
    var capped = round3(cap(raw, 13.5));
    return { raw: round3(raw), points: capped, cap: 13.5, items: items };
  }

  function academic(input) {
    var items = [];
    var raw = 0;
    var academicKind = String(input.academic || "none");
    var degreeLang = String(input.degree_lang || "");
    if (academicKind === "bachiller") {
      raw += 2;
      items.push({
        id: "nivel",
        label: "Bachiller LOE o titulación superior (MECES 1 a 4)",
        points: 2
      });
    } else if (academicKind === "filologia") {
      if (LANGS.indexOf(degreeLang) === -1) {
        throw new Error("Indica el idioma de la titulación de Filología o Traducción.");
      }
      raw += 9;
      items.push({
        id: "filologia",
        label: "Filología / Traducción e Interpretación (idioma B). No se suma el punto 2.1.",
        points: 9
      });
    }

    var used = {};
    if (academicKind === "filologia") used[degreeLang] = 9;

    var langs = input.languages || [];
    langs.forEach(function (row) {
      if (!row || !row.lang || !row.level) return;
      var lang = String(row.lang);
      var level = String(row.level);
      var via = String(row.via || "otro");
      if (LANGS.indexOf(lang) === -1) return;
      if (!LEVEL_PTS[level]) return;
      if (via === "slp" && !input.fas) {
        throw new Error("El perfil SLP solo lo pueden invocar quienes pertenezcan o hayan pertenecido a las Fuerzas Armadas.");
      }
      var pts = LEVEL_PTS[level];
      if (used[lang] != null) {
        if (pts > used[lang]) {
          raw += pts - used[lang];
          used[lang] = pts;
        }
        return;
      }
      used[lang] = pts;
      raw += pts;
      items.push({
        id: "lang-" + lang,
        label: "Idioma " + lang + " (" + level.toUpperCase() + ")",
        points: pts
      });
    });

    if (academicKind === "filologia" && !items.some(function (row) { return row.id === "filologia"; })) {
      items.push({ id: "filologia", label: "Titulación de idioma", points: 9 });
    }

    var capped = round3(cap(raw, 27));
    return { raw: round3(raw), points: capped, cap: 27, items: items };
  }

  function other(input) {
    var items = [];
    var raw = 0;
    if (input.perm_a) {
      raw += 3;
      items.push({ id: "perm_a", label: "Permiso A o A2", points: 3 });
    }
    if (input.perm_ce) {
      raw += 3;
      items.push({ id: "perm_ce", label: "Permiso C+E o D+E", points: 3 });
    }
    if (input.perm_c) {
      raw += 2;
      items.push({ id: "perm_c", label: "Permiso C1, C, C1+E, D1, D o D1+E", points: 2 });
    }
    var group = String(input.dan_group || "none");
    var years = toInt(input.dan_years, "años como deportista de alto nivel", true);
    if (group !== "none" && DAN_PTS[group]) {
      if (years > 5) {
        throw new Error("Solo se computan los últimos cinco años como deportista de alto nivel.");
      }
      var danPts = round3(years * DAN_PTS[group]);
      raw += danPts;
      items.push({
        id: "dan",
        label: "Deportista de alto nivel grupo " + group + " (" + String(DAN_PTS[group]).replace(".", ",") + " / año)",
        points: danPts
      });
    }
    var capped = round3(cap(raw, 4.5));
    return { raw: round3(raw), points: capped, cap: 4.5, items: items };
  }

  function evaluate(input) {
    var prof = professional(input);
    var acad = academic(input);
    var rest = other(input);
    var sum = round3(prof.points + acad.points + rest.points);
    var total = round3(cap(sum, 45));
    return {
      professional: prof,
      academic: acad,
      other: rest,
      sum: sum,
      total: total,
      capped: sum > 45,
      source: "Apéndice I, BOE-A-2026-9982"
    };
  }

  root.NotaOpoGcBaremo = {
    evaluate: evaluate,
    LANGS: LANGS,
    LEVEL_PTS: LEVEL_PTS
  };
})(typeof window !== "undefined" ? window : globalThis);
