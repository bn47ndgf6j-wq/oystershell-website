# oystershell.co.uk

Static website for Oystershell Limited, hosted on Cloudflare Pages.

- `src/site.html` is the design source: every page in one file, so it can be previewed on its own.
- `build.py` splits it into real pages and adds SEO (titles, descriptions, canonical URLs, Open Graph, schema.org JSON-LD, FAQ), plus `sitemap.xml`, `robots.txt`, `llms.txt`, `_headers` and `_redirects`.
- `assets/` holds the logo and icons; `images/` holds the page photos (see `images/SHOT-LIST.md`).
- `public/` is the built site that Cloudflare serves. Rebuild with `python3 build.py` after any change and commit the result.

## Cloudflare Pages settings
- Framework preset: None
- Build command: (leave empty)
- Build output directory: `public`
- Production branch: `main`

## Before launch
- Set `DRAFT = False` in `build.py`.
- Replace `FORM_ID` in `build.py` with the Formspree form ID.
