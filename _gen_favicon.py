#!/usr/bin/env python3
"""Generate favicon assets from img/favicon/ (light + dark)."""
from __future__ import annotations

import struct
import subprocess
from pathlib import Path

SITE = Path(__file__).parent
FAVICON_DIR = SITE / "img" / "favicon"
LIGHT_SOURCE = FAVICON_DIR / "fav.png"
DARK_SOURCE = FAVICON_DIR / "fav_white.png"
FALLBACK = SITE / "img" / "logo-en" / "logo-black.png"


def _resolve_light() -> Path:
    if LIGHT_SOURCE.exists():
        return LIGHT_SOURCE
    if FALLBACK.exists():
        print(f"  note: light favicon fallback {FALLBACK}")
        return FALLBACK
    raise SystemExit(f"No light favicon — upload fav.png to {FAVICON_DIR}/")


def _png_size(data: bytes) -> tuple[int, int]:
    return struct.unpack(">II", data[16:24])


def _build_ico(pngs: list[bytes]) -> bytes:
    count = len(pngs)
    header = struct.pack("<HHH", 0, 1, count)
    entries: list[bytes] = []
    blobs: list[bytes] = []
    offset = 6 + 16 * count
    for png in pngs:
        w, h = _png_size(png)
        width = 0 if w >= 256 else w
        height = 0 if h >= 256 else h
        entries.append(
            struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, len(png), offset)
        )
        blobs.append(png)
        offset += len(png)
    return header + b"".join(entries) + b"".join(blobs)


def _sips_resize(src: Path, size: int, out: Path) -> None:
    subprocess.run(
        ["sips", "-z", str(size), str(size), str(src), "--out", str(out)],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def _write_ico(src: Path, out: Path, tmp: Path) -> None:
    ico_pngs: list[bytes] = []
    for size in (16, 32, 48):
        path = tmp / f"{out.stem}-{size}.png"
        _sips_resize(src, size, path)
        ico_pngs.append(path.read_bytes())
    out.write_bytes(_build_ico(ico_pngs))


def _generate_with_sips(src: Path, ico: Path, icon: Path, apple: Path | None) -> None:
    tmp = SITE / ".favicon-tmp"
    tmp.mkdir(exist_ok=True)
    try:
        _write_ico(src, ico, tmp)
        _sips_resize(src, 192, icon)
        if apple is not None:
            _sips_resize(src, 180, apple)
    finally:
        for f in tmp.glob("*.png"):
            f.unlink()
        if tmp.exists():
            tmp.rmdir()


def _generate_with_pillow(
    src: Path, ico: Path, icon: Path, apple: Path | None
) -> None:
    from PIL import Image

    img = Image.open(src).convert("RGBA")
    side = max(img.size)
    canvas = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    offset = ((side - img.width) // 2, (side - img.height) // 2)
    canvas.paste(img, offset, img)

    def square(size: int) -> Image.Image:
        return canvas.resize((size, size), Image.Resampling.LANCZOS)

    ico_sizes = [16, 32, 48]
    ico_images = [square(s) for s in ico_sizes]
    ico_images[0].save(
        ico,
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=ico_images[1:],
    )
    square(192).save(icon, format="PNG", optimize=True)
    if apple is not None:
        square(180).save(apple, format="PNG", optimize=True)


def _generate_variant(
    src: Path, ico: Path, icon: Path, apple: Path | None = None
) -> None:
    try:
        _generate_with_pillow(src, ico, icon, apple)
    except ImportError:
        _generate_with_sips(src, ico, icon, apple)


def main() -> None:
    light = _resolve_light()
    print(f"  light: {light.relative_to(SITE)}")
    _generate_variant(
        light,
        SITE / "favicon.ico",
        SITE / "icon.png",
        SITE / "apple-touch-icon.png",
    )

    if DARK_SOURCE.exists():
        print(f"  dark:  {DARK_SOURCE.relative_to(SITE)}")
        _generate_variant(
            DARK_SOURCE,
            SITE / "favicon-dark.ico",
            SITE / "icon-dark.png",
        )
    else:
        print(f"  dark:  skipped (upload fav_white.png to {FAVICON_DIR}/)")

    print("  wrote favicon.ico, icon.png, apple-touch-icon.png")
    if DARK_SOURCE.exists():
        print("  wrote favicon-dark.ico, icon-dark.png")


if __name__ == "__main__":
    main()
