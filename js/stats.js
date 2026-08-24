/* INSAN CREATIONS live stats — fire-and-forget counters for the owner dashboard. */
(function () {
  var NS = "https://abacus.jasoncameron.dev/hit/insan-creations-sl8722569/";
  var script = document.currentScript;
  function ping(key) {
    if (!key) return;
    try {
      var img = new Image();
      img.src = NS + encodeURIComponent(key) + "?t=" + Date.now();
    } catch (e) { /* ignore */ }
  }
  function inferApp() {
    var href = ((location.href || "") + " " + (location.pathname || "")).toLowerCase();
    // Studio catalogue / product pages are the website, not the apps.
    if (href.indexOf("insan-creations") >= 0) return "studio";
    if (href.indexOf("jarvis-assitant") >= 0 || href.indexOf("/webapp") >= 0) return "jarvis";
    if (href.indexOf("universal-language") >= 0) return "language-ai";
    if (href.indexOf("/nexcode") >= 0) return "nexcode";
    if (href.indexOf("univista") >= 0) return "univista";
    if (href.indexOf("ai-study-assistant") >= 0) return "study-assistant";
    if (script && script.getAttribute("data-app")) return script.getAttribute("data-app");
    return "studio";
  }
  var app = inferApp();
  try {
    if (!localStorage.getItem("ic-person")) {
      localStorage.setItem("ic-person", String(Date.now()));
      ping("unique-people");
    }
  } catch (e) {
    ping("unique-people");
  }
  try {
    if (!sessionStorage.getItem("ic-open")) {
      sessionStorage.setItem("ic-open", "1");
      ping("site-opens");
    }
  } catch (e) {
    ping("site-opens");
  }
  try {
    var pageKey = "sess-open-" + app;
    if (!sessionStorage.getItem(pageKey)) {
      sessionStorage.setItem(pageKey, "1");
      ping("open-" + app);
    }
  } catch (e) {
    ping("open-" + app);
  }
  ping("page-views");

  window.INSAN_STATS = {
    download: function (which, kind) {
      ping("dl-total");
      ping("dl-" + (which || app));
      if (kind) ping("dl-" + (which || app) + "-" + kind);
    },
    open: function (which) {
      ping("open-" + (which || app));
    }
  };

  document.addEventListener("click", function (ev) {
    var el = ev.target && ev.target.closest ? ev.target.closest("a,button") : null;
    if (!el) return;
    var marked = el.getAttribute("data-download");
    if (el.getAttribute("data-donate")) {
      ping("donate-clicks");
    }
    if (marked) {
      window.INSAN_STATS.download(marked, el.getAttribute("data-kind") || "");
      return;
    }
    if (el.id === "dl") {
      window.INSAN_STATS.download("jarvis", "");
      return;
    }
    var href = (el.getAttribute("href") || "").toLowerCase();
    if (href.indexOf("/releases/") >= 0 || href.indexOf("download") >= 0) {
      var which = "jarvis";
      if (href.indexOf("univista") >= 0) which = "univista";
      else if (href.indexOf("study") >= 0) which = "study-assistant";
      window.INSAN_STATS.download(which, "");
    }
  }, true);
})();
