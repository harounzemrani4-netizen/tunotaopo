document.addEventListener("DOMContentLoaded", function () {
  if (window.NotaOpoAnalytics) {
    window.NotaOpoAnalytics.pageView();
  }
  var binders = [
    {
      id: "oposicion-config",
      api: "NotaOpoCalculator",
      payload: function (node) {
        return JSON.parse(node.textContent);
      },
    },
    { id: "fisicas-form", api: "NotaOpoFisicasUI" },
    { id: "gc-fisicas-form", api: "NotaOpoGcFisicasUI" },
    { id: "gc-baremo-form", api: "NotaOpoGcBaremoUI" },
    { id: "pl-fisicas-form", api: "NotaOpoPlFisicasUI" },
    { id: "progreso-root", api: "NotaOpoProgreso" },
  ];
  var b;
  for (b = 0; b < binders.length; b += 1) {
    var spec = binders[b];
    var node = document.getElementById(spec.id);
    var api = window[spec.api];
    if (!node || !api || !api.bind) continue;
    if (spec.payload) api.bind(spec.payload(node));
    else api.bind();
  }
  if (window.NotaOpoTools) {
    window.NotaOpoTools.bindClassroom();
    window.NotaOpoTools.bindShare();
  }
  function bindTheme() {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    var meta = document.querySelector('meta[name="theme-color"]');
    function stored() {
      try {
        return localStorage.getItem("tunotaopo:theme") || "";
      } catch (ignore) {
        return "";
      }
    }
    function apply(theme) {
      if (theme === "dark" || theme === "light") {
        document.documentElement.setAttribute("data-theme", theme);
        try {
          localStorage.setItem("tunotaopo:theme", theme);
        } catch (ignoreSet) {}
      } else {
        document.documentElement.removeAttribute("data-theme");
        try {
          localStorage.removeItem("tunotaopo:theme");
        } catch (ignoreDel) {}
      }
      if (meta) {
        meta.setAttribute("content", theme === "light" ? "#eef2f5" : "#0c1924");
      }
      var next = theme === "dark" ? "claro" : theme === "light" ? "automático" : "oscuro";
      btn.setAttribute("aria-label", "Cambiar a modo " + next);
      btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
      btn.setAttribute("data-theme-state", theme || "system");
    }
    apply(stored());
    btn.addEventListener("click", function () {
      var now = stored();
      if (!now) apply("dark");
      else if (now === "dark") apply("light");
      else apply("");
    });
  }
  bindTheme();
  function bindCrumbs() {
    var ol = document.querySelector(".crumbs ol");
    if (!ol || ol.children.length <= 4) return;
    var items = ol.children;
    var i;
    for (i = 2; i < items.length - 1; i += 1) {
      items[i].classList.add("crumb-collapsed");
    }
    var more = document.createElement("li");
    more.className = "crumb-more";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "crumb-more-btn";
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", "Mostrar todas las migas");
    btn.textContent = "…";
    more.appendChild(btn);
    ol.insertBefore(more, items[2]);
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      var next = !open;
      btn.setAttribute("aria-expanded", next ? "true" : "false");
      var nodes = ol.querySelectorAll(".crumb-collapsed");
      var j;
      for (j = 0; j < nodes.length; j += 1) {
        nodes[j].classList.toggle("is-open", next);
      }
      more.hidden = next;
    });
  }
  bindCrumbs();
  function normalize(value) {
    return String(value || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }
  function fold(value) {
    return normalize(value).replace(/[^a-z0-9]+/g, " ").trim();
  }
  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  function tokensMatch(hay, needle) {
    if (!needle) return true;
    if (hay.indexOf(needle) !== -1) return true;
    var tokens = needle.split(" ");
    var i;
    for (i = 0; i < tokens.length; i += 1) {
      if (tokens[i] && hay.indexOf(tokens[i]) === -1) return false;
    }
    return tokens.length > 0;
  }
  function scrollOptionIntoList(list, opt) {
    if (!list || !opt) return;
    var top = opt.offsetTop;
    var bottom = top + opt.offsetHeight;
    if (top < list.scrollTop) list.scrollTop = top;
    else if (bottom > list.scrollTop + list.clientHeight) {
      list.scrollTop = bottom - list.clientHeight;
    }
  }
  function scoreOpo(item, needle) {
    var name = fold(item.name);
    var aliases = fold(item.aliases);
    var hay = (name + " " + aliases).replace(/\s+/g, " ");
    var q = fold(needle);
    if (!q) return 1;
    if (aliases.split(" ").indexOf(q) !== -1) return 100;
    if (name.indexOf(q) === 0) return 80;
    if (hay.indexOf(q) !== -1) return 50;
    var tokens = q.split(" ");
    var i;
    for (i = 0; i < tokens.length; i += 1) {
      if (hay.indexOf(tokens[i]) === -1) return 0;
    }
    return 30;
  }
  function bindOpoSuggest() {
    var search = document.getElementById("opo-search");
    var list = document.getElementById("opo-suggest-list");
    var catalog = document.getElementById("opo-catalog");
    if (!search || !list) return;
    var items = [];
    var cards = catalog ? catalog.querySelectorAll(".catalog-card") : [];
    var i;
    for (i = 0; i < cards.length; i += 1) {
      var heading = cards[i].querySelector("h2");
      items.push({
        name: heading ? heading.textContent.trim() : cards[i].textContent.trim(),
        href: cards[i].getAttribute("href") || "/oposiciones/",
        aliases: cards[i].getAttribute("data-aliases") || "",
        hint: ((cards[i].querySelector(".card-kind") || {}).textContent || "").trim(),
        card: cards[i],
        order: i,
      });
    }
    var active = -1;
    var open = false;
    function setExpanded(value) {
      open = value;
      search.setAttribute("aria-expanded", value ? "true" : "false");
      list.hidden = !value;
    }
    function filterCatalog(needle) {
      if (!catalog) return;
      var visible = 0;
      for (i = 0; i < items.length; i += 1) {
        var keep = !needle || scoreOpo(items[i], needle) > 0;
        if (items[i].card) items[i].card.hidden = !keep;
        if (keep) visible += 1;
      }
      var empty = document.getElementById("opo-search-empty");
      if (empty) empty.hidden = !needle || visible > 0;
    }
    function paint(needle, showAll) {
      var q = fold(needle);
      var hits = items
        .map(function (item) {
          return { item: item, score: scoreOpo(item, needle) };
        })
        .filter(function (row) {
          return showAll || !q ? row.score > 0 : row.score > 0;
        });
      if (!q && !showAll) {
        list.innerHTML = "";
        setExpanded(false);
        var emptyNode = document.getElementById("opo-suggest-empty");
        if (emptyNode) emptyNode.hidden = true;
        filterCatalog("");
        return;
      }
      hits.sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        if (!q) return a.item.order - b.item.order;
        return a.item.name.localeCompare(b.item.name, "es");
      });
      list.innerHTML = hits
        .map(function (row, index) {
          return (
            '<li role="option" id="opo-opt-' +
            index +
            '" data-index="' +
            index +
            '"><a href="' +
            escapeHtml(row.item.href) +
            '"><strong>' +
            escapeHtml(row.item.name) +
            "</strong><span>" +
            escapeHtml(row.item.hint || "Abrir oposición") +
            "</span></a></li>"
          );
        })
        .join("");
      var empty = document.getElementById("opo-suggest-empty");
      if (empty) empty.hidden = hits.length > 0;
      setExpanded(hits.length > 0);
      active = hits.length ? 0 : -1;
      markActive();
      filterCatalog(needle);
      list._hits = hits;
    }
    function markActive() {
      var opts = list.querySelectorAll('[role="option"]');
      var j;
      for (j = 0; j < opts.length; j += 1) {
        opts[j].setAttribute("aria-selected", j === active ? "true" : "false");
      }
      search.setAttribute("aria-activedescendant", active >= 0 ? "opo-opt-" + active : "");
      if (active >= 0) scrollOptionIntoList(list, opts[active]);
    }
    function goActive() {
      var hits = list._hits || [];
      if (active >= 0 && hits[active]) {
        window.location.href = hits[active].item.href;
        return true;
      }
      if (hits.length === 1) {
        window.location.href = hits[0].item.href;
        return true;
      }
      return false;
    }
    var initial = String(new URLSearchParams(window.location.search).get("q") || "");
    if (initial && !search.value) search.value = initial;
    if (initial) paint(initial, false);
    search.addEventListener("focus", function () {
      paint(search.value, true);
    });
    search.addEventListener("input", function () {
      paint(search.value, true);
    });
    search.addEventListener("keydown", function (ev) {
      var hits = list._hits || [];
      if (ev.key === "ArrowDown") {
        ev.preventDefault();
        if (!open) paint(search.value, true);
        if (hits.length) {
          active = (active + 1) % hits.length;
          markActive();
        }
      } else if (ev.key === "ArrowUp") {
        ev.preventDefault();
        if (hits.length) {
          active = (active - 1 + hits.length) % hits.length;
          markActive();
        }
      } else if (ev.key === "Enter") {
        ev.preventDefault();
        if (!goActive()) paint(search.value, true);
      } else if (ev.key === "Escape") {
        setExpanded(false);
        search.removeAttribute("aria-activedescendant");
      }
    });
    if (search.form) {
      search.form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        if (!goActive()) paint(search.value, true);
      });
    }
    var wrap = search.closest(".opo-suggest");
    document.addEventListener("pointerdown", function (ev) {
      if (wrap && wrap.contains(ev.target)) return;
      setExpanded(false);
    });
  }
  bindOpoSuggest();

  function bindPlSearch() {
    var input = document.getElementById("pl-search");
    var out = document.getElementById("pl-search-results");
    var empty = document.getElementById("pl-search-empty");
    if (!input || !out) return;
    var items = null;
    var scope = input.getAttribute("data-pl-scope") || "";
    var active = -1;
    var hits = [];
    function setOpen(open) {
      out.hidden = !open;
      input.setAttribute("aria-expanded", open ? "true" : "false");
    }
    function markActive() {
      var opts = out.querySelectorAll('[role="option"]');
      var j;
      for (j = 0; j < opts.length; j += 1) {
        opts[j].setAttribute("aria-selected", j === active ? "true" : "false");
      }
      input.setAttribute("aria-activedescendant", active >= 0 ? "pl-opt-" + active : "");
      if (active >= 0) scrollOptionIntoList(out, opts[active]);
    }
    function goActive() {
      if (active >= 0 && hits[active]) {
        window.location.href = "/" + hits[active][3];
        return true;
      }
      if (hits.length === 1) {
        window.location.href = "/" + hits[0][3];
        return true;
      }
      return false;
    }
    function scorePl(row, needle) {
      var name = fold(row[1]);
      var hay = fold(row[1] + " " + row[2] + " " + row[3]);
      if (!needle) return 1;
      if (name === needle) return 100;
      if (name.indexOf(needle) === 0) return 90;
      if (name.indexOf(needle) !== -1) return 70;
      if (tokensMatch(name, needle)) return 60;
      if (hay.indexOf(needle) !== -1) return 30;
      if (tokensMatch(hay, needle)) return 15;
      return 0;
    }
    function render(needle) {
      if (!items) return;
      if (!needle) {
        out.innerHTML = "";
        setOpen(false);
        if (empty) empty.hidden = true;
        active = -1;
        hits = [];
        return;
      }
      var ranked = [];
      var i;
      for (i = 0; i < items.length; i += 1) {
        var row = items[i];
        if (scope && String(row[3]).indexOf(scope) !== 0) continue;
        var score = scorePl(row, needle);
        if (score <= 0) continue;
        ranked.push({ row: row, score: score });
      }
      ranked.sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        return String(a.row[1]).localeCompare(b.row[1], "es");
      });
      hits = ranked.slice(0, 30).map(function (item) {
        return item.row;
      });
      out.innerHTML = hits
        .map(function (row, index) {
          var flag = row[4] ? " · Calculadora publicada" : "";
          return (
            '<a role="option" id="pl-opt-' +
            index +
            '" href="/' +
            escapeHtml(row[3]) +
            '"><strong>' +
            escapeHtml(row[1]) +
            "</strong><span>" +
            escapeHtml(row[2] + flag) +
            "</span></a>"
          );
        })
        .join("");
      setOpen(hits.length > 0);
      if (empty) empty.hidden = hits.length > 0;
      active = hits.length ? 0 : -1;
      markActive();
    }
    fetch("/js/data/pl-municipios.json")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        items = data.items || [];
        var initial = new URLSearchParams(window.location.search).get("q") || "";
        if (initial && !input.value) input.value = initial;
        render(fold(input.value));
      })
      .catch(function () {
        items = [];
      });
    input.addEventListener("focus", function () {
      if (fold(input.value)) render(fold(input.value));
    });
    input.addEventListener("input", function () {
      render(fold(input.value));
    });
    input.addEventListener("keydown", function (ev) {
      if (ev.key === "ArrowDown") {
        ev.preventDefault();
        if (out.hidden) render(fold(input.value));
        if (hits.length) {
          active = (active + 1) % hits.length;
          markActive();
        }
      } else if (ev.key === "ArrowUp") {
        ev.preventDefault();
        if (hits.length) {
          active = (active - 1 + hits.length) % hits.length;
          markActive();
        }
      } else if (ev.key === "Enter") {
        ev.preventDefault();
        if (!goActive()) render(fold(input.value));
      } else if (ev.key === "Escape") {
        setOpen(false);
        input.removeAttribute("aria-activedescendant");
      }
    });
    if (input.form) {
      input.form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        if (!goActive()) render(fold(input.value));
      });
    }
    var wrap = input.closest(".pl-search-wrap") || input.closest(".pl-search");
    document.addEventListener("pointerdown", function (ev) {
      if (wrap && wrap.contains(ev.target)) return;
      setOpen(false);
    });
  }
  bindPlSearch();
  var listFilter = document.getElementById("pl-list-filter");
  var muniList = document.getElementById("pl-muni-list");
  if (listFilter && muniList) {
    listFilter.addEventListener("input", function () {
      var needle = fold(listFilter.value);
      var rows = muniList.querySelectorAll("li");
      var visible = 0;
      var i;
      for (i = 0; i < rows.length; i += 1) {
        var match = !needle || tokensMatch(fold(rows[i].textContent), needle);
        rows[i].hidden = !match;
        if (match) visible += 1;
      }
      var empty = document.getElementById("pl-list-empty");
      if (empty) empty.hidden = !needle || visible > 0;
    });
  }
  if ("serviceWorker" in navigator) {
    var host = location.hostname;
    var allowSw = location.protocol === "https:" || host === "localhost" || host === "127.0.0.1";
    if (allowSw) {
      var assetMeta = document.querySelector('meta[name="asset-v"]');
      var ver = assetMeta ? assetMeta.getAttribute("content") : "";
      var swUrl = ver ? "/sw.js?v=" + encodeURIComponent(ver) : "/sw.js";
      navigator.serviceWorker.register(swUrl).catch(function () {});
    }
  }
});
