"""THE ARCHIVE: twelve half-width "file" tiles (2 per row in the README).

Each tile is a small film frame: dark panel with a category-tinted nebula, an
animated vector emblem, the title, a one-line logline, a category chip, the
repo path or a LIVE marker, and a file index. A comet of light runs around the
border on a loop; every tile starts at a different phase so the grid shimmers.

Emblems belong to their category's family so the grid reads by colour + shape:
  quantum        Bloch sphere with an orbiting qubit / superposed 3x3 board
  ai-ml          turning reticle around a scanning eye / a voice waveform
  iot-embedded   microcontroller with data pulses running out its traces
  mobile         handset with chat bubbles and BLE signal arcs
  fullstack-web  a tiny browser window: </> + caret, or the project's own scene

Output: assets/arc-<slug>.svg for each entry of content.ARCHIVE.
"""

import math
import random
import re

from agfx import ACCENT, C, Doc, Font, blur, corners, f, glow, lin, panel, rad, stars
import content

W, H = 640, 176
RX = 16
ES = 96                       # emblem square
EX, EY = 28, (H - ES) / 2     # emblem box origin (vertically centred)
ECX, ECY = EX + ES / 2, EY + ES / 2
TX = EX + ES + 30             # text column
TR = W - 32                   # right edge of text column
TW = TR - TX                  # text column width

TITLE_Y, LINE_Y, LINE_H = 57, 84, 22
ROW_Y = 134                   # bottom-row baseline
SWEEP = 9.0                   # border light loop (s)

LABEL = {
    "quantum": "QUANTUM",
    "ai-ml": "AI · ML",
    "fullstack-web": "FULL-STACK",
    "iot-embedded": "EMBEDDED · IOT",
    "mobile": "MOBILE",
    "security": "SECURITY",
}


def slug(title: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]", "-", title.lower())).strip("-")


def two_lines(text: str, font: str, size: float, max_w: float) -> list[str]:
    """Balanced wrap into ≤ 2 lines (no widows), by measured width."""
    fo = Font.get(font)
    if fo.width(text, size) <= max_w:
        return [text]
    words = text.split()
    best, best_cost = None, None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        wa, wb = fo.width(a, size), fo.width(b, size)
        if wa > max_w or wb > max_w:
            continue
        cost = abs(wa - wb) + (0 if wa >= wb else 25)      # prefer a slightly longer first line
        if a.endswith(("·", "×", "+", "&")) or b.startswith(("·", "+")):
            cost += 60                                    # don't strand a joiner at a break
        if best_cost is None or cost < best_cost:
            best, best_cost = [a, b], cost
    if not best:
        raise ValueError(f"one-liner too long for two lines: {text!r}")
    return best


def rrect_path(x, y, w, h, r):
    """Rounded-rect outline as a path, starting top-left, clockwise."""
    return (f"M{f(x + r)} {f(y)}H{f(x + w - r)}A{r} {r} 0 0 1 {f(x + w)} {f(y + r)}"
            f"V{f(y + h - r)}A{r} {r} 0 0 1 {f(x + w - r)} {f(y + h)}H{f(x + r)}"
            f"A{r} {r} 0 0 1 {f(x)} {f(y + h - r)}V{f(y + r)}A{r} {r} 0 0 1 {f(x + r)} {f(y)}Z")


def loop_opacity(t_on: float, t_off: float = .92, dur: float = 6, peak: float = 1) -> str:
    """SMIL: fade in at t_on (fraction of the loop), hold, fade out at t_off."""
    return (f'<animate attributeName="opacity" values="0;0;{peak};{peak};0" keyTimes="0;{t_on:.3f};{t_on + .04:.3f};{t_off};1" '
            f'dur="{dur}s" repeatCount="indefinite"/>')


SPLINE = 'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"'

# ------------------------------------------------------------------ emblems --
# Each returns markup inside the 96px box centred on (ECX, ECY).

# -- quantum ------------------------------------------------------------------

def em_bloch(d, a1, a2):
    """Bloch sphere: turning meridians, precessing state vector, and a qubit
    orbiting on a tilted ring."""
    cx, cy, R, tilt = ECX, ECY + 2, 25, 0.3
    o = []
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{rad(d, "bsF", [(0, a1, .30), (.75, a1, .06), (1, a2, .18)], cx=.4, cy=.36, r=.62)}" '
             f'stroke="{a1}" stroke-width="1.4" pathLength="1" class="draw" style="animation-delay:.1s"/>')
    o.append(f'<path d="M{cx - R} {cy}A{R} {f(R * tilt)} 0 0 1 {cx + R} {cy}" stroke="{C["soft"]}" stroke-width="1" stroke-dasharray="2 3" opacity=".45"/>')
    o.append(f'<path d="M{cx - R} {cy}A{R} {f(R * tilt)} 0 0 0 {cx + R} {cy}" stroke="{C["ice"]}" stroke-width="1.3" opacity=".8"/>')
    o.append(f'<line x1="{cx}" y1="{cy - R - 7}" x2="{cx}" y2="{cy + R + 7}" stroke="{C["soft"]}" stroke-width="1" stroke-dasharray="2 3" opacity=".45"/>')
    for ph in range(2):
        o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{R}" stroke="{a2}" stroke-width="1.1" opacity=".45">'
                 f'<animate attributeName="rx" values="{R};0;{R}" dur="7s" begin="-{ph * 3.5}s" repeatCount="indefinite" {SPLINE}/></ellipse>')
    th = math.radians(48)
    pts = [(cx + R * math.sin(th) * math.cos(p), cy - R * math.cos(th) + R * math.sin(th) * math.sin(p) * tilt)
           for p in (2 * math.pi * i / 36 for i in range(37))]
    xs, ys = ";".join(f(p[0]) for p in pts), ";".join(f(p[1]) for p in pts)
    o.append(f'<ellipse cx="{cx}" cy="{f(cy - R * math.cos(th))}" rx="{f(R * math.sin(th))}" ry="{f(R * math.sin(th) * tilt)}" '
             f'stroke="{C["magenta"]}" stroke-width="1" stroke-dasharray="1 3" opacity=".7"/>')
    o.append(f'<line x1="{cx}" y1="{cy}" x2="{f(pts[0][0])}" y2="{f(pts[0][1])}" stroke="{C["magenta"]}" stroke-width="2" stroke-linecap="round" filter="url(#eg)">'
             f'<animate attributeName="x2" values="{xs}" dur="8s" repeatCount="indefinite"/>'
             f'<animate attributeName="y2" values="{ys}" dur="8s" repeatCount="indefinite"/></line>')
    o.append(f'<circle r="3.4" fill="#fff" filter="url(#eg)"><animate attributeName="cx" values="{xs}" dur="8s" repeatCount="indefinite"/>'
             f'<animate attributeName="cy" values="{ys}" dur="8s" repeatCount="indefinite"/></circle>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="2.2" fill="{C["ice"]}"/>')
    orx, ory, rot = 40, 11, -24
    orbit = f"M{cx - orx} {cy}A{orx} {ory} 0 1 0 {cx + orx} {cy}A{orx} {ory} 0 1 0 {cx - orx} {cy}Z"
    o.append(f'<g transform="rotate({rot} {cx} {cy})">'
             f'<path d="{orbit}" stroke="{a2}" stroke-width="1.2" opacity=".55" pathLength="1" class="draw" style="animation-delay:.35s"/>'
             f'<circle r="3" fill="{a2}" filter="url(#eg)"><animateMotion dur="4.6s" repeatCount="indefinite" path="{orbit}"/></circle>'
             f'</g>')
    return "".join(o)


def em_qboard(d, a1, a2):
    """Quantum tic-tac-toe: a 3x3 board where some marks sit in superposition
    (X and O cross-fading) until they are measured."""
    cx, cy, c = ECX, ECY, 20
    x0, y0 = cx - 1.5 * c, cy - 1.5 * c
    o = []
    grid = (f"M{f(x0 + c)} {f(y0 + 3)}V{f(y0 + 3 * c - 3)}M{f(x0 + 2 * c)} {f(y0 + 3)}V{f(y0 + 3 * c - 3)}"
            f"M{f(x0 + 3)} {f(y0 + c)}H{f(x0 + 3 * c - 3)}M{f(x0 + 3)} {f(y0 + 2 * c)}H{f(x0 + 3 * c - 3)}")
    o.append(f'<path d="{grid}" stroke="{a1}" stroke-width="1.6" stroke-linecap="round" opacity=".85"/>')

    def X(px, py, col, extra=""):
        s = 5.2
        return (f'<path d="M{f(px - s)} {f(py - s)}L{f(px + s)} {f(py + s)}M{f(px + s)} {f(py - s)}L{f(px - s)} {f(py + s)}" '
                f'stroke="{col}" stroke-width="2.2" stroke-linecap="round" {extra}/>')

    def O(px, py, col, extra=""):
        return f'<circle cx="{f(px)}" cy="{f(py)}" r="5.6" stroke="{col}" stroke-width="2.2" {extra}/>'

    def cell(i, j):
        return x0 + (i + .5) * c, y0 + (j + .5) * c

    for (i, j), mark in {(0, 0): "X", (2, 0): "O", (1, 1): "X", (0, 2): "O"}.items():
        px, py = cell(i, j)
        o.append((X if mark == "X" else O)(px, py, a2 if mark == "X" else C["magenta"], 'filter="url(#eg)"'))
    # superposed cells: both marks, cross-fading out of phase, with a soft halo
    for k, (i, j) in enumerate([(1, 0), (2, 1), (2, 2)]):
        px, py = cell(i, j)
        b = f"-{k * 1.1:.1f}s"
        o.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="8.5" fill="{a1}" opacity=".18" filter="url(#eb)"/>')
        o.append(f'<g opacity=".9">{X(px, py, a2)}<animate attributeName="opacity" values=".9;.12;.9" dur="3.3s" begin="{b}" repeatCount="indefinite" {SPLINE}/></g>')
        o.append(f'<g opacity=".12">{O(px, py, C["magenta"])}<animate attributeName="opacity" values=".12;.9;.12" dur="3.3s" begin="{b}" repeatCount="indefinite" {SPLINE}/></g>')
    # measurement sweep across the board
    o.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{3 * c}" height="1.4" fill="{C["ice"]}" opacity=".7" filter="url(#eg)">'
             f'<animate attributeName="y" values="{f(y0)};{f(y0 + 3 * c)};{f(y0 + 3 * c)}" keyTimes="0;.45;1" dur="5s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;.8;.8;0;0" keyTimes="0;.05;.4;.45;1" dur="5s" repeatCount="indefinite"/></rect>')
    return "".join(o)


# -- ai-ml --------------------------------------------------------------------

def reticle(cx, cy, a1, a2, rr=37):
    o = [f'<g><circle cx="{cx}" cy="{cy}" r="{rr}" stroke="{a1}" stroke-width="1.2" stroke-dasharray="3 5" opacity=".55"/>'
         f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="24s" repeatCount="indefinite"/></g>']
    ticks = []
    for ang in (0, 90, 180, 270):
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        ticks.append(f"M{f(cx + ca * (rr - 4))} {f(cy + sa * (rr - 4))}L{f(cx + ca * (rr + 6))} {f(cy + sa * (rr + 6))}")
    o.append(f'<path d="{"".join(ticks)}" stroke="{a1}" stroke-width="1.6" opacity=".9"/>')
    arc = (f"M{f(cx - 28)} {f(cy - 8)}A29 29 0 0 1 {f(cx - 8)} {f(cy - 28)}"
           f"M{f(cx + 28)} {f(cy + 8)}A29 29 0 0 1 {f(cx + 8)} {f(cy + 28)}")
    o.append(f'<g><path d="{arc}" stroke="{a2}" stroke-width="1.4" opacity=".6"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="360 {cx} {cy}" to="0 {cx} {cy}" dur="11s" repeatCount="indefinite"/></g>')
    return "".join(o)


def em_eye(d, a1, a2):
    """Scanning eye inside a turning reticle; the iris looks around, the lid blinks."""
    cx, cy = ECX, ECY
    hw, k = 31, 21
    eye_open = f"M{cx - hw} {cy}C{cx - 16} {cy - k} {cx + 16} {cy - k} {cx + hw} {cy}C{cx + 16} {cy + k} {cx - 16} {cy + k} {cx - hw} {cy}Z"
    eye_shut = f"M{cx - hw} {cy}C{cx - 16} {cy + 1} {cx + 16} {cy + 1} {cx + hw} {cy}C{cx + 16} {cy + 1} {cx - 16} {cy + 1} {cx - hw} {cy}Z"
    blink = (f'<animate attributeName="d" values="{eye_open};{eye_open};{eye_shut};{eye_open};{eye_open}" '
             f'keyTimes="0;.9;.93;.96;1" dur="7s" repeatCount="indefinite"/>')
    d.defs.append(f'<clipPath id="eyeClip"><path d="{eye_open}">{blink}</path></clipPath>')
    o = [reticle(cx, cy, a1, a2)]
    o.append(f'<path d="{eye_open}" fill="{C["void"]}" stroke="{a1}" stroke-width="1.8" stroke-linejoin="round" filter="url(#eg)">{blink}</path>')
    look = (f'<animateTransform attributeName="transform" type="translate" values="0 0;-8 -1;-8 -1;7 1;7 1;0 0;0 0" '
            f'keyTimes="0;.12;.35;.47;.7;.82;1" dur="9s" repeatCount="indefinite" calcMode="spline" '
            f'keySplines=".5 0 .5 1;0 0 1 1;.5 0 .5 1;0 0 1 1;.5 0 .5 1;0 0 1 1"/>')
    iris = (f'<g>{look}<circle cx="{cx}" cy="{cy}" r="12" fill="{rad(d, "irisF", [(0, a1, .0), (.55, a1, .25), (1, a1, .55)])}" stroke="{a1}" stroke-width="1.5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="{a1}"/>'
            f'<circle cx="{cx + 3}" cy="{cy - 3}" r="1.6" fill="#fff"/></g>')
    scan = (f'<rect x="{cx - hw}" y="{cy - 20}" width="{2 * hw}" height="1.6" fill="{a2}" filter="url(#eg)">'
            f'<animate attributeName="y" values="{cy - 19};{cy + 18};{cy - 19}" dur="3.2s" repeatCount="indefinite" {SPLINE}/></rect>')
    o.append(f'<g clip-path="url(#eyeClip)">{iris}{scan}</g>')
    return "".join(o)


def em_voice(d, a1, a2):
    """Voice-first assistant: a live speech waveform inside the reticle, with a
    small health cross."""
    cx, cy = ECX, ECY + 3
    o = [reticle(ECX, ECY, a1, a2)]
    rnd = random.Random(7)
    n, gap, bw = 11, 5, 2.6
    g = lin(d, "vG", [(0, a1), (1, a2)], 0, 1, 0, 0)
    for k in range(n):
        x = cx + (k - (n - 1) / 2) * gap - bw / 2
        env = math.cos((k - (n - 1) / 2) / (n / 2) * math.pi / 2) ** 1.2      # taller in the middle
        hs = [max(3, 26 * env * rnd.uniform(.25, 1)) for _ in range(4)]
        hs.append(hs[0])
        vals_h = ";".join(f(h) for h in hs)
        vals_y = ";".join(f(cy - h / 2) for h in hs)
        dur = rnd.uniform(1.6, 2.4)
        o.append(f'<rect x="{f(x)}" y="{f(cy - hs[0] / 2)}" width="{bw}" height="{f(hs[0])}" rx="1.3" fill="{g}">'
                 f'<animate attributeName="height" values="{vals_h}" dur="{dur:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/>'
                 f'<animate attributeName="y" values="{vals_y}" dur="{dur:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></rect>')
    o.append(f'<path d="M{cx} {ECY - 27}v8M{cx - 4} {ECY - 23}h8" stroke="{a2}" stroke-width="2.4" stroke-linecap="round" filter="url(#eg)" class="breathe"/>')
    o.append(f'<path d="M{cx - 30} {cy}H{cx - 31 + 2}M{cx + 29} {cy}H{cx + 31}" stroke="{a1}" stroke-width="1.4" opacity=".7"/>')
    return "".join(o)


# -- iot ----------------------------------------------------------------------

def em_chip(d, a1, a2):
    """Microcontroller with PCB traces; data pulses run out along the traces."""
    cx, cy, hs = ECX, ECY, 16
    o = []
    traces = [
        [(-3.5, -hs - 5), (-3.5, -27), (-15, -38)],
        [(10.5, -hs - 5), (10.5, -29), (20, -38)],
        [(hs + 5, -3.5), (29, -3.5), (38, -12)],
        [(hs + 5, 10.5), (28, 10.5), (38, 20)],
        [(3.5, hs + 5), (3.5, 28), (15, 38)],
        [(-10.5, hs + 5), (-10.5, 29), (-20, 38)],
        [(-hs - 5, 3.5), (-29, 3.5), (-38, 12)],
        [(-hs - 5, -10.5), (-28, -10.5), (-38, -20)],
    ]
    paths = ["M" + "L".join(f"{f(cx + x)} {f(cy + y)}" for x, y in t) for t in traces]
    o.append(f'<path d="{"".join(paths)}" stroke="{a1}" stroke-width="1.3" opacity=".5" stroke-linejoin="round"/>')
    for t in traces:
        x, y = t[-1]
        o.append(f'<circle cx="{f(cx + x)}" cy="{f(cy + y)}" r="2.3" fill="{C["void"]}" stroke="{a1}" stroke-width="1.3"/>')
    for i, p in enumerate(paths):
        o.append(f'<path d="{p}" pathLength="1" stroke="{a2}" stroke-width="2" stroke-linecap="round" stroke-dasharray=".22 .78" filter="url(#eg)" opacity="0">'
                 f'<animate attributeName="stroke-dashoffset" values=".22;-.78" dur="2.4s" begin="{i * .3:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="2.4s" begin="{i * .3:.1f}s" repeatCount="indefinite"/></path>')
    pins = []
    for k in (-10.5, -3.5, 3.5, 10.5):
        pins.append(f"M{f(cx + k)} {f(cy - hs)}V{f(cy - hs - 5)}M{f(cx + k)} {f(cy + hs)}V{f(cy + hs + 5)}"
                    f"M{f(cx - hs)} {f(cy + k)}H{f(cx - hs - 5)}M{f(cx + hs)} {f(cy + k)}H{f(cx + hs + 5)}")
    o.append(f'<path d="{"".join(pins)}" stroke="{a1}" stroke-width="2" opacity=".9"/>')
    o.append(f'<rect x="{cx - hs}" y="{cy - hs}" width="{2 * hs}" height="{2 * hs}" rx="4" fill="{C["panel2"]}" stroke="{a1}" stroke-width="1.7" pathLength="1" class="draw" style="animation-delay:.1s"/>')
    o.append(f'<rect x="{cx - 7}" y="{cy - 7}" width="14" height="14" rx="1.5" fill="{a1}" filter="url(#eg)">'
             f'<animate attributeName="opacity" values=".3;.95;.3" dur="2.4s" repeatCount="indefinite" {SPLINE}/></rect>')
    o.append(f'<circle cx="{cx - hs + 5}" cy="{cy - hs + 5}" r="1.6" fill="{a1}" opacity=".9"/>')
    return "".join(o)


# -- mobile -------------------------------------------------------------------

def em_phone(d, a1, a2):
    """Handset with chat bubbles arriving and BLE signal arcs radiating both ways."""
    cx, cy = ECX, ECY
    pw, ph = 28, 50
    x0, y0 = cx - pw / 2, cy - ph / 2
    o = []
    for side in (1, -1):
        for j, r in enumerate((22, 30, 38)):
            a = math.radians(32)
            x1, y1 = cx + side * r * math.cos(a), cy - r * math.sin(a)
            x2, y2 = cx + side * r * math.cos(a), cy + r * math.sin(a)
            sweep = 1 if side == 1 else 0
            o.append(f'<path d="M{f(x1)} {f(y1)}A{r} {r} 0 0 {sweep} {f(x2)} {f(y2)}" stroke="{a1}" stroke-width="2" stroke-linecap="round" opacity=".2">'
                     f'<animate attributeName="opacity" values=".15;1;.15;.15" keyTimes="0;.18;.5;1" dur="2.4s" begin="{j * .28:.2f}s" repeatCount="indefinite"/></path>')
    o.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{pw}" height="{ph}" rx="6" fill="{C["panel2"]}" stroke="{a1}" stroke-width="1.8" pathLength="1" class="draw" style="animation-delay:.1s"/>')
    o.append(f'<rect x="{f(x0 + 3)}" y="{f(y0 + 7)}" width="{pw - 6}" height="{ph - 14}" rx="2" fill="{a1}" opacity=".08"/>')
    o.append(f'<path d="M{f(cx - 4)} {f(y0 + 3.6)}H{f(cx + 4)}M{f(cx - 5)} {f(y0 + ph - 3.6)}H{f(cx + 5)}" stroke="{a1}" stroke-width="1.4" stroke-linecap="round" opacity=".8"/>')
    for bx, by, bw, col, i in [(x0 + 5, y0 + 11, 13, a2, 0), (x0 + pw - 5 - 13, y0 + 19.5, 13, a1, 1), (x0 + 5, y0 + 28, 10, a2, 2)]:
        o.append(f'<rect x="{f(bx)}" y="{f(by)}" width="{bw}" height="5.5" rx="2.75" fill="{col}">{loop_opacity(.08 + i * .2, .9, 5)}</rect>')
    lx, ly = cx, y0 + 39
    o.append(f'<path d="M{f(lx - 2.6)} {f(ly)}V{f(ly - 1.6)}A2.6 2.6 0 0 1 {f(lx + 2.6)} {f(ly - 1.6)}V{f(ly)}" stroke="{C["lime"]}" stroke-width="1.2"/>'
             f'<rect x="{f(lx - 3.8)}" y="{f(ly)}" width="7.6" height="5.4" rx="1" fill="{C["lime"]}" class="breathe"/>')
    return "".join(o)


# -- fullstack-web: a tiny browser window + the project's own scene ----------

WY = EY + 23                       # top of the browser content area
WCY = (WY + EY + ES) / 2           # its vertical centre


def chrome(a1):
    o = []
    for i, op in enumerate((.9, .55, .3)):
        o.append(f'<circle cx="{EX + 13 + i * 8}" cy="{EY + 12}" r="2.2" fill="{a1}" opacity="{op}"/>')
    o.append(f'<rect x="{EX + 40}" y="{EY + 9}" width="{ES - 53}" height="6" rx="3" fill="{a1}" opacity=".12"/>')
    o.append(f'<line x1="{EX}" y1="{WY}" x2="{EX + ES}" y2="{WY}" stroke="{a1}" stroke-width="1" opacity=".28"/>')
    return "".join(o)


def em_code(d, a1, a2):
    """</> with a blinking caret."""
    o = [chrome(a1)]
    cx, cy = ECX - 4, WCY + .5
    g = lin(d, "codeG", [(0, a1), (1, a2)])
    glyph = (f"M{f(cx - 16)} {f(cy - 11)}L{f(cx - 27)} {f(cy)}L{f(cx - 16)} {f(cy + 11)}"
             f"M{f(cx - 4)} {f(cy + 14)}L{f(cx + 5)} {f(cy - 14)}"
             f"M{f(cx + 16)} {f(cy - 11)}L{f(cx + 27)} {f(cy)}L{f(cx + 16)} {f(cy + 11)}")
    o.append(f'<path d="{glyph}" stroke="{a1}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity=".18" filter="url(#eb)"/>')
    o.append(f'<path d="{glyph}" stroke="{g}" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" filter="url(#eg)"/>')
    o.append(f'<rect x="{f(cx + 32)}" y="{f(cy - 12)}" width="3" height="24" rx="1" fill="{C["ice"]}" class="blink"/>')
    return "".join(o)


def em_bomber(d, a1, a2):
    """B-2 flying wing, top-down, banking gently through cloud streaks, framed
    by camera brackets."""
    cx, cy = ECX, WCY + 1
    o = [chrome(a1)]
    rnd = random.Random(3)
    for k in range(6):
        x = EX + 10 + k * 15 + rnd.uniform(-4, 4)
        ln = rnd.uniform(8, 16)
        dur = rnd.uniform(1.1, 1.7)
        o.append(f'<line x1="{f(x)}" y1="{WY - ln}" x2="{f(x)}" y2="{WY}" stroke="{C["ice"]}" stroke-width="1" opacity=".35">'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {ES - 23 + ln:.0f}" dur="{dur:.2f}s" begin="-{rnd.uniform(0, 2):.2f}s" repeatCount="indefinite"/></line>')
    half = [(0, -13), (34, 7), (26, 11), (18, 5.5), (10, 11), (0, 6.5)]
    pts = half + [(-x, y) for x, y in reversed(half[1:-1])]
    poly = "M" + "L".join(f"{f(cx + x)} {f(cy + y)}" for x, y in pts) + "Z"
    bank = (f'<animateTransform attributeName="transform" type="rotate" values="-5 {cx} {cy};5 {cx} {cy};-5 {cx} {cy}" '
            f'dur="7s" repeatCount="indefinite" {SPLINE}/>')
    o.append(f'<g>{bank}'
             f'<path d="{poly}" fill="{a1}" opacity=".25" filter="url(#eb)"/>'
             f'<path d="{poly}" fill="{C["night"]}" stroke="{a1}" stroke-width="1.5" stroke-linejoin="round" filter="url(#eg)"/>'
             f'<path d="M{cx} {cy - 13}V{cy + 6}M{cx - 7} {cy - 2}L{cx} {cy - 7}L{cx + 7} {cy - 2}" stroke="{a2}" stroke-width="1.1" opacity=".8"/>'
             f'</g>')
    o.append(f'<g class="breathe">{corners(cx - 39, cy - 21, 78, 40, 7, C["ice"], 1.2, .8)}</g>')
    o.append(f'<circle cx="{EX + ES - 12}" cy="{WY + 8}" r="2.6" fill="{C["red"]}" class="blink"/>')
    return "".join(o)


def em_chat(d, a1, a2):
    """Chat rooms with an in-chat AI: bubbles arrive, the AI sparkles, then types."""
    o = [chrome(a1)]
    L, R = EX + 10, EX + ES - 10
    rows = [(L, WY + 8, 44, a2, .04), (R - 36, WY + 22, 36, a1, .2), (L, WY + 36, 30, C["ice"], .38)]
    for x, y, w, col, t in rows:
        o.append(f'<g opacity="0">{loop_opacity(t, .9, 6)}<rect x="{f(x)}" y="{f(y)}" width="{w}" height="10" rx="5" fill="{col}" opacity=".85"/></g>')
    # AI sparkle next to the third bubble
    sx, sy = L + 30 + 9, WY + 41
    star = f"M{sx} {sy - 6}Q{sx} {sy} {sx + 6} {sy}Q{sx} {sy} {sx} {sy + 6}Q{sx} {sy} {sx - 6} {sy}Q{sx} {sy} {sx} {sy - 6}Z"
    o.append(f'<g opacity="0">{loop_opacity(.38, .9, 6)}<path d="{star}" fill="{C["ice"]}" filter="url(#eg)" class="breathe"/></g>')
    # typing indicator
    ty = WY + 50
    dots = "".join(f'<circle cx="{L + 7 + k * 6}" cy="{ty + 5}" r="1.7" fill="{a1}">'
                   f'<animate attributeName="cy" values="{ty + 5};{ty + 2.5};{ty + 5};{ty + 5}" keyTimes="0;.2;.4;1" dur="1.2s" begin="{k * .18:.2f}s" repeatCount="indefinite"/></circle>'
                   for k in range(3))
    o.append(f'<g opacity="0">{loop_opacity(.55, .9, 6)}<rect x="{L}" y="{ty}" width="26" height="10" rx="5" fill="{C["panel2"]}" stroke="{a1}" stroke-opacity=".6"/>{dots}</g>')
    return "".join(o)


def em_rbac(d, a1, a2):
    """Four roles, each with its own access level; the active role cycles."""
    o = [chrome(a1)]
    levels = [1, .72, .46, .24]
    dur = 6
    for k, lvl in enumerate(levels):
        x = EX + 15 + k * 22
        hy = WY + 13
        bar_h = 26 * lvl
        on = k / 4
        if k == 0:
            vals, kt = "1;0", "0;.25"
        elif k == len(levels) - 1:
            vals, kt = "0;1", f"0;{on:.2f}"
        else:
            vals, kt = "0;1;0", f"0;{on:.2f};{on + .25:.2f}"
        glyph = (f'<circle cx="{x}" cy="{hy}" r="4.3" stroke="{a1}" stroke-width="1.5"/>'
                 f'<path d="M{x - 7.5} {hy + 15}A7.5 7.5 0 0 1 {x + 7.5} {hy + 15}" stroke="{a1}" stroke-width="1.5"/>'
                 f'<rect x="{x - 3}" y="{f(EY + ES - 10 - bar_h)}" width="6" height="{f(bar_h)}" rx="1.5" fill="{a1}"/>')
        o.append(f'<g opacity=".3">{glyph}</g>')
        o.append(f'<g opacity="{vals.split(";")[0]}" filter="url(#eg)">'
                 f'<animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="{dur}s" calcMode="discrete" repeatCount="indefinite"/>'
                 f'{glyph.replace(a1, C["ice"], 2).replace(a1, a2)}</g>')
    o.append(f'<line x1="{EX + 8}" y1="{EY + ES - 9.5}" x2="{EX + ES - 8}" y2="{EY + ES - 9.5}" stroke="{a1}" stroke-width="1" opacity=".35"/>')
    return "".join(o)


def em_timetable(d, a1, a2):
    """Timed course registration: the clock bar drains while slots fill in; a
    clash lights up red."""
    o = [chrome(a1)]
    dur = 6
    bx, bw = EX + 12, ES - 24
    o.append(f'<rect x="{bx}" y="{WY + 7}" width="{bw}" height="3" rx="1.5" fill="{a1}" opacity=".15"/>')
    o.append(f'<rect x="{bx}" y="{WY + 7}" width="{bw}" height="3" rx="1.5" fill="{C["amber"]}" filter="url(#eg)">'
             f'<animate attributeName="width" values="{bw};0;0" keyTimes="0;.92;1" dur="{dur}s" repeatCount="indefinite"/></rect>')
    cw, ch, g = 12, 9, 3
    x0, y0 = ECX - (5 * cw + 4 * g) / 2, WY + 17
    picks = [(0, 0), (2, 0), (1, 1), (3, 1), (4, 0), (0, 2), (2, 2), (4, 2), (1, 3), (3, 3)]
    clash = (3, 2)
    for r in range(4):
        for c_ in range(5):
            o.append(f'<rect x="{f(x0 + c_ * (cw + g))}" y="{f(y0 + r * (ch + g))}" width="{cw}" height="{ch}" rx="1.5" fill="{a1}" fill-opacity=".06" stroke="{a1}" stroke-opacity=".22"/>')
    for k, (c_, r) in enumerate(picks):
        col = a1 if k % 3 else a2
        o.append(f'<rect x="{f(x0 + c_ * (cw + g))}" y="{f(y0 + r * (ch + g))}" width="{cw}" height="{ch}" rx="1.5" fill="{col}" opacity="0">'
                 f'{loop_opacity(.04 + k * .07, .92, dur, .85)}</rect>')
    c_, r = clash
    o.append(f'<g opacity="0">{loop_opacity(.74, .92, dur)}'
             f'<rect x="{f(x0 + c_ * (cw + g))}" y="{f(y0 + r * (ch + g))}" width="{cw}" height="{ch}" rx="1.5" fill="{C["red"]}" filter="url(#eg)" class="blink"/></g>')
    return "".join(o)


def em_notes(d, a1, a2):
    """Offline-first notes: lines type into a page while a sync ring turns."""
    o = [chrome(a1)]
    dur = 6
    px, py, pw, ph, fold = EX + 18, WY + 7, 40, 58, 9
    page = f"M{px} {py}H{px + pw - fold}L{px + pw} {py + fold}V{py + ph}H{px}Z"
    o.append(f'<path d="{page}" fill="{C["panel2"]}" stroke="{a1}" stroke-width="1.5" stroke-linejoin="round"/>')
    o.append(f'<path d="M{px + pw - fold} {py}V{py + fold}H{px + pw}" stroke="{a1}" stroke-width="1.2" opacity=".7"/>')
    lines = [(px + 6, py + 12, 18, a1, 2.6), (px + 6, py + 22, 28, C["soft"], 2), (px + 6, py + 29, 24, C["soft"], 2),
             (px + 6, py + 36, 27, C["soft"], 2), (px + 6, py + 43, 15, C["soft"], 2)]
    for k, (x, y, w, col, sw) in enumerate(lines):
        t0, t1 = .05 + k * .14, .05 + k * .14 + .12
        o.append(f'<rect x="{x}" y="{f(y - sw / 2)}" width="0" height="{sw}" rx="1" fill="{col}" opacity=".85">'
                 f'<animate attributeName="width" values="0;0;{w};{w};0" keyTimes="0;{t0:.2f};{t1:.2f};.92;1" dur="{dur}s" repeatCount="indefinite"/></rect>')
    # sync badge
    sx, sy, r = px + pw + 6, py + ph - 8, 11
    arcs = (f"M{f(sx - 5.5)} {f(sy - 2)}A6 6 0 0 1 {f(sx + 4.5)} {f(sy - 3.5)}"
            f"M{f(sx + 5.5)} {f(sy + 2)}A6 6 0 0 1 {f(sx - 4.5)} {f(sy + 3.5)}")
    heads = (f"M{f(sx + 4.5)} {f(sy - 7)}L{f(sx + 4.8)} {f(sy - 3.2)}L{f(sx + 1)} {f(sy - 3)}"
             f"M{f(sx - 4.5)} {f(sy + 7)}L{f(sx - 4.8)} {f(sy + 3.2)}L{f(sx - 1)} {f(sy + 3)}")
    o.append(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{C["void"]}" stroke="{a2}" stroke-width="1.5"/>')
    o.append(f'<g><path d="{arcs}{heads}" stroke="{C["lime"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#eg)"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {sx} {sy}" to="360 {sx} {sy}" dur="3s" repeatCount="indefinite"/></g>')
    return "".join(o)


EMBLEM_FOR = {
    "Kaledo": em_code,
    "Jeevika": em_voice,
    "Quantum Tic-Tac-Toe": em_qboard,
    "Quantum Snake": em_bloch,
    "P2P Comm": em_phone,
    "AgentX Vision": em_eye,
    "B-2 Spirit Cinematic": em_bomber,
    "ChatPal 2.0": em_chat,
    "VTOP Portal": em_rbac,
    "FFCS Simulator": em_timetable,
    "Smart Irrigation": em_chip,
    "Offline Notes": em_notes,
}
EMBLEM_BY_CAT = {"quantum": em_bloch, "ai-ml": em_eye, "iot-embedded": em_chip, "mobile": em_phone, "fullstack-web": em_code}


# --------------------------------------------------------------------- tile --

def tile(i: int, item: dict) -> Doc:
    cat = item["category"]
    a1, a2 = ACCENT[cat]
    repo = item["repo"].rsplit("/", 1)[1]
    d = Doc(W, H, title=f'{item["title"]} — {item["line"]}')
    glow(d, "eg", std=2.2, strength=2)
    glow(d, "hg", std=3.2, strength=2)
    blur(d, "eb", 3)
    blur(d, "neb", 26)

    phase = i * SWEEP / len(content.ARCHIVE)      # stagger the border comet across the grid
    lead = (i % 2) * .12                          # right-hand column lands a beat later

    op, close = panel(d, W, H, rx=RX, bars=False, grain_op=.06)
    o = [op]
    # ---- atmosphere --------------------------------------------------------------
    o.append(f'<g filter="url(#neb)">'
             f'<ellipse cx="{ECX}" cy="{ECY}" rx="120" ry="78" fill="{a1}" opacity=".22">'
             f'<animate attributeName="opacity" values=".22;.12;.22" dur="8s" begin="-{phase:.2f}s" repeatCount="indefinite"/></ellipse>'
             f'<ellipse cx="{W - 70}" cy="{H + 10}" rx="230" ry="60" fill="{a2}" opacity=".12"/>'
             f'<ellipse cx="{W * .55}" cy="-20" rx="200" ry="40" fill="{a1}" opacity=".07"/></g>')
    o.append(f'<g opacity=".55">{stars(100 + i, 34, W, H, rmax=1.15, twinkle=True)}</g>')
    d.defs.append('<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#fff" opacity=".07"/></pattern>')
    d.defs.append(f'<mask id="dotMask"><rect width="{W}" height="{H}" fill="{lin(d, "dm", [(0, "#fff", 0), (.25, "#fff", .9), (1, "#fff", 0)])}"/></mask>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotMask)"/>')
    o.append(f'<rect x="0" y="0" width="{W}" height="1.5" fill="{lin(d, "topHl", [(0, a1, 0), (.12, a1, .9), (.5, a2, .35), (1, a2, 0)])}"/>')
    # slow scan band (echoes the hero), phase-shifted per tile
    d.css.append(f"@keyframes arcScan{{from{{transform:translateY(-70px)}}to{{transform:translateY({H + 10}px)}}}}"
                 f".scan{{animation:arcScan 7.5s linear infinite}}"
                 f"@keyframes arcBeam{{0%{{transform:translateX(-30px);opacity:0}}12%{{opacity:1}}82%{{opacity:1}}100%{{transform:translateX({W + 30}px);opacity:0}}}}"
                 f".beam{{opacity:0;animation:arcBeam 1.15s cubic-bezier(.55,.05,.35,1) both}}")
    o.append(f'<rect class="scan" style="animation-delay:-{phase * .83:.2f}s" x="0" y="0" width="{W}" height="60" '
             f'fill="{lin(d, "scanG", [(0, a1, 0), (.75, a1, .035), (.93, a1, .075), (1, a1, 0)], 0, 0, 0, 1)}"/>')
    # divider between emblem and text: a dashed hairline with end ticks
    vx = EX + ES + 15
    o.append(f'<g class="fi" style="animation-delay:{lead + .3:.2f}s" stroke="{a1}">'
             f'<line x1="{vx}" y1="{EY + 6}" x2="{vx}" y2="{EY + ES - 6}" stroke-width="1" stroke-dasharray="1 4" opacity=".45"/>'
             f'<path d="M{vx - 3} {EY}H{vx + 3}M{vx - 3} {EY + ES}H{vx + 3}" stroke-width="1.2" opacity=".7"/></g>')

    # ---- emblem box ------------------------------------------------------------
    d.defs.append(f'<clipPath id="boxClip"><rect x="{EX}" y="{EY}" width="{ES}" height="{ES}" rx="12"/></clipPath>')
    emblem = EMBLEM_FOR.get(item["title"], EMBLEM_BY_CAT[cat])
    o.append(f'<g class="fi" style="animation-delay:{lead:.2f}s">'
             f'<rect x="{EX}" y="{EY}" width="{ES}" height="{ES}" rx="12" '
             f'fill="{rad(d, "boxF", [(0, a1, .16), (.7, a1, .04), (1, C["panel"], .6)], r=.75)}" stroke="{a1}" stroke-opacity=".22"/>'
             f'{corners(EX - 5, EY - 5, ES + 10, ES + 10, 9, a1, 1.4, .85)}'
             f'<g clip-path="url(#boxClip)">{emblem(d, a1, a2)}</g></g>')

    # ---- text column -----------------------------------------------------------
    title = item["title"].upper()
    halo = d.text(title, TX, TITLE_Y, "sans-sb", 26, a1, tracking=2, attrs='opacity=".45" filter="url(#eb)"')
    crisp = d.text(title, TX, TITLE_Y, "sans-sb", 26, C["text"], tracking=2)
    o.append(f'<g class="sr" style="animation-delay:{lead + .15:.2f}s">{halo}{crisp}</g>')
    lines = two_lines(item["line"], "sans", 18, TW)
    o.append(f'<g class="fi" style="animation-delay:{lead + .35:.2f}s">')
    for k, ln in enumerate(lines):
        o.append(d.text(ln, TX, LINE_Y + k * LINE_H, "sans", 18, C["soft"]))
    o.append("</g>")

    # bottom row: category chip  ·  LIVE / repo path
    lab = LABEL[cat]
    lw = d.width(lab, "mono-b", 13, 2)
    chip_h, pad = 21, 9
    cy0 = ROW_Y - 14.5
    chip_w = lw + 2 * pad + 10
    row = [f'<g class="fi" style="animation-delay:{lead + .5:.2f}s">']
    row.append(f'<rect x="{TX}" y="{f(cy0)}" width="{f(chip_w)}" height="{chip_h}" rx="4" fill="{a1}" fill-opacity=".1" stroke="{a1}" stroke-opacity=".45"/>')
    row.append(f'<rect x="{TX + pad}" y="{f(cy0 + chip_h / 2 - 2.5)}" width="5" height="5" fill="{a1}"/>')
    row.append(d.text(lab, TX + pad + 11, ROW_Y, "mono-b", 13, a1, tracking=2))
    chip_end = TX + chip_w
    if item["live"]:
        txt = "LIVE ↗"
        tw_ = d.width(txt, "mono-b", 13, 2)
        row.append(f'<circle cx="{f(TR - tw_ - 12)}" cy="{f(ROW_Y - 4.6)}" r="4" fill="{C["lime"]}" filter="url(#eg)" class="breathe"/>')
        row.append(d.text(txt, TR, ROW_Y, "mono-b", 13, C["lime"], "end", 2))
        left_edge = TR - tw_ - 18
    else:
        rw = d.width(repo, "mono", 13)
        ow = d.width("Arrow-Ghost/", "mono", 13)
        row.append(d.text("Arrow-Ghost/", TR - rw, ROW_Y, "mono", 13, C["dim"], "end"))
        row.append(d.text(repo, TR, ROW_Y, "mono", 13, C["muted"], "end"))
        left_edge = TR - rw - ow
    row.append("</g>")
    if left_edge - chip_end < 16:
        raise ValueError(f"bottom row collides for {item['title']}: gap {left_edge - chip_end:.1f}")
    o.extend(row)

    # file index, top-right
    idx = f"04.{i + 1:02d}"
    iw = d.width(idx, "mono-m", 13, 2)
    o.append(f'<g class="fi" style="animation-delay:{lead + .65:.2f}s">'
             f'<line x1="{f(TR - iw - 24)}" y1="25.5" x2="{f(TR - iw - 10)}" y2="25.5" stroke="{a1}" stroke-width="1.5"/>'
             f'{d.text(idx, TR, 30, "mono-m", 13, C["muted"], "end", 2)}</g>')

    # projector beam: one bright vertical sweep that "prints" the frame on load
    o.append(f'<g class="beam" style="animation-delay:{lead:.2f}s">'
             f'<rect x="-60" y="0" width="60" height="{H}" fill="{lin(d, "beamG", [(0, a1, 0), (1, a1, .22)])}"/>'
             f'<rect x="-1" y="0" width="2" height="{H}" fill="#fff" filter="url(#hg)"/></g>')

    o.append(close)

    # ---- border comet: a light that runs the perimeter -------------------------
    bp = rrect_path(.75, .75, W - 1.5, H - 1.5, RX - .5)
    for L, col, sw, op_, filt in [(.30, a1, 1.2, .35, ""), (.10, a1, 1.6, .9, ' filter="url(#hg)"'), (.018, "#fff", 2.2, 1, ' filter="url(#hg)"')]:
        o.append(f'<path d="{bp}" pathLength="1" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" opacity="{op_}" '
                 f'stroke-dasharray="{L} {1 - L:.3f}" stroke-dashoffset="{L}"{filt}>'
                 f'<animate attributeName="stroke-dashoffset" values="{L};{L - 1:.3f}" dur="{SWEEP}s" begin="-{phase:.2f}s" repeatCount="indefinite"/></path>')
    d.add(*o)
    return d


def build():
    paths = []
    for i, item in enumerate(content.ARCHIVE):
        paths.append(tile(i, item).save(f"arc-{slug(item['title'])}.svg"))
    return paths


if __name__ == "__main__":
    build()
