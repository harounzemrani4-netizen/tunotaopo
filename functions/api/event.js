/** Recibe un evento de uso same-origin. No guarda PII. Sin KV, solo 204. */
function sameOrigin(req) {
  var url;
  try {
    url = new URL(req.url);
  } catch (ignore) {
    return false;
  }
  var origin = req.headers.get("Origin") || "";
  var referer = req.headers.get("Referer") || "";
  if (origin) {
    try {
      return new URL(origin).origin === url.origin;
    } catch (ignoreOrigin) {
      return false;
    }
  }
  if (referer) {
    try {
      return new URL(referer).origin === url.origin;
    } catch (ignoreReferer) {
      return false;
    }
  }
  var host = req.headers.get("Host") || "";
  return Boolean(host) && host === url.host;
}

export async function onRequestPost(context) {
  var req = context.request;
  if (!sameOrigin(req)) {
    return new Response(null, { status: 403 });
  }
  var len = Number(req.headers.get("content-length") || 0);
  if (len > 2048) {
    return new Response(null, { status: 413 });
  }
  try {
    await req.text();
  } catch (ignore) {}
  return new Response(null, { status: 204 });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "content-type",
    },
  });
}
