#!/usr/bin/env python3
"""Refresh privacy/index.html body from _content without full site rebuild."""
from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
HTML = SITE / "privacy/index.html"
SECTIONS = SITE / "_content/datenschutz_sections.html"


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    sections = SECTIONS.read_text(encoding="utf-8")
    pattern = r'(<h1 id="legal-title" class="brt-h2">Privacy policy</h1>\n)(.*?)(\n      </div>\n    </section>)'
    new_html, n = re.subn(pattern, r"\1" + sections + r"\3", html, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit(f"pattern miss ({n})")
    HTML.write_text(new_html, encoding="utf-8")
    print("privacy refreshed")


if __name__ == "__main__":
    main()
