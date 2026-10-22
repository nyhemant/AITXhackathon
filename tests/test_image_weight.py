"""Guard: field-pack photos and park maps stay phone-sized (2026-10-22).

scripts/resize_photos.py brought 384 images from 262 MB to ~94 MB without
changing any URL. This stops a future upload from bringing back 2-3 MB,
1920px files that pages only show at 100-330 CSS px.
"""
from __future__ import annotations

import unittest
from pathlib import Path

try:  # Pillow is optional (not installed on the imini server)
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "static" / "field-pack" / "photos"
MAPS = ROOT / "static" / "field-pack" / "media" / "maps"

PHOTO_MAX_W, HERO_MAX_W, MAP_MAX_W = 960, 1600, 1400
PHOTO_MAX_BYTES = 450_000
HERO_MAX_BYTES = 1_600_000
MAP_MAX_BYTES = 900_000


def _jpeg_width(data: bytes) -> int:
    """Width from the JPEG SOF marker (no Pillow needed)."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
            i += 1 if marker == 0xFF else 2
            continue
        seg_len = int.from_bytes(data[i + 2:i + 4], "big")
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            return int.from_bytes(data[i + 7:i + 9], "big")
        i += 2 + seg_len
    raise ValueError("no SOF marker")


class ImageWeightTests(unittest.TestCase):
    def _check(self, path: Path, max_w: int, max_bytes: int) -> None:
        if Image is not None:
            with Image.open(path) as im:
                im.load()  # must decode
                w = im.size[0]
        else:
            w = _jpeg_width(path.read_bytes())
        self.assertLessEqual(w, max_w, f"{path.name} is {w}px wide; run scripts/resize_photos.py")
        size = path.stat().st_size
        self.assertLessEqual(size, max_bytes, f"{path.name} is {size} bytes; run scripts/resize_photos.py")

    def test_photos_are_phone_sized(self):
        files = sorted(PHOTOS.glob("*.jpg"))
        self.assertGreater(len(files), 200)
        for p in files:
            with self.subTest(p.name):
                hero = p.name.startswith("np-hero-")
                self._check(p, HERO_MAX_W if hero else PHOTO_MAX_W, HERO_MAX_BYTES if hero else PHOTO_MAX_BYTES)

    def test_park_maps_are_phone_sized(self):
        files = sorted(MAPS.glob("*.jpg"))
        self.assertGreater(len(files), 150)
        for p in files:
            with self.subTest(p.name):
                self._check(p, MAP_MAX_W, MAP_MAX_BYTES)


if __name__ == "__main__":
    unittest.main()
