(function (root) {
  "use strict";
  var started = false;
  var KEY = "tunotaopo:events";
  var MAX = 200;

  function load() {
    try {
      var rows = JSON.parse(root.localStorage.getItem(KEY) || "[]");
      return Array.isArray(rows) ? rows : [];
    } catch (ignore) {
      return [];
    }
  }

  function persist(body) {
    try {
      var rows = load();
      rows.push(body);
      if (rows.length > MAX) rows = rows.slice(-MAX);
      root.localStorage.setItem(KEY, JSON.stringify(rows));
    } catch (ignore) {}
    try {
      if (
        root.location &&
        root.location.hostname === "tunotaopo.es" &&
        root.navigator &&
        root.navigator.sendBeacon
      ) {
        root.navigator.sendBeacon("/api/event", JSON.stringify(body));
      }
    } catch (ignoreBeacon) {}
  }

  function track(eventName, payload) {
    var body = payload || {};
    body.event = eventName;
    body.ts = Date.now();
    persist(body);
    if (root.__NOTAOPO_ANALYTICS_DEBUG) {
      console.debug("analytics", body);
    }
  }

  function summary() {
    var rows = load();
    var counts = {};
    var i;
    for (i = 0; i < rows.length; i += 1) {
      var name = rows[i].event || "otro";
      counts[name] = (counts[name] || 0) + 1;
    }
    return { total: rows.length, counts: counts };
  }

  root.NotaOpoAnalytics = {
    track: track,
    summary: summary,
    pageView: function (page) {
      track("page_view", { page: page || location.pathname });
    },
    started: function (slug) {
      if (started) return;
      started = true;
      track("calculator_started", { slug: slug });
    },
    completed: function (slug) {
      track("calculator_completed", { slug: slug });
    },
    shared: function (slug) {
      track("result_shared", { slug: slug });
    },
    officialSourceClicked: function (href) {
      track("official_source_clicked", { href: href });
    }
  };
})(window);
