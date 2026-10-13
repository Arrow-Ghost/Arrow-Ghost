"""Hero: a cinematic title card.

Letterboxed frame, drifting nebula and parallax stars, a slowly turning Bloch
sphere whose state vector (the "arrow") precesses behind the name, the name
drawn stroke-first then filled, a chromatic "ghost" glitch, an anamorphic lens
flare, a live-looking REC timecode and HUD readouts.
"""

import math

from agfx import C, Doc, Font, blur, corners, f, glow, grain, lin, rad, signature, stars

W, H = 1280, 560
BAR = 38                      # letterbox bar height
CX, CY = W / 2, 262           # optical centre of the frame (above true centre — bars + subtitle)


def ket(doc, label, x, y, size, fill, font="mono"):
    """|label⟩ — Source Code Pro has no ⟩, so the closing angle is drawn."""
    fo = Font.get(font)
    t = doc.text("|" + label, x, y, font, size, fill)
    wdt = fo.width("|" + label, size)
    ax, top, bot = x + wdt + size * 0.08, y - size * 0.74, y + size * 0.16
    mid = (top + bot) / 2
    p = f'<path d="M{f(ax)} {f(top)}L{f(ax + size * 0.28)} {f(mid)}L{f(ax)} {f(bot)}" stroke="{fill}" stroke-width="{f(size * 0.075)}" fill="none" stroke-linecap="round"/>'
    return t + p


def build():
    d = Doc(W, H, title="Shrish Verma — Arrow-Ghost")
    sig = signature(d, "sig", animate=True, dur=7)
    glow(d, "glow", std=5, strength=2)
    glow(d, "glowBig", std=14, strength=1)
    blur(d, "neb", 70)
    blur(d, "flareBlur", 10)
    blur(d, "soft", 2.2)

    d.defs.append(f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    vign = rad(d, "vign", [(0, "#000", 0), (0.62, "#000", 0), (1, "#000", 0.85)], r=0.75)
    fade_x = lin(d, "fadeX", [(0, "#fff", 0), (0.18, "#fff", 1), (0.82, "#fff", 1), (1, "#fff", 0)])
    d.defs.append(f'<mask id="gridMask"><rect width="{W}" height="{H}" fill="{lin(d, "gm", [(0, "#fff", 0), (0.62, "#fff", 0), (0.78, "#fff", 0.55), (1, "#fff", 0.0)], 0, 0, 0, 1)}"/></mask>')
    d.defs.append(f'<mask id="edgeFade"><rect width="{W}" height="{H}" fill="{fade_x}"/></mask>')

    d.css.append("""
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
@keyframes fillIn{from{fill-opacity:0}to{fill-opacity:1}}
@keyframes bars{from{transform:scaleY(2.6)}to{transform:scaleY(1)}}
@keyframes ghostA{0%,86%,100%{transform:translate(0,0);opacity:0}87%{transform:translate(-7px,1px);opacity:.85}88.5%{transform:translate(5px,-2px);opacity:.7}90%{transform:translate(-2px,0);opacity:.5}91%{transform:translate(0,0);opacity:0}}
@keyframes ghostB{0%,86%,100%{transform:translate(0,0);opacity:0}87%{transform:translate(7px,-1px);opacity:.85}88.5%{transform:translate(-5px,2px);opacity:.7}90%{transform:translate(2px,0);opacity:.5}91%{transform:translate(0,0);opacity:0}}
@keyframes slice{0%,86%,92%,100%{opacity:0}87%,89%{opacity:1}}
@keyframes flare{0%{transform:translateX(-900px);opacity:0}6%{opacity:1}22%{opacity:1}30%{transform:translateX(900px);opacity:0}100%{transform:translateX(900px);opacity:0}}
@keyframes shine{0%{transform:translateX(-520px) skewX(-20deg)}35%,100%{transform:translateX(1500px) skewX(-20deg)}}
@keyframes heroScan{from{transform:translateY(-160px)}to{transform:translateY(720px)}}
@keyframes role{0%{opacity:0;transform:translateY(10px)}4%,18%{opacity:1;transform:translateY(0)}22%,100%{opacity:0;transform:translateY(-10px)}}
.l{fill:#ECEFFB;stroke-dasharray:1;animation:draw 1.7s cubic-bezier(.6,.05,.25,1) both,fillIn 1.2s ease both}
.gA{opacity:0;animation:ghostA 7s 3.2s infinite;mix-blend-mode:screen}
.gB{opacity:0;animation:ghostB 7s 3.2s infinite;mix-blend-mode:screen}
.slc{opacity:0;animation:slice 7s 3.2s infinite}
.flare{opacity:0;animation:flare 9s 2.4s infinite cubic-bezier(.5,0,.5,1)}
.shine{animation:shine 6.5s 3.6s infinite ease-in-out;transform:translateX(-520px)}
.scan{animation:heroScan 7.5s linear infinite}
.role{opacity:0;animation:role 12.5s infinite;transform-box:fill-box}
.role0{opacity:1}
.barT,.barB{animation:bars 1.6s cubic-bezier(.7,0,.2,1) both}
.barT{transform-origin:0 0}.barB{transform-origin:0 100%}
""")

    out = d.body
    out.append('<g clip-path="url(#frame)">')
    out.append(f'<rect width="{W}" height="{H}" fill="{C["void"]}"/>')

    # ---- nebula: slow-breathing colour fields --------------------------------
    out.append('<g filter="url(#neb)">')
    for (x, y, rx, ry, col, op, dx, dy, dur) in [
        (250, 430, 380, 170, C["violet"], .55, 60, -20, 26),
        (1060, 150, 360, 150, C["cyan"], .32, -50, 25, 31),
        (840, 520, 300, 110, C["magenta"], .30, -70, -10, 23),
        (520, 90, 260, 90, "#3B4BFF", .28, 40, 20, 29),
    ]:
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                   f'<animate attributeName="opacity" values="{op};{op * .55:.2f};{op}" dur="{dur * .7:.1f}s" repeatCount="indefinite"/></ellipse>')
    out.append("</g>")

    # ---- parallax star layers (seamless horizontal loop) ---------------------
    for seed, n, rmax, dur, op in [(7, 150, 1.0, 240, .7), (11, 60, 1.5, 140, .9), (23, 18, 2.1, 90, 1)]:
        layer = stars(seed, n, W, H, rmax=rmax, twinkle=True)
        out.append(f'<g opacity="{op}"><g>{layer}<g transform="translate({W} 0)">{layer}</g>'
                   f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="{dur}s" repeatCount="indefinite"/></g></g>')

    # ---- perspective grid floor ---------------------------------------------
    horizon, vpx = 395, CX
    g = []
    for i in range(-22, 23):
        x2 = vpx + i * 120
        g.append(f'<line x1="{vpx + i * 6}" y1="{horizon}" x2="{x2}" y2="{H}" />')
    rows = []
    for k in range(9):
        t = (k / 9) ** 2.1
        y = horizon + t * (H - horizon)
        rows.append(f'<line x1="0" y1="{f(y)}" x2="{W}" y2="{f(y)}"/>')
    out.append(f'<g mask="url(#gridMask)" stroke="{C["cyan"]}" stroke-width="1" opacity=".38">{"".join(g)}'
               f'<g>{"".join(rows)}<animateTransform attributeName="transform" type="translate" values="0 0;0 18" dur="1.6s" repeatCount="indefinite"/></g></g>')
    out.append(f'<line x1="0" y1="{horizon}" x2="{W}" y2="{horizon}" stroke="{C["cyan"]}" stroke-width="1" opacity=".5" mask="url(#edgeFade)"/>')
    out.append(f'<line x1="0" y1="{horizon}" x2="{W}" y2="{horizon}" stroke="{C["cyan"]}" stroke-width="4" opacity=".35" filter="url(#flareBlur)" mask="url(#edgeFade)"/>')

    # ---- Bloch sphere behind the name: the qubit's arrow ----------------------
    R, by = 178, CY - 6
    tilt = 0.27
    sph = [f'<g opacity=".0" class="fi" style="animation-delay:.3s;animation-duration:2.5s">',
           f'<g opacity=".5">',
           f'<circle cx="{CX}" cy="{by}" r="{R}" stroke="{C["line2"]}" stroke-width="1.2" fill="{rad(d, "sphFill", [(0, C["violet"], .10), (0.7, C["violet"], .03), (1, C["cyan"], .10)], cx=.42, cy=.38, r=.6)}"/>',
           # back half of the equator (dashed) / front half (solid)
           f'<path d="M{CX - R} {by} A{R} {R * tilt} 0 0 1 {CX + R} {by}" stroke="{C["muted"]}" stroke-width="1" stroke-dasharray="3 6" opacity=".7"/>',
           f'<path d="M{CX - R} {by} A{R} {R * tilt} 0 0 0 {CX + R} {by}" stroke="{C["ice"]}" stroke-width="1.1" opacity=".55"/>',
           f'<line x1="{CX}" y1="{by - R - 18}" x2="{CX}" y2="{by + R + 18}" stroke="{C["muted"]}" stroke-dasharray="2 5" opacity=".7"/>']
    # turning meridians — ellipses whose rx swings to fake a rotating globe
    for ph in range(3):
        sph.append(f'<ellipse cx="{CX}" cy="{by}" rx="{R}" ry="{R}" stroke="{C["cyan"]}" stroke-width="1" opacity=".35">'
                   f'<animate attributeName="rx" values="{R};0;{R}" keyTimes="0;.5;1" dur="9s" begin="-{ph * 3}s" repeatCount="indefinite" calcMode="spline" keySplines=".37 0 .63 1;.37 0 .63 1"/></ellipse>')
    # latitude rings
    for lat in (-0.55, 0.55):
        yy = by - R * lat
        rr = R * math.sqrt(1 - lat * lat)
        sph.append(f'<ellipse cx="{CX}" cy="{f(yy)}" rx="{f(rr)}" ry="{f(rr * tilt)}" stroke="{C["line2"]}" stroke-width="1" opacity=".8"/>')
    sph.append("</g>")
    # precessing state vector
    theta = math.radians(52)
    pts = []
    for i in range(49):
        phi = 2 * math.pi * i / 48
        x = CX + R * math.sin(theta) * math.cos(phi)
        y = by - R * math.cos(theta) + R * math.sin(theta) * math.sin(phi) * tilt
        pts.append((x, y))
    xs = ";".join(f(p[0]) for p in pts)
    ys = ";".join(f(p[1]) for p in pts)
    # precession cone ring
    sph.append(f'<ellipse cx="{CX}" cy="{f(by - R * math.cos(theta))}" rx="{f(R * math.sin(theta))}" ry="{f(R * math.sin(theta) * tilt)}" stroke="{C["magenta"]}" stroke-width="1" stroke-dasharray="1 5" opacity=".55"/>')
    sph.append(f'<line x1="{CX}" y1="{by}" x2="{f(pts[0][0])}" y2="{f(pts[0][1])}" stroke="{sig}" stroke-width="2.4" stroke-linecap="round" opacity=".95" filter="url(#glow)">'
               f'<animate attributeName="x2" values="{xs}" dur="12s" repeatCount="indefinite"/>'
               f'<animate attributeName="y2" values="{ys}" dur="12s" repeatCount="indefinite"/></line>')
    sph.append(f'<circle r="5" fill="{C["magenta"]}" filter="url(#glow)"><animate attributeName="cx" values="{xs}" dur="12s" repeatCount="indefinite"/>'
               f'<animate attributeName="cy" values="{ys}" dur="12s" repeatCount="indefinite"/></circle>')
    sph.append(f'<circle cx="{CX}" cy="{by}" r="3" fill="{C["ice"]}"/>')
    sph.append(ket(d, "0", CX + 12, by - R - 4, 17, C["ice"]))
    sph.append(ket(d, "1", CX + 12, by + R + 18, 17, C["muted"]))
    sph.append("</g>")
    out.extend(sph)

    # ---- the name -------------------------------------------------------------
    name, size, track = "SHRISH VERMA", 98, 27
    fo = Font.get("sans-l")
    tw = fo.width(name, size, track)
    x0, base = CX - tw / 2, CY + 34
    letters = list(fo.letters(name, x0, base, size, track))
    all_d = "".join(p for _, p, _, _ in letters)

    d.defs.append(f'<clipPath id="nameClip"><path d="{all_d}"/></clipPath>')
    # soft halo behind the type
    out.append(f'<path d="{all_d}" fill="{C["violet"]}" opacity=".45" filter="url(#glowBig)" class="fi" style="animation-delay:1.6s"/>')
    # ghost copies (RGB split)
    out.append(f'<g class="gA"><path d="{all_d}" fill="{C["cyan"]}"/></g>')
    out.append(f'<g class="gB"><path d="{all_d}" fill="{C["magenta"]}"/></g>')
    # letters: stroke draw, then fill
    for i, (ch, p, lx, adv) in enumerate(letters):
        dl = .25 + i * .075
        out.append(f'<path d="{p}" pathLength="1" class="l" stroke="{sig}" stroke-width="1.6" '
                   f'style="animation-delay:{dl:.2f}s,{dl + 1.15:.2f}s"/>')
    # shine sweep clipped to the type
    out.append(f'<g clip-path="url(#nameClip)"><rect class="shine" x="0" y="{base - size}" width="110" height="{size * 1.3}" '
               f'fill="{lin(d, "shineG", [(0, "#fff", 0), (.5, "#fff", .85), (1, "#fff", 0)])}"/></g>')
    # glitch slices: thin horizontal bars that tear across during the ghost moment
    for (yy, hh, dx) in [(base - 62, 7, 18), (base - 30, 4, -24), (base - 12, 3, 12)]:
        out.append(f'<g class="slc"><rect x="{f(x0 - 20 + dx)}" y="{yy}" width="{f(tw + 40)}" height="{hh}" fill="{C["cyan"]}" opacity=".35"/></g>')

    # ---- overline + role rotator ---------------------------------------------
    over = "ARROW—GHOST  ·  OPERATOR FILE 077-098-116"
    out.append(f'<g class="r" style="animation-delay:.2s">{d.text(over, CX, base - size - 26, "mono-m", 14.5, C["ice"], "middle", 4.2)}</g>')
    ow = d.width(over, "mono-m", 14.5, 4.2)
    out.append(f'<g class="r" style="animation-delay:.35s"><line x1="{f(CX - ow / 2 - 64)}" y1="{f(base - size - 31)}" x2="{f(CX - ow / 2 - 18)}" y2="{f(base - size - 31)}" stroke="{sig}" stroke-width="1.5"/>'
               f'<line x1="{f(CX + ow / 2 + 18)}" y1="{f(base - size - 31)}" x2="{f(CX + ow / 2 + 64)}" y2="{f(base - size - 31)}" stroke="{sig}" stroke-width="1.5"/></g>')

    ry = base + 56
    prefix = "BUILDING AT THE EDGE OF"
    roles = ["CYBERSECURITY", "QUANTUM COMPUTING", "ARTIFICIAL INTELLIGENCE", "EMBEDDED & IoT", "FULL-STACK WEB"]
    pw = d.width(prefix, "mono", 17, 3.2)
    maxr = max(d.width(r, "mono-b", 17, 3.2) for r in roles)
    total = pw + 40 + maxr
    rx0 = CX - total / 2
    rx_role = rx0 + pw + 40
    out.append(f'<g class="r" style="animation-delay:2.0s">{d.text(prefix, rx0, ry, "mono", 17, C["soft"], tracking=3.2)}'
               f'<path d="M{f(rx_role - 25)} {ry - 12}l7 6l-7 6" stroke="{C["cyan"]}" stroke-width="2" fill="none"/></g>')
    out.append(f'<g class="fi" style="animation-delay:2.2s">')
    n = len(roles)
    for i, r in enumerate(roles):
        col = [C["magenta"], C["violet"], C["cyan"], C["lime"], C["ice"]][i]
        rc = "role role0" if i == 0 else "role"
        out.append(f'<g class="{rc}" style="animation-delay:{2.3 + i * 2.5:.1f}s">{d.text(r, rx_role, ry, "mono-b", 17, col, tracking=3.2)}</g>')
    out.append("</g>")

    # credentials line
    cred = "B.TECH CSE @ VIT VELLORE  ·  IEEE JUNIOR CORE  ·  WEB DEV — IEEE ITC INDIA 2026"
    out.append(f'<g class="r" style="animation-delay:2.4s">{d.text(cred, CX, ry + 36, "sans-sb", 15, C["muted"], "middle", 2.6)}</g>')

    # ---- anamorphic lens flare --------------------------------------------------
    fy = base - size * .36
    out.append(f'<g class="flare" style="mix-blend-mode:screen">'
               f'<ellipse cx="{CX}" cy="{f(fy)}" rx="420" ry="3" fill="{C["ice"]}" filter="url(#flareBlur)"/>'
               f'<ellipse cx="{CX}" cy="{f(fy)}" rx="640" ry="1.1" fill="#fff" opacity=".9"/>'
               f'<ellipse cx="{CX}" cy="{f(fy)}" rx="60" ry="26" fill="{C["cyan"]}" opacity=".55" filter="url(#flareBlur)"/>'
               f'<circle cx="{CX}" cy="{f(fy)}" r="6" fill="#fff" filter="url(#soft)"/>'
               f'<circle cx="{CX - 180}" cy="{f(fy)}" r="14" fill="{C["violet"]}" opacity=".35" filter="url(#soft)"/>'
               f'<circle cx="{CX + 260}" cy="{f(fy)}" r="22" fill="{C["magenta"]}" opacity=".18" filter="url(#soft)"/></g>')

    # ---- scan band + scanlines + vignette + grain ------------------------------
    d.defs.append('<pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".045"/></pattern>')
    out.append(f'<rect width="{W}" height="{H}" fill="url(#scanlines)"/>')
    out.append(f'<rect class="scan" x="0" y="0" width="{W}" height="120" fill="{lin(d, "scanG", [(0, C["cyan"], 0), (.7, C["cyan"], .045), (.9, C["cyan"], .09), (1, C["cyan"], 0)], 0, 0, 0, 1)}"/>')
    out.append(f'<rect width="{W}" height="{H}" fill="{vign}"/>')
    out.append(grain(d, .09))

    # ---- letterbox bars with slate text ---------------------------------------
    out.append(f'<rect class="barT" width="{W}" height="{BAR}" fill="#000"/>')
    out.append(f'<rect class="barB" y="{H - BAR}" width="{W}" height="{BAR}" fill="#000"/>')
    out.append(f'<line x1="0" y1="{BAR}" x2="{W}" y2="{BAR}" stroke="{C["line"]}" />')
    out.append(f'<line x1="0" y1="{H - BAR}" x2="{W}" y2="{H - BAR}" stroke="{C["line"]}" />')
    ty = BAR / 2 + 5
    out.append(f'<g class="fi" style="animation-delay:1.2s">')
    out.append(d.text("SCENE 01", 34, ty, "mono-b", 13, C["text"], tracking=3))
    out.append(d.text("— ORIGIN STORY", 34 + d.width("SCENE 01", "mono-b", 13, 3) + 12, ty, "mono", 13, C["muted"], tracking=3))
    # REC + running timecode
    tc_x = W - 34
    out.append(timecode(d, tc_x, ty))
    out.append("</g>")

    by2 = H - BAR / 2 + 5
    out.append(f'<g class="fi" style="animation-delay:1.4s">')
    out.append(d.text("12.9692°N  79.1559°E  ·  VELLORE, IN", 34, by2, "mono", 12.5, C["muted"], tracking=2.4))
    status = "NOW BUILDING: RILEY  [CLASSIFIED]"
    sw_ = d.width(status, "mono-m", 12.5, 2.4)
    out.append(f'<circle cx="{f(W - 34 - sw_ - 14)}" cy="{by2 - 4.5}" r="3.6" fill="{C["lime"]}" class="breathe"/>')
    out.append(d.text(status, W - 34, by2, "mono-m", 12.5, C["lime"], "end", 2.4))
    out.append("</g>")

    # HUD frame corners inside the picture area
    out.append(f'<g class="fi" style="animation-delay:1.0s">{corners(26, BAR + 18, W - 52, H - 2 * BAR - 36, 22, C["cyan"], 1.4, .7)}</g>')
    # small side readouts
    out.append(f'<g class="fi" style="animation-delay:2.6s">')
    for i, (k, v) in enumerate([("SEC", "ZERO-TRUST"), ("QPU", "SUPERPOSED"), ("NET", "ENCRYPTED")]):
        yy = BAR + 54 + i * 22
        out.append(d.text(k, 46, yy, "mono-b", 11.5, C["cyan"], tracking=2))
        out.append(d.text(v, 84, yy, "mono", 11.5, C["muted"], tracking=2))
    for i, (k, v) in enumerate([(f"{public_repos():02d}", "PUBLIC REPOS"), ("06", "LIVE DEPLOYS"), ("04", "QUANTUM GAMES")]):
        yy = BAR + 54 + i * 22
        out.append(d.text(v, W - 46, yy, "mono", 11.5, C["muted"], "end", 2))
        vw = d.width(v, "mono", 11.5, 2)
        out.append(d.text(k, W - 46 - vw - 10, yy, "mono-b", 11.5, C["magenta"], "end", 1))
    out.append("</g>")

    out.append("</g>")  # frame clip
    out.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" stroke="{C["line2"]}" fill="none"/>')
    return d


def public_repos(fallback=61):
    """Live public-repo count for the HUD, so the number never goes stale on a rebuild."""
    import json
    import urllib.request
    try:
        req = urllib.request.Request("https://api.github.com/users/Arrow-Ghost", headers={"User-Agent": "arrow-ghost-build"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return int(json.load(r)["public_repos"])
    except Exception:
        return fallback


def timecode(d, right_x, y):
    """REC ● HH:MM:SS:FF that actually runs — stacked digits toggled by SMIL."""
    size, font, tr = 13, "mono-b", 1.4
    fo = Font.get(font)
    cw = fo.advance("0", size) + tr
    s = "00:00:00:00"
    total_w = cw * len(s) - tr
    x0 = right_x - total_w
    parts = []
    # static frame
    for i, ch in enumerate(s):
        if ch == ":":
            parts.append(d.text(":", x0 + i * cw, y, font, size, C["muted"]))
    # (index, digits, seconds-per-digit) — FF at 24fps, SS, MM
    cols = [(0, 10, 36000), (1, 10, 3600), (3, 6, 600), (4, 10, 60), (6, 6, 10), (7, 10, 1), (9, 3, 10 / 24), (10, 10, 1 / 24)]
    for idx, n, per in cols:
        if idx == 9:   # frames tens: 0,1,2 then wraps at 24 — handled by period of 1s
            digs = [(0, 10), (1, 10), (2, 4)]
            dur = 1.0
            acc = 0
            for dv, cnt in digs:
                kt0, kt1 = acc / 24, (acc + cnt) / 24
                parts.append(_digit(d, str(dv), x0 + idx * cw, y, font, size, dur, kt0, kt1))
                acc += cnt
            continue
        if idx == 10:
            dur = 1.0
            # 24 frames: units cycle 0-9,0-9,0-3
            seq = [i % 10 for i in range(24)]
            for dv in range(10):
                frames = [k for k, v in enumerate(seq) if v == dv]
                vals = ["1" if seq[k] == dv else "0" for k in range(24)] + ["1" if dv == 0 else "0"]
                kts = ";".join(f"{k / 24:.4f}" for k in range(24)) + ";1"
                parts.append(f'<g opacity="0">{d.text(str(dv), x0 + idx * cw, y, font, size, C["text"])}'
                             f'<animate attributeName="opacity" values="{";".join(vals)}" keyTimes="{kts}" dur="1s" calcMode="discrete" repeatCount="indefinite"/></g>')
            continue
        dur = n * per
        for dv in range(n):
            parts.append(_digit(d, str(dv), x0 + idx * cw, y, font, size, dur, dv / n, (dv + 1) / n))
    rec_w = d.width("REC", "mono-b", 13, 2.4)
    rx = x0 - 18 - rec_w
    parts.append(f'<circle cx="{f(rx - 13)}" cy="{y - 4.5}" r="5" fill="{C["red"]}" class="blink"/>')
    parts.append(d.text("REC", rx, y, "mono-b", 13, C["red"], tracking=2.4))
    return "".join(parts)


def _digit(d, ch, x, y, font, size, dur, k0, k1):
    if k0 <= 0:
        vals, kts = "1;0;0", f"0;{k1:.5f};1"
    elif k1 >= 1:
        vals, kts = "0;1;1", f"0;{k0:.5f};1"
    else:
        vals, kts = "0;1;0;0", f"0;{k0:.5f};{k1:.5f};1"
    init = "1" if k0 <= 0 else "0"
    return (f'<g opacity="{init}">{d.text(ch, x, y, font, size, C["text"])}'
            f'<animate attributeName="opacity" values="{vals}" keyTimes="{kts}" dur="{dur:g}s" calcMode="discrete" repeatCount="indefinite"/></g>')


if __name__ == "__main__":
    build().save("hero.svg")
