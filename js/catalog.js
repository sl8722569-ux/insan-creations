fetch("products.json")
  .then(function (r) { return r.json(); })
  .then(function (data) {
    var box = document.getElementById("catalog");
    if (!box) return;
    (data.products || []).forEach(function (p) {
      var el = document.createElement("article");
      el.className = "card";
      el.innerHTML =
        '<p class="badge">' + (p.status || "") + "</p>" +
        "<h3>" + p.name + "</h3>" +
        "<p>" + (p.blurb || "") + "</p>" +
        '<a class="btn" href="' + p.page + '">Open</a>';
      box.appendChild(el);
    });
    if (!(data.products || []).length) {
      box.innerHTML = "<p>No products listed yet.</p>";
    }
  })
  .catch(function () {
    var box = document.getElementById("catalog");
    if (box) {
      box.innerHTML =
        '<article class="card"><h3>J.A.R.V.I.S</h3><p>Personal assistant (Early Access).</p>' +
        '<a class="btn" href="products/jarvis.html">Open</a></article>';
    }
  });
