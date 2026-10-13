"""Mission log: the story so far, as a lit spine running from the present day
down to where it started.

A glowing central spine (signature gradient, ruler ticks) carries one node per
entry; entry cards alternate left / right and are staggered so the two columns
interlock. Node colour = category, node icon = kind (role diamond, award star,
writing nib, education cap) drawn as paths. Awards get the gold treatment
(amber card, glow, slow shine, spinning star ring) and All India Rank 1 wears
an "AIR 01" medal. On loop a light pulse travels down the spine and each node
pings as it passes. Chapter chips mark the two eras (Vellore / Noida).
"""

import math
import random

from agfx import ACCENT, C, Doc, Font, blur, corners, f, grain, lin, rad, stars, wrap
from content import TIMELINE

W = 1280
BAR = 38
SX = W / 2                     # spine x
CARD_W = 520
GAP_X = 60                     # card edge <-> spine
LX = SX - GAP_X - CARD_W       # left card x  (60)
RX = SX + GAP_X                # right card x (700)
PAD = 28
TW = CARD_W - 2 * PAD          # text width inside a card
STAG = 92                      # min vertical distance between consecutive nodes
VGAP = 24                      # min gap between two cards on the same side
NODE_DY = 33                   # node centre relative to card top (= "when" line)
ERA_BREAK = 5                  # index where the Noida era starts (chip goes above it)
ERA_EXTRA = 44                 # extra room on the spine for that chip
TOP0 = 152                     # first card top
GHOST_H = 82                   # the classified "next entry" beside the first card
GOLD = C["amber"]
GOLD_HI = "#FFE2A6"            # highlight tint of amber, for the medal numerals only

KIND_LABEL = {"role": "ROLE", "award": "AWARD", "writing": "WRITING", "edu": "EDUCATION", "build": "BUILD"}


# ------------------------------------------------------------------ helpers --

def ufilter(d, fid, std, strength=2, pad=4.0):
    """Glow with a generous region (pad = multiples of the bbox) — the default
    -50%/200% box clips blurs on thin shapes like the spine and the pulse."""
    merges = "".join('<feMergeNode in="b"/>' for _ in range(strength))
    d.defs.append(f'<filter id="{fid}" x="-{pad * 100:.0f}%" y="-{pad * 100:.0f}%" width="{(2 * pad + 1) * 100:.0f}%" height="{(2 * pad + 1) * 100:.0f}%">'
                  f'<feGaussianBlur stdDeviation="{std}" result="b"/><feMerge>{merges}<feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return f"url(#{fid})"


def ublur(d, fid, std, x, y, w, h):
    """Blur in user space (for zero-width strokes)."""
    d.defs.append(f'<filter id="{fid}" filterUnits="userSpaceOnUse" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}">'
                  f'<feGaussianBlur stdDeviation="{std}"/></filter>')
    return f"url(#{fid})"


def star_d(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for k in range(n * 2):
        r = ro if k % 2 == 0 else ri
        a = math.radians(rot + k * 180 / n)
        pts.append(f"{f(cx + r * math.cos(a))} {f(cy + r * math.sin(a))}")
    return "M" + "L".join(pts) + "Z"


def icon(kind, x, y, col, s=1.0):
    """Kind glyphs, ~16px, centred on x,y, drawn as paths."""
    def P(d, extra=""):
        return f'<path d="{d}" {extra}/>'
    if kind == "award":
        return P(star_d(x, y + .6 * s, 8.6 * s, 3.7 * s), f'fill="{col}"')
    if kind == "role":
        o, i = 7.4 * s, 3.2 * s
        return (P(f"M{f(x)} {f(y - o)}L{f(x + o)} {f(y)}L{f(x)} {f(y + o)}L{f(x - o)} {f(y)}Z", f'stroke="{col}" stroke-width="{f(1.6 * s)}" fill="none" stroke-linejoin="round"')
                + P(f"M{f(x)} {f(y - i)}L{f(x + i)} {f(y)}L{f(x)} {f(y + i)}L{f(x - i)} {f(y)}Z", f'fill="{col}"'))
    if kind == "writing":
        # fountain-pen nib, point down, with slit and breather hole
        nib = (f"M{f(x)} {f(y + 9 * s)}L{f(x - 5.6 * s)} {f(y - .5 * s)}L{f(x - 3.4 * s)} {f(y - 8 * s)}"
               f"H{f(x + 3.4 * s)}L{f(x + 5.6 * s)} {f(y - .5 * s)}Z")
        return (P(nib, f'fill="{col}"')
                + P(f"M{f(x)} {f(y + 8 * s)}V{f(y + .8 * s)}", f'stroke="{C["void"]}" stroke-width="{f(1.3 * s)}" stroke-linecap="round"')
                + f'<circle cx="{f(x)}" cy="{f(y - .4 * s)}" r="{f(1.5 * s)}" fill="{C["void"]}"/>')
    if kind == "edu":
        top = (f"M{f(x - 9.5 * s)} {f(y - 2.5 * s)}L{f(x)} {f(y - 7 * s)}L{f(x + 9.5 * s)} {f(y - 2.5 * s)}"
               f"L{f(x)} {f(y + 2 * s)}Z")
        body = f"M{f(x - 5.5 * s)} {f(y)}V{f(y + 4.6 * s)}Q{f(x)} {f(y + 8.4 * s)} {f(x + 5.5 * s)} {f(y + 4.6 * s)}V{f(y)}"
        return (P(top, f'fill="{col}"') + P(body, f'stroke="{col}" stroke-width="{f(1.6 * s)}" fill="none"')
                + P(f"M{f(x + 8 * s)} {f(y - 2 * s)}V{f(y + 5 * s)}", f'stroke="{col}" stroke-width="{f(1.3 * s)}"')
                + f'<circle cx="{f(x + 8 * s)}" cy="{f(y + 6 * s)}" r="{f(1.6 * s)}" fill="{col}"/>')
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(5 * s)}" fill="{col}"/>'


# ------------------------------------------------------------------- layout --

def measure(e, i, n):
    when, title, org, detail, cat, kind = e
    award = kind == "award"
    medal = "All India Rank 1" in title
    col = GOLD if award else ACCENT[cat][0]
    col2 = ACCENT[cat][0] if award else ACCENT[cat][1]
    tw = TW - (118 if medal else 0)
    tl = wrap(title, "sans-sb", 23, tw)
    ol = wrap(org, "sans", 18, tw)
    dl = wrap(detail, "sans", 17, tw)
    y = 38                                   # "when" baseline
    ys = {"when": y}
    y += 37
    ys["title"] = [y + k * 28 for k in range(len(tl))]
    y = ys["title"][-1] + 27
    ys["org"] = [y + k * 23 for k in range(len(ol))]
    y = ys["org"][-1] + 32
    ys["detail"] = [y + k * 23 for k in range(len(dl))]
    h = ys["detail"][-1] + 27
    if medal:
        h = max(h, 196)
    return dict(when=when, title=title, org=org, detail=detail, cat=cat, kind=kind, award=award, medal=medal,
                col=col, col2=col2, tl=tl, ol=ol, dl=dl, ys=ys, h=h, num=n - i, side=i % 2)


def layout():
    items = [measure(e, i, len(TIMELINE)) for i, e in enumerate(TIMELINE)]
    bottom = [-1e9, -1e9]
    prev = TOP0 - STAG
    for i, it in enumerate(items):
        s = it["side"]
        t = max(prev + STAG, bottom[s] + VGAP, TOP0)
        if i == ERA_BREAK:
            t = max(t, prev + STAG + ERA_EXTRA)
        if i == 1:                                   # leave room for the classified ghost entry
            t = max(t, TOP0 + 2 + GHOST_H + 26)
        it["top"] = t
        it["x"] = LX if s == 0 else RX
        it["ny"] = t + NODE_DY
        bottom[s] = t + it["h"]
        prev = t
    return items, max(bottom)


# -------------------------------------------------------------------- build --

def build():
    items, content_bottom = layout()
    spine_top = 96                                    # the PRESENT beacon
    spine_end = content_bottom + 34                   # ORIGIN terminal
    H = math.ceil(spine_end + 44 + BAR)
    d = Doc(W, H, title="Mission log — Shrish Verma, 2023 to now")

    # ---- defs ------------------------------------------------------------------
    d.defs.append(f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    neb = blur(d, "neb", 80)
    blur(d, "soft", 2.2)
    blur(d, "halo", 16)
    glow_s = ufilter(d, "glowS", 3.2, 2)
    glow_m = ufilter(d, "glowM", 6, 2)
    vign = rad(d, "vign", [(0, "#000", 0), (0.66, "#000", 0), (1, "#000", 0.8)], r=0.78)
    spine_g = lin(d, "spineG", [(0, C["ice"], 0), (0.035, C["cyan"], 1), (0.42, C["violet"], 1), (0.88, C["magenta"], 1), (1, C["magenta"], 0)],
                  0, spine_top, 0, spine_end, ' gradientUnits="userSpaceOnUse"')
    pulse_g = lin(d, "pulseG", [(0, "#fff", 0), (0.7, C["ice"], .55), (1, "#fff", 1)], 0, 0, 0, 1)
    shine_g = lin(d, "shineG", [(0, GOLD_HI, 0), (.5, GOLD_HI, .16), (1, GOLD_HI, 0)])
    medal_g = lin(d, "medalG", [(0, GOLD_HI, None), (1, GOLD, None)], 0, 0, 0, 1)
    d.defs.append('<pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".04"/></pattern>')
    spine_blur = ublur(d, "spineBlur", 5, SX - 40, spine_top - 40, 80, spine_end - spine_top + 80)

    span = spine_end - spine_top
    PULSE_DUR, PULSE_TRAVEL, PULSE_BEGIN = 7.0, 0.78, 3.4   # s, fraction of cycle spent travelling, begin

    d.css.append(f"""
@keyframes tlDraw{{from{{stroke-dashoffset:1}}to{{stroke-dashoffset:0}}}}
@keyframes tlPop{{0%{{opacity:0;transform:scale(.2)}}65%{{opacity:1;transform:scale(1.12)}}100%{{opacity:1;transform:scale(1)}}}}
@keyframes tlBars{{from{{transform:scaleY(2.6)}}to{{transform:scaleY(1)}}}}
@keyframes tlShine{{0%{{transform:translateX(0)}}30%,100%{{transform:translateX({CARD_W + 360}px)}}}}
@keyframes tlScan{{from{{transform:translateY(-200px)}}to{{transform:translateY({H + 40}px)}}}}
.spine{{stroke-dasharray:1;animation:tlDraw 2.3s linear both}}
.cn{{stroke-dasharray:1;animation:tlDraw .55s cubic-bezier(.6,.05,.25,1) both}}
.pop{{animation:tlPop .75s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:center}}
.shine{{animation:tlShine 9s ease-in-out infinite}}
.scan{{animation:tlScan 12s linear infinite}}
.barT,.barB{{animation:tlBars 1.6s cubic-bezier(.7,0,.2,1) both}}
.barT{{transform-origin:0 0}}.barB{{transform-origin:0 100%}}
""")

    out = d.body
    out.append('<g clip-path="url(#frame)">')
    out.append(f'<rect width="{W}" height="{H}" fill="{C["void"]}"/>')

    # ---- nebula: colour follows the eras (cyan present -> magenta origin) ----------
    out.append(f'<g filter="url(#{neb})">')
    for (x, y, rx_, ry_, col, op, dx, dy, dur) in [
        (240, H * .10, 380, 190, C["violet"], .42, 50, 30, 27),
        (1080, H * .14, 360, 180, C["cyan"], .30, -40, 30, 31),
        (1040, H * .45, 320, 200, C["violet"], .30, -50, -20, 24),
        (200, H * .52, 300, 200, GOLD, .10, 40, -30, 29),
        (300, H * .80, 360, 210, C["magenta"], .30, 60, -20, 26),
        (1060, H * .88, 340, 170, "#3B4BFF", .28, -40, -20, 33),
    ]:
        out.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{rx_}" ry="{ry_}" fill="{col}" opacity="{op}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                   f'<animate attributeName="opacity" values="{op};{op * .55:.2f};{op}" dur="{dur * .7:.1f}s" repeatCount="indefinite"/></ellipse>')
    out.append("</g>")
    out.append(f'<g opacity=".8">{stars(51, 120, W, H, rmax=1.2)}</g><g>{stars(77, 22, W, H, rmin=.6, rmax=1.9)}</g>')

    # ---- the hero's grid floor returns at the origin: where it all started ----------
    horizon = spine_end - 70
    floor_h = H - horizon
    gl = [f'<line x1="{f(SX + i * 5)}" y1="{f(horizon)}" x2="{f(SX + i * 96)}" y2="{f(H)}"/>' for i in range(-22, 23)]
    rows = [f'<line x1="0" y1="{f(horizon + ((k / 8) ** 2.1) * floor_h)}" x2="{W}" y2="{f(horizon + ((k / 8) ** 2.1) * floor_h)}"/>' for k in range(1, 9)]
    gm = lin(d, "floorFade", [(0, "#fff", 0), (.35, "#fff", .55), (1, "#fff", .9)], 0, 0, 0, 1)
    d.defs.append(f'<mask id="floorMask"><rect y="{f(horizon)}" width="{W}" height="{f(floor_h)}" fill="{gm}"/></mask>')
    out.append(f'<g mask="url(#floorMask)" stroke="{C["magenta"]}" stroke-width="1" opacity=".42">{"".join(gl)}'
               f'<g>{"".join(rows)}<animateTransform attributeName="transform" type="translate" values="0 0;0 {f(floor_h / 8 * .6)}" dur="1.8s" repeatCount="indefinite"/></g></g>')
    hz_fade = lin(d, "hzFade", [(0, "#fff", 0), (.2, "#fff", 1), (.8, "#fff", 1), (1, "#fff", 0)])
    d.defs.append(f'<mask id="hzMask"><rect y="{f(horizon - 20)}" width="{W}" height="40" fill="{hz_fade}"/></mask>')
    out.append(f'<g mask="url(#hzMask)"><line x1="0" y1="{f(horizon)}" x2="{W}" y2="{f(horizon)}" stroke="{C["magenta"]}" opacity=".55"/>'
               f'<rect x="0" y="{f(horizon - 2)}" width="{W}" height="4" fill="{C["magenta"]}" opacity=".4" filter="url(#soft)"/></g>')

    # ---- spine: glow, ruler, core --------------------------------------------------
    out.append(f'<path d="M{SX} {spine_top}V{f(spine_end)}" stroke="{spine_g}" stroke-width="7" opacity=".55" filter="{spine_blur}" pathLength="1" class="spine" style="animation-delay:.25s"/>')
    ticks = []
    yy = spine_top + 14
    k = 0
    while yy < spine_end - 6:
        big = k % 5 == 0
        L = 9 if big else 4.5
        ticks.append(f"M{f(SX - 7 - L)} {f(yy)}h{f(L)}M{f(SX + 7)} {f(yy)}h{f(L)}")
        yy += 16
        k += 1
    out.append(f'<path d="{"".join(ticks)}" stroke="{C["line2"]}" stroke-width="1" opacity=".8" class="fi" style="animation-delay:.6s;animation-duration:2.4s"/>')
    out.append(f'<path d="M{SX} {spine_top}V{f(spine_end)}" stroke="{spine_g}" stroke-width="2" pathLength="1" class="spine" style="animation-delay:.25s"/>')

    # ---- travelling pulse (SMIL, synced with node pings) ------------------------------
    d.defs.append(f'<clipPath id="spineClip"><rect x="{SX - 40}" y="{spine_top}" width="80" height="{f(span)}"/></clipPath>')
    PL = 150
    out.append(f'<g clip-path="url(#spineClip)"><g opacity="0">'
               f'<rect x="{SX - 1.6}" y="{spine_top - PL}" width="3.2" height="{PL}" fill="{pulse_g}"/>'
               f'<ellipse cx="{SX}" cy="{spine_top - 30}" rx="9" ry="44" fill="{C["ice"]}" opacity=".35" filter="url(#halo)"/>'
               f'<circle cx="{SX}" cy="{spine_top}" r="3.6" fill="#fff" filter="{glow_s}"/>'
               f'<animateTransform attributeName="transform" type="translate" values="0 0;0 {f(span)};0 {f(span)}" keyTimes="0;{PULSE_TRAVEL};1" dur="{PULSE_DUR}s" begin="{PULSE_BEGIN}s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values="1;1" dur="{PULSE_DUR}s" begin="{PULSE_BEGIN}s" fill="freeze"/>'
               f'</g></g>')

    def ping_at(y):
        return PULSE_TRAVEL * (y - spine_top) / span

    # ---- era chips on the spine ------------------------------------------------------
    def chip(label, cy, delay, col=C["ice"]):
        fs, tr = 13, 3
        tw_ = d.width(label, "mono-b", fs, tr)
        w_ = tw_ + 30
        return (f'<g class="fi" style="animation-delay:{delay:.2f}s">'
                f'<rect x="{f(SX - w_ / 2)}" y="{f(cy - 13)}" width="{f(w_)}" height="26" rx="13" fill="{C["void"]}" stroke="{col}" stroke-opacity=".55"/>'
                f'{d.text(label, SX, cy + 4.6, "mono-b", fs, col, "middle", tr)}</g>')

    # PRESENT beacon at the top of the spine
    bx, by_ = SX, spine_top
    out.append(f'<g class="pop" style="animation-delay:.1s">'
               f'<circle cx="{bx}" cy="{by_}" r="16" fill="{C["lime"]}" opacity=".16" filter="url(#halo)"/>'
               f'<circle cx="{bx}" cy="{by_}" r="9" fill="{C["void"]}" stroke="{C["lime"]}" stroke-width="1.6"/>'
               f'<circle cx="{bx}" cy="{by_}" r="3.6" fill="{C["lime"]}" filter="{glow_s}" class="breathe"/></g>')
    for ph in (0, 1.5):
        out.append(f'<circle cx="{bx}" cy="{by_}" r="9" stroke="{C["lime"]}" stroke-width="1.2" fill="none" opacity="0">'
                   f'<animate attributeName="r" values="9;34" dur="3s" begin="{1.2 + ph}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values=".7;0" dur="3s" begin="{1.2 + ph}s" repeatCount="indefinite"/></circle>')
    lab_y = by_ + 4.6
    out.append(f'<g class="fi" style="animation-delay:.5s">'
               f'{d.text("PRESENT DAY", bx - 40, lab_y, "mono-b", 13, C["text"], "end", 3)}'
               f'{d.text("LOG ACTIVE", bx + 40, lab_y, "mono-b", 13, C["lime"], "start", 3)}</g>')

    first_node = items[0]["ny"]
    out.append(chip("VELLORE", (spine_top + 16 + first_node - 22) / 2, .7))
    eb = items[ERA_BREAK]
    out.append(chip("NOIDA", (items[ERA_BREAK - 1]["ny"] + eb["ny"]) / 2, .3 + 2.3 * ((eb["ny"] - 40 - spine_top) / span)))

    # ---- the next entry: classified (Riley, from the whoami terminal) ------------------
    out.append(ghost(d, items, glow_s))

    # ---- entries ------------------------------------------------------------------
    for i, it in enumerate(items):
        x, t, h, s = it["x"], it["top"], it["h"], it["side"]
        col, col2, ny = it["col"], it["col2"], it["ny"]
        frac = (ny - spine_top) / span
        node_delay = .3 + 2.3 * frac
        card_delay = node_delay + .08
        edge = x + CARD_W if s == 0 else x          # spine-facing edge
        sgn = 1 if s == 0 else -1                   # direction from card towards spine

        # connector (behind node)
        nx0 = SX - 19 * sgn
        out.append(f'<path d="M{f(edge)} {f(ny)}H{f(nx0)}" stroke="{col}" stroke-width="1.4" opacity=".75" pathLength="1" class="cn" style="animation-delay:{card_delay + .35:.2f}s"/>')

        # card
        cls = "sr" if s == 0 else "sl"
        g = [f'<g class="{cls}" style="animation-delay:{card_delay:.2f}s">']
        if it["award"]:
            g.append(f'<rect x="{x}" y="{f(t)}" width="{CARD_W}" height="{f(h)}" rx="16" fill="{GOLD}" opacity=".13" filter="url(#halo)"/>')
        fill_g = lin(d, d.uid("cf"), [(0, col, .16), (.55, col, .03), (1, col, 0)] if s == 1 else [(0, col, 0), (.45, col, .03), (1, col, .16)])
        g.append(f'<rect x="{x}" y="{f(t)}" width="{CARD_W}" height="{f(h)}" rx="14" fill="{C["panel"]}" fill-opacity=".86"/>')
        g.append(f'<rect x="{x}" y="{f(t)}" width="{CARD_W}" height="{f(h)}" rx="14" fill="{fill_g}"/>')
        g.append(f'<rect x="{x + .5}" y="{f(t + .5)}" width="{CARD_W - 1}" height="{f(h - 1)}" rx="14" stroke="{col}" stroke-opacity="{.5 if it["award"] else .28}"/>')
        # top edge lit from the spine side (the spine is the light source)
        edge_g = lin(d, d.uid("eg"), [(0, col, 0), (1, col, .95)] if s == 0 else [(0, col, .95), (1, col, 0)])
        g.append(f'<rect x="{x + 14}" y="{f(t)}" width="{CARD_W - 28}" height="1.3" fill="{edge_g}"/>')
        # plug: bright segment on the spine-facing edge, around the node line
        g.append(f'<path d="M{f(edge)} {f(ny - 16)}V{f(ny + 16)}" stroke="{col}" stroke-width="2.4" filter="{glow_s}"/>')
        g.append(corners(x - 5, t - 5, CARD_W + 10, h + 10, 12, col, 1.2, .55))

        # award shine
        if it["award"]:
            cid = d.uid("cc")
            d.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{f(t)}" width="{CARD_W}" height="{f(h)}" rx="14"/></clipPath>')
            sk = h * .36
            px = x - 200
            g.append(f'<g clip-path="url(#{cid})"><path class="shine" style="animation-delay:{3.6 + i * .7:.2f}s" '
                     f'd="M{f(px + sk)} {f(t)}h120l{f(-sk * 2)} {f(h)}h-120Z" fill="{shine_g}"/></g>')

        tx = x + PAD
        ys = it["ys"]
        # when
        wy = t + ys["when"]
        if it["when"] == "NOW":
            g.append(f'<circle cx="{tx + 5}" cy="{f(wy - 5)}" r="4.5" fill="{C["lime"]}" filter="{glow_s}" class="breathe"/>')
            g.append(d.text("NOW", tx + 18, wy, "mono-b", 14, C["lime"], tracking=3))
            g.append(d.text("· IN PROGRESS", tx + 18 + d.width("NOW", "mono-b", 14, 3) + 10, wy, "mono-b", 14, C["muted"], tracking=3))
        else:
            g.append(d.text(it["when"], tx, wy, "mono-b", 14, col, tracking=3))
        # kind + entry number (top right)
        tag = f'{KIND_LABEL.get(it["kind"], it["kind"].upper())}'
        num = f'{it["num"]:02d}'
        nw = d.width(num, "mono-b", 13, 2)
        g.append(d.text(num, x + CARD_W - PAD, wy, "mono-b", 13, C["soft"], "end", 2))
        g.append(d.text(tag, x + CARD_W - PAD - nw - 12, wy, "mono-m", 13, C["muted"], "end", 2.5))
        # title
        for k, line in enumerate(it["tl"]):
            g.append(d.text(line, tx, t + ys["title"][k], "sans-sb", 23, C["text"]))
        if it["kind"] == "writing":
            lw = d.width(it["tl"][-1], "sans-sb", 23)
            g.append(f'<rect x="{f(tx + lw + 6)}" y="{f(t + ys["title"][-1] - 18)}" width="9" height="21" fill="{col}" class="blink"/>')
        for k, line in enumerate(it["ol"]):
            g.append(d.text(line, tx, t + ys["org"][k], "sans", 18, C["soft"]))
        # hairline rule
        ry = t + ys["org"][-1] + 12
        g.append(f'<path d="M{tx} {f(ry)}h{TW if not it["medal"] else TW - 118}" stroke="{C["line2"]}" stroke-dasharray="2 4"/>')
        g.append(f'<path d="M{tx} {f(ry)}h28" stroke="{col}" stroke-width="1.4"/>')
        for k, line in enumerate(it["dl"]):
            g.append(d.text(line, tx, t + ys["detail"][k], "sans", 17, C["soft"], attrs='fill-opacity=".74"'))

        if it["medal"]:
            g.append(medal(d, x + CARD_W - PAD - 46, t + h / 2 + 12, glow_m))
        g.append("</g>")
        out.extend(g)

        kt = ping_at(ny)
        k0, k1 = max(kt - .002, .001), min(kt + .09, .999)
        # awards: an anamorphic flare streaks out of the node as the pulse hits it
        if it["award"]:
            fx = SX - sgn * 160
            kf = min(kt + .1, .999)
            out.append(f'<g opacity="0" style="mix-blend-mode:screen">'
                       f'<ellipse cx="{f(SX)}" cy="{f(ny)}" rx="270" ry="2.4" fill="{GOLD}" filter="url(#soft)"/>'
                       f'<ellipse cx="{f(SX)}" cy="{f(ny)}" rx="360" ry=".8" fill="#fff" opacity=".7"/>'
                       f'<ellipse cx="{f(fx)}" cy="{f(ny)}" rx="40" ry="16" fill="{GOLD}" opacity=".35" filter="url(#halo)"/>'
                       f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k0:.4f};{kt:.4f};{kf:.4f};1" dur="{PULSE_DUR}s" begin="{PULSE_BEGIN}s" repeatCount="indefinite"/></g>')

        # node
        out.append(node(d, SX, ny, it, col, col2, node_delay, glow_s))
        # ping when the pulse passes
        out.append(f'<circle cx="{SX}" cy="{f(ny)}" r="18" stroke="{col}" stroke-width="1.6" fill="none" opacity="0">'
                   f'<animate attributeName="r" values="18;18;18;40;40" keyTimes="0;{k0:.4f};{kt:.4f};{k1:.4f};1" dur="{PULSE_DUR}s" begin="{PULSE_BEGIN}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0;.95;0;0" keyTimes="0;{k0:.4f};{kt:.4f};{k1:.4f};1" dur="{PULSE_DUR}s" begin="{PULSE_BEGIN}s" repeatCount="indefinite"/></circle>')
        # connector flash
        k2 = min(kt + .05, .999)
        out.append(f'<path d="M{f(edge)} {f(ny)}H{f(nx0)}" stroke="#fff" stroke-width="1.6" opacity="0" filter="{glow_s}">'
                   f'<animate attributeName="opacity" values="0;0;.9;0;0" keyTimes="0;{k0:.4f};{kt:.4f};{k2:.4f};1" dur="{PULSE_DUR}s" begin="{PULSE_BEGIN}s" repeatCount="indefinite"/></path>')

    # ---- ORIGIN terminal ------------------------------------------------------------
    ty = spine_end
    od = .3 + 2.3
    out.append(f'<g class="pop" style="animation-delay:{od:.2f}s">'
               f'<path d="M{SX - 9} {f(ty)}h18M{SX - 5} {f(ty + 6)}h10M{SX - 2} {f(ty + 12)}h4" stroke="{C["magenta"]}" stroke-width="1.6" stroke-linecap="round"/></g>')
    out.append(f'<g class="fi" style="animation-delay:{od + .2:.2f}s">'
               f'{d.text("ORIGIN", SX + 26, ty + 9, "mono-b", 13, C["magenta"], tracking=3)}'
               f'{d.text("· KOTHARI INTERNATIONAL SCHOOL, NOIDA", SX + 26 + d.width("ORIGIN", "mono-b", 13, 3) + 10, ty + 9, "mono", 13, C["muted"], tracking=2)}</g>')

    # ---- atmosphere ---------------------------------------------------------------
    out.append(f'<rect width="{W}" height="{H}" fill="url(#scanlines)"/>')
    out.append(f'<rect class="scan" x="0" y="0" width="{W}" height="160" fill="{lin(d, "scanG", [(0, C["cyan"], 0), (.7, C["cyan"], .025), (.9, C["cyan"], .05), (1, C["cyan"], 0)], 0, 0, 0, 1)}"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="{vign}"/>')
    out.append(grain(d, .09))

    # ---- header readouts (kinds legend left, counts right) ------------------------
    out.append(f'<g class="fi" style="animation-delay:.9s">')
    lg = [("role", "ROLE", C["cyan"]), ("award", "AWARD", GOLD), ("writing", "WRITING", C["violet"]), ("edu", "EDUCATION", C["ice"])]
    for k, (kind, lab, cc) in enumerate(lg):
        cx_ = 72 + (k % 2) * 140
        cy_ = 82 + (k // 2) * 28
        out.append(icon(kind, cx_, cy_, cc, .95))
        out.append(d.text(lab, cx_ + 16, cy_ + 4.6, "mono-m", 13, C["muted"], tracking=2.5))
    roles = sum(1 for it in items if it["kind"] == "role")
    awards = sum(1 for it in items if it["kind"] == "award")
    stats = [(f"{len(items):02d}", "ENTRIES"), (f"{roles:02d}", "ROLES"), (f"{awards:02d}", "AWARDS")]
    sx_ = W - 60
    for k, (v, lab) in enumerate(reversed(stats)):
        lw_ = max(d.width(lab, "mono-m", 13, 2.5), d.width(v, "sans-l", 30, 2))
        out.append(d.text(v, sx_, 98, "sans-l", 30, C["text"] if lab != "AWARDS" else GOLD, "end", 2))
        out.append(d.text(lab, sx_, 120, "mono-m", 13, C["muted"], "end", 2.5))
        sx_ -= lw_ + 34
    out.append("</g>")

    # ---- letterbox ------------------------------------------------------------------
    out.append(f'<rect class="barT" width="{W}" height="{BAR}" fill="#000"/>')
    out.append(f'<rect class="barB" y="{H - BAR}" width="{W}" height="{BAR}" fill="#000"/>')
    out.append(f'<line x1="0" y1="{BAR}" x2="{W}" y2="{BAR}" stroke="{C["line"]}"/>')
    out.append(f'<line x1="0" y1="{H - BAR}" x2="{W}" y2="{H - BAR}" stroke="{C["line"]}"/>')
    ty_ = BAR / 2 + 5
    out.append(f'<g class="fi" style="animation-delay:1.0s">')
    out.append(d.text("SCENE 05", 34, ty_, "mono-b", 13, C["text"], tracking=3))
    out.append(d.text("— MISSION LOG", 34 + d.width("SCENE 05", "mono-b", 13, 3) + 12, ty_, "mono", 13, C["muted"], tracking=3))
    span_txt = "2023 → NOW"
    out.append(d.text(span_txt, W - 34, ty_, "mono-b", 13, C["text"], "end", 3))
    sw = d.width(span_txt, "mono-b", 13, 3)
    out.append(d.text("LOG SPAN", W - 34 - sw - 14, ty_, "mono", 13, C["muted"], "end", 3))
    out.append("</g>")
    by2 = H - BAR / 2 + 5
    out.append(f'<g class="fi" style="animation-delay:1.2s">')
    out.append(d.text("28.5355°N 77.3910°E  NOIDA  →  12.9692°N 79.1559°E  VELLORE", 34, by2, "mono", 12.5, C["muted"], tracking=2.2))
    status = "PLAYBACK: NEWEST FIRST"
    stw = d.width(status, "mono-m", 12.5, 2.4)
    rwx, rwy = W - 34 - stw - 16, by2 - 4.5          # rewind glyph: two left-pointing triangles
    out.append(f'<path d="M{f(rwx)} {f(rwy - 5)}l-7 5l7 5ZM{f(rwx - 8)} {f(rwy - 5)}l-7 5l7 5Z" fill="{C["ice"]}" class="breathe"/>')
    out.append(d.text(status, W - 34, by2, "mono-m", 12.5, C["ice"], "end", 2.4))
    out.append("</g>")

    out.append(f'<g class="fi" style="animation-delay:.8s">{corners(26, BAR + 16, W - 52, H - 2 * BAR - 32, 22, C["cyan"], 1.4, .6)}</g>')
    out.append("</g>")
    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" stroke="{C["line2"]}" fill="none"/>')
    return d


def ghost(d, items, glow_s):
    """ENTRY 10 — not logged yet. Dashed, redacted, stamped CLASSIFIED; it hangs
    off the NOW node on the side the first card leaves empty."""
    gs = 1 - items[0]["side"]
    gx = LX if gs == 0 else RX
    gt = TOP0 + 2
    gh = GHOST_H
    gedge = gx + CARD_W if gs == 0 else gx
    ny = items[0]["ny"]
    sgn = 1 if gs == 0 else -1
    lime, red = C["lime"], C["red"]
    o = []
    # marching dashed link from the NOW node
    o.append(f'<path d="M{f(SX - 19 * sgn)} {f(ny)}H{f(gedge)}" stroke="{lime}" stroke-width="1.3" stroke-dasharray="3 5" opacity=".7" class="fi" style="animation-delay:.9s">'
             f'<animate attributeName="stroke-dashoffset" values="0;-16" dur="1.2s" repeatCount="indefinite"/></path>')
    cls = "sr" if gs == 0 else "sl"
    o.append(f'<g class="{cls}" style="animation-delay:.75s">')
    o.append(f'<rect x="{gx}" y="{f(gt)}" width="{CARD_W}" height="{f(gh)}" rx="14" fill="{C["night"]}" fill-opacity=".72"/>')
    o.append(f'<rect x="{gx + .5}" y="{f(gt + .5)}" width="{CARD_W - 1}" height="{f(gh - 1)}" rx="14" stroke="{lime}" stroke-opacity=".45" stroke-dasharray="5 6"/>')
    tx = gx + PAD
    y1, y2 = gt + 30, gt + 62
    o.append(d.text("NEXT", tx, y1, "mono-b", 14, lime, tracking=3))
    o.append(d.text("· IN DEVELOPMENT", tx + d.width("NEXT", "mono-b", 14, 3) + 10, y1, "mono-b", 14, C["muted"], tracking=3))
    # CLASSIFIED stamp
    st = "CLASSIFIED"
    sw_ = d.width(st, "mono-b", 13, 3)
    scx, scy = gx + CARD_W - PAD - sw_ / 2 - 10, y1 - 4.5
    o.append(f'<g transform="rotate(-4 {f(scx)} {f(scy)})" class="breathe">'
             f'<rect x="{f(scx - sw_ / 2 - 10)}" y="{f(scy - 12)}" width="{f(sw_ + 20)}" height="24" rx="3" stroke="{red}" stroke-width="1.5" fill="{red}" fill-opacity=".08"/>'
             f'{d.text(st, scx, scy + 4.6, "mono-b", 13, red, "middle", 3)}</g>')
    o.append(d.text("Riley", tx, y2, "sans-sb", 23, C["text"]))
    rw = d.width("Riley", "sans-sb", 23)
    sub = "a Jarvis-grade personal AI for Android"
    o.append(d.text(sub, tx + rw + 14, y2, "sans", 18, C["soft"]))
    # redaction bars fill the rest of the line
    bx = tx + rw + 14 + d.width(sub, "sans", 18) + 14
    for k, bw in enumerate([46, 28, 54]):
        if bx + bw > gx + CARD_W - PAD:
            break
        o.append(f'<rect x="{f(bx)}" y="{f(y2 - 14)}" width="{bw}" height="16" rx="2" fill="{C["line2"]}">'
                 f'<animate attributeName="opacity" values=".9;.45;.9" dur="{3.2 + k * .7:.1f}s" repeatCount="indefinite"/></rect>')
        bx += bw + 8
    o.append("</g>")
    return "".join(o)


def node(d, x, y, it, col, col2, delay, glow_s):
    award = it["award"]
    parts = [f'<g class="pop" style="animation-delay:{delay:.2f}s">',
             f'<circle cx="{x}" cy="{f(y)}" r="22" fill="{col}" opacity=".16" filter="url(#halo)"/>',
             f'<circle cx="{x}" cy="{f(y)}" r="19" stroke="{col2}" stroke-opacity=".45" stroke-width="1"/>',
             f'<circle cx="{x}" cy="{f(y)}" r="15" fill="{C["void"]}" stroke="{col}" stroke-width="1.6"/>',
             f'<g filter="{glow_s}">{icon(it["kind"], x, y, col, .82)}</g>']
    if award:
        parts.append(f'<circle cx="{x}" cy="{f(y)}" r="25" stroke="{col}" stroke-width="1.2" stroke-dasharray="1.5 5.2" opacity=".8">'
                     f'<animateTransform attributeName="transform" type="rotate" values="0 {x} {f(y)};360 {x} {f(y)}" dur="18s" repeatCount="indefinite"/></circle>')
    parts.append("</g>")
    return "".join(parts)


def medal(d, cx, cy, glow_m):
    """AIR 01 — All India Rank 1."""
    o = [f'<circle cx="{f(cx)}" cy="{f(cy)}" r="44" fill="{GOLD}" opacity=".18" filter="url(#halo)" class="breathe"/>',
         f'<circle cx="{f(cx)}" cy="{f(cy)}" r="47" stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="1.5 5" opacity=".7">'
         f'<animateTransform attributeName="transform" type="rotate" values="0 {f(cx)} {f(cy)};-360 {f(cx)} {f(cy)}" dur="26s" repeatCount="indefinite"/></circle>']
    # laurel: leaves along two arcs
    for side in (-1, 1):
        for k in range(6):
            a = math.radians(90 + side * (38 + k * 21))
            r = 54
            lx, ly = cx + r * math.cos(a), cy + r * math.sin(a)
            rot = math.degrees(a) + (90 if side > 0 else -90) + side * 28
            o.append(f'<ellipse cx="{f(lx)}" cy="{f(ly)}" rx="2.6" ry="6.2" fill="{GOLD}" opacity="{.85 - k * .1:.2f}" transform="rotate({f(rot)} {f(lx)} {f(ly)})"/>')
    fill = rad(d, d.uid("mf"), [(0, GOLD, .32), (.7, GOLD, .08), (1, C["void"], .9)], cx=.5, cy=.35, r=.7)
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="38" fill="{C["void"]}"/>')
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="38" fill="{fill}" stroke="{GOLD}" stroke-width="2" filter="{glow_m}"/>')
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="32" stroke="{GOLD}" stroke-opacity=".45"/>')
    o.append(f'<path d="{star_d(cx, cy - 22, 5, 2.1)}" fill="{GOLD_HI}"/>')
    # glints twinkling around the medal
    for k, (ang, rr, sz, dur) in enumerate([(-35, 66, 5.5, 3.1), (200, 64, 4.2, 4.3), (130, 68, 3.6, 3.7), (-150, 62, 3.2, 5.2), (40, 70, 3.8, 4.6)]):
        a = math.radians(ang)
        gx_, gy_ = cx + rr * math.cos(a), cy + rr * math.sin(a)
        s_ = sz
        sp = (f"M{f(gx_)} {f(gy_ - s_)}Q{f(gx_)} {f(gy_)} {f(gx_ + s_)} {f(gy_)}Q{f(gx_)} {f(gy_)} {f(gx_)} {f(gy_ + s_)}"
              f"Q{f(gx_)} {f(gy_)} {f(gx_ - s_)} {f(gy_)}Q{f(gx_)} {f(gy_)} {f(gx_)} {f(gy_ - s_)}Z")
        o.append(f'<path d="{sp}" fill="{GOLD_HI}" opacity=".2"><animate attributeName="opacity" values=".15;1;.15" dur="{dur}s" begin="{k * .6:.1f}s" repeatCount="indefinite"/></path>')
    o.append(d.text("AIR", cx, cy - 4, "mono-b", 13, GOLD, "middle", 3))
    o.append(d.text("01", cx, cy + 25, "sans-b", 30, "url(#medalG)", "middle", 1))
    return "".join(o)


if __name__ == "__main__":
    build().save("mission-log.svg")
