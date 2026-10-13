"""Call-to-action pills: btn-linkedin.svg, btn-email.svg, btn-play.svg.

Dark glass capsules (viewBox 400 x 84; the README shows them ~200 px wide side
by side, so every label is >= 22 px in viewBox units). Each has a signature-
gradient hairline with a comet of light running round it, a glass sheen that
sweeps across now and then, an original line icon in a HUD badge, and a tracked
mono label. The PLAY pill swaps to a lime accent and carries a pulsing LIVE dot.

Icons are drawn from scratch: the LinkedIn badge is a generic "in" monogram in
a rounded square (outline strokes), not the trademark logo.
"""

from agfx import C, Doc, blur, f, glow, grain, lin, rad
from content import BUTTONS

W, H = 400, 84
PX, PY = 3, 3                       # pill inset so the outer glow isn't clipped
PW, PH = W - 2 * PX, H - 2 * PY
PR = PH / 2
CY = H / 2
IC = PX + PR                        # icon badge centre x (concentric with the left cap)
LAB_SIZE, LAB_TR = 22, 1.6

CSS = """
@keyframes bDraw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes bComet{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
@keyframes bHead{from{stroke-dashoffset:82}to{stroke-dashoffset:-18}}
@keyframes bSheen{0%{transform:translateX(-160px) skewX(-24deg)}28%,100%{transform:translateX(520px) skewX(-24deg)}}
@keyframes bSpin{to{transform:rotate(360deg)}}
@keyframes bNudge{0%,60%,100%{transform:translate(0,0)}75%{transform:translate(2px,-2px)}}
.bB{stroke-dasharray:1;animation:bDraw 1.3s cubic-bezier(.6,.05,.25,1) both}
.bC{stroke-dasharray:24 76;animation:bComet 4.8s linear infinite}
.bH{stroke-dasharray:5 95;animation:bHead 4.8s linear infinite}
.bS{animation:bSheen 7s ease-in-out infinite;transform:translateX(-160px)}
.bR{transform-box:fill-box;transform-origin:50% 50%;animation:bSpin 18s linear infinite}
.bN{animation:bNudge 3.6s ease-in-out infinite}
"""


def icon(kind, cx, cy, col):
    sw = 2
    if kind == "linkedin":
        x0, y0, s = cx - 12, cy - 12, 24
        return (f'<rect x="{f(x0)}" y="{f(y0)}" width="{s}" height="{s}" rx="6" stroke="{col}" stroke-width="{sw}"/>'
                f'<circle cx="{f(cx - 5.5)}" cy="{f(cy - 6)}" r="1.7" fill="{col}"/>'
                f'<path d="M{f(cx - 5.5)} {f(cy - 2)}V{f(cy + 6.5)}M{f(cx - 0.5)} {f(cy + 6.5)}V{f(cy - 2)}'
                f'M{f(cx - 0.5)} {f(cy + 1.5)}C{f(cx - 0.5)} {f(cy - 1.2)} {f(cx + 1.6)} {f(cy - 2.4)} {f(cx + 3.4)} {f(cy - 2.4)}'
                f'C{f(cx + 5.6)} {f(cy - 2.4)} {f(cx + 6.5)} {f(cy - 0.8)} {f(cx + 6.5)} {f(cy + 1.8)}V{f(cy + 6.5)}" '
                f'stroke="{col}" stroke-width="{sw + .3}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')
    if kind == "email":
        x0, y0, w, h = cx - 13, cy - 9.5, 26, 19
        return (f'<rect x="{f(x0)}" y="{f(y0)}" width="{w}" height="{h}" rx="3.5" stroke="{col}" stroke-width="{sw}"/>'
                f'<path d="M{f(x0 + 2)} {f(y0 + 3)}L{f(cx)} {f(cy + 2.5)}L{f(x0 + w - 2)} {f(y0 + 3)}" stroke="{col}" '
                f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')
    # play
    return (f'<path d="M{f(cx - 5)} {f(cy - 9.5)}L{f(cx + 9.5)} {f(cy)}L{f(cx - 5)} {f(cy + 9.5)}Z" fill="{col}" '
            f'stroke="{col}" stroke-width="3" stroke-linejoin="round"/>')


def build(kind, label):
    play = kind == "play"
    acc = {"linkedin": C["cyan"], "email": C["magenta"], "play": C["lime"]}[kind]
    d = Doc(W, H, title={"linkedin": "LinkedIn — Shrish Verma", "email": "Email Shrish Verma",
                         "play": "Play Quantum Maze (live)"}[kind])
    d.css.append(CSS)
    glow(d, "bg1", std=2.6, strength=2)
    glow(d, "bg2", std=6, strength=1)
    blur(d, "bsoft", 1.4)
    blur(d, "bneb", 16)

    # border gradient: signature (lime-led on the play pill), drifting
    stops = ([(0, C["lime"]), (.5, C["cyan"]), (1, C["violet"])] if play
             else [(0, C["cyan"]), (.5, C["violet"]), (1, C["magenta"])])
    d.defs.append('<linearGradient id="bsig" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">'
                  + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
                  + '<animate attributeName="x1" values="-1;0;-1" dur="6s" repeatCount="indefinite"/>'
                    '<animate attributeName="x2" values="1;2;1" dur="6s" repeatCount="indefinite"/></linearGradient>')
    d.defs.append(f'<clipPath id="pill"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="{f(PR)}"/></clipPath>')
    glass = lin(d, "glass", [(0, "#1A2046"), (.45, "#0C0F21"), (1, "#05060D")], 0, 0, 0, 1)
    out = d.body

    # ---- glass body ---------------------------------------------------------------
    out.append('<g class="fi" style="animation-duration:.8s">')
    out.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="{f(PR)}" fill="{glass}"/>')
    out.append('<g clip-path="url(#pill)">')
    # accent light pooled behind the icon, and a faint counter-glow on the right
    out.append(f'<g filter="url(#bneb)"><ellipse cx="{f(IC)}" cy="{f(CY)}" rx="62" ry="34" fill="{acc}" opacity=".30">'
               f'<animate attributeName="opacity" values=".30;.16;.30" dur="5s" repeatCount="indefinite"/></ellipse>'
               f'<ellipse cx="{W - 70}" cy="{H + 6}" rx="120" ry="22" fill="{C["violet"]}" opacity=".22"/></g>')
    if not any('id="scanlines"' in x for x in d.defs):
        d.defs.append('<pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".03"/></pattern>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#scanlines)"/>')
    # rim light along the top of the glass + a faint floor reflection
    rim = lin(d, "rim", [(0, "#fff", 0), (.25, "#fff", .28), (.75, "#fff", .28), (1, "#fff", 0)])
    out.append(f'<rect x="{f(PR * .7)}" y="{PY + 1.5}" width="{f(W - PR * 1.4)}" height="1" fill="{rim}"/>')
    hl = lin(d, "hl", [(0, "#fff", .07), (1, "#fff", 0)], 0, 0, 0, 1)
    out.append(f'<rect x="{PX}" y="{PY}" width="{PW}" height="{f(PH * .48)}" fill="{hl}"/>')
    # glass sheen sweep
    sheen = lin(d, "sheen", [(0, "#fff", 0), (.5, "#fff", .13), (1, "#fff", 0)])
    out.append(f'<rect class="bS" style="animation-delay:{2.0 + {"linkedin": 0, "email": .7, "play": 1.4}[kind]:.1f}s" '
               f'x="0" y="-10" width="90" height="{H + 20}" fill="{sheen}"/>')
    out.append('</g>')
    out.append(f'<rect x="{PX + 2.5}" y="{PY + 2.5}" width="{PW - 5}" height="{PH - 5}" rx="{f(PR - 2.5)}" stroke="#fff" stroke-opacity=".06"/>')
    out.append('</g>')

    # ---- border: hairline drawn on, then the comet loops round it --------------------
    rect_attrs = f'x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="{f(PR)}"'
    out.append(f'<rect {rect_attrs} pathLength="1" class="bB" stroke="url(#bsig)" stroke-width="1.5" opacity=".9"/>')
    comet_col = C["lime"] if play else acc
    cd = {"linkedin": 0, "email": -1.6, "play": -3.2}[kind]
    out.append(f'<g class="fi" style="animation-delay:1.1s">'
               f'<rect {rect_attrs} pathLength="100" class="bC" style="animation-delay:{cd}s" stroke="{comet_col}" stroke-width="2.2" stroke-linecap="round" opacity=".75" filter="url(#bg1)"/>'
               f'<rect {rect_attrs} pathLength="100" class="bH" style="animation-delay:{cd}s" stroke="#fff" stroke-width="2.4" stroke-linecap="round" filter="url(#bg1)"/></g>')

    # ---- icon badge ---------------------------------------------------------------------
    br = PR - 11
    out.append(f'<g class="fi" style="animation-delay:.25s">')
    out.append(f'<circle cx="{f(IC)}" cy="{f(CY)}" r="{f(br)}" fill="{acc}" fill-opacity=".07" stroke="{acc}" stroke-opacity=".45"/>')
    # slow HUD reticle ring
    out.append(f'<circle class="bR" cx="{f(IC)}" cy="{f(CY)}" r="{f(br + 4)}" stroke="{acc}" stroke-opacity=".55" stroke-width="1" '
               f'stroke-dasharray="2 5.4" fill="none"/>')
    out.append(f'<g filter="url(#bg1)">{icon(kind, IC, CY, acc)}</g>')
    out.append('</g>')

    # ---- right element: arrow chip, or LIVE dot -------------------------------------------
    rcx = W - PX - PR + 3
    if play:
        rcx += 4
        out.append(f'<g class="fi" style="animation-delay:.9s">'
                   + "".join(f'<circle cx="{f(rcx)}" cy="{f(CY)}" r="5" stroke="{C["lime"]}" stroke-width="1.5" fill="none" opacity="0">'
                             f'<animate attributeName="r" values="5;16" dur="2.4s" begin="{b}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keySplines=".2 .6 .4 1"/>'
                             f'<animate attributeName="opacity" values=".9;0" dur="2.4s" begin="{b}s" repeatCount="indefinite"/></circle>' for b in (0, 1.2)) +
                   f'<circle cx="{f(rcx)}" cy="{f(CY)}" r="5.2" fill="{C["lime"]}" filter="url(#bg2)" class="breathe"/>'
                   f'<circle cx="{f(rcx)}" cy="{f(CY)}" r="3" fill="#EFFFF6"/></g>')
        right_edge = rcx - 18
    else:
        out.append(f'<g class="fi" style="animation-delay:.9s">'
                   f'<circle cx="{f(rcx)}" cy="{f(CY)}" r="15" stroke="{C["line2"]}" fill="#000" fill-opacity=".25"/>'
                   f'<g class="bN"><path d="M{f(rcx - 4.5)} {f(CY + 4.5)}L{f(rcx + 4.5)} {f(CY - 4.5)}M{f(rcx - 2.5)} {f(CY - 4.5)}H{f(rcx + 4.5)}V{f(CY + 2.5)}" '
                   f'stroke="{C["text"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/></g></g>')
        right_edge = rcx - 22

    # ---- label ------------------------------------------------------------------------------
    left_edge = IC + br + 12
    lw = d.width(label, "mono-b", LAB_SIZE, LAB_TR)
    lx = (left_edge + right_edge) / 2 - lw / 2
    ly = CY + LAB_SIZE * .66 / 2
    if play:
        w_play = d.width("PLAY ", "mono-b", LAB_SIZE, LAB_TR) + LAB_TR
        lab = (d.text("PLAY", lx, ly, "mono-b", LAB_SIZE, C["lime"], tracking=LAB_TR)
               + d.text(label[5:], lx + w_play, ly, "mono-b", LAB_SIZE, C["text"], tracking=LAB_TR))
    else:
        lab = d.text(label, lx, ly, "mono-b", LAB_SIZE, C["text"], tracking=LAB_TR)
    out.append(f'<g class="sr" style="animation-delay:.45s">{lab}</g>')
    print(f"  {kind}: label {lx:.0f}..{lx + lw:.0f}  (room {left_edge:.0f}..{right_edge:.0f})")
    return d


if __name__ == "__main__":
    for kind, label, _url in BUTTONS:
        build(kind, label).save(f"btn-{kind}.svg")
