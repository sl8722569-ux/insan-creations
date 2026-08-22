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
    if (script && script.getAttribute("data-app")) return script.getAttribute("data-app");
    var host = (location.hostname || "") + (location.pathname || "");
    host = host.toLowerCase();
    if (host.indexOf("univista") >= 0) return "univista";
    if (host.indexOf("jarvis") >= 0) return "jarvis";
    if (host.indexOf("study-assistant") >= 0 || host.indexOf("ai-study") >= 0) return "study-assistant";
    var p = (location.pathname || "").toLowerCase();
    if (p.indexOf("univista") >= 0) return "univista";
    if (p.indexOf("jarvis") >= 0) return "jarvis";
    if (p.indexOf("study") >= 0) return "study-assistant";
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
