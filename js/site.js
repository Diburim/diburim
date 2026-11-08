(function () {
  function runtime() {
    return {
      cfg: window.DIBURIM_CONFIG || {},
      site: window.DIBURIM_SITE || {},
      ui: window.DIBURIM_UI || {},
      pieces: window.DIBURIM_CATALOG || [],
      projects: window.DIBURIM_PROJECTS || [],
      shulchan: window.DIBURIM_SHULCHAN,
    };
  }

  const page = document.body.dataset.page || "";
  const navMap = { piece: "library", project: "projects", sheet: "resources" };

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }

  function byId(id, pieces) {
    return pieces.find(function (p) { return p.id === id; });
  }

  function readingMinutes(html) {
    const text = String(html || "").replace(/<[^>]+>/g, " ").trim();
    if (!text) return null;
    const words = text.split(/\s+/).length;
    return Math.max(1, Math.round(words / 220));
  }

  function studyGuideKicker(p) {
    if (p.kind !== "study-guide") return "";
    const parts = [];
    if (p.chelek && p.siman) parts.push(p.chelek + " Siman " + p.siman);
    else if (p.siman) parts.push("Siman " + p.siman);
    return parts.join(" · ") || p.series || "Halacha";
  }

  function formatMeta(p) {
    const bits = [];
    if (p.kind === "study-guide") bits.push(studyGuideKicker(p));
    if (p.parsha) bits.push(p.parsha);
    else if (p.holiday) bits.push(p.holiday);
    else if (p.sefer) bits.push(p.sefer);
    const mins = readingMinutes(p.body);
    if (mins) bits.push(mins + " min");
    if (p.series) bits.push(p.series);
    return bits.join(" · ");
  }

  function wash(scene) {
    return "wash-" + (scene || "sand");
  }

  function safeMediaUrl(url) {
    if (!url) return "";
    if (url.indexOf("assets/") === 0 || url.indexOf("./") === 0) return url;
    try {
      const parsed = new URL(url, window.location.href);
      if (parsed.protocol === "https:" || parsed.protocol === "http:") return parsed.href;
    } catch (err) {
      return "";
    }
    return "";
  }

  function safeExternalUrl(url) {
    return safeMediaUrl(url);
  }

  function shulchanReaderPath(cfg) {
    const raw = String((cfg && cfg.shulchanAruchPath) || "").trim();
    if (!raw) return "";
    const rel = raw.replace(/^\/+/, "");
    return rel.endsWith("/") ? rel : rel + "/";
  }

  function shulchanUrls(cfg) {
    cfg = cfg || {};
    const reader = shulchanReaderPath(cfg);
    return {
      reader: reader,
      hasReader: Boolean(reader),
      repo: safeExternalUrl(cfg.shulchanAruchRepoUrl),
    };
  }

  function shulchanActionButtons(cfg, ui, opts) {
    opts = opts || {};
    const urls = shulchanUrls(cfg);
    const readerLabel = (cfg && cfg.shulchanAruchReaderLabel) || "Open translation";
    const repoLabel = (cfg && cfg.shulchanAruchRepoLabel) || "GitHub repository";
    let html = "";
    if (urls.hasReader) {
      html += '<a class="btn btn-navy" href="' + escapeHtml(urls.reader) + '">' + escapeHtml(readerLabel) + "</a>";
    }
    if (urls.repo) {
      html += '<a class="btn btn-ghost" href="' + escapeHtml(urls.repo) + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(repoLabel) + "</a>";
    }
    if (opts.hubLink) {
      html += '<a class="btn btn-ghost" href="shulchan-aruch.html">Project hub</a>';
    }
    if (!html && opts.pending) {
      html = '<p class="muted">' + escapeHtml((ui && ui.shulchanHubPending) || "[CONTENT PENDING]") + "</p>";
    }
    return html;
  }

  function wireShulchanProject(cfg, ui) {
    const urls = shulchanUrls(cfg);
    const readerLabel = (cfg && cfg.shulchanAruchReaderLabel) || "Open translation";
    const repoLabel = (cfg && cfg.shulchanAruchRepoLabel) || "GitHub repository";
    document.querySelectorAll("[data-sa-reader], [data-external-sa]").forEach(function (node) {
      if (!urls.hasReader) {
        node.hidden = true;
        return;
      }
      node.hidden = false;
      const anchor = node.matches("a") ? node : node.querySelector("a");
      if (anchor) {
        anchor.href = urls.reader;
        anchor.textContent = readerLabel;
        anchor.removeAttribute("target");
        anchor.removeAttribute("rel");
      }
    });
    document.querySelectorAll("[data-sa-repo]").forEach(function (anchor) {
      if (!urls.repo) {
        anchor.hidden = true;
        return;
      }
      anchor.hidden = false;
      anchor.href = urls.repo;
      anchor.textContent = repoLabel;
    });
    const note = document.getElementById("sa-config-note");
    if (note) {
      if (urls.hasReader) {
        note.hidden = false;
        note.textContent = (ui && ui.shulchanOnSite) || "";
      } else {
        note.hidden = false;
        note.textContent = (ui && ui.shulchanHubPending) || "[CONTENT PENDING]";
      }
    }
    const saStats = document.querySelector(".sa-hero .stat-row");
    if (saStats) saStats.hidden = Boolean(urls.hasReader);
    const hero = document.getElementById("hero-sa-link");
    if (hero) {
      if (urls.hasReader) {
        hero.href = urls.reader;
        hero.removeAttribute("target");
        hero.removeAttribute("rel");
      } else {
        hero.href = "shulchan-aruch.html";
      }
    }
    document.querySelectorAll("[data-sa-primary]").forEach(function (link) {
      if (link.id === "hero-sa-link") return;
      if (urls.hasReader) {
        link.href = urls.reader;
        link.removeAttribute("target");
        link.removeAttribute("rel");
      }
    });
  }

  function hasAudio(p) {
    return Boolean(safeMediaUrl(p && p.audio));
  }

  function youtubeVideoId(id) {
    return /^[A-Za-z0-9_-]{11}$/.test(String(id || "").trim()) ? String(id).trim() : "";
  }

  function piecePrintPdfUrl(piece) {
    if (!piece) return "";
    return safeMediaUrl(piece.pdf) || "";
  }

  function applyLoadedArticle(piece, article) {
    if (window.DIBURIM_applyArticle) {
      window.DIBURIM_applyArticle(piece, article);
    }
  }

  function buildPieceBodyAndToc(piece, ui, loading) {
    const pending = ui.contentPending || "[CONTENT PENDING]";
    const pdfUrl = safeMediaUrl(piece.pdf);
    const temp = document.createElement("div");
    if (loading) {
      temp.innerHTML = '<p class="muted">' + escapeHtml(ui.loadingArticle || "Loading…") + "</p>";
    } else if (piece.body) {
      temp.innerHTML = piece.body;
    } else if (pdfUrl) {
      temp.innerHTML =
        '<div class="pdf-study-guide">' +
          '<p class="muted">Study guide (PDF). Use the viewer below or download for printing.</p>' +
          '<p><a class="btn btn-navy" href="' + escapeHtml(pdfUrl) + '" download target="_blank" rel="noopener">Download PDF</a></p>' +
          '<iframe class="pdf-frame" title="' + escapeHtml(piece.title) + '" src="' + escapeHtml(pdfUrl) + '"></iframe>' +
        "</div>";
    } else {
      temp.innerHTML = "<p>" + escapeHtml(pending) + "</p>";
    }
    const heads = Array.prototype.slice.call(temp.querySelectorAll("h2"));
    heads.forEach(function (h, i) {
      if (!h.id) h.id = "section-" + (i + 1);
    });
    const toc = heads.map(function (h) {
      return '<li><a href="#' + h.id + '">' + escapeHtml(h.textContent) + "</a></li>";
    }).join("");
    return { bodyHtml: temp.innerHTML, tocHtml: toc, bodyRoot: loading ? null : temp };
  }

  function mountPieceAudio(mount, piece, ui) {
    if (!hasAudio(piece)) return;
    const tools = mount.querySelector(".tools");
    if (tools && !tools.querySelector('a[href="#listen"]')) {
      const link = document.createElement("a");
      link.className = "btn btn-ghost";
      link.href = "#listen";
      link.textContent = "Audio";
      tools.insertBefore(link, tools.firstChild);
    }
    const bodyEl = mount.querySelector(".piece-body");
    if (!bodyEl || mount.querySelector("#listen")) return;
    const listen = document.createElement("div");
    listen.id = "listen";
    listen.innerHTML = playerMarkup(piece, ui);
    bodyEl.insertAdjacentElement("afterend", listen);
    bindPlayers(listen);
  }

  function initNav(cfg) {
    const target = navMap[page] || page;
    document.querySelectorAll("[data-nav]").forEach(function (link) {
      if (link.dataset.nav === target) link.setAttribute("aria-current", "page");
    });
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.getElementById("primary-nav");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        const open = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
    wireShulchanProject(cfg, window.DIBURIM_UI || {});
    document.querySelectorAll("[data-contact]").forEach(function (node) {
      if (!cfg.contactEmail) {
        node.hidden = true;
        return;
      }
      node.hidden = false;
      const anchor = node.matches("a") ? node : node.querySelector("a");
      if (anchor) {
        anchor.href = "mailto:" + cfg.contactEmail;
        anchor.textContent = cfg.contactEmail;
      }
    });
  }

  function indexKicker(p) {
    return studyGuideKicker(p) || p.parsha || p.holiday || p.series || p.sefer || "Torah";
  }

  function indexMeta(p) {
    const bits = [];
    const mins = readingMinutes(p.body);
    if (mins) bits.push(mins + " min read");
    if (p.dateDisplay) bits.push(p.dateDisplay);
    else if (p.date) bits.push(p.date);
    if (!bits.length) return formatMeta(p);
    return bits.join(" · ");
  }

  function editorialCard(p) {
    return (
      '<article class="index-entry">' +
        '<p class="index-kicker">' + escapeHtml(indexKicker(p)) + "</p>" +
        '<h3 class="index-title"><a href="piece.html?id=' + encodeURIComponent(p.id) + '">' + escapeHtml(p.title) + "</a></h3>" +
        (p.excerpt ? '<p class="index-excerpt">' + escapeHtml(p.excerpt) + "</p>" : "") +
        '<p class="index-meta">' + escapeHtml(indexMeta(p)) + "</p>" +
      "</article>"
    );
  }

  function sceneHebrew(p) {
    if (p.parshaHe) return p.parshaHe;
    if (p.kind === "study-guide") return "";
    return p.hebrewTitle || "";
  }

  function card(p) {
    const he = sceneHebrew(p);
    return (
      '<article class="entry">' +
        '<a class="scene ' + wash(p.scene) + '" href="piece.html?id=' + encodeURIComponent(p.id) + '" tabindex="-1" aria-hidden="true">' +
          (he ? '<span class="scene-word" dir="rtl" lang="he">' + escapeHtml(he) + "</span>" : "") +
        "</a>" +
        '<div class="entry-body">' +
          '<p class="kicker">' + escapeHtml(indexKicker(p)) + "</p>" +
          '<h3><a href="piece.html?id=' + encodeURIComponent(p.id) + '">' + escapeHtml(p.title) + "</a></h3>" +
          (p.hebrewTitle ? '<p class="hebrew" lang="he">' + escapeHtml(p.hebrewTitle) + "</p>" : "") +
          (p.excerpt ? '<p class="excerpt">' + escapeHtml(p.excerpt) + "</p>" : "") +
          '<p class="meta">' + escapeHtml(formatMeta(p)) + "</p>" +
        "</div>" +
      "</article>"
    );
  }

  function wave() {
    let bars = "";
    for (let i = 0; i < 42; i += 1) {
      const h = 30 + ((i * 37) % 70);
      bars += '<i style="height:' + h + "%;animation-delay:" + (i % 8) * 0.08 + 's"></i>';
    }
    return bars;
  }

  function playerMarkup(p, ui) {
    const src = safeMediaUrl(p.audio);
    if (!src) return "";
    return (
      '<div class="player is-ready" data-audio="' + escapeHtml(src) + '">' +
        '<button class="player-play" type="button" aria-label="Play">▶</button>' +
        '<div><p class="player-kicker">Listen</p>' +
        '<p class="player-title">' + escapeHtml(p.title) + "</p>" +
        '<p class="player-status">Ready</p></div>' +
        '<span class="player-time">--:--</span>' +
        '<div class="player-wave" aria-hidden="true">' + wave() + "</div>" +
        '<button class="player-bar" type="button" aria-label="Seek"><span></span></button>' +
        '<audio preload="metadata"></audio>' +
      "</div>"
    );
  }

  function bindPlayers(root) {
    (root || document).querySelectorAll(".player").forEach(function (el) {
      if (el.dataset.bound) return;
      el.dataset.bound = "1";
      const src = el.dataset.audio || "";
      const audio = el.querySelector("audio");
      const button = el.querySelector(".player-play");
      const status = el.querySelector(".player-status");
      const time = el.querySelector(".player-time");
      const bar = el.querySelector(".player-bar");
      const fill = bar.querySelector("span");
      if (!src) {
        return;
      }
      audio.src = src;
      function clock(seconds) {
        if (!isFinite(seconds)) return "--:--";
        const s = Math.max(0, Math.floor(seconds));
        return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
      }
      button.addEventListener("click", function () {
        if (audio.paused) {
          audio.play().catch(function () {
            status.textContent = "This recording could not be played.";
          });
        } else {
          audio.pause();
        }
      });
      audio.addEventListener("play", function () {
        el.classList.add("is-playing");
        button.textContent = "❚❚";
        button.setAttribute("aria-label", "Pause");
        status.textContent = "Playing";
      });
      audio.addEventListener("pause", function () {
        el.classList.remove("is-playing");
        button.textContent = "▶";
        button.setAttribute("aria-label", "Play");
        if (!audio.ended) status.textContent = "Paused";
      });
      audio.addEventListener("timeupdate", function () {
        time.textContent = clock(audio.currentTime);
        if (audio.duration) fill.style.width = (audio.currentTime / audio.duration) * 100 + "%";
      });
      audio.addEventListener("loadedmetadata", function () {
        time.textContent = clock(audio.duration);
        status.textContent = "Ready to play";
      });
      audio.addEventListener("ended", function () {
        status.textContent = "Finished";
        fill.style.width = "0";
      });
      audio.addEventListener("error", function () {
        status.textContent = "This recording could not be loaded.";
      });
      bar.addEventListener("click", function (event) {
        if (!audio.duration) return;
        const rect = bar.getBoundingClientRect();
        audio.currentTime = ((event.clientX - rect.left) / rect.width) * audio.duration;
      });
    });
  }

  function initHome(pieces, projects, ui, site) {
    const week = pieces.find(function (p) { return p.thisWeek; });
    const mount = document.getElementById("this-week");
    const heroWeek = document.getElementById("hero-week-link");
    if (heroWeek) {
      if (week && week.id) {
        heroWeek.href = "piece.html?id=" + encodeURIComponent(week.id);
        heroWeek.hidden = false;
      } else {
        heroWeek.hidden = true;
      }
    }
    if (mount) {
      if (!week) {
        mount.innerHTML = '<p class="muted">' + escapeHtml(ui.thisWeekEmpty || "[CONTENT PENDING]") + "</p>";
      } else {
        const mins = readingMinutes(week.body);
        const weekAudio = hasAudio(week);
        const hasPdf = Boolean(safeMediaUrl(week.pdf));
        const hasEssay = Boolean(week.body);
        const pieceUrl = "piece.html?id=" + encodeURIComponent(week.id);
        const primaryLabel = hasEssay ? "Read the essay" : hasPdf ? "Read the piece" : weekAudio ? "Open piece" : "Read the essay";
        mount.innerHTML =
          '<div class="week-grid">' +
            '<div class="week-copy">' +
              '<p class="kicker">This week’s Torah</p>' +
              '<h2>' + escapeHtml(week.title || "") + "</h2>" +
              (week.hebrewTitle ? '<p class="week-he hebrew" lang="he">' + escapeHtml(week.hebrewTitle) + "</p>" : "") +
              (week.excerpt ? "<p>" + escapeHtml(week.excerpt) + "</p>" : "") +
              (!hasEssay && weekAudio && ui.thisWeekAudioOnly ? '<p class="muted">' + escapeHtml(ui.thisWeekAudioOnly) + "</p>" : "") +
              '<p class="meta-row" data-week-meta>' +
                [week.parsha, week.occasion || week.dateDisplay, mins ? mins + " min read" : "", weekAudio && !hasEssay ? "Audio" : ""].filter(Boolean).map(function (bit, i) {
                  return (i ? '<span class="dot"></span>' : "") + "<span>" + escapeHtml(bit) + "</span>";
                }).join("") +
              "</p>" +
              '<div class="actions">' +
                '<a class="btn btn-navy" href="' + escapeHtml(pieceUrl) + '">' + escapeHtml(primaryLabel) + "</a>" +
                (weekAudio ? '<a class="btn btn-ghost" href="' + escapeHtml(pieceUrl) + '#listen">Listen</a>' : "") +
                (hasEssay ? '<a class="btn btn-ghost" href="' + escapeHtml(pieceUrl) + '#sources">Sources</a>' : "") +
              "</div>" +
            "</div>" +
            '<div class="week-side">' +
              (week.parshaHe ? '<a class="scene ' + wash(week.scene) + '" href="piece.html?id=' + encodeURIComponent(week.id) + '"><span class="scene-word" dir="rtl" lang="he">' + escapeHtml(week.parshaHe) + "</span></a>" : "") +
              (weekAudio ? playerMarkup(week, ui) : "") +
            "</div>" +
          "</div>";
        if (weekAudio) bindPlayers(mount);
        const loadArticle = window.DIBURIM_loadArticle;
        if (loadArticle && week.id) {
          loadArticle(week.id).then(function (article) {
            if (!document.getElementById("this-week") || !mount.querySelector(".week-grid")) return;
            applyLoadedArticle(week, article);
            const meta = mount.querySelector("[data-week-meta]");
            const readMins = readingMinutes(week.body);
            if (meta) {
              meta.innerHTML = [week.parsha, week.occasion || week.dateDisplay, readMins ? readMins + " min read" : ""].filter(Boolean).map(function (bit, i) {
                return (i ? '<span class="dot"></span>' : "") + "<span>" + escapeHtml(bit) + "</span>";
              }).join("");
            }
            if (!weekAudio && hasAudio(week)) {
              const actions = mount.querySelector(".actions");
              if (actions) {
                actions.insertAdjacentHTML(
                  "beforeend",
                  '<a class="btn btn-ghost" href="piece.html?id=' + encodeURIComponent(week.id) + '#listen">Audio</a>'
                );
              }
              const side = mount.querySelector(".week-side");
              if (side) {
                side.insertAdjacentHTML("beforeend", playerMarkup(week, ui));
                bindPlayers(mount);
              }
            }
          });
        }
      }
    }
    const recent = document.getElementById("recent-grid");
    const recentSection = document.getElementById("recent-section");
    if (recent) {
      const list = pieces
        .slice()
        .sort(function (a, b) { return (a.date || "") < (b.date || "") ? 1 : -1; })
        .filter(function (p) { return !p.thisWeek; })
        .slice(0, 6);
      if (!list.length) {
        if (recentSection) recentSection.hidden = true;
        recent.innerHTML = "";
      } else {
        if (recentSection) recentSection.hidden = false;
        recent.innerHTML = list.map(editorialCard).join("");
      }
    }
    const series = document.getElementById("series-links");
    const seriesSummary = document.getElementById("featured-series-summary");
    const featured = projects.find(function (pr) { return pr.id === (window.DIBURIM_PROJECTS_FEATURED || "devarim"); });
    if (seriesSummary && featured) {
      seriesSummary.textContent = featured.summary || "";
      seriesSummary.hidden = !featured.summary;
    }
    if (series) {
      const links = pieces.filter(function (p) {
        return p.project === "devarim" || p.seriesId === "devarim" || p.series === "Diburim";
      });
      series.innerHTML = links.length
        ? links.map(function (p) {
          return '<li><a href="piece.html?id=' + encodeURIComponent(p.id) + '"><span>' + escapeHtml(p.title) + '</span><span class="muted">' + escapeHtml(p.parsha || "") + "</span></a></li>";
        }).join("")
        : "";
      series.hidden = !links.length;
    }
    const homeProjects = document.getElementById("home-projects-grid");
    if (homeProjects) {
      const cfg = (window.DIBURIM_CONFIG || {});
      homeProjects.innerHTML = projects.slice(0, 3).map(function (project) {
        const href = projectOpenHref(project, cfg);
        return (
          '<article class="' + (project.id === "shulchan-aruch" ? "sa-home-card" : "plain-card") + '">' +
            (project.status ? '<p class="kicker">' + escapeHtml(project.status) + "</p>" : "") +
            "<h3>" + escapeHtml(project.title) + "</h3>" +
            (project.summary ? "<p>" + escapeHtml(project.summary) + "</p>" : "") +
            '<p><a class="btn btn-' + (project.id === "shulchan-aruch" ? "gold" : "ghost") + '" href="' + escapeHtml(href) + '">Open</a></p>' +
          "</article>"
        );
      }).join("");
    }
    const aboutBlurb = document.getElementById("about-blurb");
    if (aboutBlurb) {
      aboutBlurb.textContent = site.aboutBlurb || "";
      aboutBlurb.hidden = !site.aboutBlurb;
    }
  }

  function libraryHaystack(p) {
    return [
      p.title,
      p.hebrewTitle,
      p.excerpt,
      p.parsha,
      p.sefer,
      p.series,
      p.holiday,
      p.kind,
      p.siman,
      p.pdf,
      (p.topics || []).join(" "),
      String(p.body || "").replace(/<[^>]+>/g, " "),
    ].join(" ").toLowerCase();
  }

  function isHalachaPiece(p) {
    return p.kind === "study-guide" || (p.categories || []).indexOf("halacha") !== -1;
  }

  function matches(p, state) {
    if (state.q) {
      if (libraryHaystack(p).indexOf(state.q.toLowerCase()) === -1) return false;
    }
    if (state.sefer) {
      if (state.sefer === "Halachah") {
        if (!isHalachaPiece(p)) return false;
      } else if (p.sefer !== state.sefer) {
        return false;
      }
    }
    if (state.parsha && p.parsha !== state.parsha) return false;
    if (state.holiday && p.holiday !== state.holiday) return false;
    if (state.category === "halacha" && !isHalachaPiece(p)) return false;
    if (state.category === "hashkafa" && (p.categories || []).indexOf("hashkafa") === -1) return false;
    if (state.series && p.series !== state.series) return false;
    if (state.browse === "holiday" && !p.holiday) return false;
    if (state.browse === "parsha" && (!p.parsha || p.kind === "kuntres")) return false;
    if (state.browse === "series" && !p.series) return false;
    if (state.browse === "sefer" && state.sefer && p.sefer !== state.sefer) return false;
    if (state.browse === "sefer" && !state.sefer && !p.sefer) return false;
    if (state.kind && p.kind !== state.kind) return false;
    return true;
  }

  function librarySort(a, b) {
    if (a.kind === "study-guide" && b.kind === "study-guide") {
      return (a.siman || 0) - (b.siman || 0);
    }
    const da = a.date || "";
    const db = b.date || "";
    if (da !== db) {
      if (!da) return 1;
      if (!db) return -1;
      return da < db ? 1 : -1;
    }
    return String(a.title || "").localeCompare(String(b.title || ""));
  }

  function initLibrary(pieces, cfg, ui) {
    const params = new URLSearchParams(window.location.search);
    const state = {
      q: params.get("q") || "",
      sefer: params.get("sefer") || "",
      parsha: params.get("parsha") || "",
      holiday: params.get("holiday") || "",
      category: params.get("category") || "",
      series: params.get("series") || "",
      browse: params.get("browse") || "",
      kind: ""
    };
    if (state.browse === "halacha") state.category = "halacha";
    if (state.browse === "hashkafa") state.category = "hashkafa";
    if (params.get("sefer")) {
      state.sefer = params.get("sefer");
      state.browse = "sefer";
    }
    const results = document.getElementById("results");
    const meta = document.getElementById("results-meta");
    const search = document.getElementById("library-search");
    const searchTop = document.getElementById("library-search-top");
    const calendar = document.getElementById("calendar-panel");
    if (search) search.value = state.q;
    if (searchTop) searchTop.value = state.q;
    const totalEl = document.getElementById("library-total");
    if (totalEl) totalEl.textContent = "(" + pieces.length + " published pieces)";

    function draw() {
      const list = pieces.filter(function (p) { return matches(p, state); }).sort(librarySort);
      if (calendar) {
        const showCal = state.browse === "calendar";
        calendar.hidden = !showCal;
        if (showCal) {
          calendar.innerHTML = '<p class="muted">' + escapeHtml(ui.contentPending || "[CONTENT PENDING]") + "</p>";
        }
      }
      meta.textContent = list.length + (list.length === 1 ? " piece" : " pieces");
      if (!list.length) {
        let msg = ui.libraryEmpty || "[CONTENT PENDING]";
        if (!pieces.length && window.DIBURIM_BOOTSTRAP_ERROR === "catalog-empty") {
          msg = "The catalog did not load. Start the server from the Diburim project folder (where data/catalog.json lives), then open /data/catalog.json in the browser — you should see published pieces, not an empty list.";
        } else if (pieces.length && !list.length) {
          msg = "No pieces match this filter. Try All, or clear the search box.";
        }
        results.innerHTML = '<div class="empty"><p>' + escapeHtml(msg) + "</p></div>";
        return;
      }
      results.innerHTML = list.map(editorialCard).join("");
    }

    document.querySelectorAll("[data-filter]").forEach(function (button) {
      const key = button.dataset.filter;
      const value = button.dataset.value || "";
      const on = (key === "browse" && state.browse === value) || (key !== "browse" && state[key] === value) || (!value && !state.browse && !state.sefer && !state.category && !state.series && key === "browse");
      if (key === "browse" && value === "" && !state.browse && !state.sefer && !state.category && !state.series && !state.holiday && !state.parsha) button.setAttribute("aria-pressed", "true");
      if (value && ((key === "browse" && state.browse === value) || state[key] === value)) button.setAttribute("aria-pressed", "true");
      button.addEventListener("click", function () {
        if (key === "browse") {
          state.browse = value;
          state.sefer = "";
          state.parsha = "";
          state.holiday = "";
          state.series = "";
          state.category = value === "halacha" ? "halacha" : value === "hashkafa" ? "hashkafa" : "";
          if (!value) state.category = "";
          document.querySelectorAll("[data-sefer]").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        } else {
          state[key] = state[key] === value ? "" : value;
        }
        document.querySelectorAll("[data-filter]").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        button.setAttribute("aria-pressed", "true");
        draw();
      });
    });

    document.querySelectorAll("[data-sefer]").forEach(function (button) {
      const name = button.dataset.sefer;
      const count = pieces.filter(function (p) {
        if (name === "Halachah") return isHalachaPiece(p);
        return p.sefer === name;
      }).length;
      const countEl = button.querySelector(".count");
      if (countEl) countEl.textContent = String(count);
      if (state.sefer === name) button.setAttribute("aria-pressed", "true");
      button.addEventListener("click", function () {
        state.sefer = state.sefer === name ? "" : name;
        state.browse = "sefer";
        document.querySelectorAll("[data-sefer]").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        if (state.sefer) button.setAttribute("aria-pressed", "true");
        draw();
      });
    });

    function onSearchInput(value) {
      state.q = value.trim();
      if (search) search.value = state.q;
      if (searchTop) searchTop.value = state.q;
      draw();
    }
    if (search) {
      search.addEventListener("input", function () {
        onSearchInput(search.value);
      });
    }
    if (searchTop) {
      searchTop.addEventListener("input", function () {
        onSearchInput(searchTop.value);
      });
    }

    const spotlight = document.getElementById("library-this-week");
    const week = pieces.find(function (p) { return p.thisWeek; });
    if (spotlight && week) {
      const pieceUrl = "piece.html?id=" + encodeURIComponent(week.id);
      spotlight.hidden = false;
      spotlight.innerHTML =
        '<div class="library-spotlight-inner">' +
          '<p class="kicker">Continue with this week&rsquo;s Torah</p>' +
          '<h2 class="library-spotlight-title"><a href="' + escapeHtml(pieceUrl) + '">' + escapeHtml(week.title) + "</a></h2>" +
          (week.excerpt ? '<p class="library-spotlight-lede">' + escapeHtml(week.excerpt) + "</p>" : "") +
          '<p><a class="btn btn-navy" href="' + escapeHtml(pieceUrl) + '">Read the essay</a></p>' +
        "</div>";
    }

    draw();
  }

  function initArticles(pieces, ui) {
    const mount = document.getElementById("article-list");
    if (!mount) return;
    const list = pieces
      .filter(function (p) { return p.kind !== "study-guide"; })
      .sort(librarySort);
    mount.innerHTML = list.length
      ? list.map(editorialCard).join("")
      : '<p class="muted">' + escapeHtml(ui.libraryEmpty || "[CONTENT PENDING]") + "</p>";
  }

  function finishPieceArticle(mount, piece, ui) {
    const built = buildPieceBodyAndToc(piece, ui, false);
    const bodyEl = mount.querySelector(".piece-body");
    const tocEl = mount.querySelector(".toc ol");
    const metaEl = mount.querySelector(".byline .muted");
    if (bodyEl) bodyEl.innerHTML = built.bodyHtml;
    if (tocEl) tocEl.innerHTML = built.tocHtml;
    const minutes = readingMinutes(piece.body);
    if (metaEl) {
      metaEl.innerHTML = [piece.dateDisplay, minutes ? minutes + " min read" : "", piece.series].filter(Boolean).map(escapeHtml).join(" · ");
    }
    mountPieceAudio(mount, piece, ui);
    bindPiecePrint(piece);
  }

  function bindPiecePrint(piece) {
    const printBtn = document.getElementById("print-piece");
    if (!printBtn) return;
    const pdfUrl = piecePrintPdfUrl(piece);
    printBtn.replaceWith(printBtn.cloneNode(true));
    const btn = document.getElementById("print-piece");
    if (!btn) return;
    if (pdfUrl) {
      btn.textContent = "Print / save PDF";
      btn.addEventListener("click", function () {
        window.open(pdfUrl, "_blank", "noopener,noreferrer");
      });
    } else {
      btn.textContent = "Print / save as PDF";
      btn.addEventListener("click", function () {
        window.print();
      });
    }
  }

  function bindPieceChrome(mount) {
    const shareBtn = document.getElementById("share-piece");
    if (shareBtn) {
      shareBtn.addEventListener("click", function () {
        const url = window.location.href;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () {
            shareBtn.textContent = "Link copied";
          });
        } else {
          shareBtn.textContent = url;
        }
      });
    }
  }

  function initPiece(pieces, cfg, ui) {
    const id = new URLSearchParams(window.location.search).get("id");
    const piece = byId(id, pieces);
    const mount = document.getElementById("piece");
    if (!mount) return;
    if (!piece) {
      mount.innerHTML = '<div class="empty"><p>That piece is not on the shelf. <a href="library.html">Return to the library</a>.</p></div>';
      return;
    }
    document.title = piece.title + " · Diburim";
    const minutes = readingMinutes(piece.body);
    const waitingForArticle = !piece.body && !safeMediaUrl(piece.pdf);
    const built = buildPieceBodyAndToc(piece, ui, waitingForArticle);
    const sources = (piece.sources || []).map(function (s) {
      return "<li><strong>" + escapeHtml(s.t) + ".</strong> " + escapeHtml(s.n) + "</li>";
    }).join("");
    const related = pieces.filter(function (p) {
      if (p.id === piece.id) return false;
      if (piece.series && p.series === piece.series) return true;
      return (p.topics || []).some(function (t) { return (piece.topics || []).indexOf(t) !== -1; });
    }).slice(0, 3);
    const prev = byId(piece.prevId, pieces);
    const next = byId(piece.nextId, pieces);
    const parshaLabel = piece.parsha ? "Parshas " + piece.parsha : "";
    const kidsVideo = kidsVideoForPiece(cfg, piece.id);
    const kidsVideoLink = kidsVideo
      ? '<a class="btn btn-ghost" href="videos.html#parsha">Video for children</a>'
      : "";
    mount.innerHTML =
      '<div class="piece-layout piece-layout--read" data-piece-id="' + escapeHtml(piece.id) + '">' +
        '<article class="piece-read">' +
          '<p class="crumbs"><a href="library.html">Library</a> · ' + escapeHtml(piece.kind === "study-guide" ? "Halacha" : (piece.parsha || piece.holiday || piece.sefer || "Torah")) + (piece.project === "halachah" ? ' · <a href="project.html?id=halachah">Study guides</a>' : "") + "</p>" +
          (parshaLabel ? '<p class="piece-parsha kicker">' + escapeHtml(parshaLabel) + "</p>" : '<p class="kicker">' + escapeHtml(piece.kind === "study-guide" ? studyGuideKicker(piece) : (piece.occasion || piece.series || "Diburim")) + "</p>") +
          '<h1 class="piece-title">' + escapeHtml(piece.title) + "</h1>" +
          (piece.hebrewTitle ? '<p class="piece-he hebrew" lang="he">' + escapeHtml(piece.hebrewTitle) + "</p>" : "") +
          '<div class="byline byline--compact">' +
            '<p class="byline-text"><strong>' + escapeHtml((window.DIBURIM_SITE && window.DIBURIM_SITE.author) || "Rabbi Binyamin Goldberg") + "</strong><br><span class=\"muted\">" +
              [piece.dateDisplay, minutes ? minutes + " min read" : "", piece.series].filter(Boolean).map(escapeHtml).join(" · ") +
            "</span></p>" +
          "</div>" +
          '<div class="tools">' +
            '<button class="btn btn-ghost" type="button" id="print-piece">Print / Save as PDF</button>' +
            '<a class="btn btn-ghost" href="#sources">Source sheet</a>' +
            kidsVideoLink +
            '<button class="btn btn-ghost" type="button" id="share-piece">Share link</button>' +
          "</div>" +
          '<div class="piece-body article-body">' + built.bodyHtml + "</div>" +
          '<section class="sources" id="sources"><h2>Sources and Further Learning</h2><ol>' + sources + "</ol></section>" +
          '<nav class="pager" aria-label="Adjacent pieces">' +
            (prev ? '<a href="piece.html?id=' + encodeURIComponent(prev.id) + '"><small>Previous</small>' + escapeHtml(prev.title) + "</a>" : "<span></span>") +
            (next ? '<a href="piece.html?id=' + encodeURIComponent(next.id) + '"><small>Next</small>' + escapeHtml(next.title) + "</a>" : (piece.nextLabel ? '<span><small>Next</small>' + escapeHtml(piece.nextLabel) + "</span>" : "<span></span>")) +
          "</nav>" +
          (related.length ? '<h2 class="related-heading">Related</h2><div class="index-list">' + related.map(editorialCard).join("") + "</div>" : "") +
        "</article>" +
      "</div>";
    bindPieceChrome(mount);
    bindPiecePrint(piece);

    function afterArticleLoaded(article) {
      const layout = mount.querySelector(".piece-layout");
      if (!layout || layout.dataset.pieceId !== piece.id) return;
      applyLoadedArticle(piece, article);
      finishPieceArticle(mount, piece, ui);
    }

    const loadArticle = window.DIBURIM_loadArticle;
    if (loadArticle) {
      loadArticle(piece.id).then(afterArticleLoaded);
    } else if (!waitingForArticle) {
      mountPieceAudio(mount, piece, ui);
    }
  }

  function projectOpenHref(project, cfg) {
    if (project.id === "shulchan-aruch" && shulchanUrls(cfg).hasReader) {
      return shulchanUrls(cfg).reader;
    }
    return project.href || ("project.html?id=" + encodeURIComponent(project.id));
  }

  function initProjects(projects, cfg) {
    const mount = document.getElementById("project-list");
    if (!mount) return;
    mount.innerHTML = projects.map(function (project) {
      const href = projectOpenHref(project, cfg);
      return '<article class="plain-card">' +
        (project.status ? '<p class="kicker">' + escapeHtml(project.status) + "</p>" : "") +
        '<h2><a href="' + escapeHtml(href) + '">' + escapeHtml(project.title) + "</a></h2>" +
        (project.hebrew ? '<p class="hebrew" lang="he">' + escapeHtml(project.hebrew) + "</p>" : "") +
        (project.summary ? "<p>" + escapeHtml(project.summary) + "</p>" : "") +
        "</article>";
    }).join("");
  }

  function initProject(projects, pieces, ui, cfg) {
    const id = new URLSearchParams(window.location.search).get("id");
    const project = projects.find(function (item) { return item.id === id; });
    const mount = document.getElementById("project");
    if (!mount) return;
    if (!project) {
      mount.innerHTML = '<div class="empty"><p>That project is not listed. <a href="projects.html">All projects</a>.</p></div>';
      return;
    }
    document.title = project.title + " · Diburim";
    const linked = pieces.filter(function (p) { return p.project === project.id || p.series === project.title || (project.id === "devarim" && p.series === "Diburim on Devarim") || (project.id === "weekly" && p.series === "Weekly Torah") || (project.id === "halachah" && p.kind === "study-guide"); })
      .sort(function (a, b) {
        if (a.kind === "study-guide" && b.kind === "study-guide") return (a.siman || 0) - (b.siman || 0);
        return (a.date || "") < (b.date || "") ? 1 : -1;
      });
    mount.innerHTML =
      '<p class="crumbs"><a href="projects.html">Projects</a></p>' +
      (project.status ? '<p class="kicker">' + escapeHtml(project.status) + "</p>" : "") +
      "<h1>" + escapeHtml(project.title) + "</h1>" +
      (project.hebrew ? '<p class="piece-he hebrew" lang="he">' + escapeHtml(project.hebrew) + "</p>" : "") +
      (project.body ? '<div class="piece-body">' + project.body + "</div>" : "<p class=\"muted\">" + escapeHtml(ui.contentPending || "[CONTENT PENDING]") + "</p>") +
      (project.id === "shulchan-aruch"
        ? '<div class="actions">' + shulchanActionButtons(cfg, ui, { hubLink: true }) + "</div>"
        : (project.href ? '<p><a class="btn btn-navy" href="' + escapeHtml(project.href) + '">Open</a></p>' : "")) +
      (linked.length ? '<h2>Published pieces</h2><div class="index-list">' + linked.map(editorialCard).join("") + "</div>" : "");
  }

  function initSearch(pieces, ui) {
    const input = document.getElementById("q");
    const mount = document.getElementById("search-results");
    const params = new URLSearchParams(window.location.search);
    if (params.get("q") && input) input.value = params.get("q");

    function draw() {
      const q = (input.value || "").trim();
      if (!q) {
        mount.innerHTML = '<p class="muted">Search titles, parshiyot, topics, and the text of the essays.</p>';
        return;
      }
      const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      const found = pieces.filter(function (p) {
        const hay = (libraryHaystack(p) + " " + (p.sources || []).map(function (s) { return s.t; }).join(" ")).toLowerCase();
        return terms.every(function (term) { return hay.indexOf(term) !== -1; });
      });
      if (!found.length) {
        mount.innerHTML = '<div class="empty"><p>No match for “' + escapeHtml(q) + '”. Try a parashah, a topic, or a word from a verse.</p></div>';
        return;
      }
      mount.innerHTML = found.map(function (p) {
        const safe = escapeHtml(q);
        const title = escapeHtml(p.title).replace(new RegExp(safe.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "ig"), function (m) { return "<mark>" + m + "</mark>"; });
        return '<article class="result"><p class="kicker">' + escapeHtml(p.parsha || p.holiday || p.sefer || "Torah") + '</p><h2><a href="piece.html?id=' + encodeURIComponent(p.id) + '">' + title + "</a></h2>" + (p.excerpt ? "<p>" + escapeHtml(p.excerpt) + "</p>" : "") + "</article>";
      }).join("");
    }
    input.addEventListener("input", draw);
    draw();
  }

  function initResources(pieces, ui) {
    const mount = document.getElementById("resource-mount");
    if (!mount) return;
    const rows = [];
    pieces.forEach(function (p) {
      if ((p.sources || []).length) {
        rows.push({ kind: "Source sheet", title: p.title, note: String((p.sources || []).length) + " sources", href: "piece.html?id=" + encodeURIComponent(p.id) + "#sources" });
      }
      rows.push({ kind: "Print / PDF", title: p.title, note: "Print or save as PDF", href: "piece.html?id=" + encodeURIComponent(p.id) });
      if (hasAudio(p)) {
        rows.push({ kind: "Audio", title: p.title, note: "Recording attached", href: "piece.html?id=" + encodeURIComponent(p.id) + "#listen" });
      }
    });
    rows.unshift({ kind: "Video", title: "Kids videos", note: "", href: "videos.html#kids" });
    mount.innerHTML = rows.length
      ? rows.map(function (row) {
        return '<a class="resource-row" href="' + row.href + '"><span class="tag">' + escapeHtml(row.kind) + "</span><span><strong>" + escapeHtml(row.title) + "</strong>" + (row.note ? '<br><span class="muted">' + escapeHtml(row.note) + "</span>" : "") + '</span><span>Open</span></a>';
      }).join("")
      : '<p class="muted">' + escapeHtml(ui.libraryEmpty || "[CONTENT PENDING]") + "</p>";
  }

  function kidsVideoForPiece(cfg, pieceId) {
    const sections = (cfg && cfg.videoSections) || [];
    for (let si = 0; si < sections.length; si += 1) {
      const videos = sections[si].videos || [];
      for (let vi = 0; vi < videos.length; vi += 1) {
        const v = videos[vi];
        const linked = v.pieceId === pieceId || v.id === pieceId;
        if (linked && youtubeVideoId(v.youtubeId)) return v;
      }
    }
    return null;
  }

  function videoCardMarkup(video, ui) {
    const idOk = Boolean(youtubeVideoId(video.youtubeId));
    const ytId = youtubeVideoId(video.youtubeId);
    const label = video.title || video.occasion || video.parsha || "Video";
    const frame = idOk
      ? '<iframe src="https://www.youtube-nocookie.com/embed/' + escapeHtml(ytId) + '" title="' + escapeHtml(label) + '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>'
      : "";
    const kicker = video.parsha || video.occasion || "";
    const titleHtml = video.title
      ? "<h2>" + escapeHtml(video.title) + "</h2>"
      : (video.occasion ? "<h2>" + escapeHtml(video.occasion) + "</h2>" : "");
    const pieceLink = video.pieceId
      ? '<p><a href="piece.html?id=' + encodeURIComponent(video.pieceId) + '">Read the essay</a></p>'
      : "";
    return (
      '<article class="video-card">' +
        '<div class="video-frame">' + frame + "</div>" +
        '<div class="pad">' +
          (kicker && video.title ? '<p class="kicker">' + escapeHtml(kicker) + "</p>" : "") +
          titleHtml +
          pieceLink +
        "</div>" +
      "</article>"
    );
  }

  function initVideos(cfg, ui) {
    const mount = document.getElementById("video-sections") || document.getElementById("video-grid");
    if (!mount) return;
    const sections = cfg.videoSections;
    if (sections && sections.length) {
      mount.innerHTML = sections.map(function (section) {
        const cards = (section.videos || [])
          .filter(function (video) {
            return youtubeVideoId(video.youtubeId);
          })
          .map(function (video) {
            return videoCardMarkup(video, ui);
          })
          .join("");
        if (!cards) return "";
        return (
          '<section class="video-section" id="' + escapeHtml(section.id || "") + '" aria-labelledby="video-section-' + escapeHtml(section.id || "") + '">' +
            '<header class="video-section-head">' +
              '<h2 id="video-section-' + escapeHtml(section.id || "") + '">' + escapeHtml(section.heading || "") + "</h2>" +
            "</header>" +
            '<div class="video-grid">' + cards + "</div>" +
          "</section>"
        );
      }).join("");
      return;
    }
    mount.innerHTML = '<div class="video-grid">' + (cfg.videos || []).map(function (video) {
      return videoCardMarkup(video, ui);
    }).join("") + "</div>";
  }

  function renderShulchan() {
    const root = document.getElementById("shulchan");
    if (!root || !shulchan) return;
    const raw = (window.location.hash || "").replace(/^#/, "");
    const parts = raw.split("/").filter(Boolean);
    const chelekId = parts[0] || "";
    const simanN = parts[1] ? parseInt(parts[1], 10) : 0;
    const chelek = shulchan.chalakim.find(function (c) { return c.id === chelekId; });

    if (!chelek) {
      root.innerHTML =
        '<div class="chelek-grid">' + shulchan.chalakim.map(function (c) {
          return '<a class="chelek-card" href="#' + c.id + '"><p class="kicker">' + c.count + ' simanim</p><h2>' + escapeHtml(c.name) + '</h2><p class="hebrew" lang="he">' + escapeHtml(c.hebrew) + "</p><p>" + escapeHtml(c.blurb) + "</p></a>";
        }).join("") + "</div>";
      return;
    }

    if (!simanN) {
      const outline = chelek.outline.length ? chelek.outline.map(function (item) {
        return '<a class="resource-row" href="#' + chelek.id + "/" + item.n + '"><span class="tag">Siman ' + item.n + '</span><span><strong>' + escapeHtml(item.en) + '</strong><br><span class="hebrew" lang="he">' + escapeHtml(item.he) + '</span></span><span>' + (item.open ? "Open" : "Shelved") + "</span></a>";
      }).join("") : '<div class="empty"><p>The simanim of ' + escapeHtml(chelek.name) + " are mapped by number. Choose one below. Translation has not begun in this section.</p></div>";
      root.innerHTML =
        '<p class="crumbs"><a href="#">Shulchan Aruch</a> · ' + escapeHtml(chelek.name) + "</p>" +
        '<div class="section-head"><div><p class="kicker">' + chelek.count + ' simanim</p><h2>' + escapeHtml(chelek.name) + '</h2><p class="hebrew" lang="he">' + escapeHtml(chelek.hebrew) + "</p></div></div>" +
        '<form class="search-hero" id="siman-jump"><label class="sr-only" for="siman-n">Siman</label><input class="search-input" id="siman-n" inputmode="numeric" placeholder="Go to siman (1–' + chelek.count + ')"><button class="btn btn-navy" type="submit">Open</button></form>' +
        '<div class="resource-list" style="margin-top:1rem">' + outline + "</div>";
      const form = document.getElementById("siman-jump");
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        const n = parseInt(document.getElementById("siman-n").value, 10);
        if (!n || n < 1 || n > chelek.count) return;
        window.location.hash = chelek.id + "/" + n;
      });
      return;
    }

    const key = chelek.id + "/" + simanN;
    const text = shulchan.texts[key];
    const outlineItem = chelek.outline.find(function (item) { return item.n === simanN; });
    const title = (text && text.title) || (outlineItem && outlineItem.en) || ("Siman " + simanN);
    const hebrew = (text && text.hebrew) || (outlineItem && outlineItem.he) || "";
    const commentaries = shulchan.commentaries[chelek.id] || [];
    let body;
    if (!text) {
      body = '<div class="empty"><p class="forthcoming">Siman ' + simanN + " of " + escapeHtml(chelek.name) + " is on the shelf. Hebrew source, English translation, and notes will be added here. The commentaries below can be selected now; their words are not invented in advance.</p></div>";
    } else {
      body = (text.intro ? '<p class="lede">' + escapeHtml(text.intro) + "</p>" : "") + text.seifim.map(function (seif) {
        return (
          '<section id="seif-' + seif.n + '">' +
            '<div class="section-head"><h3>Se\'if ' + seif.n + "</h3>" +
            '<button class="btn btn-ghost cite-btn" type="button" data-cite="Shulchan Aruch, ' + escapeHtml(chelek.name) + " " + simanN + ":" + seif.n + '">Copy citation</button></div>' +
            '<div class="sa-pair">' +
              '<div class="sa-col"><h3>English</h3><p>' + escapeHtml(seif.mechaberEn) + "</p>" +
                (seif.remaEn ? '<div class="rema"><h3>Rema</h3><p>' + escapeHtml(seif.remaEn) + "</p></div>" : "") +
              "</div>" +
              '<div class="sa-col sa-he"><h3>עברית</h3><p class="hebrew" lang="he">' + escapeHtml(seif.mechaberHe) + "</p>" +
                (seif.remaHe ? '<div class="rema"><h3>רמ״א</h3><p class="hebrew" lang="he">' + escapeHtml(seif.remaHe) + "</p></div>" : "") +
              "</div>" +
            "</div>" +
            (seif.note ? '<p class="callout">' + escapeHtml(seif.note) + "</p>" : "") +
            '<div class="commentary-panel" data-seif="' + seif.n + '"><p class="forthcoming">Choose a commentary. Its Hebrew, translation, and notes will appear in this panel.</p></div>' +
          "</section>"
        );
      }).join("");
    }

    const rail = [];
    const marks = {};
    chelek.outline.forEach(function (item) { marks[item.n] = true; });
    const extras = [simanN - 1, simanN, simanN + 1].filter(function (n) { return n >= 1 && n <= chelek.count; });
    const nums = Object.keys(marks).map(Number).concat(extras);
    Array.from(new Set(nums)).sort(function (a, b) { return a - b; }).forEach(function (n) {
      rail.push('<a class="chip' + (n === simanN ? " is-on" : "") + '" href="#' + chelek.id + "/" + n + '">' + n + "</a>");
    });

    root.innerHTML =
      '<p class="crumbs"><a href="#">Shulchan Aruch</a> · <a href="#' + chelek.id + '">' + escapeHtml(chelek.name) + "</a> · Siman " + simanN + "</p>" +
      '<p class="kicker">Working text</p>' +
      '<div class="section-head"><div><h2>' + escapeHtml(title) + '</h2>' + (hebrew ? '<p class="hebrew" lang="he">' + escapeHtml(hebrew) + "</p>" : "") + "</div>" +
      '<div class="actions"><button class="btn btn-ghost" type="button" id="print-siman">Print / Save as PDF</button>' +
      (simanN > 1 ? '<a class="btn btn-ghost" href="#' + chelek.id + "/" + (simanN - 1) + '">Previous</a>' : "") +
      (simanN < chelek.count ? '<a class="btn btn-navy" href="#' + chelek.id + "/" + (simanN + 1) + '">Next siman</a>' : "") +
      "</div></div>" +
      '<div class="siman-rail" aria-label="Simanim">' + rail.join("") + "</div>" +
      '<div class="commentary-bar" role="group" aria-label="Commentaries">' +
        commentaries.map(function (name) {
          return '<button class="chip" type="button" data-commentary="' + escapeHtml(name) + '" aria-pressed="false">' + escapeHtml(name) + "</button>";
        }).join("") +
      "</div>" +
      body;

    const printBtn = document.getElementById("print-siman");
    if (printBtn) printBtn.addEventListener("click", function () { window.print(); });
    root.querySelectorAll(".cite-btn").forEach(function (button) {
      button.addEventListener("click", function () {
        const cite = button.dataset.cite;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(cite).then(function () { button.textContent = "Copied"; });
        }
      });
    });
    let activeCommentary = "";
    root.querySelectorAll("[data-commentary]").forEach(function (button) {
      button.addEventListener("click", function () {
        const name = button.dataset.commentary;
        activeCommentary = activeCommentary === name ? "" : name;
        root.querySelectorAll("[data-commentary]").forEach(function (b) {
          b.setAttribute("aria-pressed", b.dataset.commentary === activeCommentary ? "true" : "false");
          b.classList.toggle("is-on", b.dataset.commentary === activeCommentary);
        });
        root.querySelectorAll(".commentary-panel").forEach(function (panel) {
          panel.innerHTML = activeCommentary
            ? "<p><strong>" + escapeHtml(activeCommentary) + "</strong> on this se'if will be set here in Hebrew beside an English translation and a short note. Nothing is filled in until that work is done.</p>"
            : '<p class="forthcoming">Choose a commentary. Its Hebrew, translation, and notes will appear in this panel.</p>';
        });
      });
    });
  }

  function initSubscribeForms(cfg, ui) {
    document.querySelectorAll(".js-subscribe").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        const note = form.querySelector(".form-note");
        const data = {
          name: (form.querySelector("[name=name]") || {}).value || "",
          email: (form.querySelector("[name=email]") || {}).value || ""
        };
        if (!data.email || data.email.indexOf("@") === -1) {
          note.textContent = "Enter an email address.";
          return;
        }
        if (!cfg.subscribeEndpoint) {
          note.textContent = ui.newsletterInactive || "Newsletter signup is not connected yet.";
          return;
        }
        note.textContent = "Sending…";
        fetch(cfg.subscribeEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(data)
        }).then(function (res) {
          if (!res.ok) throw new Error("bad");
          note.textContent = "Thank you. You are on the list.";
          form.reset();
        }).catch(function () {
          note.textContent = "The list could not be reached. Nothing was confirmed. Try again later.";
        });
      });
    });
  }

  function startApp() {
    const r = runtime();
    const cfg = r.cfg;
    const ui = r.ui;
    const site = r.site;
    const pieces = r.pieces;
    const projects = r.projects;
    initNav(cfg);
    const routes = {
      home: function () { initHome(pieces, projects, ui, site); },
      library: function () { initLibrary(pieces, cfg, ui); },
      articles: function () { initArticles(pieces, ui); },
      piece: function () { initPiece(pieces, cfg, ui); },
      projects: function () { initProjects(projects, cfg); },
      project: function () { initProject(projects, pieces, ui, cfg); },
      search: function () { initSearch(pieces, ui); },
      resources: function () { initResources(pieces, ui); },
      videos: function () { initVideos(cfg, ui); }
    };
    if (routes[page]) routes[page]();
    if (page === "shulchan") {
      const urls = shulchanUrls(cfg);
      const root = document.getElementById("shulchan");
      if (urls.hasReader && root) {
        root.innerHTML =
          '<p class="actions"><a class="btn btn-navy" href="' + escapeHtml(urls.reader) + '">' +
          escapeHtml(cfg.shulchanAruchReaderLabel || "Open translation") + "</a></p>";
      } else if (root) {
        window.addEventListener("hashchange", renderShulchan);
        renderShulchan();
      }
    }
    initSubscribeForms(cfg, ui);
  }

  document.addEventListener("diburim:ready", startApp);
})();
