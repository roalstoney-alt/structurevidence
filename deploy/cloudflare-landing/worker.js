const ORIGIN = "https://structurevidence.org";

export default {
  async fetch(request) {
    const incoming = new URL(request.url);
    const originPath = incoming.pathname === "/" || incoming.pathname === "/index.html"
      ? "/landing.html"
      : incoming.pathname;
    const originUrl = new URL(originPath + incoming.search, ORIGIN);
    const response = await fetch(new Request(originUrl, request));
    const headers = new Headers(response.headers);
    headers.set("x-structevidence-landing", "structevidence.com");
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  },
};
