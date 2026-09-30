"""GitHub stats cards in the Armorix style, rebuilt by .github/workflows/profile.yml (no third-party card service).

    GITHUB_TOKEN=… python scripts/stats.py <login> <out-dir>   → stats.svg, langs.svg
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import sys
import urllib.request
from pathlib import Path

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } }
    }
  }
}
"""
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', SFMono-Regular, Consolas, 'Liberation Mono', monospace"


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def streaks(days: list[dict]) -> tuple[int, int]:
    current = longest = run = 0
    today = dt.date.today().isoformat()
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    for d in reversed(days):
        if d["contributionCount"]:
            current += 1
        elif d["date"] != today:  # today may simply not have a commit yet
            break
    return current, longest


def frame(w: int, h: int, label: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(label)}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0f16"/><stop offset="1" stop-color="#131935"/></linearGradient></defs>
<style>
  .k {{ font: 600 12px {MONO}; fill: #8b8d97; letter-spacing: 2px }}
  .v {{ font: 800 34px {FONT}; fill: #eeeee9; letter-spacing: -1px }}
  .h {{ font: 700 13px {MONO}; fill: #93a5ff; letter-spacing: 3px }}
  .l {{ font: 500 14px {FONT}; fill: #c9cad1 }}
  .grow {{ animation: grow 1.2s cubic-bezier(.2,.8,.2,1) both }}
  @keyframes grow {{ from {{ transform: scaleX(0) }} }}
  .fade {{ animation: fade .8s ease both }}
  @keyframes fade {{ from {{ opacity: 0 }} }}
</style>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="url(#bg)" stroke="#2a2e3a"/>
{body}
</svg>
'''


def stats_card(u: dict) -> str:
    repos = u["repositories"]
    stars = sum(r["stargazerCount"] for r in repos["nodes"])
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    current, longest = streaks(days)
    tiles = [("CONTRIBUTIONS", cal["totalContributions"]), ("COMMITS", u["contributionsCollection"]["totalCommitContributions"]),
             ("REPOS", repos["totalCount"]), ("STARS", stars), ("STREAK", f"{current}d"), ("BEST STREAK", f"{longest}d")]
    w, h = 480, 250
    body = ['<text class="h" x="28" y="40">GITHUB · LAST 12 MONTHS</text>']
    for i, (k, v) in enumerate(tiles):
        x, y = 28 + (i % 3) * 148, 58 + (i // 3) * 72
        body.append(f'<g class="fade" style="animation-delay:{i * 0.12:.2f}s"><text class="v" x="{x}" y="{y + 30}">{html.escape(str(v))}</text>'
                    f'<text class="k" x="{x}" y="{y + 52}">{k}</text></g>')
    # sparkline of the last 12 weeks
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"][-12:]]
    top = max(weekly) or 1
    pts = " ".join(f"{176 + i * 25:.0f},{228 - v / top * 18:.1f}" for i, v in enumerate(weekly))
    body.append(f'<polyline points="{pts}" fill="none" stroke="#4a67ff" stroke-width="2" stroke-linejoin="round"/>')
    body.append('<text class="k" x="28" y="229">12 WEEKS →</text>')
    return frame(w, h, "GitHub stats", "".join(body))


def langs_card(u: dict) -> str:
    totals: dict[str, list] = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            t = totals.setdefault(e["node"]["name"], [0, e["node"]["color"] or "#8b8d97"])
            t[0] += e["size"]
    top = sorted(totals.items(), key=lambda kv: -kv[1][0])[:8]
    total = sum(v[0] for _, v in top) or 1
    w, h = 480, 250
    body = ['<text class="h" x="28" y="40">TOP LANGUAGES</text>', '<clipPath id="bar"><rect x="28" y="62" width="424" height="12" rx="6"/></clipPath>',
            '<g clip-path="url(#bar)">']
    x = 28.0
    for name, (size, color) in top:
        width = size / total * 424
        body.append(f'<rect class="grow" style="transform-origin:{x:.1f}px 0" x="{x:.1f}" y="62" width="{width:.1f}" height="12" fill="{color}"/>')
        x += width
    body.append("</g>")
    for i, (name, (size, color)) in enumerate(top):
        cx, cy = 28 + (i % 2) * 212, 110 + (i // 2) * 34
        body.append(f'<g class="fade" style="animation-delay:{0.3 + i * 0.08:.2f}s"><circle cx="{cx + 6}" cy="{cy - 5}" r="6" fill="{color}"/>'
                    f'<text class="l" x="{cx + 20}" y="{cy}">{html.escape(name)} <tspan fill="#8b8d97">{size / total * 100:.1f}%</tspan></text></g>')
    return frame(w, h, "Top languages", "".join(body))


if __name__ == "__main__":
    login, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    user = fetch(login, os.environ["GITHUB_TOKEN"])
    (out / "stats.svg").write_text(stats_card(user), encoding="utf-8")
    (out / "langs.svg").write_text(langs_card(user), encoding="utf-8")
    print("wrote", sorted(p.name for p in out.glob("*.svg")))
