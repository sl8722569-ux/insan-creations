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
      el.innerHTML =
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
