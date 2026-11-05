/** Loads site config and catalog; article bodies load per page via DIBURIM_loadArticle. */
(function () {
  window.DIBURIM_CATALOG = [];
  window.DIBURIM_PROJECTS = [];
  window.DIBURIM_SITE = {};
  window.DIBURIM_UI = {};

  async function fetchJson(url) {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to load " + url + " (" + res.status + ")");
    return res.json();
  }

  async function loadArticleBody(id) {
    if (!id) return { body: null, bodyFormat: "html" };
    try {
      const res = await fetch("content/articles/" + encodeURIComponent(id) + ".json", { cache: "no-store" });
      if (!res.ok) return { body: null, bodyFormat: "html" };
      try {
        return await res.json();
      } catch (parseErr) {
        console.warn("Invalid article JSON for id:", id, parseErr);
        return { body: null, bodyFormat: "html" };
      }
    } catch (e) {
      return { body: null, bodyFormat: "html" };
    }
  }

  function applySiteMeta(site) {
    if (site.metaDescription) {
      const meta = document.querySelector('meta[name="description"]');
      if (meta) meta.setAttribute("content", site.metaDescription);
    }
    const ld = document.querySelector('script[type="application/ld+json"]');
    if (ld && site.metaDescription) {
      try {
        const data = JSON.parse(ld.textContent);
        data.description = site.metaDescription;
        if (site.siteName) data.name = site.siteName;
        ld.textContent = JSON.stringify(data);
      } catch (e) { /* ignore */ }
    }
    const mission = document.querySelector(".hero-mission");
    if (mission && site.mission) mission.textContent = site.mission;
    const footerTag = document.querySelector("[data-site-footer-tag]");
    if (footerTag && site.footerLine) footerTag.textContent = site.footerLine;
  }

  function applyArticleToPiece(p, article) {
    if (!p || !article) return;
    p.body = article.body != null ? article.body : null;
    p.bodyFormat = article.bodyFormat || "html";
    if (article.pdf) p.pdf = article.pdf;
    if (article.audio) p.audio = article.audio;
  }

  window.DIBURIM_loadArticle = loadArticleBody;
  window.DIBURIM_applyArticle = applyArticleToPiece;

  async function bootstrap() {
    let site = {};
    let ui = {};
    let catalog = { pieces: [] };
    let projects = { projects: [] };

    try {
      site = await fetchJson("data/site.json");
    } catch (e) {
      console.error(e);
    }
    try {
      ui = await fetchJson("data/ui.json");
    } catch (e) {
      console.error(e);
    }
    try {
      catalog = await fetchJson("data/catalog.json");
    } catch (e) {
      console.error("Catalog could not be loaded. Serve the site from the Diburim project root.", e);
    }
    try {
      projects = await fetchJson("data/projects.json");
    } catch (e) {
      console.error(e);
    }

    window.DIBURIM_SITE = site;
    window.DIBURIM_UI = ui;

    const pieces = catalog.pieces || [];
    pieces.forEach(function (p) {
      if (catalog.thisWeekId === p.id) p.thisWeek = true;
    });
    window.DIBURIM_CATALOG = pieces;
    window.DIBURIM_CATALOG_INDEX = catalog;
    window.DIBURIM_PROJECTS = projects.projects || [];
    window.DIBURIM_PROJECTS_FEATURED = projects.featuredSeriesId || null;
    window.DIBURIM_BOOTSTRAP_ERROR = pieces.length ? null : "catalog-empty";

    applySiteMeta(site);
    document.dispatchEvent(new CustomEvent("diburim:ready"));
  }

  bootstrap().catch(function (err) {
    console.error(err);
    document.dispatchEvent(new CustomEvent("diburim:ready"));
  });
})();
