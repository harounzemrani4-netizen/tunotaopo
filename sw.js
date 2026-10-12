/* TuNotaOpo: cache de CSS, JS y motor. El HTML se pide a la red. */
var CACHE = "tunotaopo-core-20260906aa";
var CORE = [
  "/offline.html",
  "/css/app.css?v=20260906aa",
  "/js/theme-boot.js?v=20260906aa",
  "/js/site.js?v=20260906aa",
  "/js/components/analytics.js?v=20260906aa",
  "/js/components/tools.js?v=20260906aa",
  "/js/engine/scoring.js?v=20260906aa",
  "/js/components/calculator.js?v=20260906aa",
  "/assets/logo.svg"
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(CORE);
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (key) { return key !== CACHE; }).map(function (key) {
          return caches.delete(key);
        })
      );
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (event) {
  var req = event.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.mode === "navigate" || (req.headers.get("accept") || "").indexOf("text/html") !== -1) {
    event.respondWith(
      fetch(req).then(function (res) {
        return res;
      }).catch(function () {
        return caches.match(req).then(function (hit) {
          return hit || caches.match("/offline.html");
        });
      })
    );
    return;
  }
  event.respondWith(
    caches.match(req).then(function (hit) {
      return hit || fetch(req).then(function (res) {
        if (res && res.ok && url.searchParams.get("v") && (url.pathname.indexOf("/js/") === 0 || url.pathname.indexOf("/css/") === 0)) {
          var copy = res.clone();
          caches.open(CACHE).then(function (cache) {
            cache.put(req, copy);
          });
        }
        return res;
      });
    })
  );
});
