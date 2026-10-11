#!/usr/bin/env python3
"""Build the project cards and the language panel.

Each project is its own SVG so the README can wrap it in a link: the card IS
the link, which removes the duplicated prose that used to sit underneath the
single combined panel.

Everything is drawn at 880px, the width of GitHub's README column, so it
renders near 1:1. The earlier 1200px canvas was downscaled to ~73%, which
turned 10px labels into ~7px and made them hard to read.

No contribution, star or follower counts: they are 23, 1 and 4. What the work
is made of is the stronger story, so that is what these show.

Notebooks are excluded from the language mix because Linguist counts embedded
base64 output images as source, which puts "Jupyter Notebook" at ~78%. That
measures saved plots, not code.

Usage:  python build/panels.py
Out:    assets/card-{slug}-{dark,light}.svg, assets/stack-{dark,light}.svg
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from header import DARK, LIGHT, OUT, Face, FONTS

W, M = 880, 48
H_CARD = 112
H_STACK = 150

GQL = """
{ user(login:"pr1tzy"){ repositories(first:100,ownerAffiliations:OWNER,
    isFork:false,privacy:PUBLIC){
  nodes{ languages(first:12,orderBy:{field:SIZE,direction:DESC}){
    edges{ size node{name} } } } } } }
"""

CARDS = [
    dict(slug="ghostline", name="GHOSTLINE",
         what="60 Hz lap telemetry, ghost comparison, corner-level time loss",
         facts="4.7K LOC   4 TEST SUITES   3 CI WORKFLOWS   4 RELEASES",
         status="LIVE", weight=1.0, accent=True),
    dict(slug="self-healing-llm-qa", name="SELF-HEALING LLM QA",
         what="Continuous eval against benchmark and live traffic, auto rollback",
         facts="DVC   MLFLOW   JENKINS   12 PIPELINE MODULES",
         status="", weight=0.52, accent=False),
    dict(slug="parkisense", name="PARKISENSE",
         what="Keystroke dynamics and drawing tremor, wavelet features",
         facts="SVM / RANDOM FOREST   APPROX 82% VALIDATION",
         status="", weight=0.34, accent=False),
]

EXCLUDE = {"Jupyter Notebook"}


def langs() -> list[tuple[str, int]]:
    cache = Path(__file__).parent / "langs.json"
    try:
        raw = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={GQL}"],
            capture_output=True, text=True, timeout=60, check=True,
            env={**os.environ, "MSYS_NO_PATHCONV": "1"}).stdout
        nodes = json.loads(raw)["data"]["user"]["repositories"]["nodes"]
        totals: dict[str, int] = {}
        for n in nodes:
            for e in n["languages"]["edges"]:
                if e["node"]["name"] in EXCLUDE:
                    continue
                totals[e["node"]["name"]] = (
                    totals.get(e["node"]["name"], 0) + e["size"])
        out = sorted(totals.items(), key=lambda kv: -kv[1])
        cache.write_text(json.dumps(out), encoding="utf-8")
        return out
    except Exception as exc:
        print(f"  (live fetch failed: {exc}; using cache)")
        return [tuple(x) for x in json.loads(cache.read_text())]


def grid(w: int, h: int, t: dict) -> str:
    lines = ([f'<line x1="{x}" y1="0" x2="{x}" y2="{h}"/>' for x in range(0, w + 1, 44)]
             + [f'<line x1="0" y1="{y}" x2="{w}" y2="{y}"/>' for y in range(0, h + 1, 44)])
    return (f'<g stroke="{t["grid"]}" stroke-opacity="{t["grid_op"]}" '
            f'stroke-width="1">{"".join(lines)}</g>')


CSS = """
.rise{opacity:0;animation:rise .7s ease-out forwards}
@keyframes rise{from{opacity:0}to{opacity:1}}
.bar{transform:scaleX(0);animation:grow 1.2s cubic-bezier(.22,.61,.24,1) forwards}
@keyframes grow{to{transform:scaleX(1)}}
@media (prefers-reduced-motion:reduce){
 .rise{animation:none;opacity:1}.bar{animation:none;transform:none}}
"""


def card(c: dict, t: dict) -> str:
    disp = Face(FONTS / "Grotesk-Gras.woff2")
    mono = Face(FONTS / "Sligoil-Micro.woff2")
    TR = 0.16
    col = t["acc"] if c["accent"] else t["fg"]
    body = []

    name, _ = disp.text(c["name"], 27, M - 2, 44)
    what, _ = mono.text(c["what"].upper(), 13, M, 68, TR)
    facts, _ = mono.text(c["facts"], 12, M, 89, TR)

    body.append(f'<g class="rise" fill="{col}">{name}</g>')
    body.append(f'<g class="rise" style="animation-delay:.06s" fill="{t["dim"]}">{what}</g>')
    body.append(f'<g class="rise" style="animation-delay:.12s" fill="{t["mute"]}">{facts}</g>')

    if c["status"]:
        st, stw = mono.text(c["status"], 11, 0, 0, TR)
        x = W - M - stw - 20
        body.append(
            f'<g class="rise" style="animation-delay:.18s" transform="translate({x},38)">'
            f'<rect x="-10" y="-13" width="{stw + 20:.0f}" height="20" rx="1" '
            f'fill="none" stroke="{t["cyan"]}" stroke-opacity=".55"/>'
            f'<g fill="{t["cyan"]}">{st}</g></g>')

    # arrow, so it reads as something you can click
    ax = W - M - 10
    body.append(
        f'<g class="rise" style="animation-delay:.2s" stroke="{t["mute"]}" '
        f'stroke-width="1.4" fill="none" opacity=".8">'
        f'<path d="M{ax-12},{89} L{ax},{89} M{ax-5},{84} L{ax},{89} L{ax-5},{94}"/></g>')

    body.append(
        f'<rect class="bar" style="animation-delay:.15s;transform-origin:{M}px center" '
        f'x="{M}" y="{H_CARD-14}" width="{(W - 2*M) * c["weight"]:.0f}" height="2" '
        f'fill="{col}" opacity="{.85 if c["accent"] else .35}"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H_CARD}" width="{W}" height="{H_CARD}" role="img" aria-label="{c['name'].title()}: {c['what']}. {c['facts']}">
<style>{CSS}</style>
<rect width="{W}" height="{H_CARD}" fill="{t['bg']}"/>
{grid(W, H_CARD, t)}
<line x1="{M}" y1="8" x2="{W-M}" y2="8" stroke="{t['fg']}" stroke-opacity="{t['rule_op']}"/>
{''.join(body)}
</svg>'''


def stack(t: dict) -> str:
    mono = Face(FONTS / "Sligoil-Micro.woff2")
    TR = 0.16
    data = langs()
    total = sum(v for _, v in data) or 1
    shown = [(k, v) for k, v in data if v / total >= 0.004][:8]
    rest = total - sum(v for _, v in shown)
    if rest > 0:
        shown.append(("OTHER", rest))

    tints = [t["acc"], t["cyan"], t["fg"], t["dim"], t["mute"],
             t["acc"], t["cyan"], t["dim"], t["mute"]]
    x0, x1, ybar = M, W - M, 76
    span = x1 - x0
    body = []

    hdr, _ = mono.text("LANGUAGE MIX / PUBLIC REPOS / SOURCE ONLY", 12, M, 46, TR)
    body.append(f'<g class="rise" fill="{t["acc"]}">{hdr}</g>')

    x = x0
    for i, (name, size) in enumerate(shown):
        w = span * size / total
        op = 1.0 if i == 0 else max(0.3, 0.9 - i * 0.1)
        body.append(
            f'<g class="bar" style="animation-delay:{.08 + i*.05}s;'
            f'transform-origin:{x}px center">'
            f'<rect x="{x:.1f}" y="{ybar}" width="{max(w-2,1):.1f}" height="12" '
            f'fill="{tints[i % len(tints)]}" opacity="{op:.2f}"/></g>')
        x += w

    lx = x0
    for i, (name, size) in enumerate(shown):
        pct = 100 * size / total
        if pct < 3.0:
            continue
        lbl, lw = mono.text(f"{name.upper()} {pct:.0f}%", 12, lx, 114, TR)
        body.append(f'<g class="rise" style="animation-delay:{.25 + i*.05}s" '
                    f'fill="{tints[i % len(tints)]}">{lbl}</g>')
        lx += lw + 26

    note, _ = mono.text("NOTEBOOKS EXCLUDED / LINGUIST COUNTS OUTPUT IMAGES AS SOURCE",
                        11, M, 138, TR)
    body.append(f'<g class="rise" style="animation-delay:.5s" fill="{t["mute"]}">{note}</g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H_STACK}" width="{W}" height="{H_STACK}" role="img" aria-label="Language mix across public repositories, source code only, notebooks excluded.">
<style>{CSS}</style>
<rect width="{W}" height="{H_STACK}" fill="{t['bg']}"/>
{grid(W, H_STACK, t)}
{''.join(body)}
</svg>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for tone, theme in (("dark", DARK), ("light", LIGHT)):
        for c in CARDS:
            p = OUT / f"card-{c['slug']}-{tone}.svg"
            p.write_text(card(c, theme), encoding="utf-8")
            print(f"{p.name}  {p.stat().st_size/1024:.0f} KB")
        p = OUT / f"stack-{tone}.svg"
        p.write_text(stack(theme), encoding="utf-8")
        print(f"{p.name}  {p.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
