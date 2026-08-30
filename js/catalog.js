fetch("products.json")
  .then(function (r) { return r.json(); })
  .then(function (data) {
    var box = document.getElementById("catalog");
    var gbox = document.getElementById("catalog-games");
    if (!box && !gbox) return;
    var list = data.products || [];
    if (!list.length) {
      if (box) box.innerHTML = "<p>No creations listed yet.</p>";
      return;
    }
    function iconFor(p) {
      if (p.id === "jarvis" || p.id === "jarvis-web") return "icons/jarvis-192.png";
      if (p.id === "study-assistant") return "icons/study-assistant-192.png";
      if (p.id === "univista") return "icons/univista-192.png";
      if (p.id === "language-ai") return "icons/language-ai-192.png";
      if (p.id === "nexcode") return "icons/nexcode-192.png";
      if (p.id === "insan-cricket") return "icons/insan-cricket-192.png";
      return "icons/insan-creations-192.png";
    }
    function downloadBtns(p) {
      var dls = p.downloads || [];
      if (!dls.length) {
        return '<a class="btn" href="' + (p.page || "#") + '">Open</a>';
      }
      return '<div class="btn-row">' + dls.map(function (d) {
        var cls = d.kind === "web" ? "btn ghost" : "btn";
        var mark = ' data-download="' + (p.id || "") + '" data-kind="' + (d.kind || "") + '"';
        var extra = d.kind === "zip" || d.kind === "apk" ? " download" : "";
        return '<a class="' + cls + '" href="' + d.href + '"' + mark + extra + ">" + d.label + "</a>";
      }).join("") + "</div>";
    }
    function card(p) {
      var el = document.createElement("article");
      el.className = "card";
      el.innerHTML =
        '<img class="app-icon" src="' + iconFor(p) + '" alt="" width="64" height="64" />' +
        '<p class="badge">' + (p.kind || "Creation") + " · " + (p.status || "") + "</p>" +
        "<h3>" + (p.name || "") + "</h3>" +
        "<p>" + (p.blurb || "") + "</p>" +
        (p.platforms ? '<p class="badge">' + p.platforms + "</p>" : "") +
        downloadBtns(p) +
        (p.page ? '<p style="margin-top:.7rem"><a href="' + p.page + '">Product page</a></p>' : "");
      return el;
    }
    var games = list.filter(function (p) { return (p.section || "") === "game"; });
    var apps = list.filter(function (p) { return (p.section || "") !== "game"; });
    if (box) {
      box.innerHTML = "";
      if (!apps.length) box.innerHTML = "<p>No apps listed yet.</p>";
      else apps.forEach(function (p) { box.appendChild(card(p)); });
    }
    if (gbox) {
      gbox.innerHTML = "";
      if (!games.length) gbox.innerHTML = "<p>No games listed yet.</p>";
      else games.forEach(function (p) { gbox.appendChild(card(p)); });
    }
  })
  .catch(function () {
    var box = document.getElementById("catalog");
    if (box) box.innerHTML = "<p>Could not load catalogue. Open products/jarvis.html directly.</p>";
  });
