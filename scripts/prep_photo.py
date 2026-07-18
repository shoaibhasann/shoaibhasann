#!/usr/bin/env python3
"""
Prep a photo so it converts to clean ASCII instead of a dark blob.

  1. Remove the background (rembg) so only the subject remains.
  2. Boost local contrast with CLAHE (OpenCV) — gives a flat face real
     highlights and shadows.
  3. Composite onto pure white so the background maps to the blank end of the
     ASCII ramp (white -> spaces).

Run once per photo:
    python scripts/prep_photo.py source-photo.jpg
Then:
    python scripts/make_ascii_svg.py

Needs the photo-only deps: pip install pillow numpy opencv-python rembg
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "source-prepped.png")


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python scripts/prep_photo.py <photo.jpg>")
    src = sys.argv[1]

    img = Image.open(src).convert("RGBA")

    # 1. background removal (optional — skipped gracefully if rembg absent)
    try:
        from rembg import remove
        img = remove(img)
    except Exception as e:  # noqa
        print(f"[prep] rembg unavailable ({e.__class__.__name__}); keeping full frame.")

    # 2. composite onto white using the alpha as a mask
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    white.paste(img, (0, 0), img)
    gray = np.array(white.convert("L"))

    # 3. CLAHE local-contrast boost
    try:
        import cv2
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
    except Exception as e:  # noqa
        print(f"[prep] OpenCV unavailable ({e.__class__.__name__}); skipping CLAHE.")

    Image.fromarray(gray).save(OUT)
    print(f"Wrote {os.path.relpath(OUT)} — now run: python scripts/make_ascii_svg.py")


if __name__ == "__main__":
    main()
