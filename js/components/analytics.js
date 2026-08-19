(function (root) {
  "use strict";
  var started = false;

  function track(eventName, payload) {
    var body = payload || {};
    body.event = eventName;
    body.ts = Date.now();
    if (root.__NOTAOPO_ANALYTICS_DEBUG) {
      console.debug("analytics", body);
    }
  }

  root.NotaOpoAnalytics = {
    track: track,
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
