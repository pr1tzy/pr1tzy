#!/usr/bin/env python3
"""Build the two data panels below the header.

Panel A - selected work, as a timing screen. Per-project engineering facts
          (source size, tests, CI, releases), not vanity counts.
Panel B - language mix across public repos, source code only.

Why no contribution/star/follower counts: they are 23, 1 and 4. Rendering them
beautifully only makes a weak signal more prominent. What the work is made of
is the stronger story, so that is what these panels show.

Why notebooks are excluded from Panel B: GitHub Linguist counts .ipynb bytes
including embedded base64 output images, which puts "Jupyter Notebook" at ~78%
of the total. That measures saved plots, not code written.

Usage:  python build/panels.py
Out:    assets/work-{dark,light}.svg, assets/stack-{dark,light}.svg
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from header import DARK, LIGHT, OUT, Face, FONTS

W_WORK, H_WORK = 1200, 356
W_STACK, H_STACK = 1200, 150

GQL = """
{ user(login:"pr1tzy"){ repositories(first:100,ownerAffiliations:OWNER,
    isFork:false,privacy:PUBLIC){
  nodes{ languages(first:12,orderBy:{field:SIZE,direction:DESC}){
    edges{ size node{name} } } } } } }
"""

# Counted from the working tree, not guessed. Refresh with:
#   git ls-files '*.py' | xargs cat | wc -l
WORK = [
    dict(name="GHOSTLINE",
         what="60 Hz lap telemetry, ghost comparison, corner-level time loss",
         facts=["4.7K LOC", "4 TEST SUITES", "3 CI WORKFLOWS", "4 RELEASES"],
         status="LIVE", weight=1.0, accent=True),
    dict(name="SELF-HEALING LLM QA",
         what="Continuous eval against benchmark and live traffic, auto rollback",
         facts=["DVC", "MLFLOW", "JENKINS", "12 PIPELINE MODULES"],
         status="", weight=0.52, accent=False),
    dict(name="PARKISENSE",
         what="Keystroke dynamics and drawing tremor, wavelet features",
         facts=["SVM / RANDOM FOREST", "~82% VALIDATION"],
         status="", weight=0.34, accent=False),
]

EXCLUDE = {"Jupyter Notebook"}


def langs() -> list[tuple[str, int]]:
    cache = Path(__file__).parent / "langs.json"
    try:
        raw = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={GQL}"],
            capture_output=True, text=True, timeout=60, check=True,
            env={**__import__("os").environ, "MSYS_NO_PATHCONV": "1"}).stdout
        nodes = json.loads(raw)["data"]["user"]["repositories"]["nodes"]
        totals: dict[str, int] = {}
        for n in nodes:
            for e in n["languages"]["edges"]:
                name = e["node"]["name"]
                if name in EXCLUDE:
                    continue
                totals[name] = totals.get(name, 0) + e["size"]
        out = sorted(totals.items(), key=lambda kv: -kv[1])
        cache.write_text(json.dumps(out), encoding="utf-8")
        return out
    except Exception as exc:                       # offline / no gh / rate limit
        print(f"  (live fetch failed: {exc}; using cache)")
        return [tuple(x) for x in json.loads(cache.read_text())]


def grid(w: int, h: int, t: dict) -> str:
    lines = ([f'<line x1="{x}" y1="0" x2="{x}" y2="{h}"/>' for x in range(0, w + 1, 60)]
             + [f'<line x1="0" y1="{y}" x2="{w}" y2="{y}"/>' for y in range(0, h + 1, 60)])
    return (f'<g stroke="{t["grid"]}" stroke-opacity="{t["grid_op"]}" '
            f'stroke-width="1">{"".join(lines)}</g>')


def anim_css(t: dict) -> str:
    return f"""
.rise{{opacity:0;animation:rise .9s ease-out forwards}}
@keyframes rise{{from{{opacity:0}}to{{opacity:1}}}}
.bar{{transform-origin:left center;transform:scaleX(0);
      animation:grow 1.4s cubic-bezier(.22,.61,.24,1) forwards}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
.sweep{{animation:sweep 6s cubic-bezier(.4,0,.2,1) infinite}}
@keyframes sweep{{0%{{opacity:0;transform:translateX(0)}}
  6%{{opacity:.5}}50%{{opacity:.5}}60%{{opacity:0;transform:translateX({W_WORK-128}px)}}
  100%{{opacity:0;transform:translateX({W_WORK-128}px)}}}}
@media (prefers-reduced-motion:reduce){{
  .rise{{animation:none;opacity:1}}
  .bar{{animation:none;transform:none}}
  .sweep{{animation:none;opacity:0}}
}}"""


def panel_work(t: dict) -> str:
    disp = Face(FONTS / "Grotesk-Gras.woff2")
    mono = Face(FONTS / "Sligoil-Micro.woff2")
    TR = 0.16
    body: list[str] = []

    hdr, _ = mono.text("SELECTED WORK", 11, 64, 54, TR)
    body.append(f'<g class="rise" style="animation-delay:0s" fill="{t["acc"]}">{hdr}</g>')
    body.append(f'<line x1="64" y1="70" x2="{W_WORK-64}" y2="70" '
                f'stroke="{t["fg"]}" stroke-opacity="{t["rule_op"]}"/>')

    y = 110
    for i, row in enumerate(WORK):
        d = 0.12 + i * 0.14
        col = t["acc"] if row["accent"] else t["fg"]
        name, nw = disp.text(row["name"], 25, 64, y)
        what, _ = mono.text(row["what"].upper(), 10, 64, y + 22, TR)
        facts, _ = mono.text("   ".join(row["facts"]), 10, 64, y + 40, TR)

        body.append(f'<g class="rise" style="animation-delay:{d}s">')
        body.append(f'<g fill="{col}">{name}</g>')
        body.append(f'<g fill="{t["mute"]}">{what}</g>')
        body.append(f'<g fill="{t["dim"]}">{facts}</g>')
        if row["status"]:
            st, stw = mono.text(row["status"], 10, 0, 0, TR)
            x = W_WORK - 64 - stw - 18
            body.append(
                f'<g transform="translate({x},{y - 4})">'
                f'<rect x="-9" y="-12" width="{stw + 18:.0f}" height="18" rx="1" '
                f'fill="none" stroke="{t["cyan"]}" stroke-opacity=".5"/>'
                f'<g fill="{t["cyan"]}" transform="translate(0,0)">{st}</g></g>')
        # scale bar: relative source size, not a score
        body.append(
            f'<rect class="bar" style="animation-delay:{d + .1}s" x="64" y="{y + 50}" '
            f'width="{(W_WORK - 128) * row["weight"]:.0f}" height="2" fill="{col}" '
            f'opacity="{.85 if row["accent"] else .35}"/>')
        body.append("</g>")
        y += 88

    sweep = (f'<rect class="sweep" x="64" y="78" width="2" height="{H_WORK-96}" '
             f'fill="{t["cyan"]}" opacity="0"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_WORK} {H_WORK}" width="{W_WORK}" height="{H_WORK}" role="img" aria-label="Selected work: Ghostline, Self-healing LLM QA, ParkiSense, with engineering metrics.">
<style>{anim_css(t)}</style>
<rect width="{W_WORK}" height="{H_WORK}" fill="{t['bg']}"/>
{grid(W_WORK, H_WORK, t)}
{sweep}
{''.join(body)}
</svg>'''


def panel_stack(t: dict) -> str:
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
    x0, x1, ybar = 64, W_STACK - 64, 78
    span = x1 - x0
    body: list[str] = []

    hdr, _ = mono.text("LANGUAGE MIX / PUBLIC REPOSITORIES / SOURCE ONLY", 11, 64, 50, TR)
    body.append(f'<g class="rise" fill="{t["acc"]}">{hdr}</g>')

    x = x0
    for i, (name, size) in enumerate(shown):
        w = span * size / total
        col = tints[i % len(tints)]
        op = 1.0 if i == 0 else max(0.22, 0.85 - i * 0.12)
        body.append(
            f'<g class="bar" style="animation-delay:{.1 + i*.06}s;'
            f'transform-origin:{x}px center">'
            f'<rect x="{x:.1f}" y="{ybar}" width="{max(w-2,1):.1f}" height="10" '
            f'fill="{col}" opacity="{op:.2f}"/></g>')
        x += w

    # labels on one line underneath
    lx = x0
    for i, (name, size) in enumerate(shown):
        pct = 100 * size / total
        if pct < 3.0:
            continue
        col = tints[i % len(tints)]
        lbl, lw = mono.text(f"{name.upper()} {pct:.0f}%", 10, lx, 112, TR)
        body.append(f'<g class="rise" style="animation-delay:{.3 + i*.05}s" '
                    f'fill="{col}" opacity="{1 if i==0 else .75}">{lbl}</g>')
        lx += lw + 26

    note, _ = mono.text(
        "NOTEBOOKS EXCLUDED: LINGUIST COUNTS EMBEDDED OUTPUT IMAGES AS SOURCE",
        9, 64, 138, TR)
    body.append(f'<g class="rise" style="animation-delay:.6s" '
                f'fill="{t["mute"]}" opacity=".6">{note}</g>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_STACK} {H_STACK}" width="{W_STACK}" height="{H_STACK}" role="img" aria-label="Language mix across public repositories, source code only, notebooks excluded.">
<style>{anim_css(t)}</style>
<rect width="{W_STACK}" height="{H_STACK}" fill="{t['bg']}"/>
{grid(W_STACK, H_STACK, t)}
{''.join(body)}
</svg>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, theme in (("dark", DARK), ("light", LIGHT)):
        for stem, fn in (("work", panel_work), ("stack", panel_stack)):
            p = OUT / f"{stem}-{name}.svg"
            p.write_text(fn(theme), encoding="utf-8")
            print(f"{p.name}  {p.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
