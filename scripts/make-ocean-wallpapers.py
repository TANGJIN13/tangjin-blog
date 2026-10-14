# -*- coding: utf-8 -*-
"""
生成「壮阔海洋」主题壁纸（SVG）—— 巨浪 / 风暴海 / 深渊。

和上一版（平静海景）的区别
--------------------------
上一版是「度假明信片」：地平线平直、浪很小、色调浅。看起来干净，但**不磅礴**。
磅礴来自三个东西，这一版全都补上：

  ① 尺度对比 —— 画面里必须有「小」的参照物（礁石 / 海鸟），
     否则再大的浪也读不出大。人眼靠比例判断尺度，没有参照就没有宏大。
  ② 明暗对比 —— 上一版整体都在 60~80% 明度，太平。
     这一版把天空压到 5~35%、浪尖提到 90%+，靠强对比撑出戏剧性。
  ③ 动势 —— 浪不是水平色带，而是**斜向的、有方向的**巨浪轮廓，
     带卷曲的浪头（curl）。水平线是"平静"，斜线才是"力量"。

另外加了体积光（丁达尔）和浪花飞沫 —— 这两个是"风暴感"的关键符号。

用法：python scripts/make-ocean-wallpapers.py
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'public', 'images', 'wallpapers')

W, H = 1920, 900


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, t):
    return mix(c, '#ffffff', t)


def darken(c, t):
    return mix(c, '#000000', t)


def wave(seed, base, amp, seg=6, lead=-200, trail=W + 200):
    """起伏的浪脊轮廓（闭合到底部）。振幅给大才有浪的感觉。"""
    span = trail - lead
    pts = []
    for i in range(seg + 1):
        x = lead + i * span / seg
        t = x / span
        y = base
        y += math.sin(t * math.tau * 1.0 + seed * 1.7) * amp
        y += math.sin(t * math.tau * 2.3 + seed * 0.9) * amp * 0.38
        y += math.sin(t * math.tau * 4.1 + seed * 2.3) * amp * 0.14
        pts.append((x, y))
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cx = (x0 + x1) / 2
        d += f' C{cx:.1f} {y0:.1f} {cx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}'
    d += f' L{trail:.1f} {H + 80:.1f} L{lead:.1f} {H + 80:.1f} Z'
    return d


def breaker(cx, cy, size):
    """
    一个卷曲的巨浪（breaker）—— 这是"磅礴"的核心元素。
    形状：左侧隆起的浪脊 → 向右卷曲的浪头（lip）→ 下方掏空的浪管。
    浪头用贝塞尔勾出卷曲感，再叠一道亮边表示被光照透的水体。
    """
    s = size
    body = (
        f'M{cx - s * 1.15:.0f} {cy + s * 0.55:.0f} '
        f'C{cx - s * 0.95:.0f} {cy - s * 0.42:.0f} '
        f'{cx - s * 0.42:.0f} {cy - s * 0.92:.0f} '
        f'{cx + s * 0.06:.0f} {cy - s * 0.86:.0f} '
        f'C{cx + s * 0.52:.0f} {cy - s * 0.81:.0f} '
        f'{cx + s * 0.86:.0f} {cy - s * 0.5:.0f} '
        f'{cx + s * 0.92:.0f} {cy - s * 0.06:.0f} '
        f'C{cx + s * 0.95:.0f} {cy + s * 0.3:.0f} '
        f'{cx + s * 0.6:.0f} {cy + s * 0.5:.0f} '
        f'{cx + s * 0.3:.0f} {cy + s * 0.38:.0f} '
        f'C{cx + s * 0.05:.0f} {cy + s * 0.26:.0f} '
        f'{cx - s * 0.1:.0f} {cy + s * 0.42:.0f} '
        f'{cx - s * 0.18:.0f} {cy + s * 0.55:.0f} Z'
    )
    lip = (
        f'M{cx - s * 0.62:.0f} {cy - s * 0.66:.0f} '
        f'C{cx - s * 0.3:.0f} {cy - s * 0.95:.0f} '
        f'{cx + s * 0.2:.0f} {cy - s * 0.9:.0f} '
        f'{cx + s * 0.62:.0f} {cy - s * 0.62:.0f} '
        f'C{cx + s * 0.86:.0f} {cy - s * 0.42:.0f} '
        f'{cx + s * 0.94:.0f} {cy - s * 0.2:.0f} '
        f'{cx + s * 0.92:.0f} {cy - s * 0.05:.0f}'
    )
    return body, lip


def build(name, sky, sea_deep, sea_mid, sun, glow, foam,
          sun_xy=(1420, 190), sun_r=54, sun_rx=520, sun_ry=340,
          breakers=None, rocks=None, birds=True, stars=False, storm=False):
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
    a('<defs>')

    a('<linearGradient id="sky" x1="0" y1="0" x2="0.1" y2="1">')
    for off, col in sky:
        a(f'<stop offset="{off}%" stop-color="{col}"/>')
    a('</linearGradient>')

    a('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{sea_mid}"/>')
    a(f'<stop offset="100%" stop-color="{sea_deep}"/>')
    a('</linearGradient>')

    a('<radialGradient id="glow" cx="50%" cy="50%" r="50%">')
    a(f'<stop offset="0%" stop-color="{sun}" stop-opacity="0.92"/>')
    a(f'<stop offset="34%" stop-color="{glow}" stop-opacity="0.5"/>')
    a(f'<stop offset="100%" stop-color="{glow}" stop-opacity="0"/>')
    a('</radialGradient>')

    a('<linearGradient id="through" x1="0" y1="0" x2="0.3" y2="1">')
    a(f'<stop offset="0%" stop-color="{lighten(foam, 0.4)}" stop-opacity="0.9"/>')
    a(f'<stop offset="60%" stop-color="{lighten(sea_mid, 0.35)}" stop-opacity="0.5"/>')
    a(f'<stop offset="100%" stop-color="{sea_mid}" stop-opacity="0"/>')
    a('</linearGradient>')

    a('<filter id="b1" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="12"/></filter>')
    a('<filter id="b2" x="-40%" y="-40%" width="180%" height="180%">'
      '<feGaussianBlur stdDeviation="34"/></filter>')
    a('<filter id="b3" x="-50%" y="-50%" width="200%" height="200%">'
      '<feGaussianBlur stdDeviation="70"/></filter>')
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

    if stars:
        a('<g fill="#ffffff">')
        rnd = 991
        for _ in range(60):
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            x = (rnd % (W - 80)) + 40
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            y = (rnd % 300) + 16
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            r = 0.9 + (rnd % 100) / 100.0 * 1.7
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            o = 0.25 + (rnd % 100) / 100.0 * 0.55
            a(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" opacity="{o:.2f}"/>')
        a('</g>')

    sx, sy = sun_xy

    if storm:
        a('<g filter="url(#b3)">')
        for cx, cy, rx, ry, op, col in [
            (300, 96, 620, 130, 0.72, darken(sky[-1][1], 0.3)),
            (1180, 62, 700, 150, 0.62, darken(sky[-1][1], 0.24)),
            (780, 176, 560, 96, 0.5, darken(sky[-1][1], 0.16)),
            (1620, 150, 480, 110, 0.44, darken(sky[-1][1], 0.2)),
            (140, 230, 420, 78, 0.34, darken(sky[-1][1], 0.1)),
        ]:
            a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}"/>')
        a('</g>')

    # 体积光：从云隙打下来的斜光柱
    a('<g filter="url(#b2)" opacity="0.5">')
    rnd = 4242
    for i in range(6):
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        x = 180 + i * 300 + (rnd % 120)
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        w = 60 + (rnd % 90)
        a(f'<rect x="{x}" y="-140" width="{w}" height="{H * 0.95:.0f}" '
          f'fill="{lighten(glow, 0.35)}" opacity="0.4" '
          f'transform="rotate(-15 {x} 300)"/>')
    a('</g>')

    a(f'<ellipse cx="{sx}" cy="{sy}" rx="{sun_rx}" ry="{sun_ry}" fill="url(#glow)"/>')
    a(f'<circle cx="{sx}" cy="{sy}" r="{sun_r}" fill="{sun}" opacity="0.9" filter="url(#b1)"/>')

    # 远景海面
    a(f'<rect x="0" y="{H * 0.42:.0f}" width="{W}" height="{H * 0.6:.0f}" fill="url(#sea)" opacity="0.9"/>')

    if rocks:
        a(f'<g fill="{darken(sea_deep, 0.32)}">')
        for rx, rw, rh in rocks:
            a(f'<path d="M{rx - rw} {H * 0.44:.0f} '
              f'Q{rx - rw * 0.5} {H * 0.44 - rh:.0f} {rx - rw * 0.15} {H * 0.44 - rh * 1.15:.0f} '
              f'Q{rx + rw * 0.3} {H * 0.44 - rh * 0.6:.0f} {rx + rw * 0.6} {H * 0.44 - rh * 0.3:.0f} '
              f'Q{rx + rw * 0.85} {H * 0.44 - rh * 0.1:.0f} {rx + rw} {H * 0.44:.0f} Z"/>')
        a('</g>')

    # 中景浪层
    layers = [
        (H * 0.50, 22, 0.14, 0.66),
        (H * 0.60, 38, 0.34, 0.78),
        (H * 0.72, 56, 0.58, 0.88),
    ]
    for i, (base, amp, t, op) in enumerate(layers):
        col = mix(sea_mid, sea_deep, t)
        a(f'<path d="{wave(i * 1.7 + 0.6, base, amp)}" fill="{col}" opacity="{op}"/>')
        a(f'<ellipse cx="{W * 0.42:.0f}" cy="{base - amp * 0.5:.0f}" rx="{W * 0.62:.0f}" '
          f'ry="{16 + i * 7}" fill="{lighten(foam, 0.5)}" opacity="{0.2 + i * 0.06:.2f}" filter="url(#b2)"/>')

    # 前景巨浪
    if breakers:
        for (cx, cy, size, _seed) in breakers:
            body, lip = breaker(cx, cy, size)
            a(f'<path d="{body}" fill="{darken(sea_deep, 0.08)}" opacity="0.96"/>')
            a(f'<path d="{body}" fill="url(#through)" opacity="0.55"/>')
            a(f'<path d="{lip}" fill="none" stroke="{lighten(foam, 0.3)}" '
              f'stroke-width="{max(3, size * 0.055):.0f}" stroke-linecap="round" opacity="0.75"/>')
            a(f'<ellipse cx="{cx + size * 0.2:.0f}" cy="{cy - size * 0.78:.0f}" '
              f'rx="{size * 0.72:.0f}" ry="{size * 0.3:.0f}" '
              f'fill="{lighten(foam, 0.55)}" opacity="0.3" filter="url(#b2)"/>')

    # 飞沫
    a(f'<g fill="{lighten(foam, 0.5)}">')
    rnd = 777
    n = 70 if storm else 40
    for _ in range(n):
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        x = (rnd % W)
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        y = int(H * 0.42) + (rnd % int(H * 0.58))
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        r = 1.2 + (rnd % 100) / 100.0 * 3.4
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        o = 0.16 + (rnd % 100) / 100.0 * 0.5
        a(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" opacity="{o:.2f}"/>')
    a('</g>')

    # 海鸟：最关键的尺度参照 —— 有鸟才知道浪有多大
    if birds:
        a(f'<g fill="none" stroke="{darken(sky[0][1], 0.42)}" stroke-width="2.6" '
          f'stroke-linecap="round" opacity="0.62">')
        for bx, by, bs in [(1180, 268, 1.0), (1252, 236, 0.78), (1096, 232, 0.66),
                           (1318, 292, 0.58), (1024, 288, 0.5)]:
            a(f'<path d="M{bx} {by} q{9 * bs:.0f} {-7 * bs:.0f} {18 * bs:.0f} 0 '
              f'M{bx + 18 * bs:.0f} {by} q{9 * bs:.0f} {-7 * bs:.0f} {18 * bs:.0f} 0"/>')
        a('</g>')

    a('<radialGradient id="vig" cx="50%" cy="38%" r="76%">'
      '<stop offset="52%" stop-color="#000" stop-opacity="0"/>'
      '<stop offset="100%" stop-color="#000" stop-opacity="0.3"/>'
      '</radialGradient>')
    a(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
    a('</svg>')

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    with open(p, 'w', encoding='utf-8') as f:
        f.write('\n'.join(s))
    return p, len('\n'.join(s))


THEMES = [
    # ① 巨浪 · 破晓 —— 冷灰蓝的天空 + 一道透光的巨浪
    dict(
        name='banner-ocean-dawn.svg',
        sky=[(0, '#1b2a3e'), (26, '#2d4358'), (52, '#4d6a7d'), (74, '#8a94a0'), (100, '#c3a894')],
        sea_deep='#0d1b2a', sea_mid='#28455f',
        sun='#ffe6c4', glow='#e8a97a', foam='#fff4e4',
        sun_xy=(1520, 250), sun_r=62, sun_rx=640, sun_ry=380,
        breakers=[(560, 720, 250, 1.0), (1420, 810, 320, 2.1)],
        rocks=[(1680, 150, 90), (300, 96, 54)],
        storm=False,
    ),
    # ② 风暴海 —— 最暗、最有压迫感的一张
    dict(
        name='banner-ocean-day.svg',
        sky=[(0, '#0a1018'), (24, '#16222e'), (50, '#2b3b4a'), (72, '#4a5a66'), (100, '#7d8a92')],
        sea_deep='#05090f', sea_mid='#1b2f42',
        sun='#e8f2ff', glow='#8fb4d4', foam='#ffffff',
        sun_xy=(900, 170), sun_r=44, sun_rx=560, sun_ry=300,
        breakers=[(400, 690, 290, 3.3), (1120, 760, 350, 4.7), (1720, 840, 240, 5.2)],
        rocks=[(1520, 180, 130)],
        storm=True,
    ),
    # ③ 落日巨浪 —— 暖冷对撞，情绪最浓
    dict(
        name='banner-ocean-dusk.svg',
        sky=[(0, '#2a1f3a'), (22, '#5c3350'), (44, '#a85a52'), (64, '#e08a52'), (82, '#f0b878'), (100, '#f7d9a8')],
        sea_deep='#12101f', sea_mid='#4a3350',
        sun='#fff0cf', glow='#f09a58', foam='#ffe9c8',
        sun_xy=(1320, 470), sun_r=88, sun_rx=760, sun_ry=260,
        breakers=[(620, 700, 270, 1.9), (1560, 800, 300, 3.7)],
        rocks=[(240, 140, 76)],
        storm=False,
    ),
    # ④ 深渊月夜 —— 月光下的一条巨浪，冷到发蓝
    dict(
        name='banner-ocean-night.svg',
        sky=[(0, '#04070f'), (28, '#0a1526'), (54, '#12253d'), (76, '#1d3a56'), (100, '#2c5470')],
        sea_deep='#02050b', sea_mid='#0e2036',
        sun='#f4f9ff', glow='#7fb0dc', foam='#dceaf8',
        sun_xy=(1420, 150), sun_r=40, sun_rx=520, sun_ry=340,
        breakers=[(700, 730, 300, 2.7), (1660, 830, 260, 4.1)],
        rocks=[(1360, 170, 110)],
        stars=True, storm=False,
    ),
]

if __name__ == '__main__':
    for t in THEMES:
        p, n = build(**t)
        print(f'{os.path.basename(p):32s} {n / 1024:6.1f} KB')
