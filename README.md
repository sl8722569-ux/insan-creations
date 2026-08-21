# INSAN CREATIONS — studio website

Independent site for **INSAN CREATIONS** (not the GitHub project UI).

- Home: catalogue of creations (`products.json`)
- First product: **J.A.R.V.I.S [EARLY ACCESS]**
- Add a new creation: append an object to `products.json` and add `products/<id>.html`

## Add another product later

```json
{
  "id": "new-app",
  "name": "New App",
  "status": "Soon",
  "blurb": "Short description.",
  "page": "products/new-app.html"
}
```

Then copy `products/jarvis.html` as a template.

## Local preview

Open `index.html` in a browser. For `products.json` fetch, use any static server if the file is blocked as `file://`.
