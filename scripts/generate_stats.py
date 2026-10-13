"""Telemetry: self-hosted GitHub stats, drawn in the profile's own style.

    python scripts/generate_stats.py

With GH_TOKEN / GITHUB_TOKEN set (the telemetry workflow), data comes from the
GraphQL API. Without a token (local preview) it falls back to the public
contributions page plus one REST call, so it never trips the anonymous rate
limit. Writes assets/telemetry.svg and assets/langs.svg.
"""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import urllib.request

from agfx import C, Doc, corners, delay, f, glow, lin, panel, stars

LOGIN = os.environ.get("GH_LOGIN") or "Arrow-Ghost"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
UA = {"User-Agent": "arrow-ghost-telemetry"}

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
# GitHub's language colours, pulled toward our palette so the spectrum stays on-brand.
LANG_COLOR = {
    "TypeScript": "#2BE4FF", "JavaScript": "#FFB547", "Python": "#8B5CFF", "Java": "#FF8A5C",
    "HTML": "#FF3D9A", "CSS": "#9CF3FF", "Dart": "#3DFFA8", "Astro": "#FF6BD5", "C++": "#F0628F",
    "C": "#9AA3C7", "GLSL": "#B9BFD9", "Kotlin": "#A97BFF", "Go": "#6FE0FF", "Shell": "#7DFFB8",
    "Jupyter Notebook": "#FFA36B", "Svelte": "#FF7A59", "Vue": "#5CFFC4",
}
FALLBACK = ["#2BE4FF", "#8B5CFF", "#FF3D9A", "#FFB547", "#3DFFA8", "#9CF3FF", "#FF8A5C", "#A97BFF"]


# ------------------------------------------------------------------ data ---

def http(url: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions restrictedContributionsCount
      totalPullRequestContributions totalIssueContributions
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount contributionLevel } } }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes { stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } }
    }
  }
}"""


def from_graphql() -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    res = json.loads(http("https://api.github.com/graphql", body, {"Authorization": f"bearer {TOKEN}"}))
    if res.get("errors"):
        raise SystemExit(f"GraphQL error: {res['errors']}")
    u = res["data"]["user"]
    cc = u["contributionsCollection"]
    days = [(d["date"], d["contributionCount"], LEVELS.get(d["contributionLevel"], 0))
            for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    langs: dict[str, int] = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "days": days,
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "since": u["createdAt"][:4],
        "langs": langs,
        "lang_basis": "BYTES OF CODE",
    }


def from_public() -> dict:
    """Token-less preview: scrape the public calendar + one REST call."""
    html = http(f"https://github.com/users/{LOGIN}/contributions").decode("utf-8")
    cells = {m.group(2): [m.group(1), 0, int(m.group(3))] for m in re.finditer(
        r'<td[^>]*?data-date="([\d-]+)"[^>]*?id="(contribution-day-component-[\d-]+)"[^>]*?data-level="(\d)"', html)}
    for m in re.finditer(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>', html):
        n = re.match(r"([\d,]+) contribution", m.group(2))
        if m.group(1) in cells and n:
            cells[m.group(1)][1] = int(n.group(1).replace(",", ""))
    days = sorted(tuple(v) for v in cells.values())
    repos = json.loads(http(f"https://api.github.com/users/{LOGIN}/repos?per_page=100"))
    own = [r for r in repos if not r["fork"]]
    langs: dict[str, int] = {}
    for r in own:
        if r["language"]:
            langs[r["language"]] = langs.get(r["language"], 0) + r["size"] * 1024
    user = json.loads(http(f"https://api.github.com/users/{LOGIN}"))
    return {
        "days": days, "repos": len(own), "stars": sum(r["stargazers_count"] for r in own),
        "followers": user.get("followers", 0), "since": (user.get("created_at") or "2021")[:4],
        "langs": langs, "lang_basis": "PRIMARY LANGUAGE × REPO SIZE (PREVIEW)",
    }


def analyse(data: dict) -> dict:
    days = sorted(data["days"])
    counts = [c for _, c, _ in days]
    total = sum(counts)
    active = sum(1 for c in counts if c)
    # longest streak
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # current streak: today may still be empty without breaking it
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    best = max(days, key=lambda d: d[1]) if days else ("", 0, 0)
    return {**data, "days": days, "total": total, "active": active, "longest": longest, "current": cur,
            "best": best, "active_pct": round(100 * active / max(1, len(days)))}


# --------------------------------------------------------------- drawing ---

W = 1280


def counter(d: Doc, x: float, y: float, label: str, value: str, sub: str, accent: str, dl: float) -> str:
    return (f'<g class="r" {delay(dl)}>'
            f'{d.text(label, x, y, "mono-b", 12.5, accent, tracking=2.6)}'
            f'{d.text(value, x - 3, y + 58, "sans-l", 58, C["text"], tracking=1)}'
            f'{d.text(sub, x, y + 84, "mono", 12.5, C["muted"], tracking=1.6, upper=True)}</g>')


def telemetry(s: dict) -> Doc:
    H = 524
    d = Doc(W, H, title=f"{LOGIN} — GitHub telemetry")
    glow(d, "cellGlow", std=3.2, strength=1)
    sync = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    o, c = panel(d, W, H, "SCENE 05 — TELEMETRY", f"LAST SYNC  {sync}", glow_color=C["cyan"])
    d.add(o, stars(61, 70, W, H, rmax=1.2, twinkle=True))
    d.css.append("""
@keyframes tmBeam{0%{transform:translateX(0);opacity:0}8%{opacity:1}72%{opacity:1}80%,100%{transform:translateX(1180px);opacity:0}}
@keyframes tmPulse{0%,100%{r:9;opacity:.9}50%{r:14;opacity:0}}
.beam{animation:tmBeam 7s 2.2s cubic-bezier(.45,0,.55,1) infinite;opacity:0}
.today{animation:tmPulse 2.4s ease-out infinite}
""")

    # ---- counters row
    best_date, best_n, _ = s["best"]
    best_sub = dt.date.fromisoformat(best_date).strftime("ON %b %d").upper() if best_date else ""
    items = [
        ("CONTRIBUTIONS · 1Y", f"{s['total']:,}", "COMMITS · PRS · ISSUES", C["cyan"]),
        ("ACTIVE DAYS", f"{s['active']}", f"{s['active_pct']}% OF THE YEAR", C["violet"]),
        ("CURRENT STREAK", f"{s['current']}", "DAYS AND COUNTING" if s["current"] else "RECHARGING", C["lime"]),
        ("LONGEST STREAK", f"{s['longest']}", "DAYS IN A ROW", C["magenta"]),
        ("PEAK DAY", f"{best_n}", best_sub, C["amber"]),
    ]
    x0, colw, top = 64, (W - 128) / 5, 92
    for i, (lab, val, sub, acc) in enumerate(items):
        x = x0 + i * colw
        if i:
            d.add(f'<line x1="{f(x - 26)}" y1="{top - 10}" x2="{f(x - 26)}" y2="{top + 92}" stroke="{C["line2"]}" opacity=".7"/>')
        d.add(counter(d, x, top, lab, val, sub, acc, .25 + i * .12))
    # streak meter under CURRENT STREAK
    sx = x0 + 2 * colw
    ratio = s["current"] / max(1, s["longest"])
    d.add(f'<g class="fi" {delay(1.1)}><rect x="{f(sx)}" y="{top + 98}" width="150" height="3" rx="1.5" fill="{C["line2"]}"/>'
          f'<rect x="{f(sx)}" y="{top + 98}" width="{f(max(3, 150 * ratio))}" height="3" rx="1.5" fill="{C["lime"]}"/></g>')

    # ---- heatmap
    days = s["days"]
    first = dt.date.fromisoformat(days[0][0])
    offset = (first.weekday() + 1) % 7          # Sunday-first rows, like GitHub
    ncols = math.ceil((len(days) + offset) / 7)
    gx, gy = 112, 262
    pitch = (W - gx - 64) / ncols
    cell = pitch - 4
    ramp = [C["line"], "#123E66", "#1C7BB0", C["cyan"], C["ice"]]
    cols: dict[int, list[str]] = {}
    hot: list[str] = []
    last_xy = None
    for idx, (date, n, lvl) in enumerate(days):
        k = idx + offset
        col, row = divmod(k, 7)
        x, y = gx + col * pitch, gy + row * pitch
        rect = f'<rect x="{f(x)}" y="{f(y)}" width="{f(cell)}" height="{f(cell)}" rx="3.2" fill="{ramp[lvl]}"{"" if lvl else " opacity=" + chr(34) + ".85" + chr(34)}/>'
        cols.setdefault(col, []).append(rect)
        if lvl >= 3:
            hot.append(rect)
        last_xy = (x + cell / 2, y + cell / 2)
    d.add(f'<g opacity=".6" filter="url(#cellGlow)">{"".join(hot)}</g>')
    for col in sorted(cols):
        d.add(f'<g class="fi" style="animation-delay:{.6 + col * .025:.3f}s;animation-duration:.6s">{"".join(cols[col])}</g>')
    if last_xy:
        d.add(f'<circle cx="{f(last_xy[0])}" cy="{f(last_xy[1])}" r="9" fill="none" stroke="{C["ice"]}" stroke-width="1.5" class="today"/>')
    # month labels
    seen = set()
    for idx, (date, _, _) in enumerate(days):
        dd = dt.date.fromisoformat(date)
        col = (idx + offset) // 7
        if dd.day <= 7 and (dd.year, dd.month) not in seen and col < ncols - 1:
            seen.add((dd.year, dd.month))
            d.add(d.text(dd.strftime("%b").upper(), gx + col * pitch, gy - 14, "mono-m", 12.5, C["muted"], tracking=2))
    for row, lab in ((1, "MON"), (3, "WED"), (5, "FRI")):
        d.add(d.text(lab, gx - 16, gy + row * pitch + cell * .75, "mono-m", 12, C["dim"], "end", 2))
    # scan beam over the grid
    gh = 7 * pitch
    beam = lin(d, "beamG", [(0, C["cyan"], 0), (.5, C["ice"], .5), (1, C["cyan"], 0)])
    d.add(f'<g class="beam"><rect x="{gx - 40}" y="{gy - 6}" width="40" height="{f(gh + 8)}" fill="{beam}" style="mix-blend-mode:screen"/>'
          f'<line x1="{gx - 20}" y1="{gy - 12}" x2="{gx - 20}" y2="{f(gy + gh + 6)}" stroke="{C["ice"]}" stroke-width="1" opacity=".7"/></g>')
    d.add(corners(gx - 18, gy - 34, W - 64 - gx + 36, gh + 52, 12, C["cyan"], 1.2, .55))

    # ---- footer readouts + legend
    fy = gy + gh + 54
    readouts = [("ORIGINAL REPOS", str(s["repos"])), ("STARS", str(s["stars"])),
                ("FOLLOWERS", str(s["followers"])), ("ON GITHUB SINCE", s["since"])]
    rx = 64
    parts = []
    for lab, val in readouts:
        parts.append(d.text(lab, rx, fy, "mono-b", 12.5, C["muted"], tracking=2.4))
        lw = d.width(lab, "mono-b", 12.5, 2.4)
        parts.append(d.text(val, rx + lw + 12, fy, "mono-b", 14, C["text"], tracking=1.5))
        rx += lw + 12 + d.width(val, "mono-b", 14, 1.5) + 40
    d.add(f'<g class="fi" {delay(1.8)}>{"".join(parts)}</g>')
    # legend drawn as LESS ▢▢▢▢▢ MORE
    lx2 = W - 64 - 5 * 15 + 3
    legend = [d.text("LESS", lx2 - 12, fy, "mono", 12, C["dim"], "end", 2)]
    for i in range(5):
        legend.append(f'<rect x="{f(lx2 + i * 15)}" y="{fy - 11}" width="12" height="12" rx="2.5" fill="{ramp[i]}"/>')
    legend.append(d.text("MORE", lx2 + 5 * 15 + 6, fy, "mono", 12, C["dim"], tracking=2))
    # shift legend left so MORE ends at the margin
    shift = (lx2 + 5 * 15 + 6 + d.width("MORE", "mono", 12, 2)) - (W - 64)
    d.add(f'<g class="fi" {delay(1.9)} transform="translate({f(-shift)} 0)">{"".join(legend)}</g>')
    d.add(c)
    return d


def langs_svg(s: dict) -> Doc:
    H = 330
    d = Doc(W, H, title=f"{LOGIN} — language spectrum")
    total = sum(s["langs"].values()) or 1
    top = sorted(s["langs"].items(), key=lambda kv: -kv[1])[:8]
    shown = sum(v for _, v in top)
    rows = [(name, v / total * 100, LANG_COLOR.get(name, FALLBACK[i % len(FALLBACK)])) for i, (name, v) in enumerate(top)]
    if total - shown > 0:
        rows.append(("Other", (total - shown) / total * 100, C["dim"]))
    o, c = panel(d, W, H, "SPECTRUM — LANGUAGES", f"{s['lang_basis']}", glow_color=C["violet"])
    d.add(o)
    d.css.append("""
@keyframes eq{0%,100%{transform:scaleY(.55)}50%{transform:scaleY(1)}}
.eq{transform-box:fill-box;transform-origin:50% 100%;animation:eq 2.6s ease-in-out infinite}
""")
    x0, x1 = 64, W - 64
    bar_y, bar_h = 168, 16
    span = x1 - x0
    # equaliser: thin bars whose envelope follows each language's share
    n_eq = 96
    eq = []
    seg_edges = []
    acc = 0.0
    for name, pct, col in rows:
        seg_edges.append((acc, acc + pct, col))
        acc += pct
    maxpct = max(p for _, p, _ in rows)
    for i in range(n_eq):
        t = (i + .5) / n_eq * 100
        seg = next((e for e in seg_edges if e[0] <= t < e[1]), seg_edges[-1])
        segpct = seg[1] - seg[0]
        hgt = 18 + 66 * (segpct / maxpct) ** .6 * (.55 + .45 * abs(math.sin(i * 1.7)))
        bx = x0 + i * span / n_eq
        eq.append(f'<rect class="eq" x="{f(bx + 1)}" y="{f(bar_y - 14 - hgt)}" width="{f(span / n_eq - 3)}" height="{f(hgt)}" rx="1.5" '
                  f'fill="{seg[2]}" opacity=".55" style="animation-delay:-{(i * .137) % 2.6:.2f}s"/>')
    d.add(f'<g class="fi" {delay(.4)}>{"".join(eq)}</g>')
    # segmented spectrum bar
    segs = []
    cx = x0
    for name, pct, col in rows:
        w_ = span * pct / 100
        segs.append(f'<rect x="{f(cx)}" y="{bar_y}" width="{f(max(1.5, w_ - 3))}" height="{bar_h}" rx="3" fill="{col}"/>')
        cx += w_
    d.defs.append(f'<clipPath id="barWipe"><rect x="{x0}" y="{bar_y - 4}" width="{span}" height="{bar_h + 8}" class="wipe" style="animation-delay:.3s;animation-duration:1.6s"/></clipPath>')
    d.add(f'<g clip-path="url(#barWipe)"><g filter="url(#{glow(d, "barGlow", 4, 1)})" opacity=".9">{"".join(segs)}</g></g>')
    # legend
    cols = 5
    lw = span / cols
    for i, (name, pct, col) in enumerate(rows):
        r_, k = divmod(i, cols)
        lx, ly = x0 + k * lw, bar_y + 62 + r_ * 40
        label = f"{pct:.1f}%" if pct >= .1 else "<0.1%"
        d.add(f'<g class="r" {delay(.8 + i * .07)}><circle cx="{f(lx + 6)}" cy="{f(ly - 6)}" r="5" fill="{col}"/>'
              f'{d.text(name, lx + 20, ly, "sans-sb", 18, C["text"])}'
              f'{d.text(label, lx + 26 + d.width(name, "sans-sb", 18), ly, "mono", 15, C["muted"], tracking=1)}</g>')
    d.add(c)
    return d


def main():
    data = None
    if TOKEN:
        try:
            data = from_graphql()
        except Exception as exc:  # token without GraphQL access, API hiccup, ...
            print(f"  graphql failed ({exc}); using public data")
    data = data or from_public()
    s = analyse(data)
    print(f"  {s['total']} contributions · streak {s['current']}/{s['longest']} · {len(s['langs'])} languages")
    telemetry(s).save("telemetry.svg")
    langs_svg(s).save("langs.svg")


if __name__ == "__main__":
    main()
