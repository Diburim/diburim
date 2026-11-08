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

  function localDateIso(d) {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + day;
  }

  function findCurrentShabbatReading(readings, todayIso) {
    if (!readings || !readings.length) return null;
    const sorted = readings.slice().sort(function (a, b) {
      return a.date < b.date ? -1 : a.date > b.date ? 1 : 0;
    });
    var current = null;
    for (var i = 0; i < sorted.length; i++) {
      if (sorted[i].date <= todayIso) current = sorted[i];
      else break;
    }
    return current || sorted[0];
  }

  function isWeeklyParshaPiece(p) {
    if (!p || !p.parsha) return false;
    if (p.kind === "study-guide" || p.kind === "kuntres") return false;
    return true;
  }

  function archiveEditionId(id) {
    return /-\d{4}$/.test(String(id || ""));
  }

  function pickWeeklyPiece(pieces, parsha, shabbatDate) {
    var candidates = pieces.filter(function (p) {
      return p.parsha === parsha && isWeeklyParshaPiece(p);
    });
    if (!candidates.length) return null;

    var exact = candidates.filter(function (p) {
      return p.date === shabbatDate;
    });
    var pool = exact.length
      ? exact
      : candidates.filter(function (p) {
          return !p.date || p.date <= shabbatDate;
        });
    if (!pool.length) pool = candidates.slice();

    pool.sort(function (a, b) {
      var da = a.date || "";
      var db = b.date || "";
      if (da !== db) return da < db ? 1 : -1;
      var aa = archiveEditionId(a.id);
      var ab = archiveEditionId(b.id);
      if (aa !== ab) return aa ? 1 : -1;
      var sa = a.series === "Weekly Torah" ? 0 : 1;
      var sb = b.series === "Weekly Torah" ? 0 : 1;
      if (sa !== sb) return sa - sb;
      return String(a.id).localeCompare(String(b.id));
    });

    return pool[0] || null;
  }

  function resolveThisWeekId(pieces, calendar, catalog) {
    var readings = (calendar && calendar.readings) || [];
    if (!readings.length) return catalog.thisWeekId || null;
    var row = findCurrentShabbatReading(readings, localDateIso(new Date()));
    if (!row || !row.parshas || !row.parshas.length) return catalog.thisWeekId || null;

    var shabbatDate = row.date;
    for (var i = 0; i < row.parshas.length; i++) {
      var pick = pickWeeklyPiece(pieces, row.parshas[i], shabbatDate);
      if (pick) return pick.id;
    }
    return catalog.thisWeekId || null;
  }

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

    var calendar = { readings: [] };
    try {
      calendar = await fetchJson("data/parsha-calendar.json");
    } catch (e) {
      console.warn("Parsha calendar unavailable; this-week falls back to catalog.thisWeekId.", e);
    }

    window.DIBURIM_SITE = site;
    window.DIBURIM_UI = ui;

    const pieces = catalog.pieces || [];
    var weekMode = catalog.thisWeekMode || "auto";
    var weekId =
      weekMode === "manual" && catalog.thisWeekId
        ? catalog.thisWeekId
        : resolveThisWeekId(pieces, calendar, catalog);
    if (!weekId && catalog.thisWeekId) weekId = catalog.thisWeekId;

    pieces.forEach(function (p) {
      p.thisWeek = weekId && p.id === weekId;
    });

    var weekPiece = pieces.find(function (p) {
      return p.thisWeek;
    });
    if (weekPiece && weekId) {
      try {
        var article = await loadArticleBody(weekId);
        applyArticleToPiece(weekPiece, article);
      } catch (e) {
        console.warn("Could not preload article for this week:", weekId, e);
      }
    }

    window.DIBURIM_THIS_WEEK_ID = weekId || null;
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
