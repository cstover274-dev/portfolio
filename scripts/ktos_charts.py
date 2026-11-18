"""Draws the figures in the Kratos write-up as SVG files in src/charts.

Numbers come from the KTOS model (Dashboard, Comps and DCF tabs) as of Nov 13, 2026.
Run:  python3 scripts/ktos_charts.py
"""
from aar_charts import OUT, BLUE, OCHRE, TEAL, RUST, GRAY, W, svg, text, bar, grid


def money(v):
    return ('−' if v < 0 else '') + f'${abs(v):,.0f}M'


# Figure 2: margin bridge (waterfall) -------------------------------------
def bridge():
    steps = [('2026E margin', 0.08906, True), ('Gross margin', 0.00406, False), ('SG&amp;A leverage', 0.04404, False),
             ('R&amp;D and M&amp;A', 0.00019, False), ('D&amp;A and stock comp', -0.03554, False), ('2036E margin', 0.10181, True)]
    H, x0, x1, top, bot = 330, 56, W - 16, 56, 284
    lo, hi = 0.06, 0.14
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    b = [text(0, 18, 'SG&amp;A does nearly all the work', 't'),
         text(0, 38, 'Adjusted EBITDA margin, my definition. Axis starts at 6% to show the steps.'),
         grid([0.06, 0.08, 0.10, 0.12, 0.14], sc, x0, x1, lambda t: f'{t * 100:.0f}%')]
    gw = (x1 - x0) / len(steps)
    bw = 76
    running = 0.0
    for i, (name, v, total) in enumerate(steps):
        x = x0 + gw * i + (gw - bw) / 2
        if total:
            running = v
            b.append(bar(x, sc(lo), sc(v), bw, BLUE, f'{name}: {v * 100:.1f}%'))
            b.append(text(x + bw / 2, sc(v) - 8, f'{v * 100:.1f}%', 'v', 'middle'))
        else:
            color = TEAL if v >= 0 else RUST
            end = running + v
            b.append(bar(x, sc(running), sc(end), bw, color, f'{name}: {v * 100:+.1f} points', r=2))
            label = f'{v * 100:+.1f} pts'.replace('-', '−')
            b.append(text(x + bw / 2, (sc(end) - 8) if v >= 0 else (sc(end) + 16), label, 'v', 'middle'))
            running = end
        if i < len(steps) - 1:
            nx = x0 + gw * (i + 1) + (gw - bw) / 2
            b.append(f'<line class="axis" x1="{x + bw:.1f}" y1="{sc(running):.1f}" x2="{nx:.1f}" y2="{sc(running):.1f}"/>')
        b.append(text(x0 + gw * i + gw / 2, bot + 24, name, 'cat', 'middle'))
    return svg(H, 'Bridge from an 8.9% adjusted EBITDA margin in 2026 to 10.2% in 2036', '\n'.join(b))


# Figure 3: cumulative free cash flow -------------------------------------
def cumulative_fcf():
    years = ['2027E', '2028E', '2029E', '2030E', '2031E', '2032E', '2033E', '2034E', '2035E', '2036E']
    vals = [-181.3, -345.0, -369.3, -324.7, -188.5, -46.0, 54.3, 163.3, 290.3, 439.4]
    H, x0, x1, top, bot = 320, 64, W - 16, 48, 280
    lo, hi = -400, 500
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    b = [text(0, 18, 'Shareholders wait until 2033', 't'),
         text(0, 38, 'Cumulative free cash flow after stock compensation and Prometheus funding, base case'),
         grid([-400, -200, 0, 200, 400], sc, x0, x1, lambda t: money(t), zero=0)]
    gw = (x1 - x0) / len(years)
    bw = 44
    for i, (yr, v) in enumerate(zip(years, vals)):
        x = x0 + gw * i + (gw - bw) / 2
        b.append(bar(x, sc(0), sc(v), bw, TEAL if v >= 0 else RUST, f'{yr}: {money(v)}'))
        if yr in ('2029E', '2033E', '2036E'):
            b.append(text(x + bw / 2, sc(v) + (16 if v < 0 else -8), money(v), 'v', 'middle'))
        b.append(text(x + bw / 2, bot + 22, yr, 'cat', 'middle'))
    return svg(H, 'Cumulative free cash flow from 2027 to 2036, bottoming near minus 369 million dollars in 2029 and turning positive in 2033', '\n'.join(b))


# Figure 4: unbilled receivables -------------------------------------------
def unbilled():
    data = [('FY2023', 70.5, '$200M', False), ('FY2024', 66.3, '$206M', False), ('FY2025', 79.2, '$292M', False),
            ('FY2026E', 93.5, '$460M', True), ('FY2027E', 95.0, '$582M', True)]
    H, x0, x1, top, bot = 320, 56, W - 16, 56, 270
    lo, hi = 0, 120
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    b = ['<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         f'<rect width="6" height="6" fill="{BLUE}" opacity="0.35"/><line x1="0" y1="0" x2="0" y2="6" stroke="{BLUE}" stroke-width="3"/></pattern></defs>',
         text(0, 18, 'More revenue is waiting to be billed', 't'),
         text(0, 38, 'Unbilled receivables in days of revenue. Hatched bars are estimates.'),
         grid([0, 30, 60, 90, 120], sc, x0, x1, lambda t: f'{t:.0f}', zero=0)]
    gw = (x1 - x0) / len(data)
    bw = 72
    for i, (yr, days, amt, est) in enumerate(data):
        x = x0 + gw * i + (gw - bw) / 2
        b.append(bar(x, sc(0), sc(days), bw, 'url(#hatch)' if est else BLUE, f'{yr}: {days:.0f} days ({amt})'))
        b.append(text(x + bw / 2, sc(days) - 8, f'{days:.0f} days ({amt})', 'v', 'middle'))
        b.append(text(x + bw / 2, bot + 22, yr, 'cat', 'middle'))
    return svg(H, 'Unbilled receivables rising from 71 days of revenue in 2023 to an estimated 95 days in 2027', '\n'.join(b))


# Figure 5: EV/EBITDA vs kept peers ----------------------------------------
def peers():
    # Comps tab, row 19 (TIKR forward EV/EBITDA, fiscal 2027, Nov 13, 2026). Mercury is trimmed as an outlier.
    data = [('KTOS', 21.82), ('WWD', 19.86), ('AVAV', 19.46), ('CW', 18.80), ('ATI', 18.19), ('BWXT', 17.54), ('DRS', 15.33)]
    median = 18.495
    H, x0, x1, top, bot = 330, 56, W - 16, 56, 280
    lo, hi = 0, 25
    sc = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    b = [text(0, 18, 'Kratos trades above every peer I keep', 't'),
         text(0, 38, 'EV / 2027 EBITDA. Line: peer median, 18.5x.'),
         grid([0, 5, 10, 15, 20, 25], sc, x0, x1, lambda t: f'{t:.0f}x', zero=0)]
    gw = (x1 - x0) / len(data)
    bw = 60
    for i, (name, m) in enumerate(data):
        x = x0 + gw * i + (gw - bw) / 2
        b.append(bar(x, sc(0), sc(m), bw, RUST if name == 'KTOS' else BLUE, f'{name}: {m:.1f}x'))
        b.append(text(x + bw / 2, sc(m) - 8, f'{m:.1f}x', 'v', 'middle'))
        b.append(text(x + bw / 2, bot + 22, name, 'cat', 'middle'))
    b.append(f'<line x1="{x0}" y1="{sc(median):.1f}" x2="{x1}" y2="{sc(median):.1f}" stroke="{GRAY}" stroke-width="2" stroke-dasharray="5 4"/>')
    return svg(H, 'Forward EV to EBITDA: Kratos 21.8x against six peers from 15.3x to 19.9x, median 18.5x', '\n'.join(b))


# Figure 6: valuation range ------------------------------------------------
def valuation():
    rows = [('DCF, perpetual growth', 6.30, 17.29, BLUE), ('DCF, 12x exit', 11.35, 28.42, BLUE),
            ('Sum of the parts', 26.77, 28.57, TEAL), ('Peer multiple', 26.56, 28.41, TEAL),
            ('Street targets', 46.0, 120.0, GRAY), ('52-week range', 31.57, 134.0, GRAY)]
    H, x0, x1, top = 360, 170, W - 16, 56
    lo, hi = 0, 140
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    rh = 40
    bot = top + rh * len(rows)
    b = [text(0, 18, 'Every method I trust sits below the price', 't'),
         text(0, 38, 'Value per share by method, bear to bull. Line: $33.91 on Nov 13.')]
    for t in range(0, 141, 20):
        b.append(f'<line class="grid" x1="{sx(t):.1f}" y1="{top}" x2="{sx(t):.1f}" y2="{bot}"/>')
        b.append(text(sx(t), bot + 18, f'${t}', anchor='middle'))
    b.append(f'<line x1="{sx(33.91):.1f}" y1="{top - 6}" x2="{sx(33.91):.1f}" y2="{bot}" stroke="{RUST}" stroke-width="2"/>')
    for i, (name, a, z, color) in enumerate(rows):
        y = top + rh * i + 10
        b.append(text(x0 - 10, y + 15, name, 'cat', 'end'))
        b.append(f'<rect x="{sx(a):.1f}" y="{y}" width="{max(sx(z) - sx(a), 3):.1f}" height="20" rx="3" fill="{color}"><title>{name}: ${a:.2f} to ${z:.2f}</title></rect>')
        lbl = f'${a:.0f} to ${z:.0f}' if z > 40 else f'${a:.2f} to ${z:.2f}'
        if z > 125:   # no room on the right: label goes before the bar
            b.append(text(sx(a) - 8, y + 15, lbl, 'v halo', 'end'))
        else:
            b.append(text(sx(z) + 8, y + 15, lbl, 'v halo'))
    return svg(H, 'Value ranges by method against the 33.91 dollar share price', '\n'.join(b))


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [('ktos-bridge', bridge), ('ktos-fcf', cumulative_fcf), ('ktos-unbilled', unbilled),
                     ('ktos-peers', peers), ('ktos-valuation', valuation)]:
        (OUT / f'{name}.svg').write_text(fn(), encoding='utf-8')
        print('wrote', name)
