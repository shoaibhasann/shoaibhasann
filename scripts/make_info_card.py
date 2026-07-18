#!/usr/bin/env python3
"""
Hand-author a full-width, neofetch-style info card SVG: a terminal window with
three traffic-light dots, a title, and a two-column key/value spec sheet.

Content is drawn fully visible (opacity 1) — GitHub's image pipeline is
unreliable about running SVG reveal animations, so nothing depends on them.

Stdlib only.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")

USER, HOST = "shoaib", "github"

# two columns of (key, value) — keep each value within ~35 chars so it never
# collides with the next column
ROWS_LEFT = [
    ("Role", "Full-Stack Developer — MERN + AI"),
    ("Education", "BCA — completed"),
    ("Base", "New Delhi, India"),
    ("Live", "6 client platforms in production"),
    ("Flow", "branding → build → deploy → SEO"),
]
ROWS_RIGHT = [
    ("Stack", "React · Next.js · TypeScript · Node"),
    ("Data", "MongoDB · PostgreSQL · Socket.IO"),
    ("AI", "LLM tooling · voice · generative media"),
    ("Status", "Accepting builds · reply < 24h"),
    ("Site", "iamshoaib.tech"),
]

BG, BORDER = "#0d1117", "#1e293b"
TITLE, KEY, VAL, DIM = "#c4b5fd", "#a855f7", "#e2e8f0", "#64748b"
DOT_R, DOT_G, DOT_B = "#ec4899", "#c026d3", "#8b5cf6"

WIDTH = 880
PAD = 30
FONT = 14
LINE_H = 30
KEY_W = 96                 # px reserved for the key column
COL_L_X = PAD              # left column key x
COL_R_X = WIDTH // 2 + 18  # right column key x
HEAD_Y = 30
RULE_Y = 52
TOP = 92                   # first row baseline


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def col(rows, key_x):
    out = []
    for i, (k, v) in enumerate(rows):
        y = TOP + i * LINE_H
        out.append(
            f'<text x="{key_x}" y="{y}" class="key">{esc(k)}</text>'
            f'<text x="{key_x + KEY_W}" y="{y}" class="val">{esc(v)}</text>'
        )
    return "".join(out)


def main():
    n = max(len(ROWS_LEFT), len(ROWS_RIGHT))
    height = TOP + (n - 1) * LINE_H + 34
    title = f"{USER}@{HOST}"
    divider_x = WIDTH // 2 + 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" font-family="'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace">
  <style>
    .win {{ fill:{BG}; stroke:{BORDER}; stroke-width:1; }}
    .title {{ fill:{TITLE}; font-size:{FONT}px; font-weight:700; }}
    .key {{ fill:{KEY}; font-size:{FONT}px; font-weight:700; }}
    .val {{ fill:{VAL}; font-size:{FONT}px; }}
    .rule {{ stroke:{BORDER}; stroke-width:1; }}
  </style>
  <rect class="win" x="1" y="1" width="{WIDTH-2}" height="{height-2}" rx="12"/>
  <circle cx="{PAD}" cy="26" r="5.5" fill="{DOT_R}"/>
  <circle cx="{PAD+18}" cy="26" r="5.5" fill="{DOT_G}"/>
  <circle cx="{PAD+36}" cy="26" r="5.5" fill="{DOT_B}"/>
  <text x="{PAD+58}" y="31" class="title">{esc(title)}</text>
  <line class="rule" x1="{PAD}" y1="{RULE_Y}" x2="{WIDTH-PAD}" y2="{RULE_Y}"/>
  <line class="rule" x1="{divider_x}" y1="{TOP-18}" x2="{divider_x}" y2="{height-18}" opacity="0.5"/>
  {col(ROWS_LEFT, COL_L_X)}
  {col(ROWS_RIGHT, COL_R_X)}
</svg>'''

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"Wrote {os.path.relpath(OUT)} — {WIDTH}x{height}, two columns.")


if __name__ == "__main__":
    main()
