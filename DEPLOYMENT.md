# Deployment — English site (www.beraterium.com)

Based on [codepo8/hosting-on-github-template](https://github.com/codepo8/hosting-on-github-template).

## Live setup

- **Canonical URL:** `https://www.beraterium.com/`
- **GitHub repo:** [beraterium-webseite-englisch](https://github.com/Tillimon33187/beraterium-webseite-englisch)
- **Hosting:** Plesk (OpusX) — same origin as legacy `en.beraterium.de`
- **Redirect (Plesk/nginx):** `en.beraterium.de/*` → `https://www.beraterium.com/$1` (301)

## Build locally

```bash
cd Webseite/site-en
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python _gen_pages.py
```

## Cross-linking with German site

- DE site: `https://www.beraterium.de/` (`Webseite/site/`)
- Language switcher + hreflang mapping: `_i18n.py` (kept in sync in both repos)
- Slug mapping documented in `_i18n.py` (`STATIC_ROUTE_MAP`, `BLOG_SLUG_MAP`)

## Content sources

| Type | Path |
|------|------|
| Generated pages | `_gen_pages.py` |
| Blog | `content/blog/*.md` |
| Team | `content/team/*.yaml` |
| Legal fragments | `_content/*.html` |
| Homepage (hand-maintained) | `index.html` (SEO/analytics/teasers patched by generator) |

Copy glossary: `EN_COPY_GLOSSARY.md`
