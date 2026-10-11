#!/usr/bin/env python3
"""Build the animated profile header.

The trace is a real Monza lap from Ghostline's bundled sample telemetry: the
player lap (1:28.197) against the ghost (1:25.750), Lotus Exos 125 S1. Nothing
here is decorative - every curve is measured data.

Type is set in the same Velvetyne faces Ghostline uses (OFL) and converted to
outlines, so the SVG carries no @font-face and renders identically everywhere.
GitHub serves README images through a proxy that makes embedded webfonts
unreliable; outlines sidestep that entirely.

Usage:  python build/header.py
Out:    assets/header-dark.svg, assets/header-light.svg
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
# Vendored so the repo builds anywhere, including CI. Fonts are Velvetyne
# (OFL, licences alongside them); the lap is Ghostline's own sample telemetry.
SAMPLES = ROOT / "vendor" / "samples"
FONTS = ROOT / "vendor" / "fonts"
OUT = ROOT / "assets"

W, H = 1200, 420

DARK = dict(
    bg="#0b0a0f", fg="#efecf4", mute="#8a8597", dim="#cbc6d6",
    acc="#9d6bff", cyan="#3ef0ff", grid="#efecf4",
    grid_op=".055", rule_op=".14", track_op=".3",
)
LIGHT = dict(
    bg="#f4f2f7", fg="#15131c", mute="#5f5a6b", dim="#45414f",
    acc="#6f3fd4", cyan="#0d8ea0", grid="#15131c",
    grid_op=".07", rule_op=".18", track_op=".35",
)


# ------------------------------------------------------------------ type

class Face:
    """A font, as outlines."""

    def __init__(self, path: Path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upem = self.font["head"].unitsPerEm

    def text(self, s: str, size: float, x: float, y: float,
             tracking: float = 0.0) -> str:
        """Return a single path `d` for `s`, baseline at (x, y).

        tracking is extra letter spacing as a fraction of the em.
        """
        scale = size / self.upem
        parts, cursor = [], 0.0
        for ch in s:
            name = self.cmap.get(ord(ch))
            if name is None:
                cursor += 0.5 * self.upem
                continue
            pen = SVGPathPen(self.glyphs)
            self.glyphs[name].draw(pen)
            d = pen.getCommands()
            if d:
                # y is flipped: font units go up, SVG goes down.
                parts.append(
                    f'<path transform="translate({x + cursor * scale:.2f},{y:.2f}) '
                    f'scale({scale:.5f},{-scale:.5f})" d="{d}"/>')
            cursor += self.glyphs[name].width + tracking * self.upem
        return "".join(parts), cursor * scale

    def width(self, s: str, size: float, tracking: float = 0.0) -> float:
        scale = size / self.upem
        total = 0.0
        for ch in s:
            name = self.cmap.get(ord(ch))
            total += (self.glyphs[name].width if name else 0.5 * self.upem)
            total += tracking * self.upem
        return total * scale


# ---------------------------------------------------------------- telemetry

def read_lap(path: Path) -> list[dict]:
    lines = [l for l in path.read_text().splitlines() if not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("\n".join(lines))))


def resample(rows: list[dict], key: str, n: int) -> list[float]:
    """Sample `key` at n evenly spaced track positions (pos is 0..1)."""
    pts = sorted((float(r["pos"]), float(r[key])) for r in rows)
    out, j = [], 0
    for i in range(n):
        target = i / (n - 1)
        while j + 1 < len(pts) and pts[j + 1][0] < target:
            j += 1
        if j + 1 >= len(pts):
            out.append(pts[-1][1])
            continue
        (p0, v0), (p1, v1) = pts[j], pts[j + 1]
        f = 0.0 if p1 == p0 else (target - p0) / (p1 - p0)
        out.append(v0 + (v1 - v0) * f)
    return out


def smooth(v: list[float], w: int = 2) -> list[float]:
    return [sum(v[max(0, i - w):min(len(v), i + w + 1)])
            / len(v[max(0, i - w):min(len(v), i + w + 1)]) for i in range(len(v))]


def trace_path(values: list[float], x0: float, x1: float, y0: float, y1: float,
               vmin: float, vmax: float) -> str:
    n = len(values)
    pts = [(x0 + (x1 - x0) * i / (n - 1),
            y1 - (y1 - y0) * (v - vmin) / (vmax - vmin))
           for i, v in enumerate(values)]
    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(1, n):
        (xp, yp), (xc, yc) = pts[i - 1], pts[i]
        cx = (xp + xc) / 2
        d.append(f"C{cx:.1f},{yp:.1f} {cx:.1f},{yc:.1f} {xc:.1f},{yc:.1f}")
    return "".join(d)


def track_path(rows: list[dict], cx: float, cy: float, size: float) -> str:
    xs = [float(r["x"]) for r in rows]
    zs = [float(r["z"]) for r in rows]
    span = max(max(xs) - min(xs), max(zs) - min(zs)) or 1.0
    scale = size / span
    ox = cx - (min(xs) + max(xs)) / 2 * scale
    oy = cy - (min(zs) + max(zs)) / 2 * scale
    step = max(1, len(xs) // 300)
    pts = [(xs[i] * scale + ox, zs[i] * scale + oy)
           for i in range(0, len(xs), step)]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


# --------------------------------------------------------------------- svg

def build(t: dict) -> str:
    disp = Face(FONTS / "Grotesk-Gras.woff2")
    mono = Face(FONTS / "Sligoil-Micro.woff2")

    you = read_lap(SAMPLES / "monza_you.csv")
    ghost = read_lap(SAMPLES / "monza_ghost.csv")

    n = 220
    sy = smooth(resample(you, "speed", n))
    sg = smooth(resample(ghost, "speed", n))
    vmin, vmax = min(min(sy), min(sg)) - 10, max(max(sy), max(sg)) + 10

    tx0, tx1, ty0, ty1 = 64, W - 64, 262, 368
    p_you = trace_path(sy, tx0, tx1, ty0, ty1, vmin, vmax)
    p_ghost = trace_path(sg, tx0, tx1, ty0, ty1, vmin, vmax)
    p_track = track_path(you, W - 150, 120, 146)

    TR = 0.16  # mono tracking
    eyebrow_a, w_a = mono.text("MUMBAI, IN", 11, 64, 76, TR)
    eyebrow_b, _ = mono.text("ML INFRASTRUCTURE / BACKEND", 11, 64 + w_a + 26, 76, TR)
    wordmark, _ = disp.text("PRITHVI SINGH", 94, 60, 176)
    tagline, _ = mono.text(
        "DISTRIBUTED TRAINING / RETRIEVAL / THE SYSTEMS AROUND THEM",
        12, 64, 212, TR)
    cap_l, _ = mono.text("MONZA / LOTUS EXOS 125 S1 / SPEED TRACE, REAL LAP",
                         11, 64, 398, TR)

    r_you, r_gh = "1:28.197 YOU", "1:25.750 GHOST"
    w_gh = mono.width(r_gh, 11, TR)
    w_sep = mono.width("  /  ", 11, TR)
    x_gh = W - 64 - w_gh
    x_sep = x_gh - w_sep
    x_you = x_sep - mono.width(r_you, 11, TR)
    cap_you, _ = mono.text(r_you, 11, x_you, 398, TR)
    cap_sep, _ = mono.text("  /  ", 11, x_sep, 398, TR)
    cap_gh, _ = mono.text(r_gh, 11, x_gh, 398, TR)

    grid = "".join(
        [f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W + 1, 60)]
        + [f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0, H + 1, 60)])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Prithvi Singh. ML infrastructure and backend. Speed trace from a real Monza lap, 1:28.197 against a 1:25.750 ghost.">
<style>
.grid line{{stroke:{t['grid']};stroke-opacity:{t['grid_op']};stroke-width:1}}
.rule{{stroke:{t['fg']};stroke-opacity:{t['rule_op']};stroke-width:1}}
.fg{{fill:{t['fg']}}} .mute{{fill:{t['mute']}}} .dim{{fill:{t['dim']}}}
.acc{{fill:{t['acc']}}} .cy{{fill:{t['cyan']}}}
.trace{{fill:none;stroke-linecap:round;stroke-linejoin:round}}

/* pathLength="1" normalises the dash maths, so the draw-in works regardless
   of how long the real path actually is. */
.draw{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 8s cubic-bezier(.22,.61,.24,1) infinite}}
@keyframes draw{{
  0%{{stroke-dashoffset:1}} 50%{{stroke-dashoffset:0}}
  90%{{stroke-dashoffset:0;opacity:1}} 97%,100%{{stroke-dashoffset:0;opacity:0}}
}}
.d2{{animation-delay:.4s}}
.cursor{{animation:cur 8s linear infinite}}
@keyframes cur{{0%,3%{{opacity:0}} 8%,88%{{opacity:1}} 95%,100%{{opacity:0}}}}
.rise{{opacity:0;animation:rise 8s ease-out infinite}}
@keyframes rise{{0%{{opacity:0}} 7%,90%{{opacity:1}} 97%,100%{{opacity:0}}}}
.r2{{animation-delay:.1s}} .r3{{animation-delay:.2s}} .r4{{animation-delay:.3s}}
@media (prefers-reduced-motion:reduce){{
  .draw{{animation:none;stroke-dashoffset:0}}
  .cursor,.rise{{animation:none;opacity:1}}
}}
</style>

<rect width="{W}" height="{H}" fill="{t['bg']}"/>
<g class="grid">{grid}</g>

<g class="rise"><g class="acc">{eyebrow_a}</g><g class="mute">{eyebrow_b}</g></g>
<g class="rise r2 fg">{wordmark}</g>
<g class="rise r3 dim">{tagline}</g>
<line class="rule" x1="64" y1="236" x2="{W-64}" y2="236"/>

<g class="rise r4">
  <path fill="none" stroke="{t['fg']}" stroke-opacity="{t['track_op']}" stroke-width="1.25" d="{p_track}"/>
  <path class="trace draw" pathLength="1" stroke="{t['acc']}" stroke-width="1.75" d="{p_track}"/>
</g>

<path class="trace draw d2" pathLength="1" stroke="{t['cyan']}" stroke-width="1.5" opacity=".7" d="{p_ghost}"/>
<path id="you" class="trace draw" pathLength="1" stroke="{t['acc']}" stroke-width="2.25" d="{p_you}"/>

<circle class="cursor" r="3.5" fill="{t['fg']}">
  <!-- keySplines mirrors the .draw easing, so the dot stays on the leading
       edge of the line instead of lagging behind it. -->
  <animateMotion dur="8s" repeatCount="indefinite" calcMode="spline"
    keyPoints="0;0;1;1;0" keyTimes="0;0.03;0.5;0.95;1"
    keySplines="0 0 1 1; .22 .61 .24 1; 0 0 1 1; 0 0 1 1">
    <mpath href="#you"/>
  </animateMotion>
</circle>

<g class="rise r4">
  <g class="mute">{cap_l}</g>
  <g class="acc">{cap_you}</g><g class="mute">{cap_sep}</g><g class="cy">{cap_gh}</g>
</g>
</svg>'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, theme in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"header-{name}.svg"
        svg = build(theme)
        p.write_text(svg, encoding="utf-8")
        print(f"{p.name}  {len(svg)/1024:.1f} KB")


if __name__ == "__main__":
    main()
