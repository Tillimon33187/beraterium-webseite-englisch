#!/usr/bin/env python3
"""Convert uploaded images to WebP and generate responsive variants."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

SITE = Path(__file__).parent
IMG_DIR = SITE / "img"
WIDTHS = (480, 960, 1440)
QUALITY = 82
DIAGRAM_QUALITY = 92
SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _save_meta(path: Path, width: int, height: int) -> None:
    rel = path.relative_to(SITE).as_posix()
    meta_path = SITE / f"{rel}.meta.json"
    meta_path.write_text(
        json.dumps({"width": width, "height": height}, indent=2) + "\n",
        encoding="utf-8",
    )


def process_image(path: Path) -> None:
    if path.suffix.lower() not in SOURCE_EXTS:
        return
    if re_suffix_width(path.stem):
        return
    if path.parent.name in ("logo", "logo-en"):
        return
    quality = DIAGRAM_QUALITY if "methode" in path.parts else QUALITY
    try:
        with Image.open(path) as im:
            im = im.convert("RGB") if im.mode in ("RGBA", "P", "LA") else im
            orig_w, orig_h = im.size
            webp_path = path.with_suffix(".webp")
            if path.suffix.lower() != ".webp":
                im.save(webp_path, "WEBP", quality=quality, method=6)
                if path != webp_path:
                    path.unlink(missing_ok=True)
                path = webp_path
            else:
                im.save(path, "WEBP", quality=quality, method=6)
            _save_meta(path, orig_w, orig_h)
            for target_w in WIDTHS:
                if orig_w <= target_w:
                    continue
                ratio = target_w / orig_w
                new_size = (target_w, max(1, round(orig_h * ratio)))
                resized = im.resize(new_size, Image.Resampling.LANCZOS)
                variant = path.with_name(f"{path.stem}-{target_w}w.webp")
                resized.save(variant, "WEBP", quality=quality, method=6)
                _save_meta(variant, new_size[0], new_size[1])
            print(f"  optimized {path.relative_to(SITE)}")
    except Exception as exc:
        print(f"  skip {path}: {exc}")


def re_suffix_width(stem: str) -> bool:
    import re

    return bool(re.search(r"-\d+w$", stem))


def main() -> None:
    if not IMG_DIR.exists():
        print("No img/ directory.")
        return
    print("Optimizing images...")
    for path in sorted(IMG_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in SOURCE_EXTS:
            process_image(path)
    print("Done.")


if __name__ == "__main__":
    main()
