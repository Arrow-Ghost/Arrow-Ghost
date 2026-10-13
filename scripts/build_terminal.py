"""Scene 01 — WHO AM I: a glass terminal and a self-declassifying dossier.

The terminal window powers on like a CRT, then types out content.TERMINAL:
commands go in key by key behind a block cursor (SMIL clip rects stepping in
discrete jumps), output prints line by line, and when the session settles the
cursor keeps blinking on a fresh prompt. On the right an ID card fills itself
in, field by field, in sync with what the terminal prints. Its generative
sigil (an arrow piercing a Bloch-sphere ring set) keeps turning forever.

Timing model: everything is driven from one timeline computed below, so the
card, the cursor and the clip rects can never drift apart.
"""

import math
import random
import re

from agfx import ACCENT, C, Doc, Font, blur, corners, f, glow, lin, panel, rad, stars
from content import TERMINAL

W, H = 1280, 680
BAR = 34

# ---- terminal geometry -------------------------------------------------------
FS, LH = 17, 29                      # mono body size / line height
CW = Font.get("mono").advance("0", FS)   # 10.2 px — every Source Code Pro weight shares it
TX, TY, TW, TH = 44, 66, 848, 548
TB = 44                              # title bar
X0 = TX + 30                         # text column 0
Y0 = TY + TB + 36                    # first baseline
MAXC = int((TX + TW - 30 - X0) // CW)    # columns that fit (77)

# ---- dossier card geometry ---------------------------------------------------
KX, KY, KW, KH = 924, 66, 312, 548
KL, KR = KX + 24, KX + KW - 24       # inner left / right
SX, SY, SR = KX + KW / 2, KY + 160, 62   # sigil centre / sphere radius

PROMPT = [("ghost", C["magenta"], "mono-b"), ("@arrow", C["cyan"], "mono-b"),
          (":", C["muted"], "mono"), ("~/dossier", C["violet"], "mono-b"), ("$ ", C["soft"], "mono-b")]
PL = sum(len(s) for s, _, _ in PROMPT)

FOCUS_COL = {"cybersecurity": ACCENT["security"][0], "quantum computing": "#A98BFF", "ai / ml": C["cyan"],
             "embedded & iot": C["lime"], "full-stack web": C["ice"]}
TAG_COL = {"building": C["lime"], "writing": C["amber"], "serving": C["cyan"]}
# copy that is true but too long for 77 columns gets a shorter, equally true phrasing
SHORTER = {"game dev using quantum computing for beginners (python)": "quantum computing game dev for beginners (python)"}


# ------------------------------------------------------------------ copy → rows --
def rows_from_terminal():
    """content.TERMINAL → list of rows. Each row: {'kind': 'cmd'|'out', 'segs': [(col, text, colour, font)], 'cmd': str}"""
    rows = []

    def out(segs):
        rows.append({"kind": "out", "segs": segs})

    for line in TERMINAL:
        if line.startswith("$"):
            cmd = line[2:] if len(line) > 2 else ""
            segs, c = [], 0
            for s, col, fo in PROMPT:
                segs.append((c, s, col, fo))
                c += len(s)
            if cmd:
                segs.append((c, cmd, C["text"], "mono-m"))
            rows.append({"kind": "cmd", "segs": segs, "cmd": cmd})
            continue

        s = line.strip()
        if s.startswith("shrish verma"):
            # "name — degree @ uni ('29). tagline" → two lines, the tagline in signature colours
            head, _, tag = s.partition("). ")
            name, _, rest = head.partition(" — ")
            deg, _, uni = rest.partition(" @ ")
            uni, _, yr = uni.partition(" (")
            segs, c = [], 0
            for txt, col, fo in [(name, C["text"], "mono-b"), (" — ", C["muted"], "mono"), (deg, C["soft"], "mono"),
                                 (" @ ", C["muted"], "mono"), (uni, C["soft"], "mono"), (" (" + yr + ").", C["muted"], "mono")]:
                segs.append((c, txt, col, fo))
                c += len(txt)
            out(segs)
            out([(0, tag, "url(#tagG)", "mono-m")])
        elif " · " in s and all(p in FOCUS_COL for p in s.split(" · ")):
            segs, c = [], 0
            for i, p in enumerate(s.split(" · ")):
                if i:
                    segs.append((c, " · ", C["muted"], "mono"))
                    c += 3
                segs.append((c, p, FOCUS_COL[p], "mono-m"))
                c += len(p)
            out(segs)
        elif s.startswith("["):
            m = re.match(r"\[(\w+)\]\s+(\S+)\s+\.+\s+(.*?)(\s+\(classified\))?$", s)
            tag, name, desc, cls = m.group(1), m.group(2), m.group(3), m.group(4)
            desc = SHORTER.get(desc, desc)
            lead = name + " " + "." * (9 - len(name))
            segs = [(0, f"[{tag}]", TAG_COL.get(tag, C["soft"]), "mono-b"), (12, name, C["text"], "mono-b"),
                    (12 + len(name), lead[len(name):], C["dim"], "mono"), (23, desc, C["soft"], "mono")]
            if cls:
                segs.append((23 + len(desc) + 2, "(classified)", C["amber"], "mono-b"))
            out(segs)
        elif re.search(r"\S\s{2,}\S", s) and "_" in s:
            # ls output: two aligned columns, file names cyan, the rank in gold
            segs = []
            for k, name in enumerate(re.split(r"\s{2,}", s)):
                c0 = k * 36
                m = re.match(r"(AIR-\d+|podium|SIH-\d+|no\.\d+)(.*)", name)
                if m:
                    segs.append((c0, m.group(1), C["amber"], "mono-b"))
                    segs.append((c0 + len(m.group(1)), m.group(2), C["cyan"], "mono"))
                else:
                    segs.append((c0, name, C["cyan"], "mono"))
            out(segs)
        elif " · " in s:
            segs, c = [], 0
            for i, p in enumerate(s.split(" · ")):
                if i:
                    segs.append((c, " · ", C["muted"], "mono"))
                    c += 3
                segs.append((c, p, C["text"], "mono"))
                c += len(p)
            out(segs)
        else:
            out([(0, s, C["soft"], "mono")])
    for r in rows:
        r["len"] = max(c + len(t) for c, t, _, _ in r["segs"])
        assert r["len"] <= MAXC, (r["len"], r["segs"])
    return rows


# ------------------------------------------------------------------ timeline --
def timeline(rows):
    """Assign reveal keyframes to every row and the cursor. Returns (T_end, cursor_kf, marks)."""
    rnd = random.Random(77)
    t, prev = 1.15, None
    cur = []           # (t, col, row)
    marks = {}         # first print time of each command's output, keyed by command
    last_cmd = None
    for i, r in enumerate(rows):
        r["kf"] = []
        if r["kind"] == "cmd":
            if prev == "out":
                t += 0.2
            r["kf"].append((t, PL))
            cur.append((t, PL, i))
            if not r["cmd"]:
                break
            t += 0.55 if last_cmd is None else 0.3
            for k, ch in enumerate(r["cmd"]):
                t += rnd.uniform(0.042, 0.074) + (0.045 if ch == " " else 0)
                r["kf"].append((t, PL + k + 1))
                cur.append((t, PL + k + 1, i))
            t += 0.24
            last_cmd = r["cmd"]
            prev = "cmd"
        else:
            t += 0.12 if prev == "cmd" else 0.075
            if prev == "cmd":
                marks[last_cmd] = (t, i)
            r["kf"].append((t, r["len"]))
            cur.append((t, 0, i + 1))
            prev = "out"
    return t, cur, marks


def kt(times, T):
    """keyTimes string, strictly increasing, last = 1."""
    out, last = [], -1.0
    for x in times:
        v = max(round(x / T, 5), round(last + 0.00002, 5))
        out.append(v)
        last = v
    return ";".join(f"{v:g}" for v in out)


# ------------------------------------------------------------------- helpers --
def ket(doc, label, x, y, size, fill, font="mono"):
    fo = Font.get(font)
    t = doc.text("|" + label, x, y, font, size, fill)
    ax, top, bot = x + fo.width("|" + label, size) + size * 0.08, y - size * 0.74, y + size * 0.16
    mid = (top + bot) / 2
    return t + (f'<path d="M{f(ax)} {f(top)}L{f(ax + size * 0.28)} {f(mid)}L{f(ax)} {f(bot)}" stroke="{fill}" '
                f'stroke-width="{f(size * 0.075)}" fill="none" stroke-linecap="round"/>')


def P(x, y):
    return f"{f(x)} {f(y)}"


def seg_text(d, col_i, txt, base, colour, font, x0=X0):
    """One run of mono text on the character grid. SVG collapses leading/trailing
    spaces, so they are turned into a column offset instead."""
    lead = len(txt) - len(txt.lstrip(" "))
    s = txt.strip(" ")
    return d.text(s, x0 + (col_i + lead) * CW, base, font, FS, colour) if s else ""


# --------------------------------------------------------------------- sigil --
def sigil(d, cx, cy, R):
    o = []
    aura = rad(d, "aura", [(0, C["violet"], .55), (.45, C["violet"], .16), (1, C["violet"], 0)])
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R * 1.75)}" fill="{aura}" class="aura"/>')

    # reticle: tick ring turning the other way
    tk = []
    for k in range(72):
        a = math.radians(k * 5)
        r1, r2 = R + 27, R + (34 if k % 6 == 0 else 30)
        tk.append(f"M{P(cx + r1 * math.cos(a), cy + r1 * math.sin(a))}L{P(cx + r2 * math.cos(a), cy + r2 * math.sin(a))}")
    o.append(f'<g stroke="{C["muted"]}" stroke-width="1" opacity=".5"><path d="{"".join(tk)}"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {P(cx, cy)}" to="-360 {P(cx, cy)}" dur="90s" repeatCount="indefinite"/></g>')
    # four reticle arcs
    rr = R + 40
    arcs = []
    for q in range(4):
        a0, a1 = math.radians(q * 90 - 22), math.radians(q * 90 + 22)
        arcs.append(f"M{P(cx + rr * math.cos(a0), cy + rr * math.sin(a0))}A{f(rr)} {f(rr)} 0 0 1 {P(cx + rr * math.cos(a1), cy + rr * math.sin(a1))}")
    o.append(f'<g stroke="{C["cyan"]}" stroke-width="1.3" opacity=".55" fill="none"><path d="{"".join(arcs)}"/>'
             f'<animateTransform attributeName="transform" type="rotate" from="0 {P(cx, cy)}" to="360 {P(cx, cy)}" dur="40s" repeatCount="indefinite"/></g>')

    # sphere body
    sf = rad(d, "sphF", [(0, C["violet"], .16), (.7, C["violet"], .05), (1, C["cyan"], .16)], cx=.4, cy=.36, r=.62)
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{R}" fill="{sf}" stroke="{C["line2"]}" stroke-width="1.2"/>')
    tilt = .28
    o.append(f'<path d="M{P(cx - R, cy)}A{R} {f(R * tilt)} 0 0 1 {P(cx + R, cy)}" stroke="{C["muted"]}" stroke-dasharray="2 5" opacity=".7"/>')
    o.append(f'<line x1="{f(cx)}" y1="{f(cy - R - 12)}" x2="{f(cx)}" y2="{f(cy + R + 12)}" stroke="{C["muted"]}" stroke-dasharray="2 4" opacity=".6"/>')
    for ph in range(3):
        o.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{R}" ry="{R}" stroke="{C["cyan"]}" stroke-width="1" opacity=".28">'
                 f'<animate attributeName="rx" values="{R};0;{R}" keyTimes="0;.5;1" dur="10s" begin="-{ph * 10 / 3:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines=".37 0 .63 1;.37 0 .63 1"/></ellipse>')
    o.append(f'<path d="M{P(cx - R, cy)}A{R} {f(R * tilt)} 0 0 0 {P(cx + R, cy)}" stroke="{C["ice"]}" stroke-width="1.1" opacity=".6"/>')

    # gyroscope ring set — tilted orbits that tumble, each with a bead
    rings = [(-24, C["cyan"], 26, 1, 7.0), (36, C["violet"], 34, -1, 9.5), (96, C["magenta"], 44, 1, 12.0)]
    for ang, col, dur, dirn, bead in rings:
        rx_, ry_ = R + 15, (R + 15) * .3
        path = f"M{P(cx - rx_, cy)}A{f(rx_)} {f(ry_)} 0 1 1 {P(cx + rx_, cy)}A{f(rx_)} {f(ry_)} 0 1 1 {P(cx - rx_, cy)}"
        o.append(f'<g><g transform="rotate({ang} {P(cx, cy)})">'
                 f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx_)}" ry="{f(ry_)}" stroke="{col}" stroke-width="1.25" opacity=".8" filter="url(#gl)">'
                 f'<animate attributeName="ry" values="{f(ry_)};{f(ry_ * .15)};{f(ry_)}" dur="{dur * .5:g}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></ellipse>'
                 f'<circle r="2.8" fill="#fff" filter="url(#gl)"><animateMotion path="{path}" dur="{bead}s" repeatCount="indefinite"/></circle>'
                 f'</g><animateTransform attributeName="transform" type="rotate" from="0 {P(cx, cy)}" to="{360 * dirn} {P(cx, cy)}" dur="{dur}s" repeatCount="indefinite"/></g>')

    # the arrow: shot clean through the sphere
    a = math.radians(-31)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    tail = (cx - 124 * ux, cy - 124 * uy)
    head = (cx + 114 * ux, cy + 114 * uy)
    tip = (head[0] + 6 * ux, head[1] + 6 * uy)
    shaft_end = (head[0] - 10 * ux, head[1] - 10 * uy)
    ag = lin(d, "arrowG", [(0, C["magenta"], 0), (.18, C["magenta"]), (.55, C["violet"]), (1, C["cyan"])],
             f(tail[0]), f(tail[1]), f(head[0]), f(head[1]), ' gradientUnits="userSpaceOnUse"')

    def arrow_paths(dx=0.0, dy=0.0):
        sh = f"M{P(tail[0] + dx, tail[1] + dy)}L{P(shaft_end[0] + dx, shaft_end[1] + dy)}"
        b = (head[0] - 14 * ux, head[1] - 14 * uy)
        hd = (f"M{P(tip[0] + dx, tip[1] + dy)}L{P(b[0] + 7 * nx + dx, b[1] + 7 * ny + dy)}"
              f"L{P(head[0] - 8 * ux + dx, head[1] - 8 * uy + dy)}L{P(b[0] - 7 * nx + dx, b[1] - 7 * ny + dy)}Z")
        fl = []
        for k in range(3):
            p0 = (tail[0] + (14 + k * 9) * ux, tail[1] + (14 + k * 9) * uy)
            for sgn in (1, -1):
                fl.append(f"M{P(p0[0] + dx, p0[1] + dy)}L{P(p0[0] - 11 * ux + sgn * 7 * nx + dx, p0[1] - 11 * uy + sgn * 7 * ny + dy)}")
        return sh, hd, "".join(fl)

    # speed streaks behind the tail
    for k, off in enumerate((-9, 0, 9)):
        s0 = (tail[0] - (18 + abs(off) * 1.4) * ux + off * nx, tail[1] - (18 + abs(off) * 1.4) * uy + off * ny)
        s1 = (tail[0] + (8 if off == 0 else -6) * ux + off * nx, tail[1] + (8 if off == 0 else -6) * uy + off * ny)
        o.append(f'<path d="M{P(*s0)}L{P(*s1)}" stroke="{C["ice"]}" stroke-width="1" stroke-dasharray="6 9" opacity="{.35 if off else .5}">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="-30" dur="{.9 + k * .2:.1f}s" repeatCount="indefinite"/></path>')

    sh, hd, fl = arrow_paths()
    # chromatic ghost copies (glitch moment only)
    for cls, col, dx in (("gA", C["cyan"], -4), ("gB", C["magenta"], 4)):
        gsh, ghd, gfl = arrow_paths(dx, -dx * .4)
        o.append(f'<g class="{cls}"><path d="{gsh}{gfl}" stroke="{col}" stroke-width="2.4"/><path d="{ghd}" fill="{col}"/></g>')
    o.append(f'<path d="{sh}" stroke="{ag}" stroke-width="2.6" stroke-linecap="round" filter="url(#gl)"/>')
    o.append(f'<path d="{fl}" stroke="{C["magenta"]}" stroke-width="1.6" stroke-linecap="round" opacity=".9"/>')
    o.append(f'<path d="{hd}" fill="{C["ice"]}" filter="url(#gl)"/>')
    # light pulse running down the shaft
    o.append(f'<path d="{sh}" pathLength="100" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="9 140" opacity=".95" filter="url(#gl)">'
             f'<animate attributeName="stroke-dashoffset" values="9;-100;-100" keyTimes="0;.42;1" dur="3.4s" repeatCount="indefinite"/></path>')
    # glass front: the part of the arrow inside the sphere sits behind it
    gf = rad(d, "glassF", [(0, "#fff", .0), (.82, C["ice"], .05), (1, C["ice"], .16)])
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{R}" fill="{gf}"/>')
    # puncture glints where the arrow pierces the sphere
    for k, sgn in enumerate((-1, 1)):
        gx, gy = cx + sgn * R * ux, cy + sgn * R * uy
        s = 7
        star = f"M{P(gx - s, gy)}Q{P(gx, gy)} {P(gx, gy - s)}Q{P(gx, gy)} {P(gx + s, gy)}Q{P(gx, gy)} {P(gx, gy + s)}Q{P(gx, gy)} {P(gx - s, gy)}Z"
        o.append(f'<path d="{star}" fill="#fff" filter="url(#gl)" opacity=".9">'
                 f'<animate attributeName="opacity" values=".25;1;.25" dur="2.6s" begin="{k * 1.3}s" repeatCount="indefinite"/></path>')
    o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="3" fill="{C["ice"]}"/>')
    o.append(ket(d, "0", cx + 7, cy - R - 16, 13, C["ice"]))
    o.append(ket(d, "1", cx + 7, cy + R + 26, 13, C["muted"]))
    return "".join(o)


# ----------------------------------------------------------------------- bus --
def bus(d, fields, FY, RH, T_end):
    """Hairline data bus in the gutter. When the terminal prints, a packet runs
    from that line across to the card field it fills in."""
    xb, x1, x2 = (TX + TW + KX) / 2, TX + TW, KX
    o = []
    ys_src = sorted({Y0 + r * LH - 6 for _, _, r in fields})
    ys_dst = [FY + k * RH + 18 for k in range(len(fields))]
    top, bot = min(ys_src + ys_dst), max(ys_src + ys_dst)
    st = [f"M{f(xb)} {f(top)}V{f(bot)}"] + [f"M{f(x1)} {f(y)}H{f(xb)}" for y in ys_src] + [f"M{f(xb)} {f(y)}H{f(x2)}" for y in ys_dst]
    o.append(f'<g class="fi" style="animation-delay:1.4s"><path d="{"".join(st)}" stroke="{C["line2"]}" stroke-width="1"/>'
             + "".join(f'<circle cx="{f(xb)}" cy="{f(y)}" r="2" fill="{C["line2"]}"/>' for y in ys_src + ys_dst) + "</g>")
    for k, (lab, t_arrive, r) in enumerate(fields):
        y0, y1 = Y0 + r * LH - 6, FY + k * RH + 18
        path = f"M{f(x1)} {f(y0)}H{f(xb)}V{f(y1)}H{f(x2)}"
        t0 = t_arrive - .42
        o.append(f'<path d="{path}" stroke="{C["cyan"]}" stroke-width="1.4" opacity="0" filter="url(#gl)">'
                 f'<animate attributeName="opacity" values="0;.9;0" dur=".8s" begin="{t0:.3f}s" fill="freeze"/></path>')
        o.append(f'<circle r="3" fill="#fff" opacity="0" filter="url(#glc)">'
                 f'<animateMotion path="{path}" dur=".42s" begin="{t0:.3f}s" fill="freeze"/>'
                 f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;.85;1" dur=".42s" begin="{t0:.3f}s" fill="freeze"/></circle>')
    # idle heartbeat once the session has settled
    o.append(f'<circle r="2.2" fill="{C["cyan"]}" opacity="0" filter="url(#glc)">'
             f'<animateMotion path="M{f(xb)} {f(top)}V{f(bot)}" dur="6s" begin="{T_end + 1:.2f}s" keyPoints="0;1;1" keyTimes="0;.32;1" calcMode="linear" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.04;.28;.32;1" dur="6s" begin="{T_end + 1:.2f}s" repeatCount="indefinite"/></circle>')
    return "".join(o)


# --------------------------------------------------------------------- build --
def build():
    d = Doc(W, H, title="Shrish Verma — whoami")
    rows = rows_from_terminal()
    T_end, cur, marks = timeline(rows)
    T = T_end + 0.05

    glow(d, "gl", std=3.2, strength=2)
    glow(d, "glc", std=5, strength=1)
    blur(d, "neb", 60)
    blur(d, "halo", 26)
    d.defs.append('<filter id="phos" filterUnits="userSpaceOnUse" x="0" y="0" width="1280" height="680">'
                  '<feGaussianBlur stdDeviation="2.4" result="b"/><feComponentTransfer in="b" result="b2"><feFuncA type="linear" slope=".6"/></feComponentTransfer>'
                  '<feMerge><feMergeNode in="b2"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    d.defs.append(f'<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="2.4" height="6" fill="{C["muted"]}" opacity=".5"/></pattern>')
    tag_w = len(next(r for r in rows if r["segs"][0][2] == "url(#tagG)")["segs"][0][1]) * CW
    lin(d, "tagG", [(0, C["cyan"]), (.5, "#A98BFF"), (1, C["magenta"])], f(X0), 0, f(X0 + tag_w), 0, ' gradientUnits="userSpaceOnUse"')
    lin(d, "callG", [(0, C["cyan"]), (.55, "#A98BFF"), (1, C["magenta"])], f(KR - 11 * CW), 0, f(KR), 0, ' gradientUnits="userSpaceOnUse"')

    d.css.append("""
@keyframes crtOn{0%{transform:scale(.5,.006);opacity:0}12%{opacity:1}40%{transform:scale(1,.006)}100%{transform:scale(1,1);opacity:1}}
@keyframes crtFlash{0%{opacity:0;transform:scaleX(.12)}16%{opacity:1}40%{opacity:1;transform:scaleX(1)}100%{opacity:0;transform:scaleX(1)}}
@keyframes out{from{opacity:1}to{opacity:0}}
@keyframes pop{from{opacity:0}to{opacity:1}}
@keyframes holo{0%{transform:translateX(-300px) skewX(-20deg)}42%,100%{transform:translateX(520px) skewX(-20deg)}}
@keyframes scanT{from{transform:translateY(-150px)}to{transform:translateY(760px)}}
@keyframes aura{0%,100%{opacity:.6}50%{opacity:1}}
@keyframes ghA{0%,86%,100%{transform:translate(0,0);opacity:0}87%{transform:translate(-5px,1px);opacity:.9}88.5%{transform:translate(4px,-2px);opacity:.7}90%{transform:translate(-2px,0);opacity:.5}91%{opacity:0}}
@keyframes ghB{0%,86%,100%{transform:translate(0,0);opacity:0}87%{transform:translate(5px,-1px);opacity:.9}88.5%{transform:translate(-4px,2px);opacity:.7}90%{transform:translate(2px,0);opacity:.5}91%{opacity:0}}
@keyframes redact{0%,90%,100%{opacity:0}90.5%,95%{opacity:1}}
@keyframes litBar{from{fill-opacity:0}to{fill-opacity:1}}
.crt{animation:crtOn 1s cubic-bezier(.7,0,.2,1) .15s both;transform-box:fill-box;transform-origin:50% 50%}
.crtf{opacity:0;animation:crtFlash 1s ease-out .15s both;transform-box:fill-box;transform-origin:50% 50%}
.out{animation:out .3s ease both}
.pop{animation:pop .14s linear both}
.holo{animation:holo 9s 4s infinite ease-in-out;transform:translateX(-300px) skewX(-20deg)}
.scanT{animation:scanT 8s linear infinite}
.aura{animation:aura 5s ease-in-out infinite}
.gA{opacity:0;animation:ghA 8s 5s infinite;mix-blend-mode:screen}
.gB{opacity:0;animation:ghB 8s 5s infinite;mix-blend-mode:screen}
.rdx{opacity:0;animation:redact 9s infinite}
.lit{animation:litBar .35s ease both}
""")

    open_, close_ = panel(d, W, H, "SCENE 01 — WHO AM I", "DOSSIER // 077-098-116", rx=20, grain_op=.075)
    o = d.body
    o.append(open_)

    # ---- backdrop: nebula + drifting stars + dot grid --------------------------
    o.append('<g filter="url(#neb)">')
    for (x, y, rx, ry, col, op, dx, dy, dur) in [
        (180, 560, 360, 170, C["violet"], .5, 70, -20, 27), (1120, 120, 300, 150, C["cyan"], .28, -60, 20, 31),
        (900, 640, 320, 110, C["magenta"], .3, -60, -10, 23), (560, 70, 300, 80, "#3B4BFF", .3, 50, 15, 29),
        (1090, 420, 170, 220, C["violet"], .34, -20, 30, 21)]:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}">'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></ellipse>')
    o.append("</g>")
    for seed, n, rmax, dur, op in [(31, 120, 1.0, 260, .6), (37, 40, 1.6, 150, .85)]:
        layer = stars(seed, n, W, H, rmax=rmax)
        o.append(f'<g opacity="{op}"><g>{layer}<g transform="translate({W} 0)">{layer}</g>'
                 f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-{W} 0" dur="{dur}s" repeatCount="indefinite"/></g></g>')
    d.defs.append('<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="12" cy="12" r=".9" fill="#9CF3FF" opacity=".16"/></pattern>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#dots)"/>')
    o.append(f'<g class="fi" style="animation-delay:.9s">{corners(22, BAR + 12, W - 44, H - 2 * BAR - 24, 18, C["cyan"], 1.3, .55)}</g>')

    # ---- terminal window -------------------------------------------------------
    o.append(f'<g class="fi" style="animation-delay:.7s;animation-duration:2s">'
             f'<rect x="{TX + 20}" y="{TY + 30}" width="{TW - 40}" height="{TH - 30}" rx="18" fill="{C["violet"]}" opacity=".32" filter="url(#halo)"/>'
             f'<rect x="{TX + 120}" y="{TY + TH - 30}" width="{TW - 240}" height="40" rx="20" fill="{C["cyan"]}" opacity=".16" filter="url(#halo)"/></g>')
    d.defs.append(f'<clipPath id="win"><rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="14"/></clipPath>')
    glass = lin(d, "glass", [(0, "#0D1124", .94), (1, "#060811", .9)], 0, 0, 0, 1)
    o.append('<g class="crt">')
    o.append(f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="14" fill="{glass}"/>')
    o.append('<g clip-path="url(#win)">')
    # inner atmosphere: faint colour wash + watermark
    o.append(f'<ellipse cx="{TX + TW * .78}" cy="{TY + TH * .85}" rx="320" ry="160" fill="{C["violet"]}" opacity=".10" filter="url(#neb)"/>')
    o.append(f'<ellipse cx="{TX + TW * .15}" cy="{TY + 120}" rx="260" ry="110" fill="{C["cyan"]}" opacity=".06" filter="url(#neb)"/>')
    # title bar
    o.append(f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TB}" fill="#05070F" opacity=".85"/>')
    o.append(f'<line x1="{TX}" y1="{TY + TB}" x2="{TX + TW}" y2="{TY + TB}" stroke="{C["line"]}"/>')
    for k, col in enumerate((C["red"], C["amber"], C["lime"])):
        o.append(f'<circle cx="{TX + 24 + k * 22}" cy="{TY + TB / 2}" r="6.2" fill="{col}" opacity=".9"/>'
                 f'<circle cx="{TX + 24 + k * 22}" cy="{TY + TB / 2}" r="6.2" fill="none" stroke="#000" stroke-opacity=".35"/>')
    title = "ghost@arrow: ~/dossier — zsh"
    o.append(d.text(title, TX + TW / 2, TY + TB / 2 + 5, "mono-m", 14, C["muted"], "middle", 1))
    o.append(d.text("#077", TX + TW - 22, TY + TB / 2 + 5, "mono", 13, C["dim"], "end", 1.5))
    # scrollbar
    o.append(f'<rect x="{TX + TW - 13}" y="{TY + TB + 12}" width="4" height="{TH - TB - 24}" rx="2" fill="{C["line"]}" opacity=".6"/>'
             f'<rect x="{TX + TW - 13}" y="{TY + TH - 150}" width="4" height="138" rx="2" fill="{C["line2"]}"/>')

    # text rows
    o.append('<g filter="url(#phos)">')
    for i, r in enumerate(rows):
        base = Y0 + i * LH
        cid = f"tl{i}"
        full = r["len"] * CW + 6
        ws = ["0"] + [f(c * CW + (6 if c == r["len"] else 0)) for _, c in r["kf"]]
        ts = [0] + [x for x, _ in r["kf"]] + [T]
        ws.append(ws[-1])
        d.defs.append(f'<clipPath id="{cid}"><rect x="{f(X0 - 3)}" y="{f(base - 21)}" width="{f(full)}" height="{LH}">'
                      f'<animate attributeName="width" values="{";".join(ws)}" keyTimes="{kt(ts, T)}" dur="{f(T)}s" calcMode="discrete" fill="freeze"/></rect></clipPath>')
        segs = "".join(seg_text(d, c, txt, base, col, fo) for c, txt, col, fo in r["segs"])
        o.append(f'<g clip-path="url(#{cid})">{segs}</g>')
        if r["kind"] == "out":
            # phosphor glint: the freshly printed line flashes white, then decays
            ghost = "".join(seg_text(d, c, txt, base, "#fff", fo) for c, txt, col, fo in r["segs"])
            o.append(f'<g opacity="0">{ghost}<animate attributeName="opacity" values=".8;0" dur=".5s" begin="{r["kf"][0][0]:.3f}s" fill="freeze"/></g>')
    o.append("</g>")

    # "(classified)" gets redacted every so often once the session settles
    for i, r in enumerate(rows):
        for c, txt, col, fo in r["segs"]:
            if txt == "(classified)":
                bx, by_ = X0 + c * CW - 2, Y0 + i * LH - 15
                o.append(f'<g class="rdx" style="animation-delay:{T_end + 1.5:.2f}s"><rect x="{f(bx)}" y="{f(by_)}" width="{f(len(txt) * CW + 4)}" height="20" fill="{C["amber"]}"/>'
                         f'{d.text("REDACTED", bx + (len(txt) * CW + 4) / 2, by_ + 15, "mono-b", 14, C["void"], "middle", 2.2)}</g>')

    # block cursor
    xs = [f(X0 + c * CW) for _, c, _ in cur]
    ys = [f(Y0 + rr * LH - 15) for _, _, rr in cur]
    ts = [0] + [x for x, _, _ in cur]
    fx, fy = xs[-1], ys[-1]
    xs, ys = [xs[0]] + xs, [ys[0]] + ys
    vis = ["0"] + ["1"] * len(cur)
    o.append(f'<rect x="{fx}" y="{fy}" width="{f(CW)}" height="20" fill="{C["ice"]}" filter="url(#glc)">'
             f'<animate attributeName="x" values="{";".join(xs)}" keyTimes="{kt(ts, T)}" dur="{f(T)}s" calcMode="discrete" fill="freeze"/>'
             f'<animate attributeName="y" values="{";".join(ys)}" keyTimes="{kt(ts, T)}" dur="{f(T)}s" calcMode="discrete" fill="freeze"/>'
             f'<animate attributeName="opacity" values="{";".join(vis)}" keyTimes="{kt(ts, T)}" dur="{f(T)}s" calcMode="discrete" fill="freeze"/>'
             f'<animate attributeName="opacity" values="1;0" keyTimes="0;.5" dur="1.1s" begin="{f(T_end)}s" calcMode="discrete" repeatCount="indefinite"/></rect>')
    o.append("</g>")  # window clip
    # border + top highlight
    edge = lin(d, "edge", [(0, C["cyan"], 0), (.2, C["cyan"], .9), (.55, "#A98BFF", .9), (.85, C["magenta"], .8), (1, C["magenta"], 0)])
    o.append(f'<rect x="{TX + .5}" y="{TY + .5}" width="{TW - 1}" height="{TH - 1}" rx="14" stroke="{C["line2"]}" fill="none"/>')
    o.append(f'<rect x="{TX + 40}" y="{TY}" width="{TW - 80}" height="1.5" fill="{edge}"/>')
    o.append("</g>")  # crt
    cy_ = TY + TH / 2
    o.append(f'<g class="crtf"><ellipse cx="{TX + TW / 2}" cy="{cy_}" rx="{TW * .62}" ry="5" fill="{C["cyan"]}" opacity=".7" filter="url(#halo)"/>'
             f'<rect x="{TX}" y="{cy_ - 2}" width="{TW}" height="4" rx="2" fill="#fff" filter="url(#glc)"/>'
             f'<ellipse cx="{TX + TW / 2}" cy="{cy_}" rx="{TW * .75}" ry=".9" fill="#fff"/>'
             f'<ellipse cx="{TX + TW / 2}" cy="{cy_}" rx="70" ry="22" fill="{C["ice"]}" opacity=".6" filter="url(#halo)"/></g>')

    o.append("@@BUS@@")
    # ---- dossier card ------------------------------------------------------------
    o.append('<g class="sl" style="animation-delay:.45s">')
    o.append(f'<rect x="{KX + 10}" y="{KY + 24}" width="{KW - 20}" height="{KH - 24}" rx="16" fill="{C["violet"]}" opacity=".22" filter="url(#halo)"/>')
    cardf = lin(d, "cardF", [(0, "#0F1330", .95), (.5, "#090C1C", .93), (1, "#070912", .95)], 0, 0, .4, 1)
    d.defs.append(f'<clipPath id="card"><rect x="{KX}" y="{KY}" width="{KW}" height="{KH}" rx="16"/></clipPath>')
    o.append(f'<rect x="{KX}" y="{KY}" width="{KW}" height="{KH}" rx="16" fill="{cardf}"/>')
    o.append('<g clip-path="url(#card)">')
    o.append(f'<rect x="{KX}" y="{KY}" width="{KW}" height="3" fill="{lin(d, "cardTop", [(0, C["cyan"]), (.5, C["violet"]), (1, C["magenta"])])}"/>')
    # header
    o.append(d.text("DOSSIER", KL, KY + 34, "mono-b", 16, C["text"], tracking=5))
    o.append(f'<rect x="{f(KR - d.width("EYES ONLY", "mono-b", 13, 2.4) - 16)}" y="{KY + 24}" width="8" height="8" fill="{C["amber"]}" class="breathe"/>')
    o.append(d.text("EYES ONLY", KR, KY + 33, "mono-b", 13, C["amber"], "end", 2.4))
    o.append(f'<line x1="{KL}" y1="{KY + 50}" x2="{KR}" y2="{KY + 50}" stroke="{C["line2"]}"/>')

    # sigil
    o.append(f'<g class="fi" style="animation-delay:.9s;animation-duration:1.8s">{sigil(d, SX, SY, SR)}</g>')
    o.append(f'<g class="fi" style="animation-delay:1.3s">{corners(KL, KY + 58, KR - KL, 208, 12, C["cyan"], 1.2, .6)}')
    o.append(d.text("SIGIL", KL + 10, KY + 80, "mono-b", 13, C["muted"], tracking=2.4))
    o.append(d.text("ψ-077", KR - 10, KY + 80, "mono", 13, C["dim"], "end", 2))
    o.append(d.text("θ 31°", KL + 10, KY + 256, "mono", 13, C["dim"], tracking=2))
    o.append(d.text("φ 0→2π", KR - 10, KY + 256, "mono", 13, C["dim"], "end", 1.5))
    o.append("</g>")

    # fields
    (t_who, r_who), (t_focus, r_focus) = marks["whoami"], marks["cat focus.txt"]
    (t_troph, r_troph), (t_log, r_log) = marks["ls ./trophies"], marks["tail now.log"]
    FY, RH = KY + 278, 36
    FLY = .42                      # bus travel time terminal → card
    # (label, decode start, source row of the packet that carries it)
    fields = [("NAME", t_who + FLY, r_who), ("CALLSIGN", t_who + .2 + FLY, r_who), ("BASE", t_who + .4 + FLY, r_who),
              ("FOCUS", t_focus + FLY, r_focus), ("CLEARANCE", t_troph + FLY, r_troph), ("STATUS", t_log + .25 + FLY, r_log)]
    rnd = random.Random(98)
    for k, (lab, t0, _) in enumerate(fields):
        top = FY + k * RH
        yb = top + 24
        o.append(f'<line x1="{KL}" y1="{top}" x2="{KR}" y2="{top}" stroke="{C["line"]}"/>')
        o.append(d.text(lab, KL, yb, "mono-m", 13, C["muted"], tracking=2.6))
        if lab == "NAME":
            val = d.text("SHRISH VERMA", KR, yb + 1, "sans-sb", 19, C["text"], "end", 1.6)
            vw = d.width("SHRISH VERMA", "sans-sb", 19, 1.6)
        elif lab == "CALLSIGN":
            val = d.text("ARROW-GHOST", KR, yb, "mono-b", 17, "url(#callG)", "end")
            vw = 11 * CW
        elif lab == "BASE":
            val = d.text("VELLORE, IN", KR, yb, "mono-b", 17, C["text"], "end")
            vw = 11 * CW
        elif lab == "FOCUS":
            parts = [("SEC", ACCENT["security"][0]), (" · ", C["muted"]), ("QUANTUM", "#A98BFF"), (" · ", C["muted"]), ("AI", C["cyan"])]
            n = sum(len(p) for p, _ in parts)
            x = KR - n * CW
            vw = n * CW
            val = ""
            for p, col in parts:
                val += d.text(p.strip(), x + (len(p) - len(p.lstrip())) * CW, yb, "mono-b", 17, col)
                x += len(p) * CW
        if lab in ("NAME", "CALLSIGN", "BASE", "FOCUS"):
            # redaction bar → scramble → value
            o.append(f'<g class="out" style="animation-delay:{t0:.2f}s"><rect x="{f(KR - vw)}" y="{yb - 13}" width="{f(vw)}" height="14" fill="url(#hatch)" stroke="{C["line2"]}"/></g>')
            n = max(4, round(vw / CW))
            for s in range(4):
                junk = "".join(rnd.choice("#%&@$*+=?<>/\\|01ABCDEFX") for _ in range(n))
                a, b = t0 + s * .07, t0 + (s + 1) * .07
                o.append(f'<g opacity="0">{d.text(junk, KR, yb, "mono-b", 17, C["cyan"] if s % 2 else C["ice"], "end")}'
                         f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{a / (b + .01):.4f};{b / (b + .01):.4f}" dur="{b + .01:.2f}s" calcMode="discrete" fill="freeze"/></g>')
            o.append(f'<g class="pop" style="animation-delay:{t0 + .33:.2f}s">{val}</g>')
        elif lab == "CLEARANCE":
            bw, gap = 17, 5
            x0 = KR - (5 * bw + 4 * gap)
            cols = [C["cyan"], "#5FA8FF", C["violet"], "#C64CD0", C["magenta"]]
            for j in range(5):
                bx = x0 + j * (bw + gap)
                o.append(f'<rect x="{bx}" y="{yb - 13}" width="{bw}" height="13" rx="2" fill="none" stroke="{C["line2"]}"/>')
                if j < 4:
                    o.append(f'<rect x="{bx}" y="{yb - 13}" width="{bw}" height="13" rx="2" fill="{cols[j]}" class="lit" style="animation-delay:{t0 + j * .14:.2f}s" filter="url(#gl)"/>')
        elif lab == "STATUS":
            sw_ = d.width("ACTIVE", "mono-b", 17)
            o.append(f'<g class="out" style="animation-delay:{t0:.2f}s">{d.text("STANDBY", KR, yb, "mono-b", 17, C["amber"], "end")}</g>')
            o.append(f'<g class="pop" style="animation-delay:{t0 + .12:.2f}s"><circle cx="{f(KR - sw_ - 14)}" cy="{yb - 6}" r="5" fill="{C["lime"]}" class="breathe" filter="url(#gl)"/>'
                     f'{d.text("ACTIVE", KR, yb, "mono-b", 17, C["lime"], "end")}</g>')
    o.append(f'<line x1="{KL}" y1="{FY + 6 * RH}" x2="{KR}" y2="{FY + 6 * RH}" stroke="{C["line"]}"/>')

    # barcode + serial
    rb = random.Random(116)
    bx, by_ = KL, KY + KH - 38
    bars = []
    while bx < KL + 150:
        wdt = rb.choice((1, 1, 2, 3))
        bars.append(f'<rect x="{bx}" y="{by_}" width="{wdt}" height="18"/>')
        bx += wdt + rb.choice((1, 2, 2, 3))
    o.append(f'<g fill="{C["soft"]}" opacity=".55">{"".join(bars)}</g>')
    o.append(d.text("077-098-116", KR, by_ + 14, "mono", 13, C["muted"], "end", 2))
    # holographic sheen
    holo = lin(d, "holoG", [(0, "#fff", 0), (.35, C["cyan"], .10), (.5, "#fff", .16), (.65, C["magenta"], .10), (1, "#fff", 0)])
    o.append(f'<rect class="holo" x="{KX}" y="{KY - 40}" width="110" height="{KH + 80}" fill="{holo}"/>')
    o.append("</g>")  # card clip
    o.append(f'<rect x="{KX + .5}" y="{KY + .5}" width="{KW - 1}" height="{KH - 1}" rx="16" stroke="{C["line2"]}" fill="none"/>')
    o.append("</g>")  # card slide

    o[o.index("@@BUS@@")] = bus(d, fields, FY, RH, T_end)

    # ---- scan band, then the panel's scanlines/vignette/grain/bars ---------------
    o.append(f'<rect class="scanT" x="0" y="0" width="{W}" height="130" fill="{lin(d, "scanG", [(0, C["cyan"], 0), (.7, C["cyan"], .025), (.9, C["cyan"], .05), (1, C["cyan"], 0)], 0, 0, 0, 1)}"/>')
    o.append(close_)
    # bottom slate text
    by2 = H - BAR / 2 + 4.5
    o.append(f'<g class="fi" style="animation-delay:1.2s">')
    o.append(d.text("TTY/077  ·  ZSH  ·  UTF-8  ·  SESSION ENCRYPTED", 28, by2, "mono", 12.5, C["muted"], tracking=2.4))
    o.append("</g>")
    st, sv = "IDENTITY VERIFIED", "VERIFYING IDENTITY"
    stw, svw = d.width(st, "mono-m", 12.5, 2.4), d.width(sv, "mono-m", 12.5, 2.4)
    o.append(f'<g class="out" style="animation-delay:{t_log + .5:.2f}s"><g class="fi" style="animation-delay:1.2s">'
             f'<circle cx="{f(W - 28 - svw - 14)}" cy="{by2 - 4.5}" r="3.6" fill="{C["amber"]}" class="blink"/>'
             f'{d.text(sv, W - 28, by2, "mono-m", 12.5, C["amber"], "end", 2.4)}</g></g>')
    o.append(f'<g class="pop" style="animation-delay:{t_log + .62:.2f}s">'
             f'<circle cx="{f(W - 28 - stw - 14)}" cy="{by2 - 4.5}" r="3.6" fill="{C["lime"]}" class="breathe"/>'
             f'{d.text(st, W - 28, by2, "mono-m", 12.5, C["lime"], "end", 2.4)}</g>')
    return d, T_end


if __name__ == "__main__":
    doc, t_end = build()
    print(f"  sequence settles at {t_end:.2f}s")
    doc.save("whoami.svg")
