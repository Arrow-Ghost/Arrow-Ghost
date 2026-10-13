"""Scene 03: FEATURED OPERATIONS.

Six cinematic scene cards, one per flagship project, built to be stacked full
width in the README. Every card shares one frame (letterboxed slate bars, HUD
corners, nebula in the category accent, a stroke-drawn title) so the six read
as a series, and each one carries its own animated vector illustration:

  OP-01 Vidi           camera HUD over a line-art corridor, tracked people, depth bar, spoken caption
  OP-02 ShadowADJ      radial FFT sphere, live meters, scrolling speech waveform
  OP-03 Quantum Maze   perspective neon maze whose doors are qubits, synced circuit + register
  OP-04 PhishGuard.js  radar + shield, DOM script being stripped, scrolling block/allow log
  OP-05 Event Horizon  shadow, photon ring, Doppler-beamed accretion disk, lensed starfield
  OP-06 Not Only SQL   hash ring, 3 replica-set shards, replication pulses, failover loop

Run from scripts/:  python build_projects.py
"""

import math
import random

from agfx import ACCENT, C, Doc, Font, blur, corners, f, glow, lin, panel, rad, stars, wrap
from content import FEATURED

W, H = 1280, 520
AW, AH = 560, 404              # art panel
AY = 56                        # art panel top
M, GAP = 44, 48                # outer margin, gap art <-> text
TW = W - 2 * M - AW - GAP      # text column width (584)

# Copy tuned to the card layout (shortened from content.py, same facts).
COPY = {
    "vidi": {
        "tag": "AI · ML — ASSISTIVE VISION",
        "desc": "A voice-first AI companion for blind and low-vision users. YOLOv8, Depth Anything V2, "
                "OCR and face recognition run on OpenVINO, and a Gemini Live agent speaks only what "
                "perception actually saw.",
    },
    "shadowadj": {
        "tag": "AI · ML — SPEECH INTELLIGENCE",
        "desc": "A consent-first AI speech coach and debate judge. 16 kHz browser audio streams to a "
                "Node backend that measures pace, pauses and fillers live; a rubric judge scores with "
                "timestamped evidence.",
    },
    "quantum-maze": {
        "tag": "QUANTUM — PUZZLE GAME",
        "desc": "A puzzle maze where every door is a qubit. Apply H, X, Y, Z, S, T and CNOT gates, then "
                "measure to open a path, computed by FastAPI + Qiskit Aer with an offline TypeScript "
                "statevector fallback.",
    },
    "phishguard": {
        "tag": "SECURITY — ZERO-TRUST RUNTIME",
        "desc": "A zero-trust runtime shield for the browser. JS Proxies around fetch and localStorage "
                "block token exfiltration, a MutationObserver strips injected scripts, and telemetry "
                "streams to a live SOC dashboard.",
    },
    "event-horizon": {
        "tag": "PHYSICS — WEBGL2 · GLSL",
        "desc": "A cinematic scroll story around a real-time black hole. A WebGL2 shader traces every "
                "pixel's photon path through Schwarzschild spacetime, so the shadow, photon ring and "
                "lensed disk come from the physics.",
    },
    "nosql": {
        "tag": "DATA SYSTEMS — WEBGL SEMINAR",
        "desc": "A scroll-driven WebGL seminar on NoSQL: a 22k-particle GPU field morphs through 20 "
                "chapters beside a 3D sharded cluster with hash routing, replication and failover, plus "
                "a server-scored live quiz.",
    },
}


# ============================================================== helpers ===

def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def ramp(stops, t):
    """Piecewise colour ramp; stops = [(pos, '#hex'), ...]."""
    t = max(0.0, min(1.0, t))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            return mix(c0, c1, (t - p0) / (p1 - p0) if p1 > p0 else 0)
    return stops[-1][1]


def ket(d, label, x, y, size, fill, font="mono-b", anchor="start"):
    """|label⟩ with a drawn closing angle (the font has no ⟩)."""
    fo = Font.get(font)
    w0 = fo.width("|" + label, size)
    if anchor == "middle":
        x -= (w0 + size * 0.36) / 2
    t = d.text("|" + label, x, y, font, size, fill)
    ax, top, bot = x + w0 + size * 0.08, y - size * 0.74, y + size * 0.16
    mid = (top + bot) / 2
    return t + (f'<path d="M{f(ax)} {f(top)}L{f(ax + size * 0.28)} {f(mid)}L{f(ax)} {f(bot)}" stroke="{fill}" '
                f'stroke-width="{f(size * 0.08)}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def xmark(x, y, s, col, sw=1.8):
    return (f'<path d="M{f(x - s)} {f(y - s)}L{f(x + s)} {f(y + s)}M{f(x + s)} {f(y - s)}L{f(x - s)} {f(y + s)}" '
            f'stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>')


def tick(x, y, s, col, sw=1.8):
    return (f'<path d="M{f(x - s)} {f(y)}L{f(x - s * .25)} {f(y + s * .75)}L{f(x + s)} {f(y - s * .8)}" stroke="{col}" '
            f'stroke-width="{sw}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def vis(intervals, T):
    """Discrete visibility over a loop of T seconds. Returns (initial opacity, <animate>)."""
    on0 = 1 if any(a <= 0 < b for a, b in intervals) else 0
    pts = sorted([(a, 1) for a, b in intervals if a > 0] + [(b, 0) for a, b in intervals if b < T])
    keys = [(0.0, on0)] + [(t / T, v) for t, v in pts]
    vals = ";".join(str(v) for _, v in keys)
    kts = ";".join(f"{k:.4f}" for k, _ in keys)
    return on0, (f'<animate attributeName="opacity" values="{vals}" keyTimes="{kts}" dur="{T}s" '
                 f'calcMode="discrete" repeatCount="indefinite"/>')


def vis_g(inner, intervals, T):
    o, a = vis(intervals, T)
    return f'<g opacity="{o}">{a}{inner}</g>'


def anim(attr, keys, T, extra=""):
    """Linear SMIL animate from [(t_seconds, value), ...] (first t must be 0, last T)."""
    vals = ";".join(str(v) for _, v in keys)
    kts = ";".join(f"{t / T:.4f}" for t, _ in keys)
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{kts}" dur="{T}s" repeatCount="indefinite"{extra}/>'


def poly(pts):
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)


def cyc_text(d, values, x, y, font, size, fill, dur, anchor="start", tracking=0.0):
    """Cycle through strings (discrete), each shown for dur/len seconds."""
    n, out = len(values), []
    for k, v in enumerate(values):
        o, a = vis([(k * dur / n, (k + 1) * dur / n)], dur)
        out.append(f'<g opacity="{o}">{a}{d.text(v, x, y, font, size, fill, anchor, tracking)}</g>')
    return "".join(out)


# ============================================================ art frame ===

def art_frame(d, ax, a1, inner, tl, tr):
    cid = d.uid("ac")
    d.defs.append(f'<clipPath id="{cid}"><rect width="{AW}" height="{AH}" rx="14"/></clipPath>')
    bg = lin(d, d.uid("abg"), [(0, "#080B19"), (1, "#03040A")], 0, 0, 0, 1)
    vg = rad(d, d.uid("avg"), [(0, "#000", 0), (0.62, "#000", 0), (1, "#000", 0.6)], r=0.78)
    top = lin(d, d.uid("atp"), [(0, "#000", .75), (1, "#000", 0)], 0, 0, 0, 1)
    scan = lin(d, d.uid("asc"), [(0, a1, 0), (.82, a1, .055), (1, a1, 0)], 0, 0, 0, 1)
    o = [f'<g transform="translate({ax} {AY})"><g class="fi" style="animation-delay:.1s;animation-duration:1.6s">',
         f'<g clip-path="url(#{cid})"><rect width="{AW}" height="{AH}" fill="{bg}"/>', inner,
         f'<rect class="ascan" width="{AW}" height="96" fill="{scan}"/>',
         f'<rect width="{AW}" height="{AH}" fill="{vg}"/>',
         f'<rect width="{AW}" height="52" fill="{top}"/></g>',
         f'<rect x=".5" y=".5" width="{AW - 1}" height="{AH - 1}" rx="14" stroke="{C["line2"]}" fill="none"/>',
         corners(10, 10, AW - 20, AH - 20, 16, a1, 1.4, .85),
         d.text(tl, 28, 33, "mono-b", 13, a1, tracking=2.6),
         d.text(tr, AW - 28, 33, "mono", 13, C["muted"], "end", 2.2),
         "</g></g>"]
    return "".join(o)


# =========================================================== OP-01 VIDI ===

def art_vidi(d, a1, a2):
    o = []
    VPX, VPY, K = 292, 152, 170.0
    WX, FY, CYL, ZF = 2.2, 1.5, -1.55, 3.4

    def P(X, Y, Z):
        return VPX + X * K / Z, VPY + Y * K / Z

    def fog(Z):
        return max(.14, min(1.0, 1.1 * math.exp(-.62 * (Z - .8))))

    def ln(p, q, op, col=C["ice"], sw=1.0):
        return (f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" stroke="{col}" '
                f'stroke-width="{sw}" stroke-opacity="{op:.2f}"/>')

    blur(d, "vBl", 7)
    blur(d, "vBl2", 2.5)
    blur(d, "vBl3", 18)
    # ---- room volumes --------------------------------------------------------
    floor = lin(d, "vFl", [(0, "#122040"), (1, "#04060C")], 0, 0, 0, 1)
    ceil = lin(d, "vCe", [(0, "#04060C"), (1, "#0E1830")], 0, 0, 0, 1)
    wallL = lin(d, "vWl", [(0, "#05070E"), (1, "#0D1630")])
    wallR = lin(d, "vWr", [(0, "#0D1630"), (1, "#05070E")])
    o.append(f'<path d="{poly([P(-WX, FY, .55), P(WX, FY, .55), P(WX, FY, ZF), P(-WX, FY, ZF)])}Z" fill="{floor}"/>')
    o.append(f'<path d="{poly([P(-WX, CYL, .55), P(WX, CYL, .55), P(WX, CYL, ZF), P(-WX, CYL, ZF)])}Z" fill="{ceil}"/>')
    o.append(f'<path d="{poly([P(-WX, CYL, .55), P(-WX, CYL, ZF), P(-WX, FY, ZF), P(-WX, FY, .55)])}Z" fill="{wallL}"/>')
    o.append(f'<path d="{poly([P(WX, CYL, .55), P(WX, CYL, ZF), P(WX, FY, ZF), P(WX, FY, .55)])}Z" fill="{wallR}"/>')
    ew = lin(d, "vEw", [(0, "#101A36"), (1, "#16234A")], 0, 0, 0, 1)
    x0, y0 = P(-WX, CYL, ZF)
    x1, y1 = P(WX, FY, ZF)
    o.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="{ew}"/>')

    # ---- floor tiles, ceiling, seams ----------------------------------------------
    g = []
    for i in range(9):
        X = -WX + i * (2 * WX / 8)
        for za, zb in ((.6, 1.2), (1.2, 1.8), (1.8, 2.5), (2.5, ZF)):
            g.append(ln(P(X, FY, za), P(X, FY, zb), .5 * fog((za + zb) / 2)))
    for Z in (1.0, 1.22, 1.48, 1.8, 2.18, 2.62, 3.05):
        g.append(ln(P(-WX, FY, Z), P(WX, FY, Z), .5 * fog(Z)))
        g.append(ln(P(-WX, CYL, Z), P(WX, CYL, Z), .3 * fog(Z)))
    for s in (-1, 1):
        for za, zb in ((.6, 1.4), (1.4, 2.4), (2.4, ZF)):
            g.append(ln(P(s * WX, FY, za), P(s * WX, FY, zb), .9 * fog((za + zb) / 2), sw=1.3))
            g.append(ln(P(s * WX, CYL, za), P(s * WX, CYL, zb), .7 * fog((za + zb) / 2), sw=1.2))
        for Z in (1.15, 1.7, 2.45):
            g.append(ln(P(s * WX, FY, Z), P(s * WX, CYL, Z), .55 * fog(Z)))
    # end wall outline
    g.append(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" stroke="{C["ice"]}" stroke-opacity=".35" fill="none"/>')
    # left wall: glass panel  /  right wall: side door
    wpts = [P(-WX, -.75, 1.78), P(-WX, -.75, 2.3), P(-WX, .45, 2.3), P(-WX, .45, 1.78)]
    g.append(f'<path d="{poly(wpts)}Z" fill="{C["cyan"]}" fill-opacity=".06" stroke="{C["ice"]}" stroke-opacity=".42"/>')
    for t in (.33, .66):
        za = 1.78 + t * (2.3 - 1.78)
        g.append(ln(P(-WX, -.75, za), P(-WX, .45, za), .3))
    sd = [P(WX, -.62, 1.9), P(WX, -.62, 2.42), P(WX, FY, 2.42), P(WX, FY, 1.9)]
    g.append(f'<path d="{poly(sd)}Z" fill="#000" fill-opacity=".25" stroke="{C["ice"]}" stroke-opacity=".38"/>')
    hx, hy = P(WX, .45, 2.33)
    g.append(f'<circle cx="{f(hx)}" cy="{f(hy)}" r="2" fill="{C["ice"]}" opacity=".5"/>')
    o.append("".join(g))

    # ceiling light panels
    for za, zb in ((1.22, 1.46), (1.86, 2.05), (2.55, 2.7)):
        q = [P(-.5, CYL, za), P(.5, CYL, za), P(.5, CYL, zb), P(-.5, CYL, zb)]
        o.append(f'<path d="{poly(q)}Z" fill="{C["ice"]}" opacity="{.75 * fog(za):.2f}" filter="url(#vBl2)"/>')
        o.append(f'<path d="{poly(q)}Z" fill="#fff" opacity="{.55 * fog(za):.2f}"/>')

    # ---- lit doorway (slightly left of centre) -------------------------------------
    dl, dr, dt = -.85, -.05, -.62
    dx0, dy0 = P(dl, dt, ZF)
    dx1, dy1 = P(dr, FY, ZF)
    spill = lin(d, "vSp", [(0, C["ice"], .32), (1, C["ice"], 0)], 0, 0, 0, 1)
    o.append(f'<path d="{poly([P(dl, FY, ZF), P(dr, FY, ZF), P(.55, FY, 1.35), P(-1.75, FY, 1.35)])}Z" fill="{spill}"/>')
    o.append(f'<ellipse cx="{f((dx0 + dx1) / 2)}" cy="{f((dy0 + dy1) / 2)}" rx="70" ry="86" fill="{C["ice"]}" opacity=".22" filter="url(#vBl3)"/>')
    door = lin(d, "vDo", [(0, "#FFFFFF", .95), (1, C["ice"], .55)], 0, 0, 0, 1)
    o.append(f'<rect x="{f(dx0)}" y="{f(dy0)}" width="{f(dx1 - dx0)}" height="{f(dy1 - dy0)}" fill="{C["ice"]}" opacity=".9" filter="url(#vBl)"/>')
    o.append(f'<rect x="{f(dx0)}" y="{f(dy0)}" width="{f(dx1 - dx0)}" height="{f(dy1 - dy0)}" fill="{door}"/>')
    o.append(f'<rect x="{f(dx0 - 3)}" y="{f(dy0 - 3)}" width="{f(dx1 - dx0 + 6)}" height="{f(dy1 - dy0 + 3)}" stroke="{C["ice"]}" stroke-opacity=".7" fill="none"/>')
    ex0, ey0 = P(-.68, -.98, ZF)
    ex1, ey1 = P(-.22, -.78, ZF)
    o.append(f'<rect x="{f(ex0)}" y="{f(ey0)}" width="{f(ex1 - ex0)}" height="{f(ey1 - ey0)}" fill="{C["lime"]}" filter="url(#vBl2)"/>'
             f'<rect x="{f(ex0)}" y="{f(ey0)}" width="{f(ex1 - ex0)}" height="{f(ey1 - ey0)}" fill="{C["lime"]}" opacity=".9"/>')

    # depth fog
    fogg = rad(d, "vFog", [(0, C["ice"], .16), (.45, C["cyan"], .05), (1, C["cyan"], 0)], cx=.5, cy=.5, r=.5)
    o.append(f'<ellipse cx="{VPX - 10}" cy="{VPY + 8}" rx="260" ry="150" fill="{fogg}"/>')

    # ---- guidance path to the door ------------------------------------------------
    gx, gy = (dx0 + dx1) / 2, dy1 + 2
    o.append(f'<ellipse cx="{f(gx)}" cy="{f(gy + 2)}" rx="26" ry="5" stroke="{a1}" stroke-width="1.4" fill="none">'
             f'<animate attributeName="rx" values="10;30" dur="2.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="ry" values="2;6" dur="2.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;0" dur="2.4s" repeatCount="indefinite"/></ellipse>')
    gp = f"M286 338C290 300 {f(gx - 14)} 262 {f(gx)} {f(gy + 2)}"
    o.append(f'<path d="{gp}" stroke="{a1}" stroke-width="7" opacity=".18" fill="none" filter="url(#vBl2)"/>')
    o.append(f'<path d="{gp}" stroke="{a1}" stroke-width="2.4" stroke-dasharray="2 9" stroke-linecap="round" fill="none">'
             f'<animate attributeName="stroke-dashoffset" values="0;-22" dur="1s" repeatCount="indefinite"/></path>')

    # ---- people (silhouettes with rim light) + tracking boxes -----------------------------
    d.css.append("""
@keyframes vLegA{from{transform:rotate(11deg)}to{transform:rotate(-11deg)}}
@keyframes vLegB{from{transform:rotate(-11deg)}to{transform:rotate(11deg)}}
.vlA,.vlB{transform-box:fill-box;transform-origin:50% 0}
.vlA{animation:vLegA .62s ease-in-out infinite alternate}
.vlB{animation:vLegB .62s ease-in-out infinite alternate}
@keyframes vBar{0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}}
.vbar{transform-box:fill-box;transform-origin:50% 50%;animation:vBar 1s ease-in-out infinite}
@keyframes vBrk{0%,100%{opacity:.55}50%{opacity:1}}
.vbrk{animation:vBrk 2.2s ease-in-out infinite}
""")

    def body(hp, col, legs=True):
        sw_t, sw_a, sw_l = .19 * hp, .052 * hp, .07 * hp
        s = [f'<circle cy="{f(-.905 * hp)}" r="{f(.068 * hp)}" fill="{col}"/>',
             f'<line y1="{f(-.79 * hp)}" y2="{f(-.5 * hp)}" stroke="{col}" stroke-width="{f(sw_t)}" stroke-linecap="round"/>']
        for sx, c in ((-1, "vlB"), (1, "vlA")):
            s.append(f'<line class="{c}" x1="{f(sx * .1 * hp)}" y1="{f(-.76 * hp)}" x2="{f(sx * .118 * hp)}" y2="{f(-.48 * hp)}" '
                     f'stroke="{col}" stroke-width="{f(sw_a)}" stroke-linecap="round"/>')
        for sx, c in ((-1, "vlA"), (1, "vlB")):
            s.append(f'<line class="{c}" x1="{f(sx * .045 * hp)}" y1="{f(-.5 * hp)}" x2="{f(sx * .05 * hp)}" y2="{f(-.035 * hp)}" '
                     f'stroke="{col}" stroke-width="{f(sw_l)}" stroke-linecap="round"/>')
        return "".join(s)

    def walker(Z, X0, X1, dur, begin, label):
        hp = 1.75 * K / Z
        fx0, fy = P(X0, FY, Z)
        fx1, _ = P(X1, FY, Z)
        bw = .44 * hp
        mover = (f'<g><animateTransform attributeName="transform" type="translate" values="{f(fx0)} {f(fy)};{f(fx1)} {f(fy)}" '
                 f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>')
        s = [mover,
             f'<ellipse cy="2" rx="{f(.2 * hp)}" ry="{f(.03 * hp)}" fill="#000" opacity=".55"/>',
             f'<g transform="translate(-1.8 -.8)" opacity=".85" filter="url(#vBl2)">{body(hp, C["ice"])}</g>',
             f'<g transform="translate(-1.2 0)">{body(hp, C["ice"])}</g>',
             body(hp, "#070B16"),
             f'<g class="vbrk">{corners(-bw / 2, -hp - 6, bw, hp + 10, 9, C["lime"], 1.6, 1)}</g>',
             f'<rect x="{f(-bw / 2)}" y="{f(-hp - 6)}" width="{f(bw)}" height="{f(hp + 10)}" stroke="{C["lime"]}" stroke-opacity=".28" fill="none"/>']
        s.append("</g>")
        # the label rides the same motion but is drawn in a later pass, above every body
        lw = d.width(label, "mono-b", 13.5, .4) + 16
        lab = (mover + f'<rect x="{f(-bw / 2)}" y="10" width="{f(lw)}" height="21" rx="3" fill="#02040A" fill-opacity=".85" stroke="{C["lime"]}" stroke-opacity=".6"/>'
               + d.text(label, -bw / 2 + 8, 25, "mono-b", 13.5, C["lime"], tracking=.4) + "</g>")
        return "".join(s), lab

    far_body, far_label = walker(2.95, 1.75, -1.55, 17, -6, "person 0.88 · 2.9 m")
    o.append(far_body)
    # door detection box
    dlab = "door · 3.4 m"
    lw = d.width(dlab, "mono-b", 13.5, .4) + 16
    o.append(f'<g class="vbrk">{corners(dx0 - 9, dy0 - 9, dx1 - dx0 + 18, dy1 - dy0 + 14, 9, a1, 1.6, 1)}</g>')
    o.append(f'<rect x="{f(dx0 - 9 + (dx1 - dx0 + 18) / 2 - lw / 2)}" y="{f(dy0 - 36)}" width="{f(lw)}" height="21" rx="3" fill="#02040A" fill-opacity=".85" stroke="{a1}" stroke-opacity=".7"/>')
    o.append(d.text(dlab, (dx0 + dx1) / 2, dy0 - 21, "mono-b", 13.5, a1, "middle", .4))
    near_body, near_label = walker(2.05, -1.95, 1.45, 13, -2, "person 0.94 · 2.1 m")
    o.extend([near_body, far_label, near_label])

    # ---- camera HUD ------------------------------------------------------------------
    hud = [f'<g stroke="{C["ice"]}" stroke-opacity=".55" stroke-width="1.2">'
           f'<path d="M262 196h10M288 196h10M280 178v10M280 204v10"/></g>']
    for k in range(27):
        y = 70 + k * 9.5
        L = 10 if k % 5 == 0 else 5
        hud.append(f'<line x1="22" y1="{f(y)}" x2="{22 + L}" y2="{f(y)}" stroke="{C["ice"]}" stroke-opacity=".35"/>')
    hud.append(f'<path d="M36 0l7 -5v10z" fill="{a1}"><animateTransform attributeName="transform" type="translate" '
               f'values="0 120;0 210;0 160;0 120" dur="9s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></path>')
    # depth colour bar (Depth Anything V2 style: near = hot, far = cool)
    dg = lin(d, "vDg", [(0, "#2A1458"), (.35, C["violet"]), (.65, C["magenta"]), (.85, C["amber"]), (1, "#FFF3C8")], 0, 0, 0, 1)
    bx, by0, by1 = AW - 30, 70, 300
    hud.append(f'<rect x="{bx}" y="{by0}" width="6" height="{by1 - by0}" rx="3" fill="{dg}" opacity=".9"/>')
    hud.append(d.text("5 m", bx - 8, by0 + 9, "mono", 13, C["muted"], "end"))
    hud.append(d.text("0 m", bx - 8, by1, "mono", 13, C["muted"], "end"))
    for dist, col in ((2.1, C["lime"]), (2.9, C["lime"]), (3.4, a1)):
        yy = by1 - (by1 - by0) * dist / 5
        hud.append(f'<path d="M{bx - 6} {f(yy)}h4M{bx + 8} {f(yy)}h4" stroke="{col}" stroke-width="2"/>')
    o.append("".join(hud))

    # ---- spoken caption -------------------------------------------------------------------
    cy0 = 346
    cap = ["<g>", f'<rect x="20" y="{cy0}" width="{AW - 40}" height="40" rx="20" fill="#03050B" fill-opacity=".86" stroke="{C["line2"]}"/>',
           d.text("VIDI", 40, cy0 + 25, "mono-b", 13, a1, tracking=2)]
    for k in range(12):
        hh = 6 + 14 * abs(math.sin(k * 1.7 + .4))
        cap.append(f'<rect class="vbar" x="{88 + k * 6}" y="{f(cy0 + 20 - hh / 2)}" width="3" height="{f(hh)}" rx="1.5" fill="{a1}" '
                   f'style="animation-delay:-{(k * .37) % 1:.2f}s;animation-duration:{.8 + (k % 4) * .17:.2f}s"/>')
    capt = "“door ahead, slightly left”"
    cw = d.width(capt, "sans-sb", 19.5) + 6
    d.defs.append(f'<clipPath id="vCap"><rect x="168" y="{cy0}" width="{f(cw)}" height="40">'
                  f'<animate attributeName="width" values="0;0;{f(cw)};{f(cw)}" keyTimes="0;.05;.25;1" dur="8s" repeatCount="indefinite"/></rect></clipPath>')
    cap.append(f'<g clip-path="url(#vCap)"><g>{anim("opacity", [(0, 1), (6.9, 1), (7.7, 0), (8, 0)], 8)}'
               f'{d.text(capt, 168, cy0 + 26.5, "sans-sb", 19.5, C["text"])}</g></g>')
    cap.append(d.text("GEMINI LIVE", AW - 40, cy0 + 25, "mono", 13, C["muted"], "end", 1.5))
    cap.append("</g>")
    o.append("".join(cap))
    return "".join(o)


# ====================================================== OP-02 SHADOWADJ ===

def blob(cx, cy, radii, rot=0.0):
    """Smooth closed blob through len(radii) points (Catmull-Rom -> cubic)."""
    n = len(radii)
    pts = [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n)) for i, r in enumerate(radii)]
    s = f"M{f(pts[0][0])} {f(pts[0][1])}"
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return s + "Z"


def art_shadow(d, a1, a2):
    o = []
    rnd = random.Random(2)
    cx, cy, r0 = 186, 180, 68
    glow(d, "sGl", 3.2, 2)
    blur(d, "sBl", 16)
    d.css.append("""
@keyframes sEqA{0%,100%{transform:scaleY(.3)}22%{transform:scaleY(1)}48%{transform:scaleY(.5)}74%{transform:scaleY(.88)}}
@keyframes sEqB{0%,100%{transform:scaleY(.55)}30%{transform:scaleY(.25)}60%{transform:scaleY(1)}85%{transform:scaleY(.4)}}
.seA,.seB{transform-box:fill-box;transform-origin:50% 100%}
.seA{animation:sEqA 1.7s ease-in-out infinite}
.seB{animation:sEqB 2.3s ease-in-out infinite}
@keyframes sPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.045)}}
.spl{transform-box:fill-box;transform-origin:50% 50%;animation:sPulse 2.6s ease-in-out infinite}
""")
    # backdrop glow
    o.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="{a1}" opacity=".16" filter="url(#sBl)"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="70" fill="{a2}" opacity=".10" filter="url(#sBl)"/>')
    # orbit ring
    o.append(f'<g><circle cx="{cx}" cy="{cy}" r="142" stroke="{C["line2"]}" stroke-dasharray="2 7" fill="none"/>'
             f'<circle cx="{cx + 142}" cy="{cy}" r="2.6" fill="{a2}"/><circle cx="{cx - 142}" cy="{cy}" r="1.8" fill="{a1}"/>'
             f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="40s" repeatCount="indefinite"/></g>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r0 - 6}" stroke="{a1}" stroke-opacity=".25" fill="none"/>')
    # FFT bars
    N = 84
    bars = []
    for k in range(N):
        th = 360 * k / N
        fi = min(k, N - k) / (N / 2)              # 0 top -> 1 bottom (mirrored spectrum)
        L = 10 + 46 * (0.62 * math.exp(-((fi - .2) / .17) ** 2) + 0.5 * math.exp(-((fi - .62) / .18) ** 2)) + rnd.uniform(0, 9)
        col = ramp([(0, C["ice"]), (.35, a1), (.75, a2), (1, a2)], fi)
        cls = "seA" if rnd.random() < .5 else "seB"
        bars.append(f'<g transform="rotate({f(th)} {cx} {cy})"><rect class="{cls}" x="{cx - 1.7}" y="{f(cy - r0 - L)}" width="3.4" height="{f(L)}" rx="1.7" '
                    f'fill="{col}" style="animation-delay:-{rnd.uniform(0, 2.3):.2f}s"/></g>')
    o.append(f'<g filter="url(#sGl)">{"".join(bars)}</g>')
    # core sphere
    core = rad(d, "sCore", [(0, mix(a1, "#FFFFFF", .3), .55), (.45, a1, .18), (1, "#050815", .95)], cx=.38, cy=.34, r=.7)
    sph = [f'<g class="spl"><circle cx="{cx}" cy="{cy}" r="56" fill="{core}" stroke="{a1}" stroke-opacity=".6" stroke-width="1.2"/>']
    for ph in range(3):
        sph.append(f'<ellipse cx="{cx}" cy="{cy}" rx="56" ry="56" stroke="{C["ice"]}" stroke-opacity=".28" fill="none">'
                   f'<animate attributeName="rx" values="56;0;56" dur="7s" begin="-{ph * 2.33:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".37 0 .63 1;.37 0 .63 1"/></ellipse>')
    for lat in (-.55, 0, .55):
        rr = 56 * math.sqrt(1 - lat * lat)
        sph.append(f'<ellipse cx="{cx}" cy="{f(cy - 56 * lat)}" rx="{f(rr)}" ry="{f(rr * .26)}" stroke="{C["ice"]}" stroke-opacity=".22" fill="none"/>')
    shapes = [blob(cx, cy, [30 + 8 * math.sin(i * 1.3 + s) + 5 * math.cos(i * 2.1 + s * 2) for i in range(8)], s * .4) for s in (0, 1.4, 2.9, 0)]
    shapes[-1] = shapes[0]
    sg = lin(d, "sBlob", [(0, a1), (1, a2)], 0, 0, 1, 1)
    sph.append(f'<path d="{shapes[0]}" fill="{sg}" fill-opacity=".28" stroke="{sg}" stroke-width="1.6" filter="url(#sGl)">'
               f'<animate attributeName="d" values="{";".join(shapes)}" dur="5s" repeatCount="indefinite" calcMode="spline" '
               f'keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></path>')
    sph.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#fff"/></g>')
    o.append("".join(sph))

    # ---- meters ------------------------------------------------------------------------
    mx, mw = 356, 182

    def card(y, label, unit):
        return (f'<rect x="{mx}" y="{y}" width="{mw}" height="80" rx="9" fill="#070A14" fill-opacity=".9" stroke="{C["line2"]}"/>'
                f'<rect x="{mx}" y="{y + 14}" width="2.5" height="22" fill="{a1}"/>'
                + d.text(label, mx + 16, y + 26, "mono-b", 13, C["soft"], tracking=2.2)
                + d.text(unit, mx + mw - 14, y + 26, "mono", 13, C["muted"], "end", 1.5))

    y1, y2, y3 = 50, 140, 230
    m = [card(y1, "PACE", "WPM"), cyc_text(d, ["142", "139", "142", "145", "142", "141"], mx + 16, y1 + 66, "sans-l", 38, C["text"], 7.2)]
    # target band 130-160 wpm
    bx0, bx1 = mx + 92, mx + mw - 16
    m.append(f'<rect x="{bx0}" y="{y1 + 56}" width="{bx1 - bx0}" height="4" rx="2" fill="{C["line2"]}"/>')
    m.append(f'<rect x="{f(bx0 + (bx1 - bx0) * .25)}" y="{y1 + 56}" width="{f((bx1 - bx0) * .5)}" height="4" rx="2" fill="{a2}" opacity=".55"/>')
    m.append(f'<circle cx="{f(bx0 + (bx1 - bx0) * .55)}" cy="{y1 + 58}" r="4.5" fill="{C["text"]}" stroke="{a1}" stroke-width="2">'
             f'<animate attributeName="cx" values="{f(bx0 + (bx1 - bx0) * .55)};{f(bx0 + (bx1 - bx0) * .48)};{f(bx0 + (bx1 - bx0) * .6)};{f(bx0 + (bx1 - bx0) * .55)}" dur="7.2s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1"/></circle>')
    m.append(d.text("130", bx0, y1 + 75, "mono", 13, C["dim"]))
    m.append(d.text("160", bx1, y1 + 75, "mono", 13, C["dim"], "end"))

    m.append(card(y2, "FILLERS", "um · uh"))
    m.append(d.text("3", mx + 16, y2 + 66, "sans-l", 38, C["amber"]))
    for k in range(3):
        m.append(f'<rect x="{mx + 50 + k * 9}" y="{y2 + 42}" width="3" height="24" rx="1.5" fill="{C["amber"]}" opacity=".8"/>')
    for k in range(3, 10):
        m.append(f'<rect x="{mx + 50 + k * 9}" y="{y2 + 42}" width="3" height="24" rx="1.5" fill="{C["line2"]}"/>')

    m.append(card(y3, "PAUSE", "LONGEST"))
    m.append(d.text("0.8s", mx + 16, y3 + 66, "sans-l", 38, C["text"]))
    pb0 = mx + 96
    for k in range(8):
        hgt = [8, 14, 4, 20, 9, 26, 12, 6][k]
        m.append(f'<rect x="{pb0 + k * 9}" y="{y3 + 66 - hgt}" width="5" height="{hgt}" rx="1" fill="{a1 if k != 5 else C["amber"]}" opacity="{.45 if k != 5 else .95}"/>')
    o.append("".join(m))

    # ---- scrolling waveform ------------------------------------------------------------------
    wy, amp, PER = 362, 21, 520
    rnd = random.Random(9)
    env = []
    x = 0
    marks = []
    while x < PER:
        if rnd.random() < .2 and x > 30 and x < PER - 80:
            gap = rnd.randint(46, 60)
            marks.append(("pause", x, gap))
            env += [0] * gap
            x += gap
            continue
        wl = rnd.randint(26, 64)
        if rnd.random() < .18:
            marks.append(("um", x, wl))
        pk = rnd.uniform(.55, 1)
        for j in range(wl):
            u = j / wl
            env.append(pk * math.sin(math.pi * u) ** .7 * (.6 + .4 * abs(math.sin(j * .55))))
        g = rnd.randint(5, 11)
        env += [0] * g
        x += wl + g
    env = env[:PER]
    while len(env) < PER:
        env.append(0)
    env[-8:] = [0] * 8
    env[:4] = [0] * 4
    step = 2
    top = [(i, wy - 1 - amp * env[i] * (.55 + .45 * abs(math.sin(i * 1.9)))) for i in range(0, PER + 1, step) if i < PER] + [(PER, wy - 1)]
    bot = [(i, wy + 1 + amp * env[i] * (.55 + .45 * abs(math.cos(i * 1.3)))) for i in range(0, PER, step)] + [(PER, wy + 1)]
    wpath = poly(top) + "L" + "L".join(f"{f(xx)} {f(yy)}" for xx, yy in reversed(bot)) + "Z"
    wg = lin(d, "sWv", [(0, a1), (.5, mix(a1, a2, .5)), (1, a2)], 0, 0, 1, 0)
    ann = []
    for kind, xx, ww in marks:
        if kind == "pause":
            ann.append(f'<path d="M{xx + 4} {wy - 8}v-6h{ww - 8}v6" stroke="{C["amber"]}" stroke-opacity=".8" fill="none"/>'
                       + d.text("0.8s", xx + ww / 2, wy - 18, "mono-b", 13, C["amber"], "middle"))
        else:
            ann.append(f'<rect x="{xx}" y="{wy + 25}" width="{ww}" height="3" rx="1.5" fill="{C["amber"]}" opacity=".75"/>')
    unit = f'<path d="{wpath}" fill="{wg}"/>{"".join(ann)}'
    d.defs.append(f'<linearGradient id="sMg" x1="20" x2="540" y1="0" y2="0" gradientUnits="userSpaceOnUse">'
                  f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".3" stop-color="#fff" stop-opacity="1"/>'
                  f'<stop offset=".86" stop-color="#fff" stop-opacity="1"/><stop offset=".87" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                  f'<mask id="sMask"><rect x="0" y="300" width="{AW}" height="104" fill="url(#sMg)"/></mask>')
    o.append(f'<line x1="20" y1="{wy}" x2="{AW - 20}" y2="{wy}" stroke="{C["line2"]}" stroke-dasharray="2 4"/>')
    o.append(f'<g mask="url(#sMask)"><g filter="url(#sGl)" opacity=".95"><g>{unit}<g transform="translate({PER} 0)">{unit}</g>'
             f'<g transform="translate({2 * PER} 0)">{unit}</g>'
             f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{PER} 0" dur="13s" repeatCount="indefinite"/></g></g></g>')
    phx = 20 + .865 * 520
    o.append(f'<line x1="{f(phx)}" y1="{wy - 32}" x2="{f(phx)}" y2="{wy + 30}" stroke="{C["text"]}" stroke-opacity=".8"/>'
             f'<circle cx="{f(phx)}" cy="{wy}" r="4" fill="{C["text"]}"><animate attributeName="r" values="3;5;3" dur="1.2s" repeatCount="indefinite"/></circle>')
    o.append(d.text("LIVE", phx + 10, wy - 20, "mono-b", 13, C["lime"], tracking=2))
    o.append(d.text("STREAM · VAD · SHA-256 ✓", 28, 318, "mono", 13, C["muted"], tracking=2))
    return "".join(o)


# =================================================== OP-03 QUANTUM MAZE ===

def art_maze(d, a1, a2):
    COLS, ROWS, ENT, EXT = 11, 6, 4, 1

    def gen(seed):
        rnd = random.Random(seed)
        Hw = [[True] * COLS for _ in range(ROWS + 1)]
        Vw = [[True] * (COLS + 1) for _ in range(ROWS)]

        def knock(c, r, nc, nr):
            if nc == c + 1:
                Vw[r][c + 1] = False
            elif nc == c - 1:
                Vw[r][c] = False
            elif nr == r + 1:
                Hw[r + 1][c] = False
            else:
                Hw[r][c] = False
        seen, stack = {(0, 0)}, [(0, 0)]
        while stack:
            c, r = stack[-1]
            nb = [(c + a, r + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))
                  if 0 <= c + a < COLS and 0 <= r + b < ROWS and (c + a, r + b) not in seen]
            if not nb:
                stack.pop()
                continue
            n = rnd.choice(nb)
            knock(c, r, *n)
            seen.add(n)
            stack.append(n)
        for _ in range(7):    # a few loops keep it airy
            c, r = rnd.randrange(1, COLS - 1), rnd.randrange(1, ROWS - 1)
            if rnd.random() < .5:
                Vw[r][c] = False
            else:
                Hw[r][c] = False
        Vw[ENT][0] = False
        Vw[EXT][COLS] = False
        return Hw, Vw

    def opened(Hw, Vw, c, r, nc, nr):
        if nc == c + 1:
            return not Vw[r][c + 1]
        if nc == c - 1:
            return not Vw[r][c]
        if nr == r + 1:
            return not Hw[r + 1][c]
        return not Hw[r][c]

    def bfs(Hw, Vw):
        start, goal = (0, ENT), (COLS - 1, EXT)
        prev, q = {start: None}, [start]
        while q:
            cur = q.pop(0)
            if cur == goal:
                break
            c, r = cur
            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (c + a, r + b)
                if 0 <= n[0] < COLS and 0 <= n[1] < ROWS and n not in prev and opened(Hw, Vw, c, r, *n):
                    prev[n] = cur
                    q.append(n)
        p, cur = [], goal
        while cur:
            p.append(cur)
            cur = prev[cur]
        return p[::-1]

    for seed in range(1, 500):
        Hw, Vw = gen(seed)
        path = bfs(Hw, Vw)
        turns = sum(1 for i in range(1, len(path) - 1)
                    if (path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]) != (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]))
        if 18 <= len(path) <= 22 and turns >= 7:
            break

    # ---- projection (perspective board, tilted toward the viewer) -------------------
    phi, Dd, hw = math.radians(50), 13.0, .48

    def p0(u, v, z):
        X, Y = u - COLS / 2, v - ROWS / 2
        depth = Dd - Y * math.sin(phi) - z * math.cos(phi)
        return X / depth, (Y * math.cos(phi) - z * math.sin(phi)) / depth, depth

    cs = [p0(u, v, z) for u in (0, COLS) for v in (0, ROWS) for z in (0, hw)]
    bx0, bx1 = min(c[0] for c in cs), max(c[0] for c in cs)
    by0, by1 = min(c[1] for c in cs), max(c[1] for c in cs)
    RX0, RX1, RY0, RY1 = 30, 530, 66, 290
    s = min((RX1 - RX0) / (bx1 - bx0), (RY1 - RY0) / (by1 - by0))
    ox = (RX0 + RX1) / 2 - s * (bx0 + bx1) / 2
    oy = (RY0 + RY1) / 2 - s * (by0 + by1) / 2

    def P(u, v, z=0.0):
        x, y, _ = p0(u, v, z)
        return ox + s * x, oy + s * y

    def depth(u, v, z=0.0):
        return p0(u, v, z)[2]

    glow(d, "mGl", 3, 2)
    blur(d, "mBl", 6)
    blur(d, "mBl2", 14)
    T = 12.0
    o = []
    # floor plate + grid
    plate = lin(d, "mPl", [(0, "#0A0726"), (1, "#120A30")], 0, 0, 0, 1)
    o.append(f'<path d="{poly([P(0, 0), P(COLS, 0), P(COLS, ROWS), P(0, ROWS)])}Z" fill="{plate}" stroke="{a1}" stroke-opacity=".5"/>')
    o.append(f'<ellipse cx="{f(P(COLS / 2, ROWS / 2)[0])}" cy="{f(P(COLS / 2, ROWS / 2)[1])}" rx="230" ry="80" fill="{a1}" opacity=".16" filter="url(#mBl2)"/>')
    gl = []
    for u in range(COLS + 1):
        gl.append(f'M{f(P(u, 0)[0])} {f(P(u, 0)[1])}L{f(P(u, ROWS)[0])} {f(P(u, ROWS)[1])}')
    for v in range(ROWS + 1):
        gl.append(f'M{f(P(0, v)[0])} {f(P(0, v)[1])}L{f(P(COLS, v)[0])} {f(P(COLS, v)[1])}')
    o.append(f'<path d="{"".join(gl)}" stroke="{a2}" stroke-opacity=".09"/>')
    for i in range(COLS):        # cell dots
        for j in range(ROWS):
            x, y = P(i + .5, j + .5)
            o.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="1" fill="{a2}" opacity=".3"/>')

    # ---- light path + schedule --------------------------------------------------------------
    pts3 = [(-.7, ENT + .5)]
    door_steps = [round(len(path) * k) for k in (.24, .5, .76)]
    door_info = []
    for i, (c, r) in enumerate(path):
        pts3.append((c + .5, r + .5))
        if i in door_steps and i + 1 < len(path):
            nc, nr = path[i + 1]
            bu, bv = (c + nc) / 2 + .5, (r + nr) / 2 + .5
            pts3.append((bu, bv))
            if nc != c:
                seg = ((max(c, nc), r), (max(c, nc), r + 1))
            else:
                seg = ((c, max(r, nr)), (c + 1, max(r, nr)))
            door_info.append({"idx": len(pts3) - 1, "seg": seg, "b": (bu, bv)})
    pts3.append((COLS + .7, EXT + .5))
    sp = [P(u, v, .02) for u, v in pts3]
    cum = [0.0]
    for a, b in zip(sp, sp[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    Ltot = cum[-1]
    for di in door_info:
        di["frac"] = cum[di["idx"]] / Ltot
    # schedule: progress p(t)
    pauses = [1.0, 1.6, 1.2]
    v = 1 / 6.4
    keys, t, fp = [(0.0, 0.0), (.5, 0.0)], .5, 0.0
    for di, pz in zip(door_info, pauses):
        t += (di["frac"] - fp) / v
        di["arr"] = t
        keys.append((t, di["frac"]))
        t += pz
        di["go"] = t
        keys.append((t, di["frac"]))
        fp = di["frac"]
    t += (1 - fp) / v
    t_end = t
    keys.append((t_end, 1.0))
    keys.append((T, 1.0))
    door_info[0]["flip"] = door_info[0]["arr"] + .35
    door_info[1]["plus"] = door_info[1]["arr"] + .25
    door_info[1]["flip"] = door_info[1]["arr"] + 1.05
    door_info[2]["flip"] = door_info[2]["arr"] + .55
    kv = ";".join(f"{1 - p:.4f}" for _, p in keys)
    kt = ";".join(f"{tt / T:.4f}" for tt, _ in keys)
    kp = ";".join(f"{p:.4f}" for _, p in keys)
    pd = poly(sp)
    fade = anim("opacity", [(0, 1), (11.25, 1), (11.8, 0), (T, 0)], T)
    o.append(f'<g>{fade}<path d="{pd}" pathLength="1" stroke="{a2}" stroke-width="12" stroke-opacity=".35" stroke-linecap="round" stroke-linejoin="round" '
             f'stroke-dasharray="1" fill="none" filter="url(#mBl)"><animate attributeName="stroke-dashoffset" values="{kv}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></path>'
             f'<path d="{pd}" pathLength="1" stroke="#E6FDFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1" fill="none">'
             f'<animate attributeName="stroke-dashoffset" values="{kv}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></path></g>')

    # ---- walls + doors, painter's order ---------------------------------------------------
    door_segs = {di["seg"] for di in door_info}
    segs = []
    for r in range(ROWS + 1):
        for c in range(COLS):
            if Hw[r][c]:
                segs.append(((c, r), (c + 1, r)))
    for r in range(ROWS):
        for c in range(COLS + 1):
            if Vw[r][c]:
                segs.append(((c, r), (c, r + 1)))
    face = lin(d, "mFace", [(0, a1, .55), (1, a1, .06)], 0, 0, 0, 1)
    items = [(depth((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), "w", (a, b)) for a, b in segs if (a, b) not in door_segs]
    for k, di in enumerate(door_info):
        a, b = di["seg"]
        items.append((depth((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) + 1e-3, "d", (a, b, k)))
    items.sort(key=lambda it: -it[0])
    tops = []
    walls = []
    for _, kind, data in items:
        if kind == "w":
            (u1, v1), (u2, v2) = data
            B1, B2, T1, T2 = P(u1, v1), P(u2, v2), P(u1, v1, hw), P(u2, v2, hw)
            walls.append(f'<path d="{poly([B1, B2, T2, T1])}Z" fill="#07051A" fill-opacity=".72"/>'
                         f'<path d="{poly([B1, B2, T2, T1])}Z" fill="{face}"/>'
                         f'<path d="M{f(T1[0])} {f(T1[1])}L{f(T2[0])} {f(T2[1])}" stroke="#C7B6FF" stroke-width="1.5" stroke-linecap="round"/>')
            tops.append(f'M{f(T1[0])} {f(T1[1])}L{f(T2[0])} {f(T2[1])}')
        else:
            (u1, v1), (u2, v2), k = data
            di = door_info[k]
            B1, B2 = P(u1, v1), P(u2, v2)
            closed = poly([B1, B2, P(u2, v2, hw), P(u1, v1, hw)]) + "Z"
            opn = poly([B1, B2, P(u2, v2, .02), P(u1, v1, .02)]) + "Z"
            tf = di["flip"]
            kk = [(0, closed), (tf, closed), (tf + .45, opn), (11.3, opn), (11.9, closed), (T, closed)]
            dcol = [(0, a2), (tf, a2), (tf + .3, C["lime"]), (11.3, C["lime"]), (11.6, a2), (T, a2)]
            walls.append(f'<path d="{closed}" fill="{a2}" fill-opacity=".38" stroke="{a2}" stroke-width="1.4" filter="url(#mGl)">'
                         f'{anim("d", kk, T)}{anim("fill", dcol, T)}{anim("stroke", dcol, T)}</path>')
    o.append(f'<path d="{"".join(tops)}" stroke="{a1}" stroke-width="5" opacity=".55" filter="url(#mBl)"/>')
    o.append("".join(walls))
    # entrance / exit portals
    for (u, v), col in (((0, ENT + .5), a2), ((COLS, EXT + .5), C["lime"])):
        x, y = P(u, v, .02)
        o.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="16" ry="6" fill="{col}" opacity=".5" filter="url(#mBl)"/>')
    # photon
    o.append(f'<g>{fade}<circle r="9" fill="{a2}" opacity=".5" filter="url(#mBl)"/><circle r="3.6" fill="#fff"/>'
             f'<animateMotion path="{pd}" keyPoints="{kp}" keyTimes="{kt}" calcMode="linear" dur="{T}s" repeatCount="indefinite"/></g>')

    # ---- kets + gate badges above doors --------------------------------------------------------
    gates = ["X", "H", "CNOT"]
    lab = []
    ket_pos = []
    for k, di in enumerate(door_info):
        (u1, v1), (u2, v2) = di["seg"]
        tx_, ty_ = P((u1 + u2) / 2, (v1 + v2) / 2, hw)
        ky = ty_ - 26
        ket_pos.append((tx_, ky))
        tf = di["flip"]
        if k == 1:
            k0 = vis_g(ket(d, "0", tx_, ky, 17, C["ice"], anchor="middle"), [(0, di["plus"]), (11.6, T)], T)
            kp_ = vis_g(ket(d, "+", tx_, ky, 17, C["cyan"], anchor="middle"), [(di["plus"], tf)], T)
            k1 = vis_g(ket(d, "1", tx_, ky, 17, C["lime"], anchor="middle"), [(tf, 11.6)], T)
            lab.append(k0 + kp_ + k1)
        else:
            lab.append(vis_g(ket(d, "0", tx_, ky, 17, C["ice"], anchor="middle"), [(0, tf), (11.6, T)], T))
            lab.append(vis_g(ket(d, "1", tx_, ky, 17, C["lime"], anchor="middle"), [(tf, 11.6)], T))
        lab.append(f'<line x1="{f(tx_)}" y1="{f(ky + 5)}" x2="{f(tx_)}" y2="{f(ty_ - 3)}" stroke="{C["ice"]}" stroke-opacity=".5"/>')
        # gate badge
        g = gates[k]
        bw = 46 if g == "CNOT" else 24
        bx, by = tx_ + 22, ky - 18
        hi = anim("stroke-opacity", [(0, .45), (di["arr"], .45), (di["arr"] + .2, 1), (di["go"], 1), (di["go"] + .4, .45), (T, .45)], T)
        badge = f'<rect x="{f(bx)}" y="{f(by)}" width="{bw}" height="24" rx="5" fill="#0B0820" fill-opacity=".9" stroke="{a2}" stroke-width="1.4">{hi}</rect>'
        if g == "CNOT":
            cy_ = by + 12
            badge += (f'<circle cx="{f(bx + 11)}" cy="{f(cy_)}" r="3.2" fill="{C["text"]}"/>'
                      f'<line x1="{f(bx + 11)}" y1="{f(cy_)}" x2="{f(bx + 33)}" y2="{f(cy_)}" stroke="{C["text"]}" stroke-width="1.4"/>'
                      f'<circle cx="{f(bx + 34)}" cy="{f(cy_)}" r="6.5" stroke="{C["text"]}" stroke-width="1.4" fill="none"/>'
                      f'<path d="M{f(bx + 27.5)} {f(cy_)}h13M{f(bx + 34)} {f(cy_ - 6.5)}v13" stroke="{C["text"]}" stroke-width="1.4"/>')
        else:
            badge += d.text(g, bx + bw / 2, by + 17.5, "mono-b", 15, C["text"], "middle")
        lab.append(badge)
    # CNOT control link: q0 door -> q2 door
    (ax_, ay_), (cx_, cy2) = ket_pos[0], ket_pos[2]
    lk = f"M{f(ax_)} {f(ay_ - 22)}Q{f((ax_ + cx_) / 2)} {f(min(ay_, cy2) - 70)} {f(cx_)} {f(cy2 - 22)}"
    lab.insert(0, f'<path d="{lk}" stroke="{a2}" stroke-width="1.3" stroke-dasharray="3 5" fill="none">'
                  f'{anim("stroke-opacity", [(0, .18), (door_info[2]["arr"], .18), (door_info[2]["arr"] + .2, .95), (door_info[2]["go"], .95), (door_info[2]["go"] + .5, .18), (T, .18)], T)}'
                  f'<animate attributeName="stroke-dashoffset" values="0;-16" dur="1s" repeatCount="indefinite"/></path>')
    o.append("".join(lab))

    # ---- register + circuit strip --------------------------------------------------------------
    sy = 318
    o.append(f'<line x1="22" y1="{sy - 12}" x2="{AW - 22}" y2="{sy - 12}" stroke="{C["line"]}"/>')
    reg = [d.text("REGISTER", 28, sy + 12, "mono-b", 13, C["muted"], tracking=2.4)]
    for k in range(3):
        x = 32 + k * 62
        reg.append(d.text(f"q{k}", x + 4, sy + 36, "mono", 13, C["dim"]))
        di = door_info[k]
        tf = di["flip"]
        if k == 1:
            reg.append(vis_g(ket(d, "0", x, sy + 62, 20, C["ice"]), [(0, di["plus"]), (11.6, T)], T))
            reg.append(vis_g(ket(d, "+", x, sy + 62, 20, C["cyan"]), [(di["plus"], tf)], T))
        else:
            reg.append(vis_g(ket(d, "0", x, sy + 62, 20, C["ice"]), [(0, tf), (11.6, T)], T))
        reg.append(vis_g(ket(d, "1", x, sy + 62, 20, C["lime"]), [(tf, 11.6)], T))
    reg.append(vis_g(d.text("ESCAPED", 224, sy + 62, "mono-b", 13, C["lime"], tracking=2), [(t_end, 11.6)], T))
    o.append("".join(reg))
    # circuit: wires q0..q2, gates at the playhead positions of each door
    X0c, X1c = 296, AW - 30
    wys = [sy + 4, sy + 30, sy + 56]
    cir = []
    for k, yw in enumerate(wys):
        cir.append(f'<line x1="{X0c}" y1="{yw}" x2="{X1c}" y2="{yw}" stroke="{C["line2"]}" stroke-width="1.2"/>')
        cir.append(d.text(f"q{k}", X0c - 10, yw + 4.5, "mono", 13, C["dim"], "end"))

    def gx(fr):
        return X0c + 14 + fr * (X1c - X0c - 28)

    def gbox(x, y, label, t_on):
        hl = anim("stroke", [(0, C["line2"]), (t_on, C["line2"]), (t_on + .15, a2), (11.6, a2), (11.8, C["line2"]), (T, C["line2"])], T)
        return (f'<rect x="{f(x - 11)}" y="{f(y - 11)}" width="22" height="22" rx="4" fill="#0B0820" stroke-width="1.4">{hl}</rect>'
                + d.text(label, x, y + 5.5, "mono-b", 14, C["text"], "middle"))
    g0, g1, g2 = (gx(di["frac"]) for di in door_info)
    cir.append(gbox(g0, wys[0], "X", door_info[0]["arr"]))
    cir.append(gbox(g1 - 13, wys[1], "H", door_info[1]["arr"]))
    # measurement box
    mxp, myp = g1 + 13, wys[1]
    hl = anim("stroke", [(0, C["line2"]), (door_info[1]["flip"], C["line2"]), (door_info[1]["flip"] + .15, C["lime"]), (11.6, C["lime"]), (11.8, C["line2"]), (T, C["line2"])], T)
    cir.append(f'<rect x="{f(mxp - 11)}" y="{f(myp - 11)}" width="22" height="22" rx="4" fill="#0B0820" stroke-width="1.4">{hl}</rect>'
               f'<path d="M{f(mxp - 6)} {f(myp + 4)}A6.5 6.5 0 0 1 {f(mxp + 6)} {f(myp + 4)}M{f(mxp)} {f(myp + 4)}L{f(mxp + 5)} {f(myp - 5)}" stroke="{C["text"]}" stroke-width="1.3" fill="none"/>')
    t3 = door_info[2]["arr"]
    hl3 = anim("stroke", [(0, C["text"]), (t3, C["text"]), (t3 + .15, C["lime"]), (11.6, C["lime"]), (11.8, C["text"]), (T, C["text"])], T)
    cir.append(f'<g stroke-width="1.5">{hl3}<line x1="{f(g2)}" y1="{wys[0]}" x2="{f(g2)}" y2="{wys[2] - 8}"/>'
               f'<circle cx="{f(g2)}" cy="{wys[2]}" r="8" fill="#0B0820"/><path d="M{f(g2 - 8)} {wys[2]}h16M{f(g2)} {wys[2] - 8}v16"/></g>'
               f'<circle cx="{f(g2)}" cy="{wys[0]}" r="4" fill="{C["text"]}"/>')
    # playhead synced to the photon
    ph_vals = ";".join(f"{f(gx(p) - X0c)} 0" for _, p in keys)
    cir.append(f'<g>{fade}<g><line x1="{X0c}" y1="{wys[0] - 16}" x2="{X0c}" y2="{wys[2] + 14}" stroke="{a2}" stroke-width="1.5"/>'
               f'<path d="M{X0c - 4} {wys[0] - 20}h8l-4 5z" fill="{a2}"/>'
               f'<animateTransform attributeName="transform" type="translate" values="{ph_vals}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></g></g>')
    o.append("".join(cir))
    return "".join(o)


# ===================================================== OP-04 PHISHGUARD ===

def art_phish(d, a1, a2):
    o = []
    glow(d, "pGl", 3.5, 2)
    blur(d, "pBl", 12)
    cx, cy, R = 152, 168, 106
    TS = 4.0
    # radar body
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R + 20}" fill="{a1}" opacity=".10" filter="url(#pBl)"/>')
    rg = rad(d, "pRd", [(0, "#1A0612", .9), (1, "#06040A", .9)])
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{rg}" stroke="{a1}" stroke-opacity=".55" stroke-width="1.3"/>')
    for k in (1 / 3, 2 / 3):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{f(R * k)}" stroke="{a1}" stroke-opacity=".22" fill="none"/>')
    o.append(f'<path d="M{cx - R} {cy}H{cx + R}M{cx} {cy - R}V{cy + R}" stroke="{a1}" stroke-opacity=".18"/>')
    tk = []
    for k in range(72):
        a = math.radians(k * 5)
        L = 7 if k % 6 == 0 else 3
        tk.append(f'M{f(cx + (R - L) * math.cos(a))} {f(cy + (R - L) * math.sin(a))}L{f(cx + R * math.cos(a))} {f(cy + R * math.sin(a))}')
    o.append(f'<path d="{"".join(tk)}" stroke="{a1}" stroke-opacity=".45"/>')
    # sweep
    ang = math.radians(-70)
    wedge = f"M{cx} {cy}L{cx + R} {cy}A{R} {R} 0 0 0 {f(cx + R * math.cos(ang))} {f(cy + R * math.sin(ang))}Z"
    d.defs.append(f'<linearGradient id="pSw" gradientUnits="userSpaceOnUse" x1="{f(cx + R * .7 * math.cos(ang))}" y1="{f(cy + R * .7 * math.sin(ang))}" '
                  f'x2="{f(cx + R * .7)}" y2="{cy + 6}"><stop offset="0" stop-color="{a1}" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="{a1}" stop-opacity=".5"/></linearGradient>')
    o.append(f'<g><path d="{wedge}" fill="url(#pSw)"/><line x1="{cx}" y1="{cy}" x2="{cx + R}" y2="{cy}" stroke="{mix(a1, "#FFFFFF", .35)}" stroke-width="1.8" filter="url(#pGl)"/>'
             f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="{TS}s" repeatCount="indefinite"/></g>')
    # blips lit by the sweep
    rnd = random.Random(4)
    for k in range(9):
        adeg = rnd.uniform(0, 360)
        rr = rnd.uniform(.42, .92) * R
        bad = k % 3 != 1
        x, y = cx + rr * math.cos(math.radians(adeg)), cy + rr * math.sin(math.radians(adeg))
        begin = adeg / 360 * TS - TS
        col = C["red"] if bad else C["lime"]
        mark = (xmark(x, y, 3.4, col, 1.6) + f'<circle cx="{f(x)}" cy="{f(y)}" r="8" stroke="{col}" stroke-width="1" fill="none"/>') if bad else \
            f'<circle cx="{f(x)}" cy="{f(y)}" r="3.2" fill="{col}"/>'
        o.append(f'<g opacity=".2">{mark}<animate attributeName="opacity" values="1;.12;.12" keyTimes="0;.7;1" dur="{TS}s" begin="{begin:.2f}s" repeatCount="indefinite"/></g>')
    # pulse rings
    for k in range(2):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="44" stroke="{a1}" stroke-width="1.4" fill="none">'
                 f'<animate attributeName="r" values="44;{R}" dur="3.2s" begin="-{k * 1.6}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".8;0" dur="3.2s" begin="-{k * 1.6}s" repeatCount="indefinite"/></circle>')
    # shield emblem
    def shield(sc):
        pts = (f"M{cx} {f(cy - 40 * sc)}C{f(cx + 14 * sc)} {f(cy - 31 * sc)} {f(cx + 27 * sc)} {f(cy - 29 * sc)} {f(cx + 33 * sc)} {f(cy - 28 * sc)}"
               f"V{f(cy + 1 * sc)}C{f(cx + 33 * sc)} {f(cy + 22 * sc)} {f(cx + 17 * sc)} {f(cy + 35 * sc)} {cx} {f(cy + 42 * sc)}"
               f"C{f(cx - 17 * sc)} {f(cy + 35 * sc)} {f(cx - 33 * sc)} {f(cy + 22 * sc)} {f(cx - 33 * sc)} {f(cy + 1 * sc)}"
               f"V{f(cy - 28 * sc)}C{f(cx - 27 * sc)} {f(cy - 29 * sc)} {f(cx - 14 * sc)} {f(cy - 31 * sc)} {cx} {f(cy - 40 * sc)}Z")
        return pts
    sf = lin(d, "pSf", [(0, mix(a1, "#000000", .35)), (1, "#12040C")], 0, 0, 0, 1)
    o.append(f'<path d="{shield(1.12)}" fill="{a1}" opacity=".35" filter="url(#pBl)"/>')
    o.append(f'<path d="{shield(1.0)}" fill="{sf}" stroke="{mix(a1, "#FFFFFF", .25)}" stroke-width="2" filter="url(#pGl)"/>')
    o.append(f'<path d="{shield(.78)}" stroke="{a2}" stroke-opacity=".6" stroke-width="1.1" fill="none"/>')
    o.append(f'<circle cx="{cx}" cy="{cy - 6}" r="7.5" fill="{C["text"]}"/><path d="M{cx - 4} {cy - 2}L{cx - 6.5} {cy + 16}H{cx + 6.5}L{cx + 4} {cy - 2}Z" fill="{C["text"]}"/>')

    # ---- DOM inspector: an injected <script> gets stripped --------------------------------------
    px, py, pw, ph_ = 288, 50, 252, 150
    dom = [f'<rect x="{px}" y="{py}" width="{pw}" height="{ph_}" rx="9" fill="#06070F" fill-opacity=".92" stroke="{C["line2"]}"/>',
           d.text("DOM · MUTATIONOBSERVER", px + 14, py + 24, "mono-b", 13, a2, tracking=1.2),
           f'<line x1="{px}" y1="{py + 34}" x2="{px + pw}" y2="{py + 34}" stroke="{C["line"]}"/>']
    fs, lh, lx = 13.5, 22, px + 14
    ly = [py + 58 + k * lh for k in range(5)]
    dom.append(d.text("<body>", lx, ly[0], "mono", fs, C["muted"]))
    dom.append(d.text('  <div id="app">', lx, ly[1], "mono", fs, C["soft"]))
    dom.append(d.text('  <script src="app.js">', lx, ly[2], "mono", fs, C["soft"]))
    dom.append(tick(px + pw - 20, ly[2] - 5, 5, C["lime"]))
    T = 7.0
    evil = '  <script src="//evil.xyz">'
    ew = d.width(evil, "mono", fs)
    inj = (f'<rect x="{lx - 6}" y="{ly[3] - 16}" width="{pw - 16}" height="22" rx="3" fill="{C["red"]}" fill-opacity=".14"/>'
           + d.text(evil, lx, ly[3], "mono", fs, C["red"])
           + f'<line x1="{lx + 14}" y1="{ly[3] - 4.5}" x2="{f(lx + ew)}" y2="{ly[3] - 4.5}" stroke="{C["red"]}" stroke-width="1.6" pathLength="1" stroke-dasharray="1">'
           + anim("stroke-dashoffset", [(0, 1), (2.0, 1), (2.6, 0), (T, 0)], T) + "</line>")
    dom.append(f'<g>{anim("opacity", [(0, 0), (.5, 0), (.8, 1), (3.6, 1), (4.1, 0), (T, 0)], T)}{inj}</g>')
    stamp = (f'<rect x="{px + pw - 98}" y="{ly[3] - 31}" width="84" height="20" rx="3" fill="#06070F" stroke="{C["red"]}"/>'
             + d.text("STRIPPED", px + pw - 56, ly[3] - 16.5, "mono-b", 12.5, C["red"], "middle", 1.4))
    dom.append(f'<g>{anim("opacity", [(0, 0), (2.6, 0), (2.8, 1), (3.6, 1), (4.1, 0), (T, 0)], T)}{stamp}</g>')
    dom.append(f'<g>{d.text("</body>", lx, ly[4], "mono", fs, C["muted"])}'
               f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -{lh};0 -{lh};0 0" '
               f'keyTimes="0;{4.0 / T:.4f};{4.5 / T:.4f};{6.6 / T:.4f};1" dur="{T}s" repeatCount="indefinite"/></g>')
    o.append("".join(dom))
    # telemetry link -> SOC
    ty = 230
    o.append(d.text("TELEMETRY", px, ty - 12, "mono-b", 13, C["muted"], tracking=2))
    o.append(d.text("WS → SOC", px + pw, ty - 12, "mono", 13, C["muted"], "end", 1.4))
    o.append(f'<line x1="{px}" y1="{ty}" x2="{px + pw - 30}" y2="{ty}" stroke="{C["line2"]}" stroke-dasharray="3 4"/>')
    o.append(f'<rect x="{px + pw - 26}" y="{ty - 9}" width="26" height="18" rx="3" stroke="{a2}" fill="#06070F"/>'
             f'<circle cx="{px + pw - 13}" cy="{ty}" r="3" fill="{a2}" class="breathe"/>')
    for k in range(4):
        o.append(f'<circle r="2.6" fill="{a2}" cy="{ty}"><animate attributeName="cx" values="{px};{px + pw - 30}" dur="2.4s" begin="-{k * .6}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="2.4s" begin="-{k * .6}s" repeatCount="indefinite"/></circle>')

    # ---- scrolling block / allow log --------------------------------------------------------------
    lx0, ly0, lw, lh2 = 18, 252, AW - 36, 136
    o.append(f'<rect x="{lx0}" y="{ly0}" width="{lw}" height="{lh2}" rx="9" fill="#05060C" fill-opacity=".92" stroke="{C["line2"]}"/>')
    o.append(d.text("RUNTIME LOG", lx0 + 14, ly0 + 22, "mono-b", 13, C["muted"], tracking=2))
    o.append(f'<circle cx="{lx0 + lw - 70}" cy="{ly0 + 17.5}" r="3.5" fill="{C["red"]}" class="blink"/>')
    o.append(d.text("LIVE", lx0 + lw - 14, ly0 + 22, "mono-b", 13, C["red"], "end", 2))
    o.append(f'<line x1="{lx0}" y1="{ly0 + 31}" x2="{lx0 + lw}" y2="{ly0 + 31}" stroke="{C["line"]}"/>')
    entries = [
        (False, "BLOCKED", "fetch → evil-cdn.xyz/steal?token"),
        (True, "ALLOWED", "api.myapp.com"),
        (False, "BLOCKED", "localStorage.jwt → cdn-x.ru"),
        (False, "STRIPPED", '<script src="//evil.xyz">'),
        (True, "ALLOWED", "fetch → api.myapp.com/v1/user"),
        (False, "BLOCKED", "fetch → paste-drop.top/up?c="),
        (True, "ALLOWED", "ws → soc.local/telemetry"),
        (True, "ALLOWED", "cdn.myapp.com/app.js"),
    ]
    LH = 24
    rows = []
    for k, (ok, verb, det) in enumerate(entries):
        y = k * LH
        col = C["lime"] if ok else C["red"]
        rows.append((tick(lx0 + 22, y - 5, 5, col) if ok else xmark(lx0 + 22, y - 5, 4.2, col, 1.8))
                    + d.text(verb, lx0 + 38, y, "mono-b", 14, col, tracking=.6)
                    + d.text(det, lx0 + 124, y, "mono", 14, C["soft"] if not ok else C["muted"])
                    + d.text(f"12:04:{31 + k * 2:02d}", lx0 + lw - 14, y, "mono", 13, C["dim"], "end"))
    block = "".join(rows)
    n = len(entries)
    d.defs.append(f'<clipPath id="pLog"><rect x="{lx0}" y="{ly0 + 33}" width="{lw}" height="{lh2 - 36}"/></clipPath>')
    o.append(f'<g clip-path="url(#pLog)"><g transform="translate(0 {ly0 + 56})"><g>{block}<g transform="translate(0 {n * LH})">{block}</g>'
             f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 -{n * LH}" dur="{n * 1.7:.1f}s" repeatCount="indefinite"/></g></g></g>')
    return "".join(o)


# ================================================== OP-05 EVENT HORIZON ===

def art_hole(d, a1, a2):
    o = []
    cx, cy, Rs = 280, 204, 56
    blur(d, "hB1", 2)
    blur(d, "hB2", 7)
    blur(d, "hB3", 20)
    blur(d, "hB4", 40)
    glow(d, "hGl", 2.2, 2)
    # nebula
    o.append(f'<g filter="url(#hB4)"><ellipse cx="90" cy="90" rx="160" ry="90" fill="{a1}" opacity=".30"/>'
             f'<ellipse cx="500" cy="330" rx="170" ry="90" fill="{C["magenta"]}" opacity=".13"/>'
             f'<ellipse cx="470" cy="70" rx="120" ry="60" fill="{a2}" opacity=".12"/></g>')
    # lensed starfield (point-lens primary + secondary images)
    rnd = random.Random(55)
    thE = 92.0
    st = []
    for _ in range(170):
        x, y = rnd.uniform(0, AW), rnd.uniform(0, AH)
        dx, dy = x - cx, y - cy
        dd = math.hypot(dx, dy) + 1e-6
        ux, uy = dx / dd, dy / dd
        br = rnd.uniform(.25, .9)
        r = rnd.uniform(.4, 1.25)
        for sgn in (1, -1):
            dp = (dd + sgn * math.sqrt(dd * dd + 4 * thE * thE)) / 2
            if abs(dp) < Rs * 1.08:
                continue
            px, py = cx + ux * dp, cy + uy * dp
            mag = br * (1 if sgn > 0 else .45)
            stretch = thE * thE / (abs(dp) * abs(dp))
            if stretch > .35 and abs(dp) < 220:
                # tangential arc
                ang = math.atan2(py - cy, px - cx)
                half = min(.22, stretch * .09)
                a0, a_1 = ang - half, ang + half
                rr = abs(dp)
                st.append(f'<path d="M{f(cx + rr * math.cos(a0))} {f(cy + rr * math.sin(a0))}A{f(rr)} {f(rr)} 0 0 1 {f(cx + rr * math.cos(a_1))} {f(cy + rr * math.sin(a_1))}" '
                          f'stroke="#fff" stroke-opacity="{mag:.2f}" stroke-width="{f(r * .9)}" stroke-linecap="round"/>')
            elif sgn > 0:
                st.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(r)}" fill="#fff" opacity="{mag:.2f}"/>')
    o.append(f'<g>{"".join(st)}</g>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="230" fill="{rad(d, "hHalo", [(0, C["ice"], .16), (.4, a1, .07), (1, a1, 0)])}"/>')

    # ---- disk geometry -------------------------------------------------------------------
    tilt = .135
    NR = 24
    r_in, r_out = 84, 252
    col_ramp = [(0, "#FFFFFF"), (.12, "#E4FCFF"), (.3, C["ice"]), (.55, C["cyan"]), (.8, a1), (1, C["magenta"])]
    rnd = random.Random(8)
    rings = []
    for k in range(NR):
        t = k / (NR - 1)
        rx = r_in + (r_out - r_in) * t ** 1.15
        ry = rx * tilt
        col = ramp(col_ramp, t)
        op = .95 * (1 - t) ** 1.25 + .1
        sw = 2.2 + 2.6 * t
        dash = [rnd.randint(8, 46), rnd.randint(4, 16), rnd.randint(2, 18), rnd.randint(4, 22)]
        per = sum(dash)
        dur = 3.2 * (rx / r_in) ** 1.5
        gid = f"hD{k}"
        d.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{f(cx - rx)}" y1="0" x2="{f(cx + rx)}" y2="0">'
                      f'<stop offset="0" stop-color="{mix(col, "#FFFFFF", .55)}" stop-opacity="{min(1, op * 1.5):.2f}"/>'
                      f'<stop offset=".45" stop-color="{col}" stop-opacity="{op:.2f}"/>'
                      f'<stop offset="1" stop-color="{mix(col, C["magenta"], .6)}" stop-opacity="{op * .32:.2f}"/></linearGradient>')
        rings.append((rx, ry, gid, sw, dash, per, dur))

    def half(rx, ry, front):
        if front:
            return f"M{f(cx - rx)} {cy}A{f(rx)} {f(ry)} 0 0 0 {f(cx + rx)} {cy}"
        return f"M{f(cx + rx)} {cy}A{f(rx)} {f(ry)} 0 0 0 {f(cx - rx)} {cy}"

    def disk(front):
        out = []
        for rx, ry, gid, sw, dash, per, dur in rings:
            out.append(f'<path d="{half(rx, ry, front)}" stroke="url(#{gid})" stroke-width="{f(sw)}" fill="none" '
                       f'stroke-dasharray="{" ".join(map(str, dash))}"><animate attributeName="stroke-dashoffset" values="0;-{per * 3}" '
                       f'dur="{f(dur * 3)}s" repeatCount="indefinite"/></path>')
        return "".join(out)

    bloom_g = f"url(#{rings[3][2]})"
    # back half of the disk (hidden behind the hole, peeks out at the sides)
    o.append(f'<g opacity=".85">{disk(False)}</g>')
    # lensed image of the far disk: the arc over the top (and a faint one beneath)
    NA = 12
    arcs_top, arcs_bot, arc_bloom = [], [], []
    for k in range(NA):
        t = k / (NA - 1)
        r = Rs + 5 + 42 * t ** 1.2
        col = ramp(col_ramp, .05 + t * .8)
        op = .95 * (1 - t) ** 1.1 + .08
        gid = f"hA{k}"
        d.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{f(cx - r)}" y1="0" x2="{f(cx + r)}" y2="0">'
                      f'<stop offset="0" stop-color="{mix(col, "#FFFFFF", .5)}" stop-opacity="{min(1, op * 1.4):.2f}"/>'
                      f'<stop offset=".5" stop-color="{col}" stop-opacity="{op:.2f}"/>'
                      f'<stop offset="1" stop-color="{mix(col, C["magenta"], .55)}" stop-opacity="{op * .4:.2f}"/></linearGradient>')
        dash = [rnd.randint(10, 40), rnd.randint(3, 12), rnd.randint(4, 20), rnd.randint(3, 10)]
        per = sum(dash)
        ry = r * .9
        arcs_top.append(f'<path d="M{f(cx + r)} {cy}A{f(r)} {f(ry)} 0 0 0 {f(cx - r)} {cy}" stroke="url(#{gid})" stroke-width="{f(2 + 2.2 * t)}" fill="none" '
                        f'stroke-dasharray="{" ".join(map(str, dash))}"><animate attributeName="stroke-dashoffset" values="0;-{per * 3}" dur="{f(4.5 + 6 * t)}s" repeatCount="indefinite"/></path>')
        if k < 5:
            rb = Rs + 2.5 + k * 2.4
            arcs_bot.append(f'<path d="M{f(cx - rb)} {cy}A{f(rb)} {f(rb * .93)} 0 0 0 {f(cx + rb)} {cy}" stroke="url(#{gid})" stroke-width="1.4" fill="none" opacity="{.5 - k * .08:.2f}"/>')
    arc_bloom.append(f'<path d="M{cx + Rs + 26} {cy}A{Rs + 26} {f((Rs + 26) * .9)} 0 0 0 {cx - Rs - 26} {cy}" stroke="{C["ice"]}" stroke-width="30" opacity=".35" fill="none" filter="url(#hB3)"/>')
    o.append("".join(arc_bloom))
    o.append(f'<g>{"".join(arcs_top)}</g>')
    # shadow + photon ring
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{Rs}" fill="#000"/>')
    pr = lin(d, "hPr", [(0, "#FFFFFF", 1), (.5, C["ice"], .9), (1, C["magenta"], .55)], f(cx - Rs), 0, f(cx + Rs), 0, ' gradientUnits="userSpaceOnUse"')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{Rs + 1.6}" stroke="{pr}" stroke-width="3" fill="none" filter="url(#hB2)" opacity=".9"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{Rs + 1.6}" stroke="{pr}" stroke-width="1.3" fill="none"><animate attributeName="stroke-opacity" values="1;.7;1" dur="5s" repeatCount="indefinite"/></circle>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{Rs + 4.2}" stroke="#fff" stroke-opacity=".22" stroke-width=".8" fill="none"/>')
    o.append(f'<g>{"".join(arcs_bot)}</g>')
    # front half of the disk crossing in front of the shadow, with bloom underneath
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="150" ry="{f(150 * tilt)}" stroke="{bloom_g}" stroke-width="34" fill="none" opacity=".55" filter="url(#hB3)"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="110" ry="{f(110 * tilt)}" stroke="#fff" stroke-width="6" fill="none" opacity=".25" filter="url(#hB2)"/>')
    o.append(f'<g>{disk(True)}</g>')
    # anamorphic flare on the approaching (bright) side
    o.append(f'<g style="mix-blend-mode:screen"><ellipse cx="{cx - 96}" cy="{cy + 4}" rx="240" ry="2.2" fill="{C["ice"]}" filter="url(#hB1)">'
             f'<animate attributeName="opacity" values=".35;.8;.35" dur="7s" repeatCount="indefinite"/></ellipse>'
             f'<circle cx="{cx - 96}" cy="{cy + 4}" r="5" fill="#fff" opacity=".8" filter="url(#hB1)"/></g>')

    # ---- HUD callouts --------------------------------------------------------------------
    hud = []
    a = math.radians(-38)
    p1 = (cx + (Rs + 2) * math.cos(a), cy + (Rs + 2) * math.sin(a))
    hud.append(f'<path d="M{f(p1[0])} {f(p1[1])}L{f(p1[0] + 44)} {f(p1[1] - 52)}H{AW - 30}" stroke="{C["ice"]}" stroke-opacity=".55" fill="none"/>'
               f'<circle cx="{f(p1[0])}" cy="{f(p1[1])}" r="2.5" fill="{C["ice"]}"/>')
    hud.append(d.text("PHOTON RING · b ≈ 2.6 rs", AW - 30, p1[1] - 58, "mono", 13, C["ice"], "end", 1))
    pi = (cx + r_in, cy)
    hud.append(f'<path d="M{f(pi[0])} {f(pi[1] + 8)}L{f(pi[0] + 30)} {cy + 62}H{AW - 30}" stroke="{C["muted"]}" stroke-opacity=".7" fill="none"/>'
               f'<circle cx="{f(pi[0])}" cy="{f(pi[1] + 8)}" r="2.2" fill="{C["muted"]}"/>')
    hud.append(d.text("ISCO · 3 rs", AW - 30, cy + 78, "mono", 13, C["muted"], "end", 1))
    hud.append(d.text("◆ BLUESHIFT", 30, cy + 58, "mono-b", 13, C["ice"], tracking=1.6))
    hud.append(d.text("approaching", 30, cy + 76, "mono", 13, C["muted"], tracking=.6))
    # telemetry: a slow dive toward the horizon
    vals = [(6.0, .913, .41), (4.0, .866, .50), (3.0, .816, .58), (2.0, .707, .71), (1.5, .577, .82), (1.2, .408, .91)]
    rows = [f"r/rs {r:4.2f}   CLOCK {c:.2f}×   v_esc {v:.2f}c" for r, c, v in vals]
    hud.append(f'<line x1="22" y1="342" x2="{AW - 22}" y2="342" stroke="{C["line"]}"/>')
    hud.append(d.text("TELEMETRY", 28, 368, "mono-b", 13, a1 if a1 != C["violet"] else mix(a1, "#FFFFFF", .3), tracking=2.4))
    hud.append(cyc_text(d, rows, 28, 390, "mono", 14, C["soft"], 12))
    hud.append(d.text("SCHWARZSCHILD", AW - 28, 368, "mono", 13, C["muted"], "end", 2))
    hud.append(d.text("PER-PIXEL GR", AW - 28, 390, "mono", 13, C["muted"], "end", 2))
    o.append("".join(hud))
    # gentle camera breathing on the whole scene
    return (f'<g transform="translate({cx} {cy})"><g><animateTransform attributeName="transform" type="scale" values="1;1.025;1" dur="16s" '
            f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/><g transform="translate({-cx} {-cy})">'
            + "".join(o[:-1]) + "</g></g></g>" + o[-1])


# ========================================================== OP-06 NOSQL ===

def art_nosql(d, a1, a2):
    o = []
    cx, cy, RX, RY = 280, 226, 200, 60
    T = 12.0
    blur(d, "nB1", 3)
    blur(d, "nB2", 12)
    glow(d, "nGl", 3, 2)
    # particle field: a slowly turning disc of points (squashed -> 3D)
    rnd = random.Random(61)
    pts = []
    for _ in range(300):
        r = 40 + 270 * math.sqrt(rnd.random())
        a = rnd.uniform(0, 2 * math.pi)
        col = a1 if rnd.random() < .6 else a2
        pts.append(f'<circle cx="{f(r * math.cos(a))}" cy="{f(r * math.sin(a))}" r="{f(rnd.uniform(.8, 2.2))}" fill="{col}" opacity="{rnd.uniform(.15, .6):.2f}"/>')
    o.append(f'<g transform="translate({cx} {cy}) scale(1 .3)"><g>{"".join(pts)}'
             f'<animateTransform attributeName="transform" type="rotate" values="0;360" dur="90s" repeatCount="indefinite"/></g></g>')
    o.append(stars(62, 60, AW, AH, rmax=1.2))
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="230" ry="90" fill="{a1}" opacity=".12" filter="url(#nB2)"/>')

    def E(deg, r=1.0):
        a = math.radians(deg)
        return cx + RX * r * math.cos(a), cy + RY * r * math.sin(a)

    # hash ring
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" stroke="{C["line2"]}" stroke-width="6" fill="none" opacity=".6"/>')
    tk = []
    for k in range(96):
        deg = k * 3.75
        p, q = E(deg, .96), E(deg, 1.04 if k % 8 else 1.09)
        tk.append(f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" stroke="{C["ice"]}" stroke-opacity="{.18 + .3 * (math.sin(math.radians(deg)) + 1) / 2:.2f}"/>')
    o.append("".join(tk))
    shards = [("A", 90, C["cyan"]), ("B", 210, C["violet"]), ("C", 330, C["magenta"])]
    for name, deg, col in shards:
        a0, a_1 = math.radians(deg - 56), math.radians(deg + 56)
        p, q = E(deg - 56), E(deg + 56)
        o.append(f'<path d="M{f(p[0])} {f(p[1])}A{RX} {RY} 0 0 1 {f(q[0])} {f(q[1])}" stroke="{col}" stroke-width="3" fill="none" opacity=".85" filter="url(#nGl)"/>')
    # token flowing around the ring
    ring_path = f"M{cx + RX} {cy}A{RX} {RY} 0 1 1 {cx - RX} {cy}A{RX} {RY} 0 1 1 {cx + RX} {cy}"
    for k in range(3):
        o.append(f'<circle r="2.6" fill="#fff"><animateMotion path="{ring_path}" dur="9s" begin="-{k * 3}s" repeatCount="indefinite"/></circle>')

    # sphere gradients
    def sph(gid, col):
        return rad(d, gid, [(0, "#FFFFFF", .95), (.28, mix(col, "#FFFFFF", .25)), (.75, col), (1, mix(col, "#000000", .55))], cx=.36, cy=.32, r=.75)
    gr = {k: sph(f"nS{k}", c) for k, c in (("cy", C["cyan"]), ("vi", C["violet"]), ("ma", C["magenta"]), ("re", C["red"]), ("am", C["amber"]), ("ic", C["ice"]))}

    router = (cx, 82)
    sets = {}
    for name, deg, col in shards:
        bx, by = E(deg)
        sc = .78 + .22 * (math.sin(math.radians(deg)) + 1) / 2
        lift = 34 * sc
        nodes = [(bx, by - lift - 20 * sc), (bx - 26 * sc, by - lift + 12 * sc), (bx + 26 * sc, by - lift + 12 * sc)]
        sets[name] = (nodes, sc, col, (bx, by))
    # router -> shards links (behind nodes)
    for name, (nodes, sc, col, base) in sets.items():
        n0 = nodes[0]
        o.append(f'<path d="M{router[0]} {router[1] + 14}L{f(n0[0])} {f(n0[1] - 16 * sc)}" stroke="{col}" stroke-opacity=".35" stroke-dasharray="3 6" fill="none">'
                 f'<animate attributeName="stroke-dashoffset" values="0;-18" dur="1.2s" repeatCount="indefinite"/></path>')
        o.append(f'<line x1="{f(base[0])}" y1="{f(base[1])}" x2="{f(base[0])}" y2="{f(nodes[1][1] + 10)}" stroke="{col}" stroke-opacity=".45" stroke-dasharray="2 3"/>'
                 f'<circle cx="{f(base[0])}" cy="{f(base[1])}" r="3.5" fill="{col}"/>')
    # routed requests
    order = [("C", .4), ("B", 2.6), ("A", 5.4), ("C", 7.6), ("B", 9.6)]
    keys_txt = {"A": "cart:19", "B": "user:42", "C": "order:7"}
    for name, t0 in order:
        nodes, sc, col, base = sets[name]
        tgt = nodes[0] if not (name == "A" and 3.0 <= t0 < 11.0) else nodes[1]
        pth = f"M{router[0]} {router[1] + 14}L{f(tgt[0])} {f(tgt[1] - 16 * sc)}"
        a, b = t0 / T, (t0 + 1.1) / T
        o.append(f'<circle r="4" fill="{col}" filter="url(#nGl)" opacity="0">'
                 f'<animateMotion path="{pth}" keyPoints="0;0;1;1" keyTimes="0;{a:.4f};{b:.4f};1" calcMode="linear" dur="{T}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{a:.4f};{a + .01:.4f};{b - .01:.4f};{b:.4f};1" dur="{T}s" repeatCount="indefinite"/></circle>')
    # router node + key label
    o.append(f'<circle cx="{router[0]}" cy="{router[1]}" r="20" fill="{C["ice"]}" opacity=".18" filter="url(#nB2)"/>')
    o.append(f'<rect x="{router[0] - 15}" y="{router[1] - 15}" width="30" height="30" rx="7" transform="rotate(45 {router[0]} {router[1]})" '
             f'fill="#0A0E1E" stroke="{C["ice"]}" stroke-width="1.5"/>'
             f'<circle cx="{router[0]}" cy="{router[1]}" r="4.5" fill="{C["ice"]}" class="breathe"/>')
    o.append(d.text("ROUTER", router[0] + 30, router[1] - 4, "mono-b", 13, C["ice"], tracking=2))
    lab = []
    for (name, t0), nxt in zip(order, order[1:] + [(None, T + order[0][1])]):
        txt = f"h({keys_txt[name]}) → {name}"
        lab.append(vis_g(d.text(txt, router[0] + 30, router[1] + 15, "mono", 13, sets[name][2]), [(t0, min(T, nxt[1]))], T))
    # first window wraps around from the end of the loop
    lab.append(vis_g(d.text(f"h({keys_txt['B']}) → B", router[0] + 30, router[1] + 15, "mono", 13, sets["B"][2]), [(0, order[0][1])], T))
    o.append("".join(lab))

    # replica sets: nodes, replication edges, pulses
    def edge(p, q, col, sc):
        s = f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" stroke="{col}" stroke-opacity=".55" stroke-width="1.3"/>'
        for k in range(2):
            s += (f'<circle r="{f(2.6 * sc)}" fill="#fff"><animateMotion path="M{f(p[0])} {f(p[1])}L{f(q[0])} {f(q[1])}" dur="1.6s" begin="-{k * .8}s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.8;1" dur="1.6s" begin="-{k * .8}s" repeatCount="indefinite"/></circle>')
        return s

    def node(p, r, grad, extra=""):
        return f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(r)}" fill="{grad}"{extra}/>'

    order_draw = sorted(sets.items(), key=lambda kv: kv[1][3][1])     # back (smaller y) first
    lbl_pos = {}
    for name, (nodes, sc, col, base) in order_draw:
        r = 14 * sc
        sg = gr["cy"] if name == "A" else (gr["vi"] if name == "B" else gr["ma"])
        if name != "A":
            o.append(edge(nodes[0], nodes[1], col, sc) + edge(nodes[0], nodes[2], col, sc))
            o.append(f'<circle cx="{f(nodes[0][0])}" cy="{f(nodes[0][1])}" r="{f(r * 1.9)}" fill="{col}" opacity=".22" filter="url(#nB2)"/>')
            o.append(node(nodes[0], r, sg) + node(nodes[1], r * .82, gr["ic"], ' opacity=".85"') + node(nodes[2], r * .82, gr["ic"], ' opacity=".85"'))
            o.append(d.text("P", nodes[0][0], nodes[0][1] + 4.6, "mono-b", 13, "#06101E", "middle"))
        else:
            n1, n2, n3 = nodes
            # edges from n1 (healthy) / from n2 (after failover)
            o.append(vis_g(edge(n1, n2, col, sc) + edge(n1, n3, col, sc), [(0, 3.0), (11.0, T)], T))
            o.append(vis_g(edge(n2, n3, col, sc), [(4.6, 11.0)], T))
            o.append(vis_g(edge(n2, n1, col, sc), [(7.4, 11.0)], T))
            o.append(f'<circle cx="{f(n1[0])}" cy="{f(n1[1])}" r="{f(r * 2)}" fill="{col}" opacity=".25" filter="url(#nB2)"/>')
            # n1: primary -> down -> recovering -> primary again
            o.append(vis_g(node(n1, r, gr["cy"]), [(0, 3.0), (11.0, T)], T))
            o.append(vis_g(node(n1, r, gr["re"]) + xmark(n1[0], n1[1], 5, "#fff", 2.2), [(3.0, 7.4)], T))
            o.append(vis_g(node(n1, r * .82, gr["ic"]), [(7.4, 11.0)], T))
            o.append(vis_g(d.text("P", n1[0], n1[1] + 4.6, "mono-b", 13, "#06101E", "middle"), [(0, 3.0), (11.0, T)], T))
            # failure shock ring
            o.append(f'<circle cx="{f(n1[0])}" cy="{f(n1[1])}" r="{f(r)}" stroke="{C["red"]}" stroke-width="2" fill="none" opacity="0">'
                     f'{anim("r", [(0, r), (3.0, r), (4.2, r * 3.2), (T, r * 3.2)], T)}{anim("opacity", [(0, 0), (2.99, 0), (3.0, .9), (4.2, 0), (T, 0)], T)}</circle>')
            # n2: secondary -> candidate -> primary -> secondary
            o.append(vis_g(node(n2, r * .82, gr["ic"]), [(0, 3.4), (11.0, T)], T))
            o.append(vis_g(node(n2, r * .9, gr["am"]), [(3.4, 4.6)], T))
            o.append(vis_g(node(n2, r, gr["cy"]) + d.text("P", n2[0], n2[1] + 4.6, "mono-b", 13, "#06101E", "middle"), [(4.6, 11.0)], T))
            o.append(f'<circle cx="{f(n2[0])}" cy="{f(n2[1])}" r="{f(r)}" stroke="{C["amber"]}" stroke-width="1.6" fill="none" opacity="0">'
                     f'{anim("r", [(0, r), (3.4, r), (4.0, r * 2.2), (4.01, r), (4.6, r * 2.2), (T, r * 2.2)], T)}'
                     f'{anim("opacity", [(0, 0), (3.39, 0), (3.4, .9), (4.0, 0), (4.01, .9), (4.6, 0), (T, 0)], T)}</circle>')
            o.append(vis_g(node(n3, r * .82, gr["ic"]), [(0, 3.4), (4.6, T)], T))
            o.append(vis_g(node(n3, r * .82, gr["am"]), [(3.4, 4.6)], T))
        # shard label
        lx, ly = base[0], base[1] + (26 if name == "A" else -88 * sc)
        lbl_pos[name] = (lx, ly)
    for name, (lx, ly) in lbl_pos.items():
        col = sets[name][2]
        rng = {"A": "0x55–0xAA", "B": "0xAA–0xFF", "C": "0x00–0x55"}[name]
        o.append(d.text(f"SHARD {name}", lx, ly, "mono-b", 13, col, "middle", 2))
        o.append(d.text(rng, lx, ly + 17, "mono", 13, C["muted"], "middle", .5))

    # ---- status bar ------------------------------------------------------------------------------
    o.append(f'<line x1="22" y1="342" x2="{AW - 22}" y2="342" stroke="{C["line"]}"/>')
    o.append(d.text("REPLICA SET A", 28, 368, "mono-b", 13, C["muted"], tracking=2.2))
    stat = [((0, 3.0), "● HEALTHY · n1 PRIMARY", C["lime"]),
            ((3.0, 4.6), "✕ n1 DOWN · ELECTION", C["red"]),
            ((4.6, 7.4), "▲ n2 ELECTED PRIMARY", C["amber"]),
            ((7.4, 11.0), "↺ n1 BACK · SYNCING", C["cyan"]),
            ((11.0, T), "● n1 PRIMARY · PRIORITY", C["lime"])]
    for (t0, t1), txt, col in stat:
        o.append(vis_g(d.text(txt.replace("✕", "×").replace("↺", "·"), 28, 391, "mono-b", 14, col, tracking=.8), [(t0, t1)], T))
    o.append(d.text("QUORUM", AW - 28, 368, "mono-b", 13, C["muted"], "end", 2.2))
    qt = "R + W > N · 2 + 2 > 3"
    o.append(d.text(qt, AW - 48, 391, "mono", 14, C["soft"], "end", .4))
    o.append(tick(AW - 34, 386, 6, C["lime"], 2))
    return "".join(o)


ARTS = {
    "viewfinder": (art_vidi, "CAM 01 // PERCEPTION", "OPENVINO · YOLOv8n"),
    "waveform": (art_shadow, "SHADOWADJ // LIVE DELIVERY", "16 kHz · VAD"),
    "maze": (art_maze, "QUBIT DOORS // QISKIT AER", "3 QUBITS"),
    "shield": (art_phish, "RUNTIME SHIELD // ARMED", "ZERO-TRUST"),
    "blackhole": (art_hole, "GR RAY-MARCH // GLSL", "WEBGL2"),
    "cluster": (art_nosql, "CLUSTER // 3 SHARDS × RS", "HASH ROUTING"),
}


# =========================================================== text side ===

def text_block(d, p, cp, tx, a1, a2):
    o = []
    y0 = 80
    # tag row
    o.append('<g class="sr" style="animation-delay:.3s">')
    o.append(f'<path d="M{tx} {y0 - 5}l5.5 -5.5l5.5 5.5l-5.5 5.5z" fill="{a1}"/>')
    cx_ = tx + 22
    o.append(d.text(p["code"], cx_, y0, "mono-b", 15, a1, tracking=4))
    cw = d.width(p["code"], "mono-b", 15, 4)
    lx = cx_ + cw + 14
    o.append(f'<line x1="{f(lx)}" y1="{y0 - 5}" x2="{f(lx + 30)}" y2="{y0 - 5}" stroke="{a1}" stroke-opacity=".6"/>')
    o.append(d.text(cp["tag"], lx + 44, y0, "mono-m", 14, C["muted"], tracking=3))
    o.append("</g>")

    # title: per-letter stroke draw, then gradient fill (same move as the hero)
    title = p["title"]
    fo = Font.get("sans-l")
    size = 60
    while fo.width(title, size, size * .17) > TW - 8:
        size -= 1
    track = size * .17
    base = 142
    tw = fo.width(title, size, track)
    letters = list(fo.letters(title, tx, base, size, track))
    all_d = "".join(pp for _, pp, _, _ in letters)
    fill_g = lin(d, "tFillG", [(0, "#FFFFFF"), (.5, "#E6EBFF"), (1, mix(a1, "#FFFFFF", .15))], f(tx), 0, f(tx + max(tw, 260)), 0, ' gradientUnits="userSpaceOnUse"')
    stroke_g = lin(d, "tStrokeG", [(0, a1), (1, a2)], f(tx), 0, f(tx + max(tw, 260)), 0, ' gradientUnits="userSpaceOnUse"')
    d.defs.append(f'<clipPath id="tClip"><path d="{all_d}"/></clipPath>')
    o.append(f'<g opacity=".42"><path d="{all_d}" fill="{a1}" filter="url(#tHalo)" class="fi" style="animation-delay:1.3s"/></g>')
    o.append(f'<g class="gA"><path d="{all_d}" fill="{C["cyan"]}"/></g><g class="gB"><path d="{all_d}" fill="{C["magenta"]}"/></g>')
    for i, (ch, pp, lx_, adv) in enumerate(letters):
        dl = .45 + i * .065
        o.append(f'<path d="{pp}" pathLength="1" class="tl" fill="{fill_g}" stroke="{stroke_g}" stroke-width="1.2" '
                 f'style="animation-delay:{dl:.2f}s,{dl + 1.0:.2f}s"/>')
    o.append(f'<g clip-path="url(#tClip)"><rect class="tshine" x="{f(tx - 160)}" y="{base - size}" width="110" height="{f(size * 1.3)}" '
             f'fill="{lin(d, "tShG", [(0, "#fff", 0), (.5, "#fff", .8), (1, "#fff", 0)])}"/></g>')

    # tagline
    o.append(f'<g class="r" style="animation-delay:1.0s">{d.text(p["tagline"], tx, 182, "sans-l", 24, mix(a1, "#FFFFFF", .22))}</g>')
    # description
    lines = wrap(cp["desc"], "sans", 19.5, TW)
    assert len(lines) <= 3, (p["key"], lines)
    for k, ln in enumerate(lines):
        o.append(f'<g class="r" style="animation-delay:{1.15 + k * .08:.2f}s">{d.text(ln, tx, 220 + k * 27, "sans", 19.5, C["soft"])}</g>')
    # highlights with drawn bullets
    for k, hl in enumerate(p["highlights"]):
        y = 309 + k * 28.5
        o.append(f'<g class="sr" style="animation-delay:{1.45 + k * .12:.2f}s">'
                 f'<path d="M{tx + 6} {y - 12}l6 6l-6 6l-6 -6z" stroke="{a1}" stroke-width="1.4" fill="none"/>'
                 f'<circle cx="{tx + 6}" cy="{y - 6}" r="1.8" fill="{a2}"/>'
                 + d.text(hl, tx + 24, y, "sans", 19, C["text"]) + "</g>")
    # stack chips
    x, y = tx, 383
    for k, sname in enumerate(p["stack"]):
        wdt = d.width(sname, "sans-sb", 16, .3) + 26
        if x + wdt > tx + TW:
            break
        o.append(f'<g class="fi" style="animation-delay:{1.8 + k * .07:.2f}s">'
                 f'<rect x="{f(x)}" y="{y}" width="{f(wdt)}" height="30" rx="15" fill="#0B0E1A" stroke="{C["line2"]}"/>'
                 + d.text(sname, x + 13, y + 20.5, "sans-sb", 16, C["soft"], tracking=.3) + "</g>")
        x += wdt + 8
    # status chip
    y = 425
    o.append(f'<g class="r" style="animation-delay:2.3s">')
    if p["live"]:
        host = p["live"].split("://", 1)[1].rstrip("/")
        lab, val = "LIVE", host
        wdt = d.width(lab, "mono-b", 15, 2) + d.width(val, "mono-m", 15, .6) + 64
        o.append(f'<rect x="{tx}" y="{y}" width="{f(wdt)}" height="32" rx="16" fill="{C["lime"]}" fill-opacity=".07" stroke="{C["lime"]}" stroke-opacity=".55"/>')
        o.append(f'<circle cx="{tx + 18}" cy="{y + 16}" r="6" fill="{C["lime"]}" opacity=".25" class="breathe"/><circle cx="{tx + 18}" cy="{y + 16}" r="3.6" fill="{C["lime"]}"/>')
        o.append(d.text(lab, tx + 32, y + 21.5, "mono-b", 15, C["lime"], tracking=2))
        lw = d.width(lab, "mono-b", 15, 2)
        o.append(d.text("·  " + val, tx + 32 + lw + 10, y + 21.5, "mono-m", 15, mix(C["lime"], "#FFFFFF", .35), tracking=.6))
    else:
        repo = p["repo"].rstrip("/").split("/")[-1]
        lab, val = "SOURCE", f"github.com/Arrow-Ghost/{repo}"
        wdt = d.width(lab, "mono-b", 15, 2) + d.width("·  " + val, "mono-m", 15, .6) + 52
        o.append(f'<rect x="{tx}" y="{y}" width="{f(wdt)}" height="32" rx="16" fill="#0B0E1A" stroke="{C["line2"]}"/>')
        o.append(f'<path d="M{tx + 18} {y + 10.5}l5.5 5.5l-5.5 5.5l-5.5 -5.5z" fill="{C["muted"]}"/>')
        o.append(d.text(lab, tx + 32, y + 21.5, "mono-b", 15, C["muted"], tracking=2))
        lw = d.width(lab, "mono-b", 15, 2)
        o.append(d.text("·  " + val, tx + 32 + lw + 10, y + 21.5, "mono-m", 15, C["soft"], tracking=.6))
    o.append("</g>")
    return "".join(o)


CARD_CSS = """
@keyframes tDraw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes tFill{from{fill-opacity:0}to{fill-opacity:1}}
.tl{stroke-dasharray:1;animation:tDraw 1.5s cubic-bezier(.6,.05,.25,1) both,tFill 1s ease both}
@keyframes tGA{0%,88%,100%{transform:translate(0,0);opacity:0}89%{transform:translate(-6px,1px);opacity:.8}90.5%{transform:translate(4px,-1px);opacity:.6}92%{transform:translate(0,0);opacity:0}}
@keyframes tGB{0%,88%,100%{transform:translate(0,0);opacity:0}89%{transform:translate(6px,-1px);opacity:.8}90.5%{transform:translate(-4px,1px);opacity:.6}92%{transform:translate(0,0);opacity:0}}
.gA{opacity:0;animation:tGA 9s 3.4s infinite;mix-blend-mode:screen}
.gB{opacity:0;animation:tGB 9s 3.4s infinite;mix-blend-mode:screen}
@keyframes tShine{0%{transform:translateX(0) skewX(-20deg)}38%,100%{transform:translateX(860px) skewX(-20deg)}}
.tshine{animation:tShine 7s 3s infinite ease-in-out}
@keyframes aScan{from{transform:translateY(-100px)}to{transform:translateY(420px)}}
.ascan{animation:aScan 6.5s linear infinite}
"""


def build_card(i, p):
    a1, a2 = ACCENT[p["category"]]
    cp = COPY[p["key"]]
    d = Doc(W, H, title=f'{p["code"]} — {p["title"]}: {p["tagline"]}')
    d.css.append(CARD_CSS)
    blur(d, "tHalo", 12)
    blur(d, "cNeb", 70)
    art_left = i % 2 == 0
    ax = M if art_left else W - M - AW
    tx = M + AW + GAP if art_left else M
    op, cl = panel(d, W, H, "SCENE 03 — FEATURED OPERATIONS", f'{p["code"]} / 06', glow_color=a1)
    out = d.body
    out.append(op)
    # nebula: accent fields drifting slowly behind art and type
    acx = ax + AW / 2
    tcx = tx + TW / 2
    out.append('<g filter="url(#cNeb)">')
    for (x, y, rx, ry, col, opa, dx, dy, dur) in [
        (acx, AY + AH * .55, 330, 200, a1, .34, 40, -20, 24),
        (tcx, 120, 300, 110, a2, .14, -50, 20, 29),
        (tcx + (180 if art_left else -180), 470, 280, 90, "#3B4BFF", .2, 30, -10, 21),
    ]:
        out.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{opa}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></ellipse>')
    out.append("</g>")
    out.append(f'<g opacity=".55">{stars(100 + i, 80, W, H, rmax=1.3)}</g>')
    # giant scene numeral watermark behind the type
    num = p["code"][-2:]
    fo = Font.get("sans-xl")
    nsz = 330
    nw = fo.width(num, nsz, 10)
    nx = tx + TW - nw + 10
    out.append(f'<g class="fi" style="animation-delay:.6s"><path d="{fo.text_path(num, nx, H - 40, nsz, 10)}" fill="none" stroke="{a1}" stroke-opacity=".10" stroke-width="1.2"/></g>')
    # art
    fn, tl, tr = ARTS[p["motif"]]
    out.append(art_frame(d, ax, a1, fn(d, a1, a2), tl, tr))
    # text
    out.append(text_block(d, p, cp, tx, a1, a2))
    out.append(cl)
    # bottom slate: reel progress + next-scene cue
    by = H - 13
    for k in range(6):
        cur = k == i
        out.append(f'<rect x="{28 + k * 24}" y="{by - 6}" width="18" height="3" rx="1.5" fill="{a1 if cur else C["line2"]}"/>')
    out.append(d.text(f"FILE 03.0{i + 1} · DECLASSIFIED", 28 + 6 * 24 + 10, by, "mono", 12.5, C["muted"], tracking=3))
    if i + 1 < len(FEATURED):
        nxt = FEATURED[i + 1]
        cue = f'NEXT  {nxt["code"]} · {nxt["title"]}'
    else:
        cue = "NEXT SCENE  04 · THE ARCHIVE"
    out.append(d.text(cue, W - 46, by, "mono", 12.5, C["muted"], "end", 3))
    out.append(f'<path d="M{W - 38} {by - 9}l6 4.5l-6 4.5z" fill="{a1}"/>')
    return d


def main():
    for i, p in enumerate(FEATURED):
        d = build_card(i, p)
        d.save(f'op-{p["key"]}.svg')


if __name__ == "__main__":
    main()
