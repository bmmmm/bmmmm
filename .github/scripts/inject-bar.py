#!/usr/bin/env python3
"""Inject a contribution-harvest bar below a Platane/snk snake SVG.

The bar is coupled to the snake: it steps forward exactly when the snake eats
a green cell (read from each cell's @keyframes eat-time), so the eaten squares
look like they pile into the bar below. When the snake is done the bar tips
purple and a calm 'coffee: EAGAIN' note holds until the loop restarts.

Runs as a post-processing step (the snake is regenerated nightly). Fail-soft:
on any unexpected shape the original SVG is left intact so the workflow still
publishes a working snake instead of breaking the README.
"""
import re
import sys

BAR_H = 78           # extra viewBox height for the bar strip
GREEN = "#39d353"    # harvest fill (matches the brightest contribution cells)
PURPLE = "#bf00ff"   # coffee / stalled state (matches the snake)
TRACK_W = 820
TRACK_X = 0
TRACK_Y = 22
TRACK_H = 18


def parse_eat_times(svg):
    return sorted(float(x) for x in
                  re.findall(r"@keyframes c\d+\{([\d.]+)%", svg))


def parse_dur_ms(svg):
    m = re.search(r"animation:\s*none\s+(\d+)ms", svg)
    return int(m.group(1)) if m else 70100


def step_anim(eat_times):
    """Build (keyTimes, values) for a width that jumps on each eat event."""
    n = len(eat_times)
    step = TRACK_W / n
    kts, vals = [0.0], [0.0]
    for i, t in enumerate(eat_times):
        kts.append(t / 100.0)
        vals.append(min((i + 1) * step, TRACK_W))
    if kts[-1] < 1.0:                 # hold full until the loop restarts
        kts.append(1.0)
        vals.append(TRACK_W)
    out_k, out_v, last = [], [], -1.0  # enforce strictly increasing keyTimes
    for k, v in zip(kts, vals):
        if k <= last:
            k = last + 1e-6
        k = min(k, 1.0)
        out_k.append(k)
        out_v.append(v)
        last = k
    return (";".join(f"{k:.6f}" for k in out_k),
            ";".join(f"{v:.1f}" for v in out_v))


def build_bar(base_y, eat_times, dur_ms):
    by = f"{base_y:g}"
    dur = f"{dur_ms}ms"
    kstr, vstr = step_anim(eat_times)
    done = max(eat_times) / 100.0           # snake finished here
    flip_end = min(done + 0.022, 0.96)
    harv_out0 = max(done - 0.05, 0.0)       # harvest label fades out early,
    harv_out1 = max(done - 0.025, 0.0)      # leaving a gap before coffee shows
    coffee_dim = 0.965                       # coffee fully gone well before the
    coffee_gone = 0.985                      # loop seam, so nothing overlaps
    n = len(eat_times)
    return (
        f'<g transform="translate(0,{by})" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
        # track
        f'<rect x="{TRACK_X}" y="{TRACK_Y}" width="{TRACK_W}" height="{TRACK_H}"'
        f' rx="3" fill="#161b22" stroke="#30363d"/>'
        # harvest fill: steps with every eaten cell, then tips purple when done
        f'<rect x="{TRACK_X}" y="{TRACK_Y}" height="{TRACK_H}" rx="3" '
        f'fill="{GREEN}">'
        f'<animate attributeName="width" calcMode="discrete" values="{vstr}" '
        f'keyTimes="{kstr}" dur="{dur}" repeatCount="indefinite"/>'
        f'<animate attributeName="fill" values="{GREEN};{GREEN};{PURPLE}" '
        f'keyTimes="0;{done:.4f};{flip_end:.4f}" dur="{dur}" '
        f'repeatCount="indefinite"/></rect>'
        # label while harvesting (dim)
        f'<text x="2" y="62" font-size="12" fill="#8b949e">'
        f'harvesting {n} contributions...'
        f'<animate attributeName="opacity" values="1;1;0;0" '
        f'keyTimes="0;{harv_out0:.4f};{harv_out1:.4f};1" dur="{dur}" '
        f'repeatCount="indefinite"/></text>'
        # coffee note when done (big, calm, holds ~loop end)
        f'<text x="2" y="63" font-size="17" fill="{PURPLE}" opacity="0">'
        f'coffee: EAGAIN, refill required'
        f'<animate attributeName="opacity" values="0;0;1;1;0;0" '
        f'keyTimes="0;{done:.4f};{flip_end:.4f};{coffee_dim:.4f};'
        f'{coffee_gone:.4f};1" dur="{dur}" repeatCount="indefinite"/></text>'
        f'</g>'
    )


def main():
    if len(sys.argv) < 2:
        print("usage: inject-bar.py <snake.svg>", file=sys.stderr)
        return 0
    path = sys.argv[1]
    with open(path, encoding="utf-8") as fh:
        svg = fh.read()

    tag = re.search(r"<svg\b[^>]*>", svg)
    vb = re.search(
        r'viewBox="(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)"', svg)
    eat_times = parse_eat_times(svg)
    if not tag or not vb or not eat_times:
        print("inject-bar: unexpected snake shape, leaving it untouched",
              file=sys.stderr)
        return 0

    min_y = float(vb.group(2))
    vb_h = float(vb.group(4))
    new_vb_h = vb_h + BAR_H
    base_y = min_y + vb_h

    open_tag = tag.group(0)
    new_open = re.sub(
        r'(viewBox="-?[\d.]+\s+-?[\d.]+\s+-?[\d.]+\s+)-?[\d.]+(")',
        lambda m: f"{m.group(1)}{new_vb_h:g}{m.group(2)}", open_tag, count=1)
    new_open = re.sub(
        r'(\bheight=")([\d.]+)(")',
        lambda m: f"{m.group(1)}{float(m.group(2)) + BAR_H:g}{m.group(3)}",
        new_open, count=1)

    svg = svg.replace(open_tag, new_open, 1)
    idx = svg.rfind("</svg>")
    svg = svg[:idx] + build_bar(base_y, eat_times, parse_dur_ms(svg)) + svg[idx:]

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"inject-bar: {len(eat_times)} steps, dur {parse_dur_ms(svg)}ms, "
          f"viewBox h {vb_h:g}->{new_vb_h:g}", file=sys.stderr)
    return 0


sys.exit(main())
