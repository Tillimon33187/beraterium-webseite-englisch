#!/usr/bin/env python3
"""Deprecated. Old BLOCK dropped Consent Mode + linker. Use site/scripts/refresh_ga4_head.py."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "site" / "scripts"
sys.path.insert(0, str(ROOT))
from refresh_ga4_head import main as refresh_main  # noqa: E402

if __name__ == "__main__":
    print("inject_ga4.py → refresh_ga4_head.py --root site-en", file=sys.stderr)
    site_en = Path(__file__).resolve().parents[1]
    sys.argv = [str(ROOT / "refresh_ga4_head.py"), "--root", str(site_en), *sys.argv[1:]]
    raise SystemExit(refresh_main())
