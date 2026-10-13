#!/usr/bin/env python3
"""Accumulate GitHub traffic (views / unique visitors / clones) for this repo.

GitHub only keeps 14 days of traffic data. This script is run daily by
.github/workflows/track-views.yml, merges the latest window into
stats/traffic.json (deduplicated by day), renders stats/views.svg and refreshes
the numbers between the <!-- VIEWS:START --> / <!-- VIEWS:END --> markers in
README.md, so the repository keeps a lifetime view counter.

Requires: GITHUB_TOKEN (or TRAFFIC_TOKEN) with read access to repository
traffic ("Administration: read" for fine-grained PATs; push access for classic).
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATS = ROOT / "stats" / "traffic.json"
BADGE = ROOT / "stats" / "views.svg"
README = ROOT / "README.md"

REPO = os.environ.get("GITHUB_REPOSITORY", "chen742/Awesome_AI_Research_Ideas")
TOKEN = os.environ.get("TRAFFIC_TOKEN") or os.environ.get("GITHUB_TOKEN")


def api(path: str) -> dict:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/traffic/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def load_stats() -> dict:
    if STATS.exists():
        return json.loads(STATS.read_text())
    return {"views": {}, "clones": {}, "updated": None}


def merge(stats: dict, key: str, payload: dict) -> None:
    for day in payload.get(key, []):
        stamp = day["timestamp"][:10]
        stats[key][stamp] = {"count": day["count"], "uniques": day["uniques"]}


def totals(stats: dict, key: str) -> tuple[int, int]:
    rows = stats[key].values()
    return sum(r["count"] for r in rows), sum(r["uniques"] for r in rows)


def badge(label: str, value: str, color: str = "ff69b4") -> str:
    lw, vw = 6 * len(label) + 20, 7 * len(value) + 20
    w = lw + vw
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="20" role="img" aria-label="{label}: {value}">
<linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<clipPath id="r"><rect width="{w}" height="20" rx="3" fill="#fff"/></clipPath>
<g clip-path="url(#r)"><rect width="{lw}" height="20" fill="#555"/><rect x="{lw}" width="{vw}" height="20" fill="#{color}"/><rect width="{w}" height="20" fill="url(#s)"/></g>
<g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
<text x="{lw/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text><text x="{lw/2}" y="14">{label}</text>
<text x="{lw + vw/2}" y="15" fill="#010101" fill-opacity=".3">{value}</text><text x="{lw + vw/2}" y="14">{value}</text>
</g></svg>
"""


def update_readme(views: int, uniques: int, clones: int, updated: str) -> None:
    if not README.exists():
        return
    text = README.read_text(encoding="utf-8")
    block = (
        "<!-- VIEWS:START -->\n"
        f"| 👀 累计浏览 | 🧑‍💻 独立访客 | 📥 累计克隆 | 🕒 更新于 |\n"
        f"|:--:|:--:|:--:|:--:|\n"
        f"| **{views:,}** | **{uniques:,}** | **{clones:,}** | {updated} |\n"
        "<!-- VIEWS:END -->"
    )
    new = re.sub(r"<!-- VIEWS:START -->.*?<!-- VIEWS:END -->", block, text, flags=re.S)
    if new != text:
        README.write_text(new, encoding="utf-8")


def main() -> int:
    if not TOKEN:
        print("No GITHUB_TOKEN / TRAFFIC_TOKEN set", file=sys.stderr)
        return 1
    stats = load_stats()
    try:
        merge(stats, "views", api("views"))
        merge(stats, "clones", api("clones"))
    except Exception as exc:  # noqa: BLE001
        print(f"Traffic API failed: {exc}", file=sys.stderr)
        return 1
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats["updated"] = now
    STATS.parent.mkdir(exist_ok=True)
    STATS.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n")
    v, u = totals(stats, "views")
    c, _ = totals(stats, "clones")
    BADGE.write_text(badge("👀 views", f"{v:,} · {u:,} unique"))
    update_readme(v, u, c, now)
    print(f"views={v} uniques={u} clones={c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
