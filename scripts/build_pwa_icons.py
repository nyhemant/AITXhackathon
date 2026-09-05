#!/usr/bin/env python3
"""Build Field Trip Kit PWA icons from the existing 1Less mark.

No generated animal art. Re-run after the mark changes:

  python3 scripts/build_pwa_icons.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image


REPO = Path(__file__).resolve().parents[1]
MARK = REPO / "1LessMark.png"
START_HERO = REPO / "static" / "start" / "hero-giraffe.jpg"
TEACH = REPO / "static" / "start" / "teach-card.jpg"
OUT = REPO / "static" / "pwa"
CREAM = (246, 243, 236, 255)  # --paper #f6f3ec


def _fit_mark(mark: Image.Image, canvas: int, fill: float) -> Image.Image:
    out = Image.new("RGBA", (canvas, canvas), CREAM)
    side = max(1, int(canvas * fill))
    fitted = mark.resize((side, side), Image.Resampling.LANCZOS)
    if fitted.mode != "RGBA":
        fitted = fitted.convert("RGBA")
    x = (canvas - side) // 2
    y = (canvas - side) // 2
    out.alpha_composite(fitted, (x, y))
    return out


def _cover(src: Image.Image, width: int, height: int) -> Image.Image:
    im = src.convert("RGB")
    scale = max(width / im.width, height / im.height)
    new_w = max(width, int(im.width * scale + 0.5))
    new_h = max(height, int(im.height * scale + 0.5))
    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - width) // 2
    top = (new_h - height) // 2
    return im.crop((left, top, left + width, top + height))


def main() -> None:
    if not MARK.is_file():
        raise SystemExit(f"missing mark: {MARK}")
    OUT.mkdir(parents=True, exist_ok=True)
    mark = Image.open(MARK).convert("RGBA")

    any_192 = _fit_mark(mark, 192, 0.92)
    any_512 = _fit_mark(mark, 512, 0.92)
    mask_192 = _fit_mark(mark, 192, 0.72)
    mask_512 = _fit_mark(mark, 512, 0.72)
    apple = _fit_mark(mark, 180, 0.90)

    any_192.convert("RGB").save(OUT / "icon-192.png", "PNG", optimize=True)
    any_512.convert("RGB").save(OUT / "icon-512.png", "PNG", optimize=True)
    mask_192.convert("RGB").save(OUT / "icon-192-maskable.png", "PNG", optimize=True)
    mask_512.convert("RGB").save(OUT / "icon-512-maskable.png", "PNG", optimize=True)
    apple.convert("RGB").save(OUT / "apple-touch-icon.png", "PNG", optimize=True)

    if START_HERO.is_file():
        _cover(Image.open(START_HERO), 1080, 1920).save(
            OUT / "screenshot-start-narrow.jpg", "JPEG", quality=82, optimize=True
        )
    if TEACH.is_file():
        _cover(Image.open(TEACH), 1920, 1080).save(
            OUT / "screenshot-cards-wide.jpg", "JPEG", quality=82, optimize=True
        )
    print(f"wrote icons into {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
