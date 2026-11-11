"""Draws the five figures in the AAR write-up as SVG files in src/charts.

The numbers are the ones behind the charts in the original report.
Run:  python3 scripts/aar_charts.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'src' / 'charts'
BLUE, OCHRE, TEAL, RUST, GRAY = '#2B63A8', '#B8780A', '#0A9480', '#B5532E', '#8A929C'
W = 760


def svg(height, label, body):
    return (f'<svg class="chart" viewBox="0 0 {W} {height}" role="img" aria-label="{label}" '
            f'xmlns="http://www.w3.org/2000/svg">\n{body}\n</svg>\n')


def text(x, y, s, cls='', anchor='start'):
    c = f' class="{cls}"' if cls else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}"{c}>{s}</text>'


def bar(x, y_base, y_val, w, color, tip, r=4):
    """A bar from the baseline to its value, rounded only at the value end."""
    r = min(r, abs(y_val - y_base) / 2, w / 2)
    s = 1 if y_val > y_base else -1   # 1: bar hangs down (negative value)
    d = (f'M{x:.1f},{y_base:.1f} L{x:.1f},{y_val - s * r:.1f} Q{x:.1f},{y_val:.1f} {x + r:.1f},{y_val:.1f} '
         f'L{x + w - r:.1f},{y_val:.1f} Q{x + w:.1f},{y_val:.1f} {x + w:.1f},{y_val - s * r:.1f} L{x + w:.1f},{y_base:.1f} Z')
    return f'<path d="{d}" fill="{color}"><title>{tip}</title></path>'


def legend(items, x, y):
    out = []
    for name, color, dash in items:
        if dash is None:
            out.append(f'<rect x="{x}" y="{y - 9}" width="10" height="10" rx="2" fill="{color}"/>')
        else:
            out.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 18}" y2="{y - 4}" stroke="{color}" stroke-width="2" stroke-dasharray="{dash}"/>')
        tx = x + (16 if dash is None else 24)
        out.append(text(tx, y, name))
        x = tx + 7.0 * len(name) + 22
    return '\n'.join(out)


def grid(ticks, scale, x0, x1, fmt, zero=None):
    out = []
    for t in ticks:
        y = scale(t)
        cls = 'axis' if zero is not None and abs(t - zero) < 1e-9 else 'grid'
        out.append(f'<line class="{cls}" x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}"/>')
        out.append(text(x0 - 8, y + 4, fmt(t), anchor='end'))
    return '\n'.join(out)


def pct(v, d=1):
    return f'{v * 100:+.{d}f}%'.replace('+', '+').replace('-', '−')


# 1. Selloff: grouped bars -------------------------------------------------
def selloff():
    cats = ['AIR', 'VSE (VSEC)', 'HEICO (HEI)', 'Airlines ETF (JETS)']
    series = [('Pre-deal (Aug 17 to Sept 28)', BLUE, [-0.251, -0.283, -0.18, -0.076]),
              ('Deal reaction (Sept 28 to Oct 5)', OCHRE, [-0.112, -0.037, -0.01, -0.021]),
              ('After (Oct 5 to Oct 26)', TEAL, [-0.048, -0.121, 0.027, -0.052])]
    H, x0, x1, top, bot = 350, 56, W - 16, 78, 312
    lo, hi = -0.30, 0.05
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    b = [text(0, 18, 'Most of AIR’s drop was sector-wide', 't'),
         legend([(n, c, None) for n, c, _ in series], 0, 46),
         grid([0.0, -0.1, -0.2, -0.3], sc, x0, x1, lambda t: f'{t * 100:.0f}%'.replace('-', '−'), zero=0.0)]
    gw = (x1 - x0) / len(cats)
    bw, gap = 38, 2
    for i, cat in enumerate(cats):
        gx = x0 + gw * i + (gw - (3 * bw + 2 * gap)) / 2
        for j, (name, color, vals) in enumerate(series):
            v = vals[i]
            x = gx + j * (bw + gap)
            b.append(bar(x, sc(0), sc(v), bw, color, f'{cat}, {name}: {pct(v)}'))
            if i == 0:   # label only the subject of the report
                b.append(text(x + bw / 2, sc(v) + 15, pct(v), 'v', 'middle'))
        b.append(text(x0 + gw * i + gw / 2, bot + 28, cat, 'cat', 'middle'))
    return svg(H, 'Share price change by period for AIR, VSE, HEICO and the airlines ETF', '\n'.join(b))


# 2. Margin bridge: waterfall ------------------------------------------------
def bridge():
    steps = [('FY2026 pro forma', 0.15926, True), ('Mix shift', 0.00218, False),
             ('AAR margin gains', 0.01415, False), ('Cost synergies', 0.01257, False), ('FY2030E', 0.18817, True)]
    H, x0, x1, top, bot = 330, 56, W - 16, 56, 284
    lo, hi = 0.15, 0.20
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    b = [text(0, 18, 'Base case lands just short of 19%', 't'),
         text(0, 38, 'Combined EBITDA margin. Axis starts at 15% to show the steps.'),
         grid([0.15, 0.16, 0.17, 0.18, 0.19, 0.20], sc, x0, x1, lambda t: f'{t * 100:.0f}%')]
    # management's 19-20% target band
    b.append(f'<rect x="{x0}" y="{sc(0.20):.1f}" width="{x1 - x0}" height="{sc(0.19) - sc(0.20):.1f}" fill="{GRAY}" opacity="0.14"/>')
    b.append(text(x1 - 6, sc(0.195) + 4, 'Management target, 19% to 20%', anchor='end'))
    gw = (x1 - x0) / len(steps)
    bw = 84
    running = 0.0
    for i, (name, v, total) in enumerate(steps):
        x = x0 + gw * i + (gw - bw) / 2
        if total:
            running = v
            b.append(bar(x, sc(lo), sc(v), bw, BLUE, f'{name}: {v * 100:.1f}%'))
            b.append(text(x + bw / 2, sc(v) - 8, f'{v * 100:.1f}%', 'v', 'middle'))
        else:
            b.append(bar(x, sc(running), sc(running + v), bw, TEAL, f'{name}: +{v * 100:.1f} points', r=2))
            b.append(text(x + bw / 2, sc(running + v) - 8, f'+{v * 100:.1f} pts', 'v', 'middle'))
            running += v
        if i < len(steps) - 1:   # connector to the next bar
            nx = x0 + gw * (i + 1) + (gw - bw) / 2
            b.append(f'<line class="axis" x1="{x + bw:.1f}" y1="{sc(running):.1f}" x2="{nx:.1f}" y2="{sc(running):.1f}"/>')
        b.append(text(x0 + gw * i + gw / 2, bot + 24, name, 'cat', 'middle'))
    return svg(H, 'Bridge from a 15.9% combined EBITDA margin in fiscal 2026 to 18.8% in fiscal 2030', '\n'.join(b))


# 3. Leverage paths: lines ---------------------------------------------------
def leverage():
    years = ['FY2027 (close)', 'FY2028', 'FY2029', 'FY2030']
    lines = [('Bear', RUST, None, [4.047, 3.721, 3.396, 3.135]),
             ('Base', BLUE, None, [3.773, 3.067, 2.423, 1.909]),
             ('Base, rates +2 pts', BLUE, '5 4', [3.773, 3.086, 2.456, 1.952]),
             ('Bull', TEAL, None, [3.624, 2.716, 1.922, 1.306])]
    H, x0, x1, top, bot = 360, 56, W - 150, 78, 318
    lo, hi = 1.0, 4.5
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    xs = [x0 + 30 + i * (x1 - x0 - 60) / 3 for i in range(4)]
    b = [text(0, 18, 'Cash flow, not rates, drives leverage', 't'),
         legend([(n, c, d or '0') for n, c, d, _ in lines] + [('Management target', GRAY, '2 4')], 0, 46),
         grid([1, 2, 3, 4], sc, x0, x1, lambda t: f'{t:.1f}x')]
    b.append(f'<line x1="{x0}" y1="{sc(3):.1f}" x2="{x1}" y2="{sc(3):.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="2 4"/>')
    for name, color, dash, vals in lines:
        pts = ' '.join(f'{x:.1f},{sc(v):.1f}' for x, v in zip(xs, vals))
        da = f' stroke-dasharray="{dash}"' if dash else ''
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"{da}/>')
        if not dash:
            for x, v, yr in zip(xs, vals, years):
                b.append(f'<circle cx="{x:.1f}" cy="{sc(v):.1f}" r="4" fill="{color}" stroke="#fff" stroke-width="2"><title>{name}, {yr}: {v:.1f}x</title></circle>')
    b.append(text(xs[-1] + 12, sc(3.135) + 4, 'Bear 3.1x', 'v'))
    b.append(text(xs[-1] + 12, sc(1.93) + 4, 'Base 1.9x', 'v'))
    b.append(text(xs[-1] + 12, sc(1.93) + 19, '(2.0x if rates +2 pts)'))
    b.append(text(xs[-1] + 12, sc(1.306) + 4, 'Bull 1.3x', 'v'))
    for x, yr in zip(xs, years):
        b.append(text(x, bot + 24, yr, 'cat', 'middle'))
    b.append(text(0, 70, 'Net debt / EBITDA'))
    return svg(H, 'Net debt to EBITDA from closing to fiscal 2030 under bear, base and bull cases', '\n'.join(b))


# 4. Accretion by synergies: bars ---------------------------------------------
def accretion():
    data = [('0%', -0.03178), ('25%', 0.01262), ('50%', 0.05702), ('75%', 0.10143), ('100%', 0.14583)]
    H, x0, x1, top, bot = 330, 56, W - 16, 56, 270
    lo, hi = -0.05, 0.16
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    b = [text(0, 18, 'Year-one accretion hinges on synergies', 't'),
         text(0, 38, 'Change in FY2028 EPS vs AAR on its own, by share of the $75M synergies achieved'),
         grid([-0.05, 0.0, 0.05, 0.10, 0.15], sc, x0, x1, lambda t: f'{t * 100:.0f}%'.replace('-', '−'), zero=0.0)]
    gw = (x1 - x0) / len(data)
    bw = 72
    for i, (cat, v) in enumerate(data):
        x = x0 + gw * i + (gw - bw) / 2
        b.append(bar(x, sc(0), sc(v), bw, BLUE, f'{cat} of synergies: {pct(v)} EPS'))
        b.append(text(x + bw / 2, sc(v) + (16 if v < 0 else -8), pct(v), 'v', 'middle'))
        b.append(text(x0 + gw * i + gw / 2, bot + 30, cat, 'cat', 'middle'))
        if cat == '25%':
            b.append(text(x0 + gw * i + gw / 2, bot + 46, 'my assumption', anchor='middle'))
    return svg(H, 'Change in fiscal 2028 earnings per share at 0, 25, 50, 75 and 100 percent of synergies', '\n'.join(b))


# 5. Multiple vs margin: scatter ---------------------------------------------
def multiple():
    pts = [('VSE', 0.16, 23.5, BLUE, 'r', True), ('HEICO', 0.28, 32.0, BLUE, 'r', True),
           ('FTAI', 0.32, 19.4, BLUE, 'l', True), ('AerSale', 0.079, 16.7, BLUE, 'r', True),
           ('AAR, Oct 26', 0.108, 12.7, RUST, 'b', True), ('AAR + MRO', 0.147, 12.6, TEAL, 'r', True),
           ('AAR, Sept 28', 0.108, 14.62, RUST, 'l', False)]
    H, x0, x1, top, bot = 380, 56, W - 16, 78, 322
    xlo, xhi, ylo, yhi = 0.05, 0.35, 10, 35
    sx = lambda v: x0 + (v - xlo) / (xhi - xlo) * (x1 - x0)
    sy = lambda v: top + (yhi - v) / (yhi - ylo) * (bot - top)
    b = [text(0, 18, 'AAR’s multiple lags its margins', 't'),
         legend([('Peers', BLUE, None), ('AAR', RUST, None), ('AAR + MRO', TEAL, None)], 0, 46),
         text(0, 70, 'EV / EBITDA'),
         grid([10, 15, 20, 25, 30, 35], sy, x0, x1, lambda t: f'{t}x')]
    for t in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]:
        b.append(text(sx(t), bot + 20, f'{t * 100:.0f}%', anchor='middle'))
    b.append(text((x0 + x1) / 2, bot + 42, 'EBITDA margin', anchor='middle'))
    for name, mx, my, color, side, solid in pts:
        x, y = sx(mx), sy(my)
        fill = color if solid else '#fff'
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{fill}" stroke="{color if not solid else "#fff"}" stroke-width="2">'
                 f'<title>{name}: {my:.1f}x EV/EBITDA at a {mx * 100:.1f}% margin</title></circle>')
        label = f'{name} {my:.1f}x'
        if side == 'r':
            b.append(text(x + 12, y + 4, label, 'v'))
        elif side == 'l':
            b.append(text(x - 12, y + 4, label, 'v', 'end'))
        else:
            b.append(text(x, y + 22, label, 'v', 'middle'))
    return svg(H, 'EV to EBITDA multiple against EBITDA margin for AAR, AAR plus MRO and four peers', '\n'.join(b))


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [('aar-selloff', selloff), ('aar-bridge', bridge), ('aar-leverage', leverage),
                     ('aar-accretion', accretion), ('aar-multiple', multiple)]:
        (OUT / f'{name}.svg').write_text(fn(), encoding='utf-8')
        print('wrote', name)
