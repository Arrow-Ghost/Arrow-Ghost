"""Chapter title cards: the slim film-title strips placed between README sections.

One card per entry in content.SECTIONS (h-01.svg ... h-06.svg). They are built
as one series: identical grid and choreography, and each card takes its hue
from its position along the signature cyan -> violet -> magenta sweep, so
scrolling the profile walks the whole gradient.

Anatomy (viewBox 1280 x 132):
  left   tiny CHAPTER label over a big outlined numeral (vector paths) that is
         stroke-drawn in the signature gradient, then faintly filled; a light
         pulse keeps tracing its outline and it ghost-glitches now and then
  centre the title (per-letter rise) with a "// subtitle" typed on underneath,
         then a hairline rule running to the right edge with a slow glint
  right  SEQUENCE label, "02 / 06" index and a 6-segment progress bar
"""

import math
import random

from agfx import C, Doc, Font, blur, corners, f, glow, grain, lin, rad, stars
from content import SECTIONS
from fontTools.pens.boundsPen import BoundsPen

W, H = 1280, 132
RX = 16
M = 44                     # side margin
ROW1, ROW2, ROW3 = 36, 66, 97   # baselines: micro labels / title + index / subtitle + bars

# signature stops
SIG = [(0.0, C["cyan"]), (0.5, C["violet"]), (1.0, C["magenta"])]


def _hex(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    ra, rb = _hex(a), _hex(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ra, rb))


def sig_at(t):
    """Colour at position t (0..1) along the signature gradient."""
    if t <= 0.5:
        return mix(C["cyan"], C["violet"], t / 0.5)
    return mix(C["violet"], C["magenta"], (t - 0.5) / 0.5)


def ink(fo, ch):
    bp = BoundsPen(fo.glyphs)
    fo.glyphs[fo.gname(ch)].draw(bp)
    return bp.bounds  # xmin, ymin, xmax, ymax in font units


def numeral(text, x, base, size, gap):
    """Digits placed by their ink (Source Sans digits are tabular, so '01'
    would look gappy) — returns ([(path_d, x0, x1)], right_edge)."""
    fo = Font.get("sans-xl")
    s = size / fo.upm
    out, cx = [], x
    for ch in text:
        x0, _, x1, _ = ink(fo, ch)
        ox = cx - x0 * s
        out.append((fo.glyph_path(ch, ox, base, size), cx, cx + (x1 - x0) * s))
        cx += (x1 - x0) * s + gap
    return out, cx - gap


CSS = """
@keyframes hdDraw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes hdFill{from{fill-opacity:0}to{fill-opacity:.2}}
@keyframes hdTrace{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes hdGrowX{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes hdGrowY{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes hdCaret{0%,24%{opacity:1}25%,49%{opacity:0}50%,74%{opacity:1}75%,100%{opacity:0}}
@keyframes hdGA{0%,90%,100%{transform:translate(0,0);opacity:0}91%{transform:translate(-5px,1px);opacity:.9}92.5%{transform:translate(4px,-1px);opacity:.7}94%{transform:translate(-1px,0);opacity:.4}95%{transform:translate(0,0);opacity:0}}
@keyframes hdGB{0%,90%,100%{transform:translate(0,0);opacity:0}91%{transform:translate(5px,-1px);opacity:.9}92.5%{transform:translate(-4px,1px);opacity:.7}94%{transform:translate(1px,0);opacity:.4}95%{transform:translate(0,0);opacity:0}}
@keyframes hdShine{0%{transform:translateX(-200px) skewX(-22deg)}30%,100%{transform:translateX(900px) skewX(-22deg)}}
@keyframes hdChar{0%{opacity:0}1%{opacity:1;fill:#FFFFFF}100%{opacity:1}}
@keyframes hdLit{0%,100%{opacity:.75}50%{opacity:1}}
.hdN{stroke-dasharray:1;animation:hdDraw 1.5s cubic-bezier(.6,.05,.25,1) both,hdFill 1.2s ease both}
.hdT{stroke-dasharray:.07 .93;animation:hdTrace 7s linear infinite}
.hdGA{opacity:0;animation:hdGA 11s infinite;mix-blend-mode:screen}
.hdGB{opacity:0;animation:hdGB 11s infinite;mix-blend-mode:screen}
.hdRule{transform-box:fill-box;transform-origin:0 50%;animation:hdGrowX 1.3s cubic-bezier(.7,0,.2,1) both}
.hdDiv{transform-box:fill-box;transform-origin:50% 50%;animation:hdGrowY .9s cubic-bezier(.7,0,.2,1) both}
.hdCaret{animation:hdCaret 2.4s steps(1) both}
.hdShine{animation:hdShine 10s ease-in-out infinite;transform:translateX(-200px)}
.hdC{animation:hdChar .7s ease-out both}
.hdLit{animation:hdLit 3.2s ease-in-out infinite}
"""


def build(idx):
    num, title, sub = SECTIONS[idx]
    n_total = len(SECTIONS)
    t = idx / (n_total - 1)
    acc = sig_at(t)                       # this chapter's hue
    acc2 = sig_at(min(1, t + 0.25))
    d = Doc(W, H, title=f"Chapter {num} — {title.title()}")
    d.css.append(CSS)
    rnd = random.Random(100 + idx)

    glow(d, "hg", std=3.2, strength=2)
    glow(d, "hgBig", std=9, strength=1)
    blur(d, "hneb", 38)
    blur(d, "hsoft", 1.6)
    d.defs.append(f'<clipPath id="strip"><rect width="{W}" height="{H}" rx="{RX}"/></clipPath>')

    out = d.body
    out.append('<g clip-path="url(#strip)">')
    out.append(f'<rect width="{W}" height="{H}" fill="{C["void"]}"/>')

    # ---- nebula: the chapter hue pooled behind the numeral, a cooler field drifting right
    out.append('<g filter="url(#hneb)" class="fi" style="animation-duration:2s">')
    for (x, y, rx_, ry_, col, op, dx, dur) in [
        (110, 70, 210, 64, acc, .42, 30, 19),
        (520, 150, 380, 52, C["violet"], .22, -60, 27),
        (1130, -10, 300, 56, acc2, .20, -50, 23),
        (860, 132, 260, 40, C["magenta"] if t < .5 else C["cyan"], .10, 70, 31),
    ]:
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx_}" ry="{ry_}" fill="{col}" opacity="{op}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} 0;0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                   f'<animate attributeName="opacity" values="{op};{op * .6:.2f};{op}" dur="{dur * .7:.1f}s" repeatCount="indefinite"/></ellipse>')
    out.append('</g>')
    out.append(f'<g opacity=".55">{stars(31 + idx * 7, 46, W, H, rmax=1.1, twinkle=True)}</g>')

    # ---- huge ghost numeral bleeding off the right side (editorial depth) ----
    ghost_size = 290
    gx, gy = 770, 222
    gd = "".join(p for p, _, _ in numeral(num, gx, gy, ghost_size, 22)[0])
    gfade = lin(d, d.uid("gf"), [(0, acc, .0), (.25, acc, .55), (.6, acc, .25), (1, acc, 0)], 0, 0, 0, 1)
    out.append(f'<path d="{gd}" stroke="{gfade}" stroke-width="1" opacity=".5" class="fi" style="animation-delay:.4s;animation-duration:2.4s"/>')

    # ---- left: CHAPTER + numeral ---------------------------------------------
    out.append(f'<g class="fi" style="animation-delay:.05s">'
               f'{d.text("CHAPTER", M, ROW1, "mono-b", 13, C["ice"], tracking=4.2)}</g>')
    lab_w = d.width("CHAPTER", "mono-b", 13, 4.2)
    nsize, nbase = 84, 112
    digits, nright = numeral(num, M - 1, nbase, nsize, 9)
    nleft = M - 1
    ng = d.uid("ng")
    d.defs.append(
        f'<linearGradient id="{ng}" gradientUnits="userSpaceOnUse" x1="{f(nleft)}" y1="0" x2="{f(nright)}" y2="0" spreadMethod="reflect">'
        + "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in SIG)
        + f'<animate attributeName="x1" values="{f(nleft)};{f(nleft - (nright - nleft))};{f(nleft)}" dur="8s" repeatCount="indefinite"/>'
        f'<animate attributeName="x2" values="{f(nright)};{f(nleft)};{f(nright)}" dur="8s" repeatCount="indefinite"/></linearGradient>')
    all_d = "".join(p for p, _, _ in digits)
    # halo
    out.append(f'<path d="{all_d}" fill="{acc}" opacity=".55" filter="url(#hgBig)" class="fi" style="animation-delay:1.3s;animation-duration:1.6s"/>')
    # RGB ghosts (the "ghost" in Arrow-Ghost)
    gdl = 5 + idx * 1.3
    out.append(f'<g class="hdGA" style="animation-delay:{gdl:.1f}s"><path d="{all_d}" fill="{C["cyan"]}" opacity=".8"/></g>')
    out.append(f'<g class="hdGB" style="animation-delay:{gdl:.1f}s"><path d="{all_d}" fill="{C["magenta"]}" opacity=".8"/></g>')
    for i, (p, _, _) in enumerate(digits):
        dl = .15 + i * .16
        out.append(f'<path d="{p}" pathLength="1" class="hdN" stroke="url(#{ng})" stroke-width="1.3" fill="url(#{ng})" '
                   f'stroke-linejoin="round" style="animation-delay:{dl:.2f}s,{dl + 1.0:.2f}s"/>')
    # light pulse tracing the outline forever
    out.append(f'<g class="fi" style="animation-delay:2.2s"><path d="{all_d}" pathLength="1" class="hdT" stroke="#fff" '
               f'stroke-width="1.6" stroke-linecap="round" filter="url(#hg)" style="animation-delay:-{idx * 1.1:.1f}s"/></g>')

    # ---- divider --------------------------------------------------------------
    col_r = max(lab_w + M, nright)
    dx_ = col_r + 30
    divg = lin(d, d.uid("dg"), [(0, acc, 0), (.5, acc, .9), (1, acc, 0)], 0, 0, 0, 1)
    out.append(f'<rect class="hdDiv" style="animation-delay:.45s" x="{f(dx_)}" y="22" width="1" height="{H - 44}" fill="{divg}"/>')
    out.append(f'<g class="fi" style="animation-delay:1.1s"><rect x="{f(dx_ - 1.5)}" y="{ROW2 - 13}" width="4" height="4" fill="{acc}" transform="rotate(45 {f(dx_ + .5)} {ROW2 - 11})" filter="url(#hg)"/></g>')

    # ---- title (vector letters, per-letter rise) --------------------------------
    tx = dx_ + 30
    tsize, ttrack = 38, 8.5
    fo = Font.get("sans-l")
    letters = list(fo.letters(title, tx, ROW2, tsize, ttrack))
    tw = fo.width(title, tsize, ttrack)
    tg = lin(d, d.uid("tg"), [(0, "#FFFFFF"), (1, "#C3C9E6")], 0, 0, 0, 1)
    t_all = "".join(p for _, p, _, _ in letters)
    tid = d.uid("tc")
    d.defs.append(f'<clipPath id="{tid}"><path d="{t_all}"/></clipPath>')
    out.append(f'<path d="{t_all}" fill="{acc}" opacity=".35" filter="url(#hgBig)" class="fi" style="animation-delay:1.4s"/>')
    for i, (ch, p, lx, adv) in enumerate(letters):
        out.append(f'<path d="{p}" fill="{tg}" class="r" style="animation-delay:{.55 + i * .035:.3f}s"/>')
    shine = lin(d, d.uid("sh"), [(0, "#fff", 0), (.5, "#fff", .9), (1, "#fff", 0)])
    out.append(f'<g clip-path="url(#{tid})"><rect class="hdShine" style="animation-delay:{3.2 + idx * .9:.1f}s" '
               f'x="{f(tx)}" y="{ROW2 - 34}" width="70" height="44" fill="{shine}"/></g>')

    # ---- subtitle, typed on ----------------------------------------------------
    s_size, s_tr = 18, 1.2
    pre = "// "
    s_all = pre + sub
    nchar = len(s_all)
    cw = Font.get("mono").advance("a", s_size) + s_tr
    per = .034
    t0 = 1.35
    type_dur = nchar * per
    chars = []
    for k, ch in enumerate(s_all):
        if ch == " ":
            continue
        is_pre = k < 2
        chars.append(d.text(ch, tx + k * cw, ROW3, "mono-b" if is_pre else "mono", s_size,
                            acc if is_pre else C["muted"], cls="hdC", attrs=f'style="animation-delay:{t0 + k * per:.3f}s"'))
    out.append("".join(chars))
    car_x0 = tx
    d.css.append(f"@keyframes hdType{{from{{transform:translateX(0)}}to{{transform:translateX({f(nchar * cw)}px)}}}}")
    out.append(f'<g style="animation:hdType {type_dur:.2f}s steps({nchar},jump-start) {t0}s both">'
               f'<rect x="{f(car_x0 + 1)}" y="{ROW3 - 14}" width="9" height="17" fill="{acc}" class="hdCaret" style="animation-delay:{t0 + type_dur:.2f}s"/></g>')

    # ---- right: SEQUENCE / index / progress ------------------------------------
    R = W - M
    i_size, i_tr = 22, 2
    tot = f"/ {n_total:02d}"
    w_num = d.width(num, "mono-b", i_size, i_tr)
    w_tot = d.width(tot, "mono", i_size, i_tr)
    gap_i = 10
    ix = R - w_num - w_tot - gap_i
    seg_w, seg_g = 28, 6
    bar_w = n_total * seg_w + (n_total - 1) * seg_g
    left_r = min(ix, R - bar_w)
    out.append(f'<g class="sl" style="animation-delay:1.5s">'
               f'{d.text("SEQUENCE", R, ROW1, "mono-b", 13, C["muted"], "end", 4.2)}'
               f'{d.text(num, ix, ROW2, "mono-b", i_size, C["text"], tracking=i_tr)}'
               f'{d.text(tot, ix + w_num + gap_i, ROW2, "mono", i_size, C["muted"], tracking=i_tr)}</g>')
    bx = R - bar_w
    by = ROW3 - 6
    segs = []
    for k in range(n_total):
        x = bx + k * (seg_w + seg_g)
        if k < idx:
            segs.append(f'<rect x="{f(x)}" y="{by}" width="{seg_w}" height="4" rx="2" fill="{sig_at(k / (n_total - 1))}" opacity=".42" class="fi" style="animation-delay:{1.7 + k * .08:.2f}s"/>')
        elif k == idx:
            lg = lin(d, d.uid("lg"), [(0, sig_at(max(0, t - .12))), (1, sig_at(min(1, t + .12)))])
            segs.append(f'<g class="fi" style="animation-delay:{1.7 + k * .08:.2f}s"><g class="hdLit">'
                        f'<rect x="{f(x - 2)}" y="{by - 2}" width="{seg_w + 4}" height="8" rx="4" fill="{acc}" opacity=".55" filter="url(#hgBig)"/>'
                        f'<rect x="{f(x)}" y="{by - .5}" width="{seg_w}" height="5" rx="2.5" fill="{lg}" filter="url(#hg)"/></g></g>')
        else:
            segs.append(f'<rect x="{f(x)}" y="{by}" width="{seg_w}" height="4" rx="2" fill="{C["line2"]}" class="fi" style="animation-delay:{1.7 + k * .08:.2f}s"/>')
    out.extend(segs)

    # ---- hairline rule with travelling glint -------------------------------------
    ra = tx + tw + 32
    rb = left_r - 32
    ry = ROW2 - 12.5
    rg = lin(d, d.uid("rg"), [(0, C["line2"], 0), (.08, C["line2"], 1), (.9, C["line2"], 1), (1, C["line2"], 0)])
    out.append(f'<rect class="hdRule" style="animation-delay:1.25s" x="{f(ra)}" y="{f(ry - .5)}" width="{f(rb - ra)}" height="1" fill="{rg}"/>')
    # micro ticks along the rule, like a film-edit timeline
    ticks = []
    step = 24
    k = 0
    xx = ra + 12
    while xx < rb - 10:
        hh = 5 if k % 5 == 0 else 2.5
        ticks.append(f'<rect x="{f(xx)}" y="{f(ry + 3)}" width="1" height="{hh}" fill="{C["dim"]}"/>')
        xx += step
        k += 1
    out.append(f'<g class="fi" style="animation-delay:1.9s" opacity=".7">{"".join(ticks)}</g>')
    # end marks
    out.append(f'<g class="fi" style="animation-delay:2.1s">'
               f'<path d="M{f(rb + 6)} {f(ry - 4)}l4 4l-4 4" stroke="{acc}" stroke-width="1.4" fill="none"/>'
               f'<circle cx="{f(ra - 6)}" cy="{f(ry)}" r="1.8" fill="{acc}"/></g>')
    # the glint (clipped to the rule so it never overshoots)
    gid = d.uid("gc")
    span = rb - ra
    d.defs.append(f'<clipPath id="{gid}"><rect x="{f(ra)}" y="{f(ry - 10)}" width="{f(span)}" height="20"/></clipPath>')
    glg = lin(d, d.uid("gl"), [(0, acc, 0), (.55, acc, .55), (.9, "#fff", 1), (1, "#fff", 0)])
    gdur = 6.5 + idx * .35
    out.append(f'<g clip-path="url(#{gid})"><g>'
               f'<rect x="-260" y="{f(ry - 1)}" width="260" height="2" fill="{glg}" filter="url(#hg)"/>'
               f'<ellipse cx="-10" cy="{f(ry)}" rx="70" ry="1.2" fill="#fff" opacity=".8"/>'
               f'<ellipse cx="-6" cy="{f(ry)}" rx="26" ry="6" fill="{acc}" opacity=".5" filter="url(#hsoft)"/>'
               f'<circle cx="-4" cy="{f(ry)}" r="2" fill="#fff" filter="url(#hsoft)"/>'
               f'<circle cx="-4" cy="{f(ry)}" r="1.3" fill="#fff"/>'
               f'<animateTransform attributeName="transform" type="translate" values="{f(ra)} 0;{f(rb + 270)} 0;{f(rb + 270)} 0" '
               f'keyTimes="0;.62;1" dur="{gdur:.2f}s" begin="{2.4 + idx * .5:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines=".55 0 .35 1;0 0 1 1"/>'
               f'</g></g>')

    # ---- frame dressing: scanlines, vignette, grain, HUD corners, border -----------
    if not any('id="scanlines"' in x for x in d.defs):
        d.defs.append('<pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".04"/></pattern>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#scanlines)"/>')
    vg = rad(d, d.uid("vg"), [(0, "#000", 0), (.7, "#000", 0), (1, "#000", .6)], r=.72)
    out.append(f'<rect width="{W}" height="{H}" fill="{vg}"/>')
    out.append(grain(d, .08, fid=d.uid("gr")))
    out.append(f'<g class="fi" style="animation-delay:.2s">{corners(10, 10, W - 20, H - 20, 9, acc, 1.2, .55)}</g>')
    out.append('</g>')
    # top edge light (glassy) + border
    eg = lin(d, d.uid("eg"), [(0, "#fff", 0), (.3, acc, .5), (.7, acc2, .5), (1, "#fff", 0)])
    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{RX}" stroke="{C["line2"]}" fill="none"/>')
    out.append(f'<rect x="{RX}" y=".5" width="{W - 2 * RX}" height="1" fill="{eg}" opacity=".7"/>')
    return d


if __name__ == "__main__":
    for i in range(len(SECTIONS)):
        build(i).save(f"h-{SECTIONS[i][0]}.svg")
