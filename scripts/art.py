"""Draws the animated SVGs of the profile (banner, Armorix card) — pure SVG + CSS, no external services.

    python scripts/art.py      → assets/banner.svg, assets/armorix.svg
"""

from __future__ import annotations

import html
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Consolas, 'Liberation Mono', monospace"
ACCENT, ACCENT2, INK, MUTED = "#4a67ff", "#93a5ff", "#eeeee9", "#8b8d97"


def shield_points(cx: float, cy: float, scale: float, count: int, seed: int) -> list[tuple[float, float, float]]:
    """Dots inside the Armorix shield outline (the logo path), keyhole left empty."""
    rnd = random.Random(seed)
    pts = []
    while len(pts) < count:
        x, y = rnd.uniform(16, 48), rnd.uniform(12, 53)
        top = 18 - (6 * (1 - abs(x - 32) / 16))  # the roof: 12 at the centre, 18 at the edges
        if y < top:
            continue
        if y > 31:  # the rounded bottom: narrows to the tip at y≈53
            half = 16 * math.sqrt(max(0.0, 1 - ((y - 31) / 22) ** 2))
            if abs(x - 32) > half:
                continue
        if math.hypot(x - 32, y - 29) < 5 or (32 < y < 41.5 and abs(x - 32) < 1.4 + (y - 32) * 0.08):
            continue
        pts.append((cx + (x - 32) * scale, cy + (y - 32) * scale, rnd.uniform(0.9, 2.3)))
    return pts


def banner() -> str:
    w, h = 1200, 380
    rnd = random.Random(7)
    dots = shield_points(960, 190, 7.2, 900, 3)
    circles = []
    for i, (x, y, r) in enumerate(dots):
        delay = rnd.uniform(0, 4)
        circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" style="animation-delay:{delay:.2f}s"/>')
    grid = "".join(f'<circle cx="{x}" cy="{y}" r="1"/>' for x in range(20, w, 32) for y in range(20, h, 32))
    roles = ["Full-Stack Developer", "Cybersecurity Specialist", "Founder of Armorix", "Offline AI · AppSec · DevSecOps"]
    typed = []
    for i, role in enumerate(roles):
        typed.append(f'<text class="role r{i}" x="64" y="236">{role}<tspan class="caret">▌</tspan></text>')
    n = len(roles)
    step = 100 / n
    role_css = []
    for i in range(n):
        a, b = i * step, (i + 1) * step
        role_css.append(
            f"@keyframes show{i} {{ 0%,{a:.2f}% {{ opacity:0; clip-path: inset(0 100% 0 0) }} "
            f"{a + 0.1:.2f}% {{ opacity:1; clip-path: inset(0 100% 0 0) }} "
            f"{a + step * 0.45:.2f}% {{ opacity:1; clip-path: inset(0 0 0 0) }} "
            f"{b - 0.4:.2f}% {{ opacity:1; clip-path: inset(0 0 0 0) }} {b:.2f}%,100% {{ opacity:0 }} }}"
            f".r{i} {{ animation: show{i} {n * 3.2:.1f}s steps(40, end) infinite; }}"
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Abubakr Abduvohidov — Full-Stack Developer, Cybersecurity Specialist, Founder of Armorix">
<defs>
  <radialGradient id="glow" cx="80%" cy="50%" r="55%"><stop offset="0" stop-color="#1c2560"/><stop offset="1" stop-color="#08090c"/></radialGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACCENT2}" stop-opacity="0"/><stop offset=".5" stop-color="{ACCENT2}" stop-opacity=".55"/><stop offset="1" stop-color="{ACCENT2}" stop-opacity="0"/></linearGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="22"/></clipPath>
</defs>
<style>
  .grid circle {{ fill: #ffffff; opacity: .05 }}
  .shield circle {{ fill: {ACCENT}; animation: twinkle 4s ease-in-out infinite; }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .35 }} 50% {{ opacity: 1 }} }}
  .shield {{ animation: sway 9s ease-in-out infinite; transform-origin: 960px 190px; }}
  @keyframes sway {{ 0%,100% {{ transform: scaleX(1) }} 50% {{ transform: scaleX(.86) }} }}
  .scan {{ animation: sweep 3.6s linear infinite; }}
  @keyframes sweep {{ from {{ transform: translateY(-40px) }} to {{ transform: translateY({h}px) }} }}
  .hi {{ font: 600 22px {MONO}; fill: {ACCENT2}; letter-spacing: 3px }}
  .name {{ font: 800 64px {FONT}; fill: {INK}; letter-spacing: -2px }}
  .role {{ font: 500 30px {MONO}; fill: {INK}; opacity: 0 }}
  .caret {{ fill: {ACCENT}; animation: blink 1s steps(1) infinite }}
  @keyframes blink {{ 50% {{ opacity: 0 }} }}
  .tags {{ font: 600 17px {MONO}; fill: {MUTED}; letter-spacing: 1px }}
  .dot {{ fill: #1fd08c; animation: blink 1.6s steps(1) infinite }}
  {"".join(role_css)}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important }} .r0 {{ opacity: 1 }} }}
</style>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="url(#glow)"/>
  <g class="grid">{grid}</g>
  <g class="shield">{"".join(circles)}</g>
  <rect class="scan" x="760" y="0" width="420" height="40" fill="url(#scan)"/>
  <text class="hi" x="64" y="98">SALOM · ПРИВЕТ · HELLO 👋</text>
  <text class="name" x="62" y="172">Abubakr Abduvohidov</text>
  {"".join(typed)}
  <circle class="dot" cx="70" cy="306" r="6"/>
  <text class="tags" x="86" y="312">UZBEKISTAN · REACT · NODE · PYTHON · AST TAINT ANALYSIS · LOCAL AI</text>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="22" fill="none" stroke="#2a2e3a"/>
</svg>
'''


def card() -> str:
    w, h = 1200, 300
    dots = shield_points(1060, 150, 4.6, 420, 11)
    rnd = random.Random(5)
    circles = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.8:.2f}" style="animation-delay:{rnd.uniform(0, 3):.2f}s"/>' for x, y, r in dots)
    lines = [
        ("#8a90a0", "$ armorix scan ./shop"),
        ("#ff7b72", "CRITICAL  CWE-89   app.php:14    SQL injection ← $_GET['id']"),
        ("#ffb454", "HIGH      CWE-918  api.go:31     SSRF ← r.URL.Query()"),
        ("#8a90a0", "$ armorix fix . --apply"),
        ("#7ee2a8", "[ok] patch verified by re-scan · 0 bytes sent over the network"),
    ]
    term = "".join(
        f'<text class="t t{i}" xml:space="preserve" x="48" y="{150 + i * 28}" fill="{c}">{html.escape(s)}</text>'
        for i, (c, s) in enumerate(lines)
    )
    t_css = "".join(f".t{i} {{ animation-delay: {i * 0.9:.1f}s }}" for i in range(len(lines)))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Armorix — offline AI code auditor: finds and fixes vulnerabilities without the internet">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0f16"/><stop offset="1" stop-color="#141a3a"/></linearGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="20"/></clipPath>
</defs>
<style>
  .shield circle {{ fill: {ACCENT}; animation: tw 3s ease-in-out infinite }}
  @keyframes tw {{ 0%,100% {{ opacity: .3 }} 50% {{ opacity: 1 }} }}
  .title {{ font: 800 40px {FONT}; fill: {INK}; letter-spacing: -1px }}
  .sub {{ font: 500 19px {FONT}; fill: {MUTED} }}
  .pill {{ font: 700 13px {MONO}; fill: {ACCENT2}; letter-spacing: 2px }}
  .t {{ font: 500 17px {MONO}; opacity: 0; animation: type 9s steps(1) infinite }}
  @keyframes type {{ 0% {{ opacity: 0 }} 4%,88% {{ opacity: 1 }} 96%,100% {{ opacity: 0 }} }}
  {t_css}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important }} .t {{ opacity: 1 }} }}
</style>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <g class="shield">{circles}</g>
  <text class="pill" x="48" y="54">FEATURED PROJECT · v0.3.0 · 100% OFFLINE</text>
  <text class="title" x="46" y="100">Armorix</text>
  <text class="sub" x="232" y="99">finds, fixes and re-verifies vulnerabilities — on your machine</text>
  {term}
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="20" fill="none" stroke="#2a2e3a"/>
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "banner.svg").write_text(banner(), encoding="utf-8")
    (OUT / "armorix.svg").write_text(card(), encoding="utf-8")
    for p in sorted(OUT.glob("*.svg")):
        print(p.name, f"{p.stat().st_size / 1024:.0f} KB")
