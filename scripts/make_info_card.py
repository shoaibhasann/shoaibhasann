#!/usr/bin/env python3
"""
Hand-author a neofetch-style info card SVG. Each row fades + slides in on a
short stagger so the panel looks like it is printing next to the portrait.

Content is the story the contribution graph can't tell (role, stack,
highlights) — keep GitHub *stats* out of here; the heatmap covers those.

Set STATIC=1 to emit a frozen frame (handy for local Quick Look previews).
Stdlib only.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

USER = "shoaib"
HOST = "github"

# (key, value)  — value colour is the accent; None key = a plain full-width line
ROWS = [
    ("Role",      "Full-Stack Developer — MERN + AI"),
    ("Education", "BCA — completed"),
    ("Base",      "New Delhi, India"),
    ("Live",      "6 client platforms in production"),
    ("Stack",     "React · Next.js · TypeScript · Node"),
    ("Data",      "MongoDB · PostgreSQL · REST · Socket.IO"),
    ("AI",        "LLM tooling · voice · generative media"),
    ("Flow",      "branding → build → deploy → SEO"),
    ("Status",    "Accepting builds · reply < 24h"),
    ("Site",      "iamshoaib.tech"),
]

BG = "#0d1117"
BORDER = "#1e293b"
TITLE = "#c4b5fd"
KEY = "#a855f7"
VAL = "#e2e8f0"
DIM = "#64748b"
DOT_R, DOT_G, DOT_B = "#ec4899", "#c026d3", "#8b5cf6"  # traffic-light dots

PAD = 22
LINE_H = 26
TOP = 64
FONT = 14
KEY_W = 92  # px reserved for the key column


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    width = 500
    height = TOP + len(ROWS) * LINE_H + 34
    title = f"{USER}@{HOST}"
    rule_y = TOP - 18

    # Rows are drawn fully visible (opacity 1) — NOT revealed by animation.
    # GitHub's image pipeline is unreliable about running SVG animations from a
    # hidden start (opacity:0 + animate), which can leave the card blank.
    lines = []
    for i, (k, v) in enumerate(ROWS):
        y = TOP + i * LINE_H
        lines.append(
            f'<g>'
            f'<text x="{PAD}" y="{y}" class="key">{esc(k)}</text>'
            f'<text x="{PAD + KEY_W}" y="{y}" class="val">{esc(v)}</text>'
            f'</g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace">
  <style>
    .win {{ fill:{BG}; stroke:{BORDER}; stroke-width:1; }}
    .title {{ fill:{TITLE}; font-size:{FONT}px; font-weight:700; }}
    .key {{ fill:{KEY}; font-size:{FONT}px; font-weight:700; }}
    .val {{ fill:{VAL}; font-size:{FONT}px; }}
    .rule {{ stroke:{BORDER}; stroke-width:1; }}
  </style>
  <rect class="win" x="1" y="1" width="{width-2}" height="{height-2}" rx="12"/>
  <circle cx="24" cy="26" r="5.5" fill="{DOT_R}"/>
  <circle cx="42" cy="26" r="5.5" fill="{DOT_G}"/>
  <circle cx="60" cy="26" r="5.5" fill="{DOT_B}"/>
  <text x="82" y="31" class="title">{esc(title)}</text>
  <line class="rule" x1="{PAD}" y1="{rule_y}" x2="{width-PAD}" y2="{rule_y}"/>
  {''.join(lines)}
</svg>'''

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"Wrote {os.path.relpath(OUT)} — {len(ROWS)} rows{' (static)' if STATIC else ''}.")


if __name__ == "__main__":
    main()
