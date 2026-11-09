#!/usr/bin/env python3
"""Deprecated. Old BLOCK dropped Consent Mode + linker. Use refresh_ga4_head.py."""
from __future__ import annotations

import sys
from pathlib import Path

from refresh_ga4_head import main as refresh_main


if __name__ == "__main__":
    print("inject_ga4.py → refresh_ga4_head.py (Consent Mode + localhost guard)", file=sys.stderr)
    sys.argv = [str(Path(__file__).with_name("refresh_ga4_head.py")), *sys.argv[1:]]
    raise SystemExit(refresh_main())
