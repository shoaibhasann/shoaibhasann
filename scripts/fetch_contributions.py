#!/usr/bin/env python3
"""
Fetch the public GitHub contribution calendar for a user and write
data/contributions.json (raw days + derived stats).

No token, no GraphQL, no third-party service: GitHub serves the calendar as
public HTML at https://github.com/users/<user>/contributions — the same
fragment the profile page itself renders.

Stdlib only (urllib + regex) so the daily GitHub Action needs no pip install.
Pass --html <path> to parse a saved file instead of hitting the network.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime

USERNAME = os.environ.get("GH_USERNAME", "shoaibhasann")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "contributions.json")

CELL_RE = re.compile(
    r'data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*?'
    r'id="contribution-day-component-(?P<row>\d+)-(?P<col>\d+)"[^>]*?'
    r'data-level="(?P<level>\d)"'
)
TIP_RE = re.compile(
    r'<tool-tip[^>]*for="contribution-day-component-(?P<row>\d+)-(?P<col>\d+)"[^>]*>'
    r'(?P<text>[^<]*)</tool-tip>'
)
COUNT_RE = re.compile(r"^(\d[\d,]*)\s+contribution")


def fetch_html(argv):
    if "--html" in argv:
        path = argv[argv.index("--html") + 1]
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    url = f"https://github.com/users/{USERNAME}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile-art)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def parse(html):
    # tooltip text -> count, keyed by (row, col)
    counts = {}
    for m in TIP_RE.finditer(html):
        key = (int(m.group("row")), int(m.group("col")))
        cm = COUNT_RE.match(m.group("text").strip())
        counts[key] = int(cm.group(1).replace(",", "")) if cm else 0

    days = []
    for m in CELL_RE.finditer(html):
        row, col = int(m.group("row")), int(m.group("col"))
        days.append(
            {
                "date": m.group("date"),
                "weekday": row,          # 0 = Sunday .. 6 = Saturday
                "week": col,             # column index, 0 .. 52
                "level": int(m.group("level")),
                "count": counts.get((row, col), 0),
            }
        )
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"]) if days else {"count": 0, "date": None}

    # longest streak of consecutive days with count > 0
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    # current streak: trailing run of count > 0 (a zero on the final day,
    # i.e. "today", does not break an otherwise-live streak)
    current = 0
    for i in range(len(days) - 1, -1, -1):
        if days[i]["count"] > 0:
            current += 1
        elif i == len(days) - 1:
            continue  # today has no contribution yet — keep looking back
        else:
            break

    # per-month totals for the window
    monthly = {}
    for d in days:
        mk = d["date"][:7]
        monthly[mk] = monthly.get(mk, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly,
        "range": {"from": days[0]["date"], "to": days[-1]["date"]} if days else {},
    }


def main():
    html = fetch_html(sys.argv[1:])
    days = parse(html)
    if not days:
        raise SystemExit("No contribution cells parsed — GitHub markup may have changed.")
    payload = {
        "user": USERNAME,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stats": compute_stats(days),
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    s = payload["stats"]
    print(
        f"Wrote {os.path.relpath(OUT)} — {len(days)} days, {s['total']} contributions, "
        f"current streak {s['current_streak']}, longest {s['longest_streak']}."
    )


if __name__ == "__main__":
    main()
