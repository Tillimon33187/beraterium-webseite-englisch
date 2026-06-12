# GitHub Pages Deployment — English site (en.beraterium.de)

Based on [codepo8/hosting-on-github-template](https://github.com/codepo8/hosting-on-github-template).

## Quick Setup

1. Create a **separate** GitHub repository (e.g. `beraterium-site-en`).
2. Push the contents of `Webseite/site-en/` to the `main` branch root.
3. In **Settings → Pages**:
   - Source: **Deploy from a branch**
   - Branch: `main`, folder: **/ (root)**
4. Add DNS: `CNAME` for `en.beraterium.de` → `{username}.github.io` (file `CNAME` included).
5. Site URL: `https://en.beraterium.de/`

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
| Homepage (hand-maintained) | `index.html` (team/blog teasers patched by generator) |

Copy glossary: `EN_COPY_GLOSSARY.md`
