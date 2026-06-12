# Beraterium Static Website

## Purpose

Static HTML/CSS/JS website for Beraterium, based on [h5bp/html5-boilerplate-template](https://github.com/h5bp/html5-boilerplate-template).

## Tech Stack

- HTML5 semantic markup
- Vanilla CSS (mobile-first, H5BP base in `css/style.css`)
- Vanilla JavaScript (no framework)
- Optional: Webpack dev server (`npm start`) for local development
- Deployment: GitHub Pages (see `DEPLOYMENT.md`)

## Project Structure

```
Webseite/site/
├── index.html              # Home page (hero slideshow)
├── page-template.html      # Copy for new inner pages
├── 404.html                # Not-found page
├── partials/               # Header, footer, asset snippets (copy into pages)
├── css/
│   ├── brt.css             # Site-wide Beraterium design system
│   ├── brt-fallback.css    # Fallback when brt.css fails to load (file://)
│   └── style.css           # H5BP base (optional)
├── js/
│   ├── brt-init.js         # CSS load fallback detection
│   ├── brt-site.js         # Header, nav, scroll reveals (all pages)
│   ├── brt-hero.js         # Hero slideshow (index.html only)
│   └── app.js              # H5BP entry (legacy)
├── ueber-uns/index.html
├── team/index.html
├── mission-vision/index.html
├── methode/index.html
├── angebote/index.html
├── angebote/startups/index.html
├── angebote/kmu/index.html
├── angebote/solo/index.html
├── risikoradar/index.html
├── blog/index.html
├── kontakt/index.html
├── impressum/index.html
├── datenschutz/index.html
├── agb/index.html
├── danke/index.html
├── _gen_pages.py           # Regenerate inner pages from briefings
└── DEPLOYMENT.md
```

## New Page Checklist

1. Copy `page-template.html` to `ordner/index.html` (or duplicate `methode/index.html`).
2. Set `body class="brt-page brt-page--inner"` and `header` with `site-header--solid`.
3. Include assets from `partials/head-assets-subpage.html` (`../css/brt.css`, etc.).
4. Load `../js/brt-site.js` only — **not** `brt-hero.js`.
5. Copy header/footer from `partials/` and adjust `../` paths if nested deeper.
6. Add page content inside `<div class="brt"><main>…</main></div>`.
7. Briefing copy lives in `Webseite/Briefing/Seiten/`.

## Reference Repositories

Local clones live in `_refs/` at the project root:

| Repo | Purpose |
|------|---------|
| `html5-boilerplate-template` | Site base |
| `html5-boilerplate` | Full H5BP documentation and patterns |
| `cursor-best-practices` | Cursor rules structure |
| `awesome-cursorrules` | Community rule examples |
| `hosting-on-github-template` | GitHub Pages deployment |
| `github-page-pwa` | Optional PWA / offline support |

## Build & Dev

```bash
cd Webseite/site
npm install
npm start    # webpack dev server
npm run build  # output to dist/
```

For GitHub Pages, serve files from the repository root (no build step required).

## CMS & Content Build

Blog articles, team profiles, and images are managed via **Decap CMS** at `/admin/`. Full spec: `Webseite/Briefing/Seiten/18_BACKEND_CMS.md`.

```bash
cd Webseite/site
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python _optimize_images.py   # optional: WebP + srcset
.venv/bin/python _gen_pages.py         # regenerates blog, team, sitemap, homepage teaser
```

Content sources: `content/blog/*.md`, `content/team/*.yaml`, `img/`.

## Conventions

- German UI copy (`lang="de"`)
- BEM-style class names for components (e.g. `site-header__nav`)
- Semantic HTML: `header`, `main`, `nav`, `footer`
- Mobile-first responsive CSS
- Scripts at end of `<body>`, deferred loading where possible
