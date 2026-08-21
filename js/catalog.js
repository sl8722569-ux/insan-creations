fetch("products.json")
  .then(function (r) { return r.json(); })
  .then(function (data) {
    var box = document.getElementById("catalog");
    if (!box) return;
    var list = data.products || [];
    if (!list.length) {
      box.innerHTML = "<p>No creations listed yet.</p>";
      return;
    }
    list.forEach(function (p) {
      var el = document.createElement("article");
      el.className = "card";
      var href = p.page || "#";
      var icon = p.icon || ("icons/" + (p.id || "") + "-192.png");
      if (p.id === "jarvis" || p.id === "jarvis-web") icon = "icons/jarvis-192.png";
      if (p.id === "study-assistant") icon = "icons/study-assistant-192.png";
      if (p.id === "univista") icon = "icons/univista-192.png";
      if (p.id === "studio-site") icon = "icons/insan-creations-192.png";
      if (String(p.page || "").indexOf("products/") === 0) {
        icon = "../" + icon.replace(/^icons/, "icons");
        // catalog on home uses icons/ from root; on products pages catalog isn't used
      }
      var iconSrc = "icons/";
      if (p.id === "jarvis" || p.id === "jarvis-web") iconSrc += "jarvis-192.png";
      else if (p.id === "study-assistant") iconSrc += "study-assistant-192.png";
      else if (p.id === "univista") iconSrc += "univista-192.png";
      else iconSrc += "insan-creations-192.png";
      el.innerHTML =
        '<img class="app-icon" src="' + iconSrc + '" alt="" width="64" height="64" />' +
        '<p class="badge">' + (p.kind || "Creation") + " · " + (p.status || "") + "</p>" +
        "<h3>" + (p.name || "") + "</h3>" +
        "<p>" + (p.blurb || "") + "</p>" +
        (p.platforms ? '<p class="badge">' + p.platforms + "</p>" : "") +
        '<a class="btn" href="' + href + '">Open</a>';
      box.appendChild(el);
    });
  })
  .catch(function () {
    var box = document.getElementById("catalog");
    if (box) box.innerHTML = "<p>Could not load catalogue. Open products/jarvis.html directly.</p>";
  });
