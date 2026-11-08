/**
 * Serve the Diburim static site from Worker assets; proxy /shulchan_aruch/* to GitHub Pages
 * (corpus too large for Workers asset manifest).
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/shulchan_aruch" || url.pathname.startsWith("/shulchan_aruch/")) {
      const origin = (env.SHULCHAN_PAGES_ORIGIN || "https://diburim.github.io").replace(/\/$/, "");
      const upstream = origin + url.pathname + url.search;
      const headers = new Headers(request.headers);
      headers.delete("host");
      const init = {
        method: request.method,
        headers,
        redirect: "follow",
      };
      if (request.method !== "GET" && request.method !== "HEAD") {
        init.body = request.body;
      }
      const res = await fetch(upstream, init);
      const out = new Headers(res.headers);
      out.delete("content-encoding");
      return new Response(res.body, { status: res.status, statusText: res.statusText, headers: out });
    }
    return env.ASSETS.fetch(request);
  },
};
