#!/usr/bin/env python3
"""
Render data/contributions.json as an animated 53-week x 7-day heatmap SVG.

The reveal is a diagonal, box-after-box slide-in driven entirely by CSS
keyframes embedded in the SVG (plays once on load, then freezes). GitHub runs
these when the file is placed with <img>, so no JS is needed.

Aurora palette — deliberately NOT GitHub green.
Stdlib only.
"""
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "contrib-heatmap.svg")

# level 0..4  ->  empty, indigo, violet, magenta, fuchsia
PALETTE = ["#161b22", "#3730a3", "#6d28d9", "#a21caf", "#ec4899"]

CELL = 12          # box size
GAP = 3            # gap between boxes
PAD_X = 22         # left/right padding
PAD_TOP = 38       # room for month labels above the grid
PAD_BOT = 58       # room for legend + stats footer
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    with open(SRC, encoding="utf-8") as fh:
        data = json.load(fh)
    days = data["days"]
    stats = data["stats"]

    weeks = max(d["week"] for d in days) + 1
    grid_w = weeks * (CELL + GAP) - GAP
    width = grid_w + PAD_X * 2
    height = PAD_TOP + 7 * (CELL + GAP) - GAP + PAD_BOT

    def cx(week):
        return PAD_X + week * (CELL + GAP)

    def cy(weekday):
        return PAD_TOP + weekday * (CELL + GAP)

    # month labels: first week whose first day falls in each month
    month_marks = {}
    for d in days:
        if d["weekday"] == 0:  # top of a column
            m = int(d["date"][5:7])
            month_marks.setdefault(m, d["week"])

    # SMIL only: CSS animations do NOT run inside an <img>-loaded SVG on GitHub
    # (Chrome pauses them), but SMIL <animate> does. Each box starts hidden and
    # fades in on a staggered, diagonal cascade, then freezes.
    rects = []
    max_delay = 0.0
    for d in days:
        wk, wd, lvl = d["week"], d["weekday"], d["level"]
        delay = round((wk + wd) * 0.018, 3)      # diagonal cascade
        max_delay = max(max_delay, delay)
        title = (f'{d["count"]} contribution' + ("s" if d["count"] != 1 else "")
                 + f' on {d["date"]}') if d["count"] else f'No contributions on {d["date"]}'
        rects.append(
            f'<rect x="{cx(wk)}" y="{cy(wd)}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[lvl]}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay}s" dur="0.4s" fill="freeze"/>'
            f'<title>{esc(title)}</title></rect>'
        )

    # month labels row (visible by default — labels don't animate)
    mlabels = "".join(
        f'<text x="{cx(wk)}" y="{PAD_TOP - 16}" class="mlabel">{MONTHS[m-1]}</text>'
        for m, wk in sorted(month_marks.items(), key=lambda kv: kv[1])
    )
    # weekday labels
    wlabels = "".join(
        f'<text x="{PAD_X - 8}" y="{cy(wd) + CELL - 2}" class="wlabel">{lbl}</text>'
        for wd, lbl in WEEKDAY_LABELS.items()
    )

    # legend
    legend_y = height - 30
    legend_x = width - PAD_X - (len(PALETTE) * (CELL + GAP)) - 40
    legend = [f'<text x="{legend_x - 8}" y="{legend_y + CELL - 2}" class="legend" text-anchor="end">Less</text>']
    for i, col in enumerate(PALETTE):
        legend.append(
            f'<rect x="{legend_x + i*(CELL+GAP)}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{col}"/>'
        )
    legend.append(
        f'<text x="{legend_x + len(PALETTE)*(CELL+GAP) + 4}" y="{legend_y + CELL - 2}" class="legend">More</text>'
    )

    total = stats["total"]
    cur = stats["current_streak"]
    longest = stats["longest_streak"]
    footer = (f'{total:,} contributions in the last year'
              f'  ·  current streak {cur}d'
              f'  ·  longest {longest}d')

    reveal_total = round(max_delay + 0.5, 2)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace">
  <style>
    .card {{ fill:#0d1117; stroke:#1e293b; stroke-width:1; }}
    .mlabel {{ fill:#64748b; font-size:10px; }}
    .wlabel {{ fill:#64748b; font-size:9px; text-anchor:end; }}
    .legend {{ fill:#94a3b8; font-size:10px; }}
    .footer {{ fill:#94a3b8; font-size:11px; }}
  </style>
  <rect class="card" x="1" y="1" width="{width-2}" height="{height-2}" rx="12"/>
  <g>{mlabels}{wlabels}</g>
  {''.join(rects)}
  <g>{''.join(legend)}</g>
  <text x="{PAD_X}" y="{height - 14}" class="footer">{esc(footer)}</text>
</svg>'''

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"Wrote {os.path.relpath(OUT)} — {weeks} weeks, reveal ~{reveal_total}s, {total} contributions.")


if __name__ == "__main__":
    main()
