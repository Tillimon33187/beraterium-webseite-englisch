#!/usr/bin/env python3
"""Replace the Consent-Mode GA4 head on all HTML pages (no full _gen_pages rebuild).

Usage:
  python3 Webseite/site/scripts/refresh_ga4_head.py
  python3 Webseite/site/scripts/refresh_ga4_head.py --root Webseite/site-en
  python3 Webseite/site/scripts/refresh_ga4_head.py --selfcheck
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
SITE_DE = SCRIPT.parents[1]
GEN_PAGES = SITE_DE / "_gen_pages.py"
HEAD_RE = re.compile(
    r"  <!-- Google Consent Mode v2 \+ GA4 \(CookieYes (?:setzt|sets) analytics_storage\) -->\n"
    r"(?:  <script\b[\s\S]*?</script>\n)+",
)
LOCAL_REF = re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?\b", re.I)


def load_head(gen_pages: Path = GEN_PAGES) -> str:
    text = gen_pages.read_text(encoding="utf-8")
    mid = text.find("GA4_MEASUREMENT_ID =")
    start = text.find("GA4_ANALYTICS_HEAD =")
    end = text.find("\nNAV =", start)
    if mid < 0 or start < 0 or end < 0:
        raise RuntimeError(f"GA4 constants not found in {gen_pages}")
    ns: dict[str, object] = {}
    exec(text[mid:end], ns)  # noqa: S102 — slice of our generator, not user input
    head = ns.get("GA4_ANALYTICS_HEAD")
    if not isinstance(head, str) or "brtGa4Local" not in head:
        raise RuntimeError("GA4_ANALYTICS_HEAD missing brtGa4Local guard")
    return head if head.endswith("\n") else head + "\n"


def replace_head(html: str, head: str) -> str | None:
    m = HEAD_RE.search(html)
    if not m:
        return None
    return html[: m.start()] + head + html[m.end() :]


def patch_tree(root: Path, head: str) -> dict[str, int]:
    counts = {"updated": 0, "unchanged": 0, "no-block": 0}
    for path in sorted(root.rglob("*.html")):
        html = path.read_text(encoding="utf-8")
        new = replace_head(html, head)
        if new is None:
            counts["no-block"] += 1
            continue
        if new == html:
            counts["unchanged"] += 1
            continue
        path.write_text(new, encoding="utf-8")
        counts["updated"] += 1
    return counts


def selfcheck() -> None:
    head = load_head()
    assert "brtGa4Local" in head
    assert "ignore_referrer" in head
    assert "127.0.0.1" in head
    sample = (
        "  <!-- End cookieyes banner -->\n"
        "  <!-- Google Consent Mode v2 + GA4 (CookieYes setzt analytics_storage) -->\n"
        "  <script>old()</script>\n"
        "  <script async src='https://www.googletagmanager.com/gtag/js?id=G-BM435GHE6W'></script>\n"
        "  <script>gtag('config', 'G-BM435GHE6W');</script>\n"
        "  <title>x</title>\n"
    )
    out = replace_head(sample, head)
    assert out is not None
    assert "brtGa4Local" in out
    assert "gtag/js?id=G-BM435GHE6W" in out
    assert sample.split("<title>")[0] != out.split("<title>")[0]
    assert "<title>x</title>" in out
    assert LOCAL_REF.search("http://127.0.0.1:8765/preise/")
    assert LOCAL_REF.search("http://localhost:8766/")
    assert not LOCAL_REF.search("https://www.google.com/")
    assert not LOCAL_REF.search("https://www.beraterium.de/")
    print("ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=SITE_DE)
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args()
    if args.selfcheck:
        selfcheck()
        return 0
    head = load_head()
    counts = patch_tree(args.root.resolve(), head)
    print(counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
