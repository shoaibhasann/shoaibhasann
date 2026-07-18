#!/usr/bin/env python3
"""
Turn a prepped portrait (source-prepped.png) into a self-typing, monochrome
ASCII-art SVG. Each row is revealed by a left-to-right clip wipe with a block
cursor riding the edge, staggered top to bottom; it prints once and freezes.

The motion is SMIL inside the SVG, so GitHub plays it when the file is placed
with <img>.

Fallback: if Pillow or source-prepped.png is unavailable, render the bundled
scripts/portrait.txt instead — so the profile still animates before you add a
photo. Replace it any time with:
    python scripts/prep_photo.py your-photo.jpg
    python scripts/make_ascii_svg.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PREPPED = os.path.join(HERE, "..", "source-prepped.png")
FALLBACK = os.path.join(HERE, "portrait.txt")
OUT = os.path.join(HERE, "..", "shoaib-ascii.svg")

RAMP = " .`:-=+*cs#%@"        # bright (sparse) -> dark (dense)
COLS = 84                      # character grid width when converting a photo
INK = "#c4b5fd"               # one light-lavender fill — monochrome on purpose
BG = "#0d1117"
BORDER = "#1e293b"
DIM = "#64748b"

CHAR_W = 7.0                  # monospace advance at FONT
FONT = 11.6
LINE_H = 12.4
PAD = 20
TOP = 46                      # window chrome height


def from_image():
    from PIL import Image  # noqa: only needed in photo mode
    img = Image.open(PREPPED).convert("L")
    w, h = img.size
    # characters are ~2x taller than wide; correct the aspect
    rows = max(1, int(COLS * (h / w) * 0.5))
    img = img.resize((COLS, rows))
    px = img.load()
    lines = []
    for y in range(rows):
        line = []
        for x in range(COLS):
            b = px[x, y]                       # 0=black .. 255=white
            idx = int((255 - b) / 255 * (len(RAMP) - 1))
            line.append(RAMP[idx])
        lines.append("".join(line).rstrip())
    return lines


def from_text():
    with open(FALLBACK, encoding="utf-8") as fh:
        return [ln.rstrip("\n") for ln in fh.readlines()]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    try:
        lines = from_image()
        mode = "photo"
    except Exception:
        lines = from_text()
        mode = "portrait.txt"

    # trim trailing blank lines
    while lines and not lines[-1].strip():
        lines.pop()

    ncols = max((len(ln) for ln in lines), default=1)
    grid_w = ncols * CHAR_W
    width = int(grid_w + PAD * 2)
    height = int(TOP + len(lines) * LINE_H + PAD)

    stagger = 0.09

    # SMIL only (CSS animation is ignored inside an <img> SVG on GitHub). Each
    # row prints in with a short fade + rise, top to bottom, then freezes. A
    # block cursor blinks on the last row to keep the terminal feel.
    body = []
    for i, line in enumerate(lines):
        y = TOP + i * LINE_H
        begin = round(i * stagger, 3)
        body.append(
            f'<text x="{PAD}" y="{y}" class="art" opacity="0" xml:space="preserve">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="0.3s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 4" to="0 0" '
            f'begin="{begin}s" dur="0.3s" fill="freeze"/>'
            f'{esc(line)}</text>'
        )

    last_y = TOP + (len(lines) - 1) * LINE_H
    cursor_begin = round(len(lines) * stagger + 0.1, 3)
    cursor = (
        f'<rect class="cur" x="{PAD}" y="{last_y + 4}" width="{CHAR_W:.1f}" height="3" opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{cursor_begin}s"/>'
        f'<animate attributeName="opacity" values="1;1;0;0;1" dur="1.1s" begin="{cursor_begin}s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    label = "~/portrait.sh"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace">
  <style>
    .win {{ fill:{BG}; stroke:{BORDER}; stroke-width:1; }}
    .art {{ fill:{INK}; font-size:{FONT}px; letter-spacing:0; }}
    .cur {{ fill:{INK}; }}
    .label {{ fill:{DIM}; font-size:11px; }}
  </style>
  <rect class="win" x="1" y="1" width="{width-2}" height="{height-2}" rx="12"/>
  <circle cx="24" cy="25" r="5.5" fill="#ec4899"/>
  <circle cx="42" cy="25" r="5.5" fill="#c026d3"/>
  <circle cx="60" cy="25" r="5.5" fill="#8b5cf6"/>
  <text x="82" y="29" class="label">{esc(label)}</text>
  {''.join(body)}
  {cursor}
</svg>'''

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"Wrote {os.path.relpath(OUT)} — {len(lines)} rows from {mode}.")


if __name__ == "__main__":
    main()
