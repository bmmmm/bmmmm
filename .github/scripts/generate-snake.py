#!/usr/bin/env python3
"""Terminal snake: render the GitHub contribution graph as an animated
character-cell SVG. Replaces Platane/snk entirely.

The grid is text — contribution levels 0-4 map to `·· ░░ ▒▒ ▓▓ ██` in the
GitHub greens, so intensity is double-coded (glyph density + color) and the
graph echoes the shade ramp in the profile README. A purple block snake
walks the year boustrophedon (column by column, alternating direction, the
way a print head reads a page) and grazes the shades off the grid; eaten
cells leave a dim `··` trail. An ASCII harvest bar below steps forward on
every eaten cell — the exact coupling idea from the old inject-bar.py.

The snake stops one cell short of the last contribution in its path. That
cell flips into a heart (CP437 0x03), the bar holds just under 100%, and
the terminal types the finding: `off by one`.

Outputs snake.svg (dark) and snake-light.svg. Pure SMIL — no JS, works
inside GitHub's README <img>/<picture> sandbox.

Usage: generate-snake.py [--login USER | --json FILE] [--out DIR]
Needs `gh` (authenticated / GH_TOKEN) when fetching via --login.
"""
import argparse
import json
import subprocess
import sys

# ---- character-cell geometry (font-size 13 -> advance 7.8px, square cells)
FS = 13
CW = 7.8                 # one monospace character
CELL_W = 2 * CW          # one grid cell = two characters
ROW_H = 15.6
PAD = 16
COLS_MAX = 54
MONO = "ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,monospace"

STEP_MS = 100            # snake speed: one cell per step
HOLD_MS = 8000           # end pause: heart + `off by one` hold, then loop
TYPE_MS = 70             # typewriter stagger per character
BAR_CHARS = 90           # inner width of the ascii harvest bar

LEVEL_GLYPH = ["··", "░░", "▒▒", "▓▓", "██"]
SNAKE_GLYPHS = ["██", "▓▓", "▓▓", "▒▒", "▒▒", "░░", "░░"]   # head first
SNAKE_FADE = [1, .95, .9, .8, .7, .55, .4]

PALETTES = {
    "dark": dict(
        panel="#161b22", level0="#21262d", trail="#30363d",
        greens=["#0e4429", "#006d32", "#26a641", "#39d353"],
        snake="#bf00ff", muted="#8b949e", cursor="#e6edf3",
    ),
    "light": dict(
        panel="#f6f8fa", level0="#d0d7de", trail="#afb8c1",
        greens=["#9be9a8", "#40c463", "#30a14e", "#216e39"],
        snake="#bf00ff", muted="#57606a", cursor="#1f2328",
    ),
}

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{weeks{contributionDays{contributionLevel weekday}}}}}}"""


def fetch_calendar(login):
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={login}"],
        check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def build_grid(payload):
    """-> grid[row][col] = level 0..4 or None (day outside the calendar)."""
    weeks = (payload["data"]["user"]["contributionsCollection"]
             ["contributionCalendar"]["weeks"])
    grid = [[None] * len(weeks) for _ in range(7)]
    for c, week in enumerate(weeks):
        for day in week["contributionDays"]:
            grid[day["weekday"]][c] = LEVELS[day["contributionLevel"]]
    return grid


def boustrophedon(grid):
    """Column-by-column path over all present cells, alternating direction."""
    cols = len(grid[0])
    path = []
    for c in range(cols):
        rows = range(7) if c % 2 == 0 else range(6, -1, -1)
        path.extend((r, c) for r in rows if grid[r][c] is not None)
    return path


def fmt(x):
    return f"{x:.6f}".rstrip("0").rstrip(".")


def render(grid, pal):
    cols = len(grid[0])
    path = boustrophedon(grid)
    edible = [i for i, (r, c) in enumerate(path) if grid[r][c] > 0]
    if len(edible) < 2:
        raise SystemExit("generate-snake: not enough contributions to graze")
    spared_i = edible[-1]                    # the heart: last edible cell
    eats = edible[:-1]                       # everything the snake gets
    K = spared_i - 1                         # head halts one cell short
    dur_ms = K * STEP_MS + HOLD_MS
    dur = f"{dur_ms}ms"
    t = lambda step: step * STEP_MS / dur_ms
    stop_t = t(K)

    x = lambda c: PAD + c * CELL_W
    y = lambda r: PAD + FS + r * ROW_H      # text baseline per grid row
    grid_bottom = PAD + 7 * ROW_H
    bar_y = grid_bottom + 24
    W = round(2 * PAD + cols * CELL_W)
    H = round(bar_y + 6 + PAD)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" rx="6" fill="{pal["panel"]}"/>',
         f'<g font-family="{MONO}" font-size="{FS}" xml:space="preserve">']

    # static under-layer: every cell as `··` (empty stays dim, eaten shows
    # trail). One absolutely-placed text per cell: column alignment must not
    # depend on the fallback font's advance width.
    for r in range(7):
        for c in range(cols):
            lvl = grid[r][c]
            if lvl is None:
                continue
            fill = pal["level0"] if lvl == 0 else pal["trail"]
            s.append(f'<text x="{x(c)}" y="{y(r)}" fill="{fill}">··</text>')

    # shade layer: one text per contribution cell, hidden at its eat time.
    # Colors shifted one level up — glyph density already encodes the level,
    # and unshifted level-1 green is near-invisible at 25% pixel coverage.
    eat_at = {path[i]: t(i) for i in eats}
    for r in range(7):
        for c in range(cols):
            lvl = grid[r][c]
            if not lvl:
                continue
            glyph = LEVEL_GLYPH[lvl]
            fill = pal["greens"][min(lvl, 3)]
            el = f'<text x="{x(c)}" y="{y(r)}" fill="{fill}">{glyph}'
            when = stop_t if (r, c) == path[spared_i] else eat_at.get((r, c))
            if when is not None:
                el += (f'<animate attributeName="opacity" calcMode="discrete" '
                       f'values="1;0" keyTimes="0;{fmt(when)}" dur="{dur}" '
                       f'repeatCount="indefinite"/>')
            s.append(el + '</text>')

    # the spared cell becomes a heart when the snake halts beside it
    hr, hc = path[spared_i]
    s.append(f'<text x="{x(hc)}" y="{y(hr)}" fill="{pal["snake"]}" opacity="0">♥'
             f'<animate attributeName="opacity" calcMode="discrete" '
             f'values="0;1" keyTimes="0;{fmt(stop_t)}" dur="{dur}" '
             f'repeatCount="indefinite"/></text>')

    # snake: head + fading tail, each segment walking the path with an offset
    key_times = ";".join(fmt(t(k)) for k in range(K + 1)) + ";1"
    for g, (glyph, fade) in enumerate(zip(SNAKE_GLYPHS, SNAKE_FADE)):
        pts = [path[max(0, k - g)] for k in range(K + 1)]
        pts.append(pts[-1])                  # hold through the end pause
        vals = ";".join(f"{x(c):g} {y(r):g}" for r, c in pts)
        s.append(f'<text x="0" y="0" fill="{pal["snake"]}" opacity="{fade}">'
                 f'{glyph}<animateTransform attributeName="transform" '
                 f'type="translate" calcMode="discrete" values="{vals}" '
                 f'keyTimes="{key_times}" dur="{dur}" '
                 f'repeatCount="indefinite"/></text>')

    # ascii harvest bar: [ track ] with a clipped fill stepping on every eat
    bar_x = PAD + CW
    bar_w = BAR_CHARS * CW
    n = len(edible)
    bar_kt = "0;" + ";".join(fmt(t(i)) for i in eats)
    bar_vals = "0;" + ";".join(fmt((i + 1) / n * bar_w) for i in range(len(eats)))
    s.append(f'<text x="{PAD}" y="{bar_y}" fill="{pal["muted"]}">[</text>')
    s.append(f'<text x="{bar_x}" y="{bar_y}" fill="{pal["level0"]}" '
             f'textLength="{bar_w:g}" lengthAdjust="spacingAndGlyphs">'
             f'{"░" * BAR_CHARS}</text>')
    s.append(f'<clipPath id="harvest"><rect x="{bar_x}" y="{bar_y - FS}" '
             f'width="0" height="{ROW_H + 4}">'
             f'<animate attributeName="width" calcMode="discrete" '
             f'values="{bar_vals}" keyTimes="{bar_kt}" dur="{dur}" '
             f'repeatCount="indefinite"/></rect></clipPath>')
    s.append(f'<text x="{bar_x}" y="{bar_y}" fill="{pal["greens"][3]}" '
             f'textLength="{bar_w:g}" lengthAdjust="spacingAndGlyphs" '
             f'clip-path="url(#harvest)">{"█" * BAR_CHARS}</text>')
    s.append(f'<text x="{bar_x + bar_w}" y="{bar_y}" fill="{pal["muted"]}">]'
             f'</text>')

    # the terminal types its finding, one character at a time
    text_x = bar_x + (BAR_CHARS + 2) * CW
    for i, ch in enumerate("off by one"):
        if ch == " ":
            continue
        at = min(stop_t + (i + 1) * TYPE_MS / dur_ms, 0.999)
        s.append(f'<text x="{fmt(text_x + i * CW)}" y="{bar_y}" '
                 f'fill="{pal["muted"]}" opacity="0">{ch}'
                 f'<animate attributeName="opacity" calcMode="discrete" '
                 f'values="0;1" keyTimes="0;{fmt(at)}" dur="{dur}" '
                 f'repeatCount="indefinite"/></text>')

    # block cursor, always blinking at the end of the line
    s.append(f'<text x="{fmt(text_x + 11 * CW)}" y="{bar_y}" '
             f'fill="{pal["cursor"]}">▋'
             f'<animate attributeName="opacity" calcMode="discrete" '
             f'values="1;0" keyTimes="0;0.5" dur="1.2s" '
             f'repeatCount="indefinite"/></text>')

    s.append('</g></svg>')
    return "\n".join(s), dict(cells=n, eaten=len(eats), dur_s=dur_ms / 1000)


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--login")
    src.add_argument("--json")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()

    if args.json:
        with open(args.json, encoding="utf-8") as fh:
            payload = json.load(fh)
    else:
        payload = fetch_calendar(args.login)
    grid = build_grid(payload)

    import os
    os.makedirs(args.out, exist_ok=True)
    for name, theme in (("snake.svg", "dark"), ("snake-light.svg", "light")):
        svg, info = render(grid, PALETTES[theme])
        dst = os.path.join(args.out, name)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"{dst}: {info['eaten']}/{info['cells']} cells eaten, "
              f"one spared, loop {info['dur_s']:.1f}s, {len(svg)} bytes",
              file=sys.stderr)


if __name__ == "__main__":
    main()
