"""Closing card: the README footer.

Letterboxed end-of-film frame, everything centred: THANKS FOR WATCHING, a large
TO BE CONTINUED… (stroke-drawn, then filled, with a slow shimmer), the tag line,
the ARROW—GHOST studio lockup with a tiny precessing Bloch-arrow, and the
post-credits teaser for Riley, its description under amber redaction bars that
glitch now and then. Drifting stars, nebula and the hero's grid floor behind.

Run standalone:  python build_credits.py   ->  assets/credits.svg
"""

import math

from agfx import C, Doc, Font, blur, corners, f, glow, lin, panel, rad, signature, stars
from content import CREDITS_TAG

W, H = 1280, 600
BAR = 34                         # panel() letterbox bar height
PT, PB = BAR, H - BAR            # picture area

# ---- the end card, centred -------------------------------------------------
RC = W / 2
TITLE_S = 62
AMBER = C["amber"]


def P(x, y):
    return f"{f(x)} {f(y)}"


# ------------------------------------------------------------- bloch logo --
def bloch_logo(d, cx, cy, R, sig):
    tilt = .3
    o = [f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R * 1.9)}" fill="{rad(d, "logoAura", [(0, C["violet"], .45), (.5, C["violet"], .1), (1, C["violet"], 0)])}" class="breathe"/>',
         f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R)}" fill="{rad(d, "logoF", [(0, C["violet"], .18), (.7, C["violet"], .05), (1, C["cyan"], .2)], cx=.4, cy=.36, r=.62)}" stroke="{C["ice"]}" stroke-opacity=".55" stroke-width="1.1"/>',
         f'<path d="M{P(cx - R, cy)}A{f(R)} {f(R * tilt)} 0 0 1 {P(cx + R, cy)}" stroke="{C["muted"]}" stroke-dasharray="1.5 3" opacity=".8"/>',
         f'<path d="M{P(cx - R, cy)}A{f(R)} {f(R * tilt)} 0 0 0 {P(cx + R, cy)}" stroke="{C["ice"]}" stroke-width="1" opacity=".7"/>',
         f'<line x1="{f(cx)}" y1="{f(cy - R - 5)}" x2="{f(cx)}" y2="{f(cy + R + 5)}" stroke="{C["muted"]}" stroke-dasharray="1.5 3" opacity=".7"/>']
    # turning meridian
    o.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(R)}" ry="{f(R)}" stroke="{C["cyan"]}" stroke-width=".9" opacity=".45">'
             f'<animate attributeName="rx" values="{f(R)};0;{f(R)}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines=".37 0 .63 1;.37 0 .63 1"/></ellipse>')
    # tick ring
    rr = R + 8
    tk = []
    for k in range(36):
        a = math.radians(k * 10)
        r2 = rr + (4 if k % 9 == 0 else 2)
        tk.append(f"M{P(cx + rr * math.cos(a), cy + rr * math.sin(a))}L{P(cx + r2 * math.cos(a), cy + r2 * math.sin(a))}")
    o.append(f'<g stroke="{C["cyan"]}" stroke-width="1" opacity=".5"><path d="{"".join(tk)}"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {P(cx, cy)}" to="360 {P(cx, cy)}" dur="40s" repeatCount="indefinite"/></g>')
    # precessing state vector
    th = math.radians(48)
    pts = []
    for i in range(49):
        ph = 2 * math.pi * i / 48
        pts.append((cx + R * math.sin(th) * math.cos(ph), cy - R * math.cos(th) + R * math.sin(th) * math.sin(ph) * tilt))
    xs = ";".join(f(p[0]) for p in pts)
    ys = ";".join(f(p[1]) for p in pts)
    o.append(f'<ellipse cx="{f(cx)}" cy="{f(cy - R * math.cos(th))}" rx="{f(R * math.sin(th))}" ry="{f(R * math.sin(th) * tilt)}" stroke="{C["magenta"]}" stroke-dasharray="1 3" opacity=".6"/>')
    o.append(f'<line x1="{f(cx)}" y1="{f(cy)}" x2="{f(pts[0][0])}" y2="{f(pts[0][1])}" stroke="{sig}" stroke-width="2" stroke-linecap="round" filter="url(#glow)">'
             f'<animate attributeName="x2" values="{xs}" dur="8s" repeatCount="indefinite"/><animate attributeName="y2" values="{ys}" dur="8s" repeatCount="indefinite"/></line>')
    o.append(f'<circle r="2.8" fill="{C["magenta"]}" filter="url(#glow)"><animate attributeName="cx" values="{xs}" dur="8s" repeatCount="indefinite"/>'
             f'<animate attributeName="cy" values="{ys}" dur="8s" repeatCount="indefinite"/></circle>')
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="1.8" fill="{C["ice"]}"/>')
    return "".join(o)


# ------------------------------------------------------------ the end card --
def title(d, sig, y_base):
    """TO BE CONTINUED… — vector letters, stroke-drawn then filled, with a shimmer."""
    txt, size, tr = "TO BE CONTINUED…", TITLE_S, 9
    fo = Font.get("sans-xl")
    tw = fo.width(txt, size, tr)
    x0 = RC - tw / 2
    letters = list(fo.letters(txt, x0, y_base, size, tr))
    all_d = "".join(p for _, p, _, _ in letters)
    d.defs.append(f'<clipPath id="tbcClip"><path d="{all_d}"/></clipPath>')
    o = [f'<path d="{all_d}" fill="{C["violet"]}" opacity=".5" filter="url(#glowBig)" class="fi" style="animation-delay:1.5s"/>']
    for i, (ch, p, lx, adv) in enumerate(letters):
        dl = .45 + i * .06
        if ch == "…":     # the ellipsis keeps breathing: the story isn't over
            o.append(f'<path d="{p}" pathLength="1" class="l ell" stroke="{sig}" stroke-width="1.3" style="animation-delay:{dl:.2f}s,{dl + 1.0:.2f}s,3.6s"/>')
        else:
            o.append(f'<path d="{p}" pathLength="1" class="l" stroke="{sig}" stroke-width="1.3" style="animation-delay:{dl:.2f}s,{dl + 1.0:.2f}s"/>')
    # shimmer: a soft parallelogram of light sliding through the glyphs
    top, bot = y_base - size * .9, y_base + size * .2
    sk = (bot - top) * .38
    sx = x0 - 160
    shine = lin(d, "shineG", [(0, "#fff", 0), (.5, "#fff", .9), (1, "#fff", 0)])
    o.append(f'<g clip-path="url(#tbcClip)"><path class="shine" d="M{P(sx + sk, top)}h70l{f(-sk)} {f(bot - top)}h-70z" fill="{shine}"/>'
             f'<path class="shine2" d="M{P(sx + sk, top)}h26l{f(-sk)} {f(bot - top)}h-26z" fill="{C["ice"]}" opacity=".55"/></g>')
    return "".join(o), x0, tw


def overline(d, s, y, sig):
    size, tr = 14, 6
    w = d.width(s, "mono-m", size, tr)
    o = d.text(s, RC, y, "mono-m", size, C["ice"], "middle", tr)
    ly = y - 5
    o += (f'<line x1="{f(RC - w / 2 - 70)}" y1="{f(ly)}" x2="{f(RC - w / 2 - 20)}" y2="{f(ly)}" stroke="{sig}" stroke-width="1.5"/>'
          f'<line x1="{f(RC + w / 2 + 20)}" y1="{f(ly)}" x2="{f(RC + w / 2 + 70)}" y2="{f(ly)}" stroke="{sig}" stroke-width="1.5"/>')
    return o


def lockup(d, cy, sig):
    """ARROW—GHOST studio lockup: Bloch-arrow logo + wordmark + file number."""
    R = 21
    word, ws, wt = "ARROW—GHOST", 24, 7
    sub, ss, st = "OPERATOR FILE 077-098-116", 12.5, 3.2
    ww = d.width(word, "mono-b", ws, wt)
    sw = d.width(sub, "mono", ss, st)
    tw = max(ww, sw)
    total = 2 * (R + 12) + 18 + tw
    lx = RC - total / 2 + R + 12
    tx = lx + R + 12 + 18
    o = [f'<g class="fi" style="animation-delay:1.9s;animation-duration:1.6s">{bloch_logo(d, lx, cy, R, sig)}</g>',
         f'<g class="sl" style="animation-delay:2.0s">',
         d.text(word, tx, cy + 4, "mono-b", ws, sig, tracking=wt),
         d.text(sub, tx + 1, cy + 24, "mono", ss, C["muted"], tracking=st),
         "</g>"]
    return "".join(o)


def teaser(d, x, y, w, h):
    """POST-CREDITS SCENE: RILEY — description redacted; the bars glitch now and then."""
    o = [f'<g class="r" style="animation-delay:2.3s">']
    o.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14" fill="{C["night"]}" fill-opacity=".78"/>')
    o.append(f'<rect x="{f(x + .5)}" y="{f(y + .5)}" width="{f(w - 1)}" height="{f(h - 1)}" rx="14" stroke="{AMBER}" stroke-opacity=".5" stroke-dasharray="5 6">'
             f'<animate attributeName="stroke-dashoffset" values="0;-22" dur="2.2s" repeatCount="indefinite"/></rect>')
    o.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="14" fill="{rad(d, "tzGlow", [(0, AMBER, .10), (1, AMBER, 0)], cx=.12, cy=0, r=.9)}"/>')
    px = x + 26
    # header
    hy = y + 36
    o.append(f'<path d="M{P(px, hy - 11)}l9 5.5l-9 5.5z" fill="{AMBER}"/>')
    lab = "POST-CREDITS SCENE:"
    o.append(d.text(lab, px + 18, hy, "mono-b", 14, AMBER, tracking=3))
    lw = d.width(lab, "mono-b", 14, 3)
    o.append(d.text("RILEY", px + 18 + lw + 12, hy + 1, "sans-sb", 22, C["text"], tracking=5))
    o.append(f'<line x1="{f(px)}" y1="{f(y + 54)}" x2="{f(x + w - 26)}" y2="{f(y + 54)}" stroke="{AMBER}" stroke-opacity=".22"/>')
    # redacted description: the real words sit underneath the bars (seen only when they glitch)
    lines = ["A Jarvis-grade personal AI for Android.", "Codename RILEY. Clearance required."]
    by = [y + 90, y + 122]
    WG = 9                                    # word gap, wide enough for the bars to read as separate
    under, layers = [], []
    n0 = len(lines[0].split(" "))
    for li, (s, yy) in enumerate(zip(lines, by)):
        bars, cx = [], px
        for word in s.split(" "):
            ww = d.width(word, "sans", 19)
            under.append(d.text(word, cx, yy, "sans", 19, C["ice"]))
            bars.append((cx - 2, ww + 4))
            cx += ww + WG
        rects = "".join(f'<rect x="{f(bx)}" y="{f(yy - 16)}" width="{f(bw)}" height="20" rx="2"/>' for bx, bw in bars)
        layers.append(f'<g class="gc{li}" fill="{C["cyan"]}">{rects}</g><g class="gm{li}" fill="{C["magenta"]}">{rects}</g>'
                      f'<g class="rd{li}" fill="{AMBER}">{rects}</g>')
    o.append(f'<g class="ux0">{"".join(under[:n0])}</g><g class="ux1">{"".join(under[n0:])}</g>' + "".join(layers))
    # footer: status + the CLASSIFIED stamp pressed into the corner
    fy = y + h - 22
    o.append(f'<circle cx="{f(px + 4)}" cy="{f(fy - 4.5)}" r="3.6" fill="{C["lime"]}" class="breathe"/>')
    o.append(d.text("IN DEVELOPMENT", px + 16, fy, "mono-m", 12.5, C["lime"], tracking=2.6))
    st = "[CLASSIFIED]"
    sw = d.width(st, "mono-b", 13, 2.4)
    scx, scy = x + w - 26 - sw / 2 - 10, fy - 5
    o.append(f'<g transform="rotate(-5 {P(scx, scy)})"><g class="breathe">'
             f'<rect x="{f(scx - sw / 2 - 10)}" y="{f(scy - 13)}" width="{f(sw + 20)}" height="26" rx="3" stroke="{C["red"]}" stroke-width="1.5" fill="{C["red"]}" fill-opacity=".08"/>'
             f'{d.text(st, scx, scy + 4.6, "mono-b", 13, C["red"], "middle", 2.4)}</g></g>')
    o.append("</g>")
    return "".join(o)


CSS = """
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes fillIn{from{fill-opacity:0}to{fill-opacity:1}}
@keyframes shine{0%{transform:translateX(0)}38%,100%{transform:translateX(980px)}}
@keyframes ell{0%,100%{opacity:1}50%{opacity:.35}}
@keyframes rd{0%,88%,100%{transform:translate(0,0);opacity:1}88.8%{transform:translate(-5px,0);opacity:.2}89.8%{transform:translate(6px,0);opacity:.85}90.8%{transform:translate(-2px,0);opacity:.1}92%{transform:translate(0,0);opacity:1}}
@keyframes gc{0%,88%,92%,100%{opacity:0;transform:translate(0,0)}88.8%{opacity:.7;transform:translate(-9px,-1px)}90.8%{opacity:.5;transform:translate(4px,1px)}}
@keyframes gm{0%,88%,92%,100%{opacity:0;transform:translate(0,0)}88.8%{opacity:.7;transform:translate(8px,1px)}90.8%{opacity:.5;transform:translate(-5px,0)}}
@keyframes ux{0%,88%,92%,100%{opacity:0}88.8%{opacity:.9}89.8%{opacity:.25}90.8%{opacity:1}}
@keyframes credScan{from{transform:translateY(-140px)}to{transform:translateY(760px)}}
.l{fill:#ECEFFB;stroke-dasharray:1;animation:draw 1.6s cubic-bezier(.6,.05,.25,1) both,fillIn 1.2s ease both}
.ell{animation:draw 1.6s cubic-bezier(.6,.05,.25,1) both,fillIn 1.2s ease both,ell 2.8s 3.4s ease-in-out infinite}
.shine{animation:shine 7s 3.2s infinite cubic-bezier(.45,0,.35,1)}
.shine2{animation:shine 7s 3.32s infinite cubic-bezier(.45,0,.35,1)}
.rd0{animation:rd 8.5s 4s infinite}
.rd1{animation:rd 10.5s 6.2s infinite}
.gc0{opacity:0;animation:gc 8.5s 4s infinite}.gm0{opacity:0;animation:gm 8.5s 4s infinite}
.gc1{opacity:0;animation:gc 10.5s 6.2s infinite}.gm1{opacity:0;animation:gm 10.5s 6.2s infinite}
.ux0{opacity:0;animation:ux 8.5s 4s infinite}.ux1{opacity:0;animation:ux 10.5s 6.2s infinite}
@keyframes bars{from{transform:scaleY(3.2)}to{transform:scaleY(1)}}
.barT,.barB{animation:bars 1.6s cubic-bezier(.7,0,.2,1) both}
.barT{transform-origin:0 0}.barB{transform-origin:0 100%;transform-box:fill-box}
.scan{animation:credScan 9s linear infinite}
"""


def build():
    d = Doc(W, H, title="Closing card — Shrish Verma. To be continued…")
    d.css.append(CSS)
    sig = signature(d, "sig", animate=True, dur=7)
    glow(d, "glow", std=3, strength=2)
    glow(d, "glowBig", std=12, strength=1)
    blur(d, "neb", 70)
    blur(d, "flareBlur", 9)

    op, cl = panel(d, W, H, grain_op=.08)
    out = d.body
    out.append(op)

    # ---- nebula --------------------------------------------------------------
    out.append('<g filter="url(#neb)">')
    for (x, y, rx_, ry_, col, opa, dx, dy, dur) in [
        (250, 470, 360, 150, C["violet"], .5, 50, -20, 27),
        (1080, 120, 330, 130, C["cyan"], .26, -50, 22, 31),
        (900, 540, 320, 110, C["magenta"], .26, -60, -10, 23),
        (980, 420, 220, 90, AMBER, .10, 30, -12, 19),
        (520, 80, 240, 80, "#3B4BFF", .26, 40, 20, 29),
    ]:
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx_}" ry="{ry_}" fill="{col}" opacity="{opa}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                   f'<animate attributeName="opacity" values="{opa};{opa * .55:.2f};{opa}" dur="{dur * .7:.1f}s" repeatCount="indefinite"/></ellipse>')
    out.append("</g>")

    # ---- stars drifting slowly upward (parallax) ------------------------------
    for seed, n, rmax, dur, opa in [(31, 120, 1.0, 160, .6), (37, 40, 1.6, 95, .85)]:
        layer = stars(seed, n, W, H, rmax=rmax, twinkle=True)
        out.append(f'<g opacity="{opa}"><g>{layer}<g transform="translate(0 {H})">{layer}</g>'
                   f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 -{H}" dur="{dur}s" repeatCount="indefinite"/></g></g>')

    # ---- perspective grid floor (the hero's floor, seen again at the end) ----
    horizon = 474
    d.defs.append(f'<mask id="gridMask" maskUnits="userSpaceOnUse" x="0" y="{horizon}" width="{W}" height="{PB - horizon}"><rect y="{horizon}" width="{W}" height="{PB - horizon}" fill="{lin(d, "gm", [(0, "#fff", 0), (.35, "#fff", .5), (1, "#fff", .15)], 0, 0, 0, 1)}"/></mask>')
    gl_ = []
    for i in range(-24, 25):
        gl_.append(f'<line x1="{f(W / 2 + i * 7)}" y1="{horizon}" x2="{f(W / 2 + i * 110)}" y2="{PB}"/>')
    rows = []
    for k in range(7):
        yy = horizon + ((k / 7) ** 2.1) * (PB - horizon)
        rows.append(f'<line x1="0" y1="{f(yy)}" x2="{W}" y2="{f(yy)}"/>')
    out.append(f'<g mask="url(#gridMask)" stroke="{C["cyan"]}" stroke-width="1" opacity=".42">{"".join(gl_)}'
               f'<g>{"".join(rows)}<animateTransform attributeName="transform" type="translate" values="0 0;0 13" dur="1.8s" repeatCount="indefinite"/></g></g>')
    hz = lin(d, "hzG", [(0, C["cyan"], 0), (.2, C["cyan"], 1), (.8, C["cyan"], 1), (1, C["cyan"], 0)])
    out.append(f'<rect x="0" y="{horizon - .5}" width="{W}" height="1" fill="{hz}" opacity=".45"/>'
               f'<rect x="0" y="{horizon - 2}" width="{W}" height="4" fill="{hz}" opacity=".3" filter="url(#flareBlur)"/>')

    # ---- projector spill: a soft pool of light behind the card --------------
    out.append(f'<ellipse cx="{RC}" cy="200" rx="460" ry="190" fill="{rad(d, "spill", [(0, C["ice"], .07), (.55, C["violet"], .05), (1, C["violet"], 0)])}"/>')

    # ---- the end card -------------------------------------------------------------
    out.append(f'<g class="r" style="animation-delay:.25s">{overline(d, "THANKS FOR WATCHING", 96, sig)}</g>')
    t_markup, tx0, tw = title(d, sig, 176)
    out.append(t_markup)
    out.append(f'<g class="r" style="animation-delay:1.6s">{d.text(CREDITS_TAG, RC, 218, "sans", 19, C["soft"], "middle")}</g>')
    # hairline between the end card and the studio lockup
    out.append(f'<g class="fi" style="animation-delay:1.8s"><rect x="{RC - 200}" y="245.5" width="400" height="1" fill="{lin(d, "divG", [(0, C["line2"], 0), (.5, C["line2"], 1), (1, C["line2"], 0)])}"/>'
               f'<path d="M{P(RC, 242)}l4 4l-4 4l-4 -4z" fill="{C["violet"]}"/></g>')
    out.append(lockup(d, 290, sig))
    out.append(teaser(d, RC - 270, 338, 540, 176))

    # anamorphic flare across the title, now and then
    fy = 176 - TITLE_S * .36
    out.append(f'<g class="flare" style="mix-blend-mode:screen">'
               f'<ellipse cx="{RC}" cy="{f(fy)}" rx="300" ry="2.4" fill="{C["ice"]}" filter="url(#flareBlur)"/>'
               f'<ellipse cx="{RC}" cy="{f(fy)}" rx="460" ry=".9" fill="#fff" opacity=".85"/>'
               f'<circle cx="{RC}" cy="{f(fy)}" r="5" fill="#fff" filter="url(#flareBlur)"/></g>')
    d.css.append("@keyframes flare{0%{transform:translateX(-700px);opacity:0}6%{opacity:1}22%{opacity:1}30%{transform:translateX(700px);opacity:0}100%{transform:translateX(700px);opacity:0}}"
                 ".flare{opacity:0;animation:flare 11s 2.6s infinite cubic-bezier(.5,0,.5,1)}")

    # ---- scan band + HUD --------------------------------------------------------
    out.append(f'<rect class="scan" x="0" y="0" width="{W}" height="120" fill="{lin(d, "scanG", [(0, C["cyan"], 0), (.7, C["cyan"], .035), (.9, C["cyan"], .07), (1, C["cyan"], 0)], 0, 0, 0, 1)}"/>')
    out.append(f'<g class="fi" style="animation-delay:1.0s">{corners(26, PT + 16, W - 52, PB - PT - 32, 22, C["cyan"], 1.4, .7)}</g>')
    out.append(cl)
    d.defs.append(f'<clipPath id="frameClip"><rect width="{W}" height="{H}" rx="20"/></clipPath>')
    out.append(f'<g clip-path="url(#frameClip)"><rect class="barT" width="{W}" height="{BAR}" fill="#000"/><rect class="barB" y="{H - BAR}" width="{W}" height="{BAR}" fill="#000"/>'
               f'<line x1="0" y1="{BAR}" x2="{W}" y2="{BAR}" stroke="{C["line"]}"/><line x1="0" y1="{H - BAR}" x2="{W}" y2="{H - BAR}" stroke="{C["line"]}"/></g>'
               f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" stroke="{C["line2"]}" fill="none"/>')

    # ---- slate bars -----------------------------------------------------------------
    ty = BAR / 2 + 5
    out.append('<g class="fi" style="animation-delay:1.2s">')
    out.append(d.text("FIN", 34, ty, "mono-b", 13, C["text"], tracking=3))
    out.append(d.text("— CLOSING CARD", 34 + d.width("FIN", "mono-b", 13, 3) + 12, ty, "mono", 13, C["muted"], tracking=3))
    out.append(d.text("END OF REEL", W - 34, ty, "mono", 12.5, C["muted"], "end", 3))
    by2 = H - BAR / 2 + 5
    out.append(d.text("© 2026 SHRISH VERMA", 34, by2, "mono-m", 12.5, C["soft"], tracking=2.6))
    out.append(d.text("12.9692°N  79.1559°E  ·  VELLORE, IN", W - 34, by2, "mono", 12.5, C["muted"], "end", 2.4))
    out.append("</g>")
    return d


if __name__ == "__main__":
    build().save("credits.svg")
