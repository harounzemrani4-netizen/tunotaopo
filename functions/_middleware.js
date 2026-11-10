var FAMILIES = ["policia-nacional", "guardia-civil", "auxiliar-age", "auxilio-judicial", "ayudantes-iipp", "policia-local"];
var MERGED_SECTIONS = ["requisitos", "fechas", "notas-corte", "examenes-oficiales"];
var PL_PAGES = ["pruebas", "pruebas-fisicas", "temario"];

function moved(url, pathname, hash) {
  url.pathname = pathname;
  url.search = "";
  url.hash = hash || "";
  return Response.redirect(url.toString(), 301);
}

function gone() {
  return new Response(
    '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>Página retirada · TuNotaOpo</title></head>' +
      '<body><h1>Esta página ya no existe</h1><p>Solo publicamos calculadoras con boletín oficial. <a href="/oposiciones/policia-local/">Policía Local de Madrid</a> · <a href="/">Inicio</a></p></body></html>',
    { status: 410, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=3600" } }
  );
}

export function onRequest(context) {
  var url = new URL(context.request.url);
  var path = url.pathname;
  if (path === "/progreso" || path === "/progreso/" || path.indexOf("/progreso/") === 0) {
    return moved(url, "/oposiciones/progreso/");
  }
  if (path === "/academias" || path === "/academias/" || path === "/academias/index.html") {
    return moved(url, "/oposiciones/academias/");
  }
  var parts = path.split("/").filter(Boolean);
  if (parts[0] === "oposiciones" && FAMILIES.indexOf(parts[1]) !== -1 && parts.length >= 3) {
    var section = parts[2];
    if (MERGED_SECTIONS.indexOf(section) !== -1) {
      return moved(url, "/oposiciones/" + parts[1] + "/", section);
    }
    if (parts[1] === "policia-local" && PL_PAGES.indexOf(section) === -1 && section !== "index.html") {
      if (section === "comunidad-de-madrid") {
        if (parts[3] === "madrid" && parts[4] === "madrid") return moved(url, "/calculadoras/policia-local/");
        return moved(url, "/oposiciones/policia-local/");
      }
      return gone();
    }
  }
  return context.next();
}
