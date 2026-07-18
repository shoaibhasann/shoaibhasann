#!/usr/bin/env python3
"""
Prep a photo so it converts to a clean ASCII portrait instead of a dark blob.

  1. Remove the background (rembg) so only the subject remains.
  2. Auto-crop to the subject, then keep the head + shoulders (HS_FRAC).
  3. Composite onto pure white so the background maps to the blank end of the
     ASCII ramp (white -> spaces).
  4. Stretch contrast (2-98 percentile) + a mild gamma so a flat, dark subject
     gets real highlights and shadows. Uses numpy (no OpenCV needed).

Run once per photo:
    python scripts/prep_photo.py profile.jpeg          # default head+shoulders
    python scripts/prep_photo.py profile.jpeg 0.7      # keep more of the torso
Then:
    python scripts/make_ascii_svg.py

Needs: pip install pillow numpy rembg   (rembg is optional but strongly
recommended — without it the background is kept and only contrast is applied.)
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "source-prepped.png")
HS_FRAC_DEFAULT = 0.58   # fraction of the subject's height to keep (head + shoulders)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python scripts/prep_photo.py <photo.jpg> [head_shoulders_fraction]")
    src = sys.argv[1]
    hs_frac = float(sys.argv[2]) if len(sys.argv) > 2 else HS_FRAC_DEFAULT

    img = Image.open(src).convert("RGBA")

    # 1. background removal -> 2. auto-crop to subject
    try:
        from rembg import remove
        print("[prep] removing background (first run downloads a model ~176MB)...")
        img = remove(img)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
    except Exception as e:  # noqa
        print(f"[prep] rembg unavailable ({e.__class__.__name__}); keeping full frame.")

    # 3. head + shoulders crop
    w, h = img.size
    img = img.crop((0, 0, w, int(h * hs_frac)))

    # composite onto white using alpha as the mask (alpha is 255 everywhere if
    # rembg was skipped, so this is a no-op flatten in that case)
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    white.paste(img, (0, 0), img)
    gray = np.array(white.convert("L")).astype(np.float32)

    # 4. contrast stretch on the subject pixels, then a gentle gamma
    subject = gray < 250
    if subject.any():
        lo, hi = np.percentile(gray[subject], (2, 98))
        gray = np.clip((gray - lo) / max(hi - lo, 1.0) * 255.0, 0, 255)
        gray[~subject] = 255.0                 # keep the background pure white
    gray = 255.0 * (gray / 255.0) ** 0.85      # open up the shadows a touch

    Image.fromarray(gray.astype("uint8")).save(OUT)
    print(f"Wrote {os.path.relpath(OUT)} ({Image.open(OUT).size}) — "
          f"now run: python scripts/make_ascii_svg.py")


if __name__ == "__main__":
    main()
