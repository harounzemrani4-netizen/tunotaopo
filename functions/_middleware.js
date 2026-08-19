export function onRequest(context) {
  var url = new URL(context.request.url);
  var path = url.pathname;
  if (path === "/progreso" || path === "/progreso/" || path.indexOf("/progreso/") === 0) {
    url.pathname = "/oposiciones/progreso/";
    url.search = "";
    return Response.redirect(url.toString(), 301);
  }
  if (path === "/academias" || path === "/academias/" || path === "/academias/index.html") {
    url.pathname = "/oposiciones/academias/";
    url.search = "";
    return Response.redirect(url.toString(), 301);
  }
  return context.next();
}
