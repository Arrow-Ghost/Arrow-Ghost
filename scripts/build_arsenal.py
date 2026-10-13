"""Scene 02 — THE ARSENAL.

Left: an orbital reactor. A pulsing qubit core (Bloch sphere with a precessing
state vector) sits inside four tilted orbits; one node per domain rides them
(SMIL animateMotion) with comet trails, depth-dimming on the far side, and an
always-upright label that stays on the outward side of its orbit.

Right: the loadout. Eight domain rows, each a glyph + mono label + tool count,
followed by tool chips wrapped to width. Chips stagger in during the intro.

After the intro a 24 s "target lock" cycle scans the list: a beam links each
domain's orbit node to its row, the row lights up and a glint runs across its
chips. Everything shares one SMIL timeline so beams, reticles and rows agree.
"""

import math

from agfx import ACCENT, C, Doc, Font, blur, corners, f, glow, grain, lin, rad, signature, stars
from content import ARSENAL

W = 1280
BAR = 38

# ---------------------------------------------------------------- layout ---
DIV_X = 458                    # divider between reactor (left) and loadout (right)
RX0 = DIV_X + 16               # row content start (glyph tile)
RIGHT = W - 44                 # right margin
LABEL_FONT, LABEL_SIZE, LABEL_TR = "mono-b", 15, 2.2
SUB_FONT, SUB_SIZE, SUB_TR = "mono", 13, 2
CHIP_FONT, CHIP_SIZE = "sans-sb", 17
CHIP_H, CHIP_PITCH, CHIP_PAD, CHIP_GAP = 28, 36, 11, 7
ROW_PAD = 9
TOP = BAR + 14                 # first row top

HALO = f'stroke="{C["void"]}" stroke-width="4" paint-order="stroke" stroke-linejoin="round"'

SHORT = ["LANG", "WEB", "AI/ML", "QUANTUM", "SEC", "IoT", "DATA", "MOBILE"]
GLYPHS = ["code", "globe", "eye", "atom", "shield", "chip", "db", "phone"]

CYCLE_SLOT = 3.0               # seconds each domain is "locked"
CYCLE_BEGIN = 3.4              # lock cycle starts once the intro has settled
CYCLE = CYCLE_SLOT * len(ARSENAL)

ORBITS = [
    # rx, ry, tilt°, seconds per lap, ring-flow direction, domains (two per orbit, opposite)
    (90, 32, -24, 15, 1, (3, 4)),      # QUANTUM · SEC
    (126, 44, 32, 21, -1, (2, 5)),     # AI · IoT
    (156, 54, -58, 28, 1, (1, 7)),     # WEB · MOBILE
    (182, 62, 74, 36, -1, (0, 6)),     # LANG · DATA
]


def glyph(kind, x, y, col, sw=1.5):
    """20x20 stroke icons drawn in place (top-left x,y)."""
    def P(d):
        return f'<path d="{d}" stroke="{col}" stroke-width="{sw}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    X = lambda v: f(x + v)
    Y = lambda v: f(y + v)
    if kind == "code":
        return P(f"M{X(6)} {Y(5)}L{X(1.5)} {Y(10)}L{X(6)} {Y(15)}M{X(14)} {Y(5)}L{X(18.5)} {Y(10)}L{X(14)} {Y(15)}M{X(11.5)} {Y(3.5)}L{X(8.5)} {Y(16.5)}")
    if kind == "globe":
        return (f'<circle cx="{X(10)}" cy="{Y(10)}" r="8" stroke="{col}" stroke-width="{sw}"/>'
                f'<ellipse cx="{X(10)}" cy="{Y(10)}" rx="3.6" ry="8" stroke="{col}" stroke-width="{sw}"/>'
                + P(f"M{X(2)} {Y(10)}H{X(18)}M{X(3.5)} {Y(5.8)}H{X(16.5)}M{X(3.5)} {Y(14.2)}H{X(16.5)}"))
    if kind == "eye":
        return (P(f"M{X(1)} {Y(10)}Q{X(10)} {Y(1.5)} {X(19)} {Y(10)}Q{X(10)} {Y(18.5)} {X(1)} {Y(10)}Z")
                + f'<circle cx="{X(10)}" cy="{Y(10)}" r="3.2" stroke="{col}" stroke-width="{sw}"/>'
                + f'<circle cx="{X(10)}" cy="{Y(10)}" r="1.1" fill="{col}"/>')
    if kind == "atom":
        out = [f'<circle cx="{X(10)}" cy="{Y(10)}" r="1.7" fill="{col}"/>']
        for a in (0, 60, 120):
            out.append(f'<ellipse cx="{X(10)}" cy="{Y(10)}" rx="9" ry="3.6" transform="rotate({a} {X(10)} {Y(10)})" stroke="{col}" stroke-width="{sw * .85:.2f}"/>')
        return "".join(out)
    if kind == "shield":
        return P(f"M{X(10)} {Y(1.5)}L{X(17.5)} {Y(4.5)}V{Y(10)}C{X(17.5)} {Y(14.2)} {X(14.4)} {Y(17.2)} {X(10)} {Y(18.8)}"
                 f"C{X(5.6)} {Y(17.2)} {X(2.5)} {Y(14.2)} {X(2.5)} {Y(10)}V{Y(4.5)}Z M{X(6.6)} {Y(10)}L{X(9)} {Y(12.4)}L{X(13.6)} {Y(7.6)}")
    if kind == "chip":
        pins = []
        for v in (7.5, 10, 12.5):
            pins.append(f"M{X(v)} {Y(1.5)}V{Y(4.5)}M{X(v)} {Y(15.5)}V{Y(18.5)}M{X(1.5)} {Y(v)}H{X(4.5)}M{X(15.5)} {Y(v)}H{X(18.5)}")
        return (f'<rect x="{X(4.5)}" y="{Y(4.5)}" width="11" height="11" rx="1.8" stroke="{col}" stroke-width="{sw}"/>'
                + P("".join(pins)) + f'<rect x="{X(8)}" y="{Y(8)}" width="4" height="4" fill="{col}" opacity=".8"/>')
    if kind == "db":
        return (f'<ellipse cx="{X(10)}" cy="{Y(4.5)}" rx="7" ry="2.6" stroke="{col}" stroke-width="{sw}"/>'
                + P(f"M{X(3)} {Y(4.5)}V{Y(15.5)}A7 2.6 0 0 0 {X(17)} {Y(15.5)}V{Y(4.5)}M{X(3)} {Y(10)}A7 2.6 0 0 0 {X(17)} {Y(10)}"))
    if kind == "phone":
        return (f'<rect x="{X(5)}" y="{Y(1.5)}" width="10" height="17" rx="2.4" stroke="{col}" stroke-width="{sw}"/>'
                + P(f"M{X(8.6)} {Y(15.4)}H{X(11.4)}M{X(8.6)} {Y(3.8)}H{X(11.4)}"))
    return ""


def ket(doc, label, x, y, size, fill, font="mono", anchor="start"):
    """|label⟩ with a drawn closing angle (the font lacks ⟩)."""
    fo = Font.get(font)
    wdt = fo.width("|" + label, size) + size * 0.36
    if anchor == "middle":
        x -= wdt / 2
    t = doc.text("|" + label, x, y, font, size, fill)
    ax, top, bot = x + fo.width("|" + label, size) + size * 0.08, y - size * 0.74, y + size * 0.16
    mid = (top + bot) / 2
    return t + (f'<path d="M{f(ax)} {f(top)}L{f(ax + size * 0.28)} {f(mid)}L{f(ax)} {f(bot)}" stroke="{fill}" '
                f'stroke-width="{f(size * 0.075)}" fill="none" stroke-linecap="round"/>')


# ------------------------------------------------------------- timeline ---

def lock_window(i, fade=0.35):
    """values/keyTimes for an opacity that is 1 during domain i's lock slot, else 0."""
    a = i * CYCLE_SLOT / CYCLE
    b = (i + 1) * CYCLE_SLOT / CYCLE
    fd = fade / CYCLE
    kt, vals = [0.0], [0]
    if a > 0:
        kt.append(a)
        vals.append(0)
    kt += [a + fd, b - fd]
    vals += [1, 1]
    if b < 1:
        kt.append(b)
        vals.append(0)
    kt.append(1.0)
    vals.append(0)
    return ";".join(str(v) for v in vals), ";".join(f"{k:.4f}" for k in kt)


def anim_lock(i, attr="opacity", fade=0.35):
    v, k = lock_window(i, fade)
    return (f'<animate attributeName="{attr}" values="{v}" keyTimes="{k}" dur="{CYCLE:g}s" '
            f'begin="{CYCLE_BEGIN}s" repeatCount="indefinite"/>')


# ------------------------------------------------------------- geometry ---

def ellipse_samples(rx, ry, alpha, cx, cy, k=72):
    """k+1 points equally spaced by ARC LENGTH along the tilted ellipse,
    starting at t=0 and running in +t (clockwise on screen) — the same
    parametrisation a paced animateMotion uses. Returns [(x, y, depth)],
    depth = sin t (front = +1)."""
    n = 2000
    ca, sa = math.cos(alpha), math.sin(alpha)
    pts, cum = [], [0.0]
    for j in range(n + 1):
        t = 2 * math.pi * j / n
        lx, ly = rx * math.cos(t), ry * math.sin(t)
        pts.append((t, cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
        if j:
            cum.append(cum[-1] + math.hypot(pts[j][1] - pts[j - 1][1], pts[j][2] - pts[j - 1][2]))
    total = cum[-1]
    out, j = [], 0
    for s in range(k + 1):
        target = total * s / k
        while j < n - 1 and cum[j + 1] < target:
            j += 1
        j1 = j + 1
        seg = cum[j1] - cum[j] or 1
        u = min(1.0, max(0.0, (target - cum[j]) / seg))
        t = pts[j][0] + (pts[j1][0] - pts[j][0]) * u
        lx, ly = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca, math.sin(t)))
    return out


def ellipse_path(rx, ry, alpha_deg, cx, cy):
    a = math.radians(alpha_deg)
    sx, sy = cx + rx * math.cos(a), cy + rx * math.sin(a)
    ex, ey = cx - rx * math.cos(a), cy - rx * math.sin(a)
    return (f"M{f(sx)} {f(sy)}A{f(rx)} {f(ry)} {f(alpha_deg)} 0 1 {f(ex)} {f(ey)}"
            f"A{f(rx)} {f(ry)} {f(alpha_deg)} 0 1 {f(sx)} {f(sy)}Z")


def half_path(rx, ry, alpha_deg, cx, cy, front=True):
    """Front half = local +y side (t in 0..pi)."""
    a = math.radians(alpha_deg)
    sx, sy = cx + rx * math.cos(a), cy + rx * math.sin(a)
    ex, ey = cx - rx * math.cos(a), cy - rx * math.sin(a)
    if front:
        return f"M{f(sx)} {f(sy)}A{f(rx)} {f(ry)} {f(alpha_deg)} 0 1 {f(ex)} {f(ey)}"
    return f"M{f(ex)} {f(ey)}A{f(rx)} {f(ry)} {f(alpha_deg)} 0 1 {f(sx)} {f(sy)}"


# ------------------------------------------------------------- loadout ---

def layout_rows(doc):
    """Measure every row: label column width, chip positions, row heights."""
    lab_w = max(doc.width(d, LABEL_FONT, LABEL_SIZE, LABEL_TR) for d, _, _ in ARSENAL)
    label_x = RX0 + 36
    chip_x0 = label_x + lab_w + 20
    fo = Font.get(CHIP_FONT)
    rows, y = [], TOP
    for i, (dom, cat, tools) in enumerate(ARSENAL):
        chips, cx, line = [], chip_x0, 0
        for t in tools:
            w = fo.width(t, CHIP_SIZE) + 2 * CHIP_PAD
            if cx > chip_x0 and cx + w > RIGHT:
                line += 1
                cx = chip_x0
            chips.append((t, cx, line, w))
            cx += w + CHIP_GAP
        nlines = line + 1
        chips_h = CHIP_H + (nlines - 1) * CHIP_PITCH
        h = max(chips_h, 40) + 2 * ROW_PAD
        rows.append(dict(i=i, dom=dom, cat=cat, tools=tools, chips=chips, y=y, h=h, nlines=nlines))
        y += h
    return rows, label_x, chip_x0, y


def build():
    d = Doc(W, 100, title="The Arsenal — Shrish Verma's loadout: 8 domains of tools and stacks")
    rows, label_x, chip_x0, rows_bottom = layout_rows(d)
    H = rows_bottom + 14 + BAR
    d.h = H
    n_tools = sum(len(t) for _, _, t in ARSENAL)
    CX = DIV_X / 2 + 4
    CY = (BAR + 64 + H - BAR - 58) / 2

    sig = signature(d, "sig", animate=True, dur=7)
    glow(d, "glowS", std=2.2, strength=2)
    blur(d, "neb", 60)
    blur(d, "flareBlur", 6)

    d.defs.append(f'<clipPath id="frame"><rect width="{W}" height="{f(H)}" rx="20"/></clipPath>')
    vign = rad(d, "vign", [(0, "#000", 0), (0.6, "#000", 0), (1, "#000", 0.8)], r=0.78)
    d.defs.append('<pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".04"/></pattern>')
    d.defs.append(f'<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r=".9" fill="{C["line2"]}"/></pattern>')
    d.defs.append(f'<mask id="dotMask"><rect x="{DIV_X}" y="{BAR}" width="{W - DIV_X}" height="{f(H - 2 * BAR)}" '
                  f'fill="{lin(d, "dm", [(0, "#fff", .55), (0.5, "#fff", .15), (1, "#fff", .0)])}"/></mask>')
    d.defs.append(f'<mask id="starMask"><rect width="{W}" height="{f(H)}" fill="{lin(d, "sm", [(0, "#fff", 1), (0.34, "#fff", .9), (0.48, "#fff", .25), (1, "#fff", .12)])}"/></mask>')

    d.css.append(f"""
@keyframes bars{{from{{transform:scaleY(2.4)}}to{{transform:scaleY(1)}}}}
@keyframes arsScan{{from{{transform:translateY(-160px)}}to{{transform:translateY({f(H + 160)}px)}}}}
@keyframes flow{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-60}}}}
@keyframes flowR{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:60}}}}
@keyframes beamFlow{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-16}}}}
@keyframes corePulse{{0%,100%{{transform:scale(1);opacity:.85}}50%{{transform:scale(1.18);opacity:1}}}}
@keyframes spin{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
@keyframes spinR{{from{{transform:rotate(0deg)}}to{{transform:rotate(-360deg)}}}}
@keyframes specGlint{{0%{{transform:translateX(-120px)}}40%,100%{{transform:translateX({DIV_X}px)}}}}
@keyframes flareP{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
.barT,.barB{{animation:bars 1.5s cubic-bezier(.7,0,.2,1) both}}
.barT{{transform-origin:0 0}}.barB{{transform-origin:0 100%}}
.scan{{animation:arsScan 9s linear infinite}}
.core{{transform-box:fill-box;transform-origin:center;animation:corePulse 3.2s ease-in-out infinite}}
.spin{{transform-origin:{f(CX)}px {f(CY)}px;animation:spin 140s linear infinite}}
.spinR{{transform-origin:{f(CX)}px {f(CY)}px;animation:spinR 60s linear infinite}}
.spinF{{transform-origin:{f(CX)}px {f(CY)}px;animation:spin 18s linear infinite}}
.beam{{stroke-dasharray:3 5;animation:beamFlow .9s linear infinite}}
.glint{{animation:specGlint 7s 3.4s ease-in-out infinite;transform:translateX(-120px)}}
.flareP{{animation:flareP 3.2s ease-in-out infinite}}
.chip{{animation-duration:.7s}}
""")

    out = d.body
    out.append('<g clip-path="url(#frame)">')
    out.append(f'<rect width="{W}" height="{f(H)}" fill="{C["void"]}"/>')

    # ---- nebula --------------------------------------------------------------
    out.append('<g filter="url(#neb)">')
    for (x, y, rx_, ry_, col, op, dx, dy, dur) in [
        (CX - 20, CY + 40, 250, 210, C["violet"], .42, 30, -20, 24),
        (CX + 60, CY - 130, 200, 130, C["cyan"], .22, -30, 20, 29),
        (CX - 120, CY + 210, 180, 90, C["magenta"], .24, 40, -10, 21),
        (980, H + 40, 420, 120, C["violet"], .22, -50, 0, 33),
        (1180, BAR - 10, 300, 90, C["cyan"], .10, -40, 10, 27),
    ]:
        out.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{rx_}" ry="{ry_}" fill="{col}" opacity="{op}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                   f'<animate attributeName="opacity" values="{op};{op * .55:.2f};{op}" dur="{dur * .7:.1f}s" repeatCount="indefinite"/></ellipse>')
    out.append("</g>")

    # ---- stars (masked toward the reactor) + dot grid under the loadout ---------------------
    out.append('<g mask="url(#starMask)">')
    for seed, n, rmax, dur, op in [(31, 110, 1.0, 260, .65), (37, 40, 1.5, 150, .85), (41, 12, 2.0, 95, 1)]:
        layer = stars(seed, n, W, H, rmax=rmax, twinkle=True)
        out.append(f'<g opacity="{op}"><g>{layer}<g transform="translate({W} 0)">{layer}</g>'
                   f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="{dur}s" repeatCount="indefinite"/></g></g>')
    out.append("</g>")
    out.append(f'<rect x="{DIV_X}" y="{BAR}" width="{W - DIV_X}" height="{f(H - 2 * BAR)}" fill="url(#dots)" mask="url(#dotMask)"/>')

    reactor(d, out, CX, CY, H, rows, sig)
    loadout(d, out, rows, chip_x0, label_x)

    # ---- divider -------------------------------------------------------------------------
    out.append(f'<g class="fi" style="animation-delay:.5s">'
               f'<line x1="{DIV_X}" y1="{BAR + 14}" x2="{DIV_X}" y2="{f(H - BAR - 14)}" stroke="{C["line2"]}" stroke-width="1"/>')
    for k in range(int((H - 2 * BAR - 28) // 12) + 1):
        yy = BAR + 14 + k * 12
        ln = 5 if k % 5 == 0 else 2.5
        out.append(f'<line x1="{DIV_X - ln}" y1="{f(yy)}" x2="{DIV_X}" y2="{f(yy)}" stroke="{C["line2"]}"/>')
    out.append("</g>")

    # ---- scan band, scanlines, vignette, grain ---------------------------------------
    out.append(f'<rect width="{W}" height="{f(H)}" fill="url(#scanlines)"/>')
    out.append(f'<rect class="scan" x="0" y="0" width="{W}" height="120" fill="{lin(d, "scanG", [(0, C["cyan"], 0), (.7, C["cyan"], .035), (.9, C["cyan"], .07), (1, C["cyan"], 0)], 0, 0, 0, 1)}"/>')
    out.append(f'<rect width="{W}" height="{f(H)}" fill="{vign}"/>')
    out.append(grain(d, .08))

    # ---- letterbox slate bars ----------------------------------------------------------
    out.append(f'<rect class="barT" width="{W}" height="{BAR}" fill="#000"/>')
    out.append(f'<rect class="barB" y="{f(H - BAR)}" width="{W}" height="{BAR}" fill="#000"/>')
    out.append(f'<line x1="0" y1="{BAR}" x2="{W}" y2="{BAR}" stroke="{C["line"]}"/>')
    out.append(f'<line x1="0" y1="{f(H - BAR)}" x2="{W}" y2="{f(H - BAR)}" stroke="{C["line"]}"/>')
    ty = BAR / 2 + 5
    out.append('<g class="fi" style="animation-delay:1.1s">')
    out.append(d.text("SCENE 02", 34, ty, "mono-b", 13, C["text"], tracking=3))
    out.append(d.text("— THE ARSENAL", 34 + d.width("SCENE 02", "mono-b", 13, 3) + 12, ty, "mono", 13, C["muted"], tracking=3))
    rtxt = f"8 DOMAINS · {n_tools} TOOLS"
    rw = d.width(rtxt, "mono", 13, 3)
    out.append(d.text(rtxt, W - 34, ty, "mono", 13, C["muted"], "end", 3))
    lw = d.width("LOADOUT //", "mono-b", 13, 3)
    out.append(d.text("LOADOUT //", W - 34 - rw - 12, ty, "mono-b", 13, C["text"], "end", 3))
    out.append(f'<circle cx="{f(W - 34 - rw - 12 - lw - 16)}" cy="{ty - 4.5}" r="3.6" fill="{C["cyan"]}" class="breathe"/>')
    out.append("</g>")

    by2 = H - BAR / 2 + 5
    out.append('<g class="fi" style="animation-delay:1.3s">')
    out.append(d.text("PRIMARY: PYTHON · TYPESCRIPT · C++ · QISKIT", 34, by2, "mono", 12.5, C["muted"], tracking=2.4))
    status = "ALL SYSTEMS ARMED"
    sw_ = d.width(status, "mono-m", 12.5, 2.4)
    out.append(f'<circle cx="{f(W - 34 - sw_ - 14)}" cy="{f(by2 - 4.5)}" r="3.6" fill="{C["lime"]}" class="breathe"/>')
    out.append(d.text(status, W - 34, by2, "mono-m", 12.5, C["lime"], "end", 2.4))
    out.append("</g>")

    out.append(f'<g class="fi" style="animation-delay:.9s">{corners(22, BAR + 12, W - 44, H - 2 * BAR - 24, 18, C["cyan"], 1.3, .55)}</g>')
    out.append("</g>")  # frame clip
    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{f(H - 1)}" rx="20" stroke="{C["line2"]}" fill="none"/>')
    return d


# ================================================================ REACTOR ===

def reactor(d, out, CX, CY, H, rows, sig):
    K = 72
    # ---- outer HUD dial ------------------------------------------------------------------
    R_D = 186
    ticks = []
    for k in range(72):
        a = math.radians(k * 5)
        r1 = R_D - (9 if k % 6 == 0 else 4)
        ticks.append(f"M{f(CX + R_D * math.cos(a))} {f(CY + R_D * math.sin(a))}L{f(CX + r1 * math.cos(a))} {f(CY + r1 * math.sin(a))}")
    out.append(f'<g class="fi" style="animation-delay:.2s;animation-duration:2s">'
               f'<g class="spin"><path d="{"".join(ticks)}" stroke="{C["line2"]}" stroke-width="1.1"/>'
               f'<circle cx="{f(CX)}" cy="{f(CY)}" r="{R_D + 6}" stroke="{C["line"]}" stroke-width="1"/></g>')
    arcs = []
    for a0 in (20, 140, 260):
        a1 = a0 + 34
        p0 = (CX + (R_D + 6) * math.cos(math.radians(a0)), CY + (R_D + 6) * math.sin(math.radians(a0)))
        p1 = (CX + (R_D + 6) * math.cos(math.radians(a1)), CY + (R_D + 6) * math.sin(math.radians(a1)))
        arcs.append(f"M{f(p0[0])} {f(p0[1])}A{R_D + 6} {R_D + 6} 0 0 1 {f(p1[0])} {f(p1[1])}")
    out.append(f'<g class="spinR"><path d="{"".join(arcs)}" stroke="{C["cyan"]}" stroke-width="2" opacity=".7" stroke-linecap="round"/></g>')
    out.append(f'<path d="M{f(CX - R_D - 12)} {f(CY)}H{f(CX - R_D + 14)}M{f(CX + R_D - 14)} {f(CY)}H{f(CX + R_D + 12)}'
               f'M{f(CX)} {f(CY - R_D - 12)}V{f(CY - R_D + 14)}M{f(CX)} {f(CY + R_D - 14)}V{f(CY + R_D + 12)}" stroke="{C["ice"]}" stroke-width="1.2" opacity=".55"/>')
    out.append("</g>")

    # ---- core halo + shockwaves -------------------------------------------------------------
    halo = rad(d, "halo", [(0, C["ice"], .5), (0.25, C["cyan"], .26), (0.6, C["violet"], .11), (1, C["violet"], 0)])
    out.append(f'<circle cx="{f(CX)}" cy="{f(CY)}" r="160" fill="{halo}" class="breathe"/>')
    for k in range(3):
        b = f"{1.2 + k * 1.8:.1f}s"
        out.append(f'<circle cx="{f(CX)}" cy="{f(CY)}" r="44" stroke="{C["cyan"]}" stroke-width="1.2" opacity="0">'
                   f'<animate attributeName="r" values="44;186" dur="5.4s" begin="{b}" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".2 .6 .4 1"/>'
                   f'<animate attributeName="opacity" values=".5;0" dur="5.4s" begin="{b}" repeatCount="indefinite"/>'
                   f'<animate attributeName="stroke-width" values="2;.4" dur="5.4s" begin="{b}" repeatCount="indefinite"/></circle>')

    # ---- holo-projector base + light cone -------------------------------------------------
    by_ = CY + 236
    cone = lin(d, "cone", [(0, C["cyan"], 0), (0.55, C["cyan"], .05), (1, C["cyan"], .16)], 0, 0, 0, 1)
    out.append(f'<g class="fi" style="animation-delay:.4s;animation-duration:2s">'
               f'<path d="M{f(CX - 30)} {f(CY + 30)}L{f(CX + 30)} {f(CY + 30)}L{f(CX + 132)} {f(by_)}L{f(CX - 132)} {f(by_)}Z" fill="{cone}"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(by_)}" rx="150" ry="22" fill="{rad(d, "plate", [(0, C["cyan"], .28), (0.6, C["cyan"], .07), (1, C["cyan"], 0)])}"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(by_)}" rx="148" ry="21" stroke="{C["cyan"]}" stroke-width="1" stroke-dasharray="1 6" opacity=".7" style="animation:flow 9s linear infinite"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(by_)}" rx="132" ry="18" stroke="{C["cyan"]}" stroke-width="1.3" opacity=".65"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(by_)}" rx="100" ry="13.5" stroke="{C["ice"]}" stroke-width="1" stroke-dasharray="14 6 2 6" opacity=".5" style="animation:flowR 7s linear infinite"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(by_)}" rx="62" ry="8.5" stroke="{C["violet"]}" stroke-width="1.2" opacity=".7"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(by_)}" rx="22" ry="3.2" fill="{C["ice"]}" opacity=".8" filter="url(#flareBlur)"/>'
               f'</g>')

    # ---- orbits: back halves + flowing energy (behind the core) ---------------------------
    for oi, (rx, ry, tilt, T, dirn, doms) in enumerate(ORBITS):
        back = half_path(rx, ry, tilt, CX, CY, front=False)
        full = ellipse_path(rx, ry, tilt, CX, CY)
        out.append(f'<g class="fi" style="animation-delay:{.3 + oi * .15:.2f}s">'
                   f'<path d="{back}" stroke="{C["soft"]}" stroke-width="1" stroke-dasharray="2 5" opacity=".35"/>'
                   f'<path d="{full}" stroke="{C["ice"]}" stroke-width="1.6" stroke-dasharray="1 13" opacity=".55" stroke-linecap="round" '
                   f'style="animation:{"flow" if dirn > 0 else "flowR"} {5 + oi * 2.2:.1f}s linear infinite"/></g>')

    # ---- the core: Bloch sphere + plasma nucleus ----------------------------------------
    R = 50
    tilt = 0.3
    out.append('<g class="fi" style="animation-delay:.1s;animation-duration:1.8s">')
    out.append(f'<circle cx="{f(CX)}" cy="{f(CY)}" r="{R}" fill="{rad(d, "sph", [(0, C["violet"], .2), (0.7, C["violet"], .07), (1, C["cyan"], .22)], cx=.4, cy=.36, r=.62)}" stroke="{C["ice"]}" stroke-opacity=".5" stroke-width="1.2"/>')
    out.append(f'<path d="M{f(CX - R)} {f(CY)}A{R} {R * tilt} 0 0 1 {f(CX + R)} {f(CY)}" stroke="{C["muted"]}" stroke-dasharray="2 4" opacity=".8"/>')
    out.append(f'<path d="M{f(CX - R)} {f(CY)}A{R} {R * tilt} 0 0 0 {f(CX + R)} {f(CY)}" stroke="{C["ice"]}" stroke-width="1.1" opacity=".7"/>')
    out.append(f'<line x1="{f(CX)}" y1="{f(CY - R - 8)}" x2="{f(CX)}" y2="{f(CY + R + 8)}" stroke="{C["muted"]}" stroke-dasharray="2 4" opacity=".7"/>')
    for ph in range(2):
        out.append(f'<ellipse cx="{f(CX)}" cy="{f(CY)}" rx="{R}" ry="{R}" stroke="{C["cyan"]}" stroke-width="1" opacity=".45">'
                   f'<animate attributeName="rx" values="{R};0;{R}" keyTimes="0;.5;1" dur="8s" begin="-{ph * 4}s" repeatCount="indefinite" calcMode="spline" keySplines=".37 0 .63 1;.37 0 .63 1"/></ellipse>')
    # fast energy ring hugging the sphere
    out.append(f'<g class="spinF"><circle cx="{f(CX)}" cy="{f(CY)}" r="{R + 9}" stroke="{C["cyan"]}" stroke-width="1.4" stroke-dasharray="22 8 3 8" opacity=".55"/></g>')
    # nucleus: soft bloom + hot centre (gradients only — cheap to animate)
    bloom = rad(d, "bloom", [(0, "#FFFFFF", .9), (0.18, C["ice"], .75), (0.45, C["cyan"], .3), (1, C["violet"], 0)])
    out.append(f'<circle class="core" cx="{f(CX)}" cy="{f(CY)}" r="40" fill="{bloom}"/>')
    out.append(f'<circle cx="{f(CX)}" cy="{f(CY)}" r="7" fill="#fff"/>')
    # precessing state vector
    theta = math.radians(48)
    pts = []
    for i in range(49):
        phi = 2 * math.pi * i / 48
        pts.append((CX + R * math.sin(theta) * math.cos(phi), CY - R * math.cos(theta) + R * math.sin(theta) * math.sin(phi) * tilt))
    xs = ";".join(f(p[0]) for p in pts)
    ys = ";".join(f(p[1]) for p in pts)
    out.append(f'<ellipse cx="{f(CX)}" cy="{f(CY - R * math.cos(theta))}" rx="{f(R * math.sin(theta))}" ry="{f(R * math.sin(theta) * tilt)}" stroke="{C["magenta"]}" stroke-dasharray="1 4" opacity=".7"/>')
    out.append(f'<line x1="{f(CX)}" y1="{f(CY)}" x2="{f(pts[0][0])}" y2="{f(pts[0][1])}" stroke="{sig}" stroke-width="2.4" stroke-linecap="round" filter="url(#glowS)">'
               f'<animate attributeName="x2" values="{xs}" dur="10s" repeatCount="indefinite"/><animate attributeName="y2" values="{ys}" dur="10s" repeatCount="indefinite"/></line>')
    out.append(f'<circle r="4.2" fill="{C["magenta"]}" cx="{f(pts[0][0])}" cy="{f(pts[0][1])}"><animate attributeName="cx" values="{xs}" dur="10s" repeatCount="indefinite"/>'
               f'<animate attributeName="cy" values="{ys}" dur="10s" repeatCount="indefinite"/></circle>')
    out.append(ket(d, "0", CX, CY - R - 14, 14, C["ice"], anchor="middle"))
    out.append(ket(d, "1", CX, CY + R + 25, 14, C["muted"], anchor="middle"))
    out.append("</g>")
    # anamorphic streak through the core
    out.append(f'<g class="fi" style="animation-delay:.6s"><g class="flareP" style="mix-blend-mode:screen">'
               f'<ellipse cx="{f(CX)}" cy="{f(CY)}" rx="112" ry="3.2" fill="{C["ice"]}" opacity=".45" filter="url(#flareBlur)"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(CY)}" rx="128" ry=".9" fill="#fff" opacity=".55"/>'
               f'<ellipse cx="{f(CX)}" cy="{f(CY)}" rx="1.2" ry="58" fill="#fff" opacity=".35"/></g></g>')

    # ---- orbits: front halves -----------------------------------------------------------------
    for oi, (rx, ry, tilt_, T, dirn, doms) in enumerate(ORBITS):
        front = half_path(rx, ry, tilt_, CX, CY, front=True)
        cols = [ACCENT[ARSENAL[k][1]][0] for k in doms]
        grad = lin(d, f"og{oi}", [(0, cols[0]), (1, cols[1])])
        dl = f"animation-delay:{.35 + oi * .18:.2f}s"
        out.append(f'<path d="{front}" pathLength="1" class="draw" style="{dl}" stroke="{grad}" stroke-width="4" opacity=".35" filter="url(#flareBlur)"/>'
                   f'<path d="{front}" pathLength="1" class="draw" style="{dl}" stroke="{grad}" stroke-width="1.5" opacity=".9"/>')

    # ---- nodes with comet trails, depth and upright outward labels -----------------------
    for oi, (rx, ry, tilt_, T, dirn, doms) in enumerate(ORBITS):
        full = ellipse_path(rx, ry, tilt_, CX, CY)
        samples = ellipse_samples(rx, ry, math.radians(tilt_), CX, CY, K)
        kt = ";".join(f"{k / K:.4f}" for k in range(K + 1))
        for slot, di in enumerate(doms):
            col, col2 = ACCENT[ARSENAL[di][1]]
            begin = -(T * slot / 2) - T * 0.13 * oi      # opposite phases, orbits staggered
            bs = f"{begin:.2f}s"
            fade_in = f'class="fi" style="animation-delay:{1.0 + oi * .15:.2f}s"'
            # comet trail: dashes that end exactly at the node (pathLength = 1)
            for L, sw, op in ((0.085, 1.5, .22), (0.045, 2.2, .45), (0.02, 2.8, .85)):
                out.append(f'<path d="{full}" pathLength="1" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" '
                           f'stroke-dasharray="{L} {1 - L:.3f}" stroke-dashoffset="{L}" opacity="{op}" {fade_in}>'
                           f'<animate attributeName="stroke-dashoffset" values="{L};{L - 1:.3f}" dur="{T}s" begin="{bs}" repeatCount="indefinite"/></path>')
            # depth: opacity and scale follow sin(t)
            opv = ";".join(f"{.4 + .6 * (z + 1) / 2:.2f}" for _, _, z in samples)
            scv = ";".join(f"{.6 + .4 * (z + 1) / 2:.2f}" for _, _, z in samples)
            # label offset: always on the outward side, centred on the radial direction
            lab = SHORT[di]
            lw = d.width(lab, "mono-b", 13, 1.6)
            offs = []
            for x, y, _ in samples:
                ux, uy = x - CX, y - CY
                m = math.hypot(ux, uy) or 1
                ux, uy = ux / m, uy / m
                ox = ux * (15 + lw / 2) - lw / 2
                oy = uy * 17 + 4.6
                offs.append(f"{f(ox)} {f(oy)}")
                if x + ox < 40 or x + ox + lw > DIV_X - 8:
                    print(f"   ! label {lab} leaves the reactor zone at x={x + ox:.0f}")
            ng = rad(d, f"ng{di}", [(0, col, .6), (0.4, col, .22), (1, col, 0)])
            sx, sy, _ = samples[0]
            out.append(f'<g {fade_in}><g>'
                       f'<animateMotion path="{full}" dur="{T}s" begin="{bs}" repeatCount="indefinite"/>'
                       f'<animate attributeName="opacity" values="{opv}" keyTimes="{kt}" dur="{T}s" begin="{bs}" repeatCount="indefinite"/>'
                       f'<g><animateTransform attributeName="transform" type="scale" values="{scv}" keyTimes="{kt}" dur="{T}s" begin="{bs}" repeatCount="indefinite"/>'
                       f'<circle r="16" fill="{ng}"/>'
                       f'<circle r="8.5" stroke="{col}" stroke-width="1" opacity=".65"/>'
                       f'<circle r="4.8" fill="{col}"/><circle r="2" fill="#fff"/></g>'
                       # target-lock reticle
                       f'<g opacity="0">{anim_lock(di)}'
                       f'<circle r="15" stroke="{col}" stroke-width="1.4" stroke-dasharray="6 3.4"/>'
                       f'<path d="M-22 0H-16M16 0H22M0 -22V-16M0 16V22" stroke="{col}" stroke-width="1.6"/></g>'
                       f'<g><animateTransform attributeName="transform" type="translate" values="{";".join(offs)}" keyTimes="{kt}" dur="{T}s" begin="{bs}" repeatCount="indefinite"/>'
                       f'{d.text(lab, 0, 0, "mono-b", 13, col, tracking=1.6, attrs=HALO)}</g>'
                       f'</g></g>')
            # the lock beam: from the moving node to its row anchor
            row = rows[di]
            ay = row["y"] + ROW_PAD + 13
            def beam_d(x, y):
                c1 = x + (DIV_X - x) * 0.55
                return f"M{f(x)} {f(y)}C{f(c1)} {f(y)} {f(DIV_X - 70)} {f(ay)} {DIV_X} {f(ay)}"
            dv = ";".join(beam_d(x, y) for x, y, _ in samples)
            mv = f'<animate attributeName="d" values="{dv}" keyTimes="{kt}" dur="{T}s" begin="{bs}" repeatCount="indefinite"/>'
            d0 = beam_d(sx, sy)
            out.append(f'<g opacity="0">{anim_lock(di)}'
                       f'<path d="{d0}" stroke="{col}" stroke-width="5" opacity=".12" stroke-linecap="round">{mv}</path>'
                       f'<path class="beam" d="{d0}" stroke="{col}" stroke-width="1.4" opacity=".95">{mv}</path>'
                       f'<path d="M{DIV_X - 5} {f(ay)}l5 -5l5 5l-5 5z" fill="{col}"/></g>')

    # ---- HUD readouts --------------------------------------------------------------------
    x0, y0 = 44, BAR + 34
    out.append('<g class="sr" style="animation-delay:.6s">')
    out.append(d.text("REACTOR", x0, y0, "mono-b", 13, C["cyan"], tracking=2.6))
    out.append(d.text("// ARSENAL CORE", x0 + d.width("REACTOR", "mono-b", 13, 2.6) + 10, y0, "mono", 13, C["muted"], tracking=2.6))
    out.append(d.text("4 ORBITS · 8 NODES", x0, y0 + 21, "mono", 13, C["muted"], tracking=2.6))
    out.append("</g>")
    xr = DIV_X - 26
    out.append('<g class="sl" style="animation-delay:.7s">')
    out.append(d.text("CORE STATE", xr, y0, "mono", 13, C["muted"], "end", 2.6))
    out.append(d.text("SUPERPOSED", xr, y0 + 21, "mono-b", 13, C["magenta"], "end", 2.6))
    out.append("</g>")

    # ---- loadout spectrum (bottom of reactor zone): tools per domain, true to scale --------
    sx0, sx1 = 44, DIV_X - 26
    sy = H - BAR - 30
    total = sum(len(t) for _, _, t in ARSENAL)
    gap = 3
    avail = sx1 - sx0 - gap * (len(ARSENAL) - 1)
    out.append('<g class="fi" style="animation-delay:1.6s">')
    out.append(d.text("LOADOUT SPECTRUM", sx0, sy - 14, "mono", 13, C["muted"], tracking=2.6))
    out.append(d.text(f"{total} TOOLS", sx1, sy - 14, "mono-b", 13, C["text"], "end", 2.6))
    out.append("</g>")
    xx = sx0
    for i, (dom, cat, tools) in enumerate(ARSENAL):
        wseg = avail * len(tools) / total
        col = ACCENT[cat][0]
        out.append(f'<rect x="{f(xx)}" y="{f(sy)}" width="{f(wseg)}" height="6" rx="1.5" fill="{col}" opacity=".85" class="wipe" style="animation-delay:{1.7 + i * .09:.2f}s"/>')
        xx += wseg + gap
    d.defs.append(f'<clipPath id="specClip"><rect x="{sx0}" y="{f(sy)}" width="{f(sx1 - sx0)}" height="6"/></clipPath>')
    out.append(f'<g clip-path="url(#specClip)"><rect class="glint" x="0" y="{f(sy)}" width="90" height="6" fill="{lin(d, "glG", [(0, "#fff", 0), (.5, "#fff", .9), (1, "#fff", 0)])}"/></g>')


# ================================================================ LOADOUT ===

def loadout(d, out, rows, chip_x0, label_x):
    for r in rows:
        i, dom, cat, tools = r["i"], r["dom"], r["cat"], r["tools"]
        col, col2 = ACCENT[cat]
        y, h = r["y"], r["h"]
        base = 0.45 + i * 0.2
        # active-row highlight (lock cycle)
        hg = lin(d, f"hl{i}", [(0, col, .16), (0.45, col, .05), (1, col, 0)])
        out.append(f'<g opacity="0">{anim_lock(i)}'
                   f'<rect x="{DIV_X + 1}" y="{f(y + 3)}" width="{f(W - DIV_X - 26)}" height="{f(h - 6)}" fill="{hg}"/>'
                   f'<rect x="{DIV_X + 1}" y="{f(y + 3)}" width="3" height="{f(h - 6)}" fill="{col}" filter="url(#glowS)"/>'
                   f'{corners(RIGHT - 6, y + 6, 12, h - 12, 7, col, 1.3, .9)}</g>')
        # row slot marker (always on)
        out.append(f'<rect x="{DIV_X + 1}" y="{f(y + ROW_PAD + 2)}" width="2" height="22" fill="{col}" opacity=".7" class="fi" style="animation-delay:{base:.2f}s"/>')
        # glyph tile + label + count
        ly = y + ROW_PAD + 17
        out.append(f'<g class="sr" style="animation-delay:{base:.2f}s">'
                   f'<rect x="{RX0}" y="{f(y + ROW_PAD)}" width="26" height="26" rx="6" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-opacity=".45"/>'
                   f'{glyph(GLYPHS[i], RX0 + 3, y + ROW_PAD + 3, col)}'
                   f'{d.text(dom, label_x, ly, LABEL_FONT, LABEL_SIZE, col, tracking=LABEL_TR)}'
                   f'{d.text(f"{len(tools):02d} TOOLS", label_x, ly + 21, SUB_FONT, SUB_SIZE, C["muted"], tracking=SUB_TR)}'
                   f'</g>')
        # chips
        stroke = lin(d, f"cs{i}", [(0, col, .75), (1, col2, .55)], extra=' gradientUnits="objectBoundingBox"')
        clip = []
        for j, (t, cx, line, w) in enumerate(r["chips"]):
            cy = y + ROW_PAD + line * CHIP_PITCH
            dl = base + 0.12 + j * 0.045
            clip.append(f'<rect x="{f(cx)}" y="{f(cy)}" width="{f(w)}" height="{CHIP_H}" rx="{CHIP_H / 2}"/>')
            out.append(f'<g class="r chip" style="animation-delay:{dl:.2f}s">'
                       f'<rect x="{f(cx + .5)}" y="{f(cy + .5)}" width="{f(w - 1)}" height="{CHIP_H - 1}" rx="{(CHIP_H - 1) / 2}" fill="{col}" fill-opacity=".07" stroke="{stroke}"/>'
                       f'{d.text(t, cx + w / 2, cy + 19.5, CHIP_FONT, CHIP_SIZE, C["text"], "middle")}</g>')
        # glint across this row's chips while it is locked
        cid = f"rc{i}"
        d.defs.append(f'<clipPath id="{cid}">{"".join(clip)}</clipPath>')
        a = (i * CYCLE_SLOT + .35) / CYCLE
        b = (i * CYCLE_SLOT + 1.75) / CYCLE
        x_from, x_to = chip_x0 - 160, RIGHT + 40
        kts = "0" + (f";{a:.4f}" if a > 0 else "") + f";{b:.4f};1"
        vals = f"{x_from} 0" + (f";{x_from} 0" if a > 0 else "") + f";{x_to} 0;{x_to} 0"
        out.append(f'<g clip-path="url(#{cid})"><rect x="0" y="{f(y)}" width="120" height="{f(h)}" '
                   f'fill="{lin(d, f"gl{i}", [(0, "#fff", 0), (.5, "#fff", .32), (1, "#fff", 0)])}" transform="translate({x_from} 0)">'
                   f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{kts}" dur="{CYCLE:g}s" begin="{CYCLE_BEGIN}s" repeatCount="indefinite"/></rect></g>')
        # hairline separator
        if i < len(rows) - 1:
            out.append(f'<line x1="{RX0}" y1="{f(y + h)}" x2="{RIGHT}" y2="{f(y + h)}" stroke="{C["line"]}" stroke-width="1" pathLength="1" class="draw" style="animation-delay:{base + .1:.2f}s"/>')


if __name__ == "__main__":
    build().save("arsenal.svg")
