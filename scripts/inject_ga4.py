#!/usr/bin/env python3
"""Inject GA4 snippet after CookieYes on all public EN HTML pages."""
from __future__ import annotations

from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
ANCHOR = "  <!-- End cookieyes banner -->\n"
START = "  <!-- GA4_START -->\n"
END = "  <!-- GA4_END -->\n"
BLOCK = (
    START
    + """  <!-- Google tag (gtag.js) — loads only after Analytics consent (CookieYes) -->
  <script type="text/plain" data-cookieyes="analytics" async src="https://www.googletagmanager.com/gtag/js?id=G-BM435GHE6W"></script>
  <script type="text/plain" data-cookieyes="analytics">
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-BM435GHE6W');
  </script>
"""
    + END
)
SKIP = {SITE / "admin" / "index.html"}


def patch(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    if "G-BM435GHE6W" in html:
        if START in html:
            i = html.find(START)
            j = html.find(END, i)
            if j < 0:
                return "skip-broken"
            path.write_text(html[:i] + BLOCK + html[j + len(END) :], encoding="utf-8")
            return "updated"
        return "already"
    if ANCHOR not in html:
        return "no-anchor"
    path.write_text(html.replace(ANCHOR, ANCHOR + BLOCK, 1), encoding="utf-8")
    return "inserted"


def main() -> None:
    counts: dict[str, int] = {}
    for path in sorted(SITE.glob("**/*.html")):
        if path in SKIP or "/.venv/" in str(path) or "/_content/" in str(path):
            continue
        status = patch(path)
        counts[status] = counts.get(status, 0) + 1
    print(counts)


if __name__ == "__main__":
    main()
