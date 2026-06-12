#!/usr/bin/env python3
"""Generate favicon assets from img/favicon/favicon.png."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

SITE = Path(__file__).parent
FAVICON_DIR = SITE / "img" / "favicon"
SOURCE_CANDIDATES = (
    FAVICON_DIR / "fav.png",
    FAVICON_DIR / "favicon.png",
)
FALLBACK = SITE / "img" / "logo-en" / "logo-black.png"


def _load_source() -> tuple[Image.Image, Path]:
    path = next((p for p in SOURCE_CANDIDATES if p.exists()), None)
    if path is None:
        path = FALLBACK if FALLBACK.exists() else None
    if path is None:
        raise SystemExit(
            f"No favicon source found. Upload fav.png (or favicon.png) to {FAVICON_DIR}/"
        )
    if path == FALLBACK:
        print(f"  note: using fallback {FALLBACK} — upload fav.png to {FAVICON_DIR}/")
    else:
        print(f"  using {path.relative_to(SITE)}")
    img = Image.open(path).convert("RGBA")
    side = max(img.size)
    canvas = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    offset = ((side - img.width) // 2, (side - img.height) // 2)
    canvas.paste(img, offset, img)
    return canvas, path


def _square(img: Image.Image, size: int) -> Image.Image:
    return img.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    src, _ = _load_source()
    ico_sizes = [16, 32, 48]
    ico_images = [_square(src, s) for s in ico_sizes]
    ico_images[0].save(
        SITE / "favicon.ico",
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=ico_images[1:],
    )
    _square(src, 192).save(SITE / "icon.png", format="PNG", optimize=True)
    _square(src, 180).save(SITE / "apple-touch-icon.png", format="PNG", optimize=True)
    print("  wrote favicon.ico, icon.png, apple-touch-icon.png")


if __name__ == "__main__":
    main()
