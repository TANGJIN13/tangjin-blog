# -*- coding: utf-8 -*-
"""
生成「大海」主题壁纸（SVG）。

沿用站点既有的插画语言（见 wallpaper-01.svg）：分层渐变 + 柔和模糊的
浪沫分隔 + 远处的光晕。

设计要点
--------
· 1920x800，preserveAspectRatio="xMidYMid slice"，与既有壁纸一致。
· 天空渐变承载情绪；海面用 5 条错落的色带做出纵深。
· 每条色带顶部压一道高斯模糊的亮线 —— 这是「浪沫」的关键，
  没有它色带之间就是生硬的色阶断层。
· 浪形用三组正弦叠加，振幅要足够大（40~90px）才看得出起伏；
  振幅太小会退化成一条直线，海就变成了色块。
· 日/月倒影必须画在色带**之后**，否则会被色带完全盖住。
· 中心区域保持干净 —— 首屏要压座右铭文字。

用法：python scripts/make-ocean-wallpapers.py
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'public', 'images', 'wallpapers')

W, H = 1920, 800
HORIZON = 452          # 海平线基准高度


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, t):
    return mix(c, '#ffffff', t)


def darken(c, t):
    return mix(c, '#000000', t)


def wave_path(seed, base_y, amp, segments=6, lead=-180, trail=W + 180):
    """
    起伏的海浪轮廓。

    三组正弦叠加：低频决定大的起伏走向，中频加不规则感，
    高频只做一点点毛边。用正弦（而非随机）保证同一 seed 可复现。
    """
    span = trail - lead
    pts = []
    for i in range(segments + 1):
        x = lead + i * span / segments
        t = x / span
        y = base_y
        y += math.sin(t * math.tau * 1.0 + seed * 1.7) * amp
        y += math.sin(t * math.tau * 2.0 + seed * 0.9) * amp * 0.34
        y += math.sin(t * math.tau * 3.5 + seed * 2.3) * amp * 0.13
        pts.append((x, y))

    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cx = (x0 + x1) / 2
        d += f' C{cx:.1f} {y0:.1f} {cx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}'
    d += f' L{trail:.1f} {H + 60:.1f} L{lead:.1f} {H + 60:.1f} Z'
    return d


def build(name, sky, sun_color, sun_glow, sea_shallow, sea_deep,
          sun_x=1305, sun_y=250, sun_r=54, sun_rx=470, sun_ry=300,
          foam='#ffffff', island=None, stars=False, petals=None):
    s = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
    a('<defs>')

    a('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">')
    for off, col in sky:
        a(f'<stop offset="{off}%" stop-color="{col}"/>')
    a('</linearGradient>')

    # 海面整体渐变：远处浅、近处深
    a('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{sea_shallow}"/>')
    a(f'<stop offset="100%" stop-color="{sea_deep}"/>')
    a('</linearGradient>')

    a('<radialGradient id="glow" cx="50%" cy="50%" r="50%">')
    a(f'<stop offset="0%" stop-color="{sun_color}" stop-opacity="0.95"/>')
    a(f'<stop offset="30%" stop-color="{sun_glow}" stop-opacity="0.6"/>')
    a(f'<stop offset="100%" stop-color="{sun_glow}" stop-opacity="0"/>')
    a('</radialGradient>')

    # 水面倒影：从上往下淡出的一道光柱
    a('<linearGradient id="reflect" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{lighten(sun_color, 0.25)}" stop-opacity="0.55"/>')
    a(f'<stop offset="55%" stop-color="{lighten(sun_color, 0.25)}" stop-opacity="0.2"/>')
    a(f'<stop offset="100%" stop-color="{lighten(sun_color, 0.25)}" stop-opacity="0"/>')
    a('</linearGradient>')

    # 地平线附近的光雾，让海天交界不至于是一条硬边
    a('<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{lighten(sun_glow, 0.55)}" stop-opacity="0"/>')
    a(f'<stop offset="100%" stop-color="{lighten(sun_glow, 0.55)}" stop-opacity="0.75"/>')
    a('</linearGradient>')

    a('<filter id="soft" x="-25%" y="-25%" width="150%" height="150%">'
      '<feGaussianBlur stdDeviation="14"/></filter>')
    a('<filter id="softer" x="-35%" y="-35%" width="170%" height="170%">'
      '<feGaussianBlur stdDeviation="34"/></filter>')
    a('</defs>')

    # ---------- 天空 ----------
    a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

    if stars:
        a('<g fill="#ffffff">')
        rnd = 20261014
        for i in range(52):
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            x = (rnd % (W - 80)) + 40
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            y = (rnd % 340) + 18
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            r = 0.9 + (rnd % 100) / 100.0 * 1.6
            o = 0.25 + (rnd % 100) / 100.0 * 0.55
            a(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" opacity="{o:.2f}"/>')
        a('</g>')

    # 日/月
    a(f'<ellipse cx="{sun_x}" cy="{sun_y}" rx="{sun_rx}" ry="{sun_ry}" fill="url(#glow)"/>')
    a(f'<circle cx="{sun_x}" cy="{sun_y}" r="{sun_r}" fill="{sun_color}" opacity="0.92" filter="url(#soft)"/>')

    # 高空卷云
    a('<g filter="url(#softer)">')
    for cx, cy, rx, ry, op in [
        (400, 138, 500, 24, 0.46),
        (1420, 96, 580, 20, 0.38),
        (900, 214, 460, 16, 0.30),
        (1720, 236, 360, 13, 0.26),
        (200, 296, 430, 17, 0.20),
    ]:
        a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
          f'fill="{lighten(sky[0][1], 0.4)}" opacity="{op}"/>')
    a('</g>')

    # ---------- 海 ----------
    # 远方的岛（可选）：给画面一个焦点，也让海平线不只是一条直线
    if island:
        ix, iw, ih, col = island
        a(f'<path d="M{ix - iw} {HORIZON + 4} '
          f'Q{ix - iw * 0.45} {HORIZON - ih * 0.62} {ix - iw * 0.12} {HORIZON - ih} '
          f'Q{ix + iw * 0.1} {HORIZON - ih * 0.55} {ix + iw * 0.42} {HORIZON - ih * 0.3} '
          f'Q{ix + iw * 0.75} {HORIZON - ih * 0.12} {ix + iw} {HORIZON + 4} Z" '
          f'fill="{col}" opacity="0.5"/>')

    # 海平线上的光雾
    a(f'<rect x="0" y="{HORIZON - 70}" width="{W}" height="80" fill="url(#haze)"/>')

    # 五条色带：由远及近，越近越暗越饱和
    # (基准y, 振幅, 混色比, 透明度, 浪沫透明度, 浪沫厚度)
    layers = [
        (HORIZON + 10, 16, 0.05, 0.62, 0.34, 16),
        (HORIZON + 74, 34, 0.26, 0.74, 0.30, 20),
        (HORIZON + 150, 52, 0.50, 0.83, 0.28, 24),
        (HORIZON + 232, 68, 0.74, 0.90, 0.26, 28),
        (HORIZON + 310, 84, 0.92, 0.96, 0.24, 32),
    ]

    for i, (by, amp, t, op, foam_op, foam_ry) in enumerate(layers):
        col = mix(sea_shallow, sea_deep, t)
        a(f'<path d="{wave_path(seed=i * 1.31 + 0.4, base_y=by, amp=amp)}" '
          f'fill="{col}" opacity="{op}"/>')
        # 浪沫：贴着浪尖压一条模糊亮线
        a(f'<ellipse cx="{W / 2}" cy="{by - amp * 0.55:.0f}" rx="{W * 0.78:.0f}" '
          f'ry="{foam_ry}" fill="{lighten(foam, 0.55)}" opacity="{foam_op:.2f}" '
          f'filter="url(#softer)"/>')

    # 日/月在水面的倒影：必须画在色带之后才看得见
    a(f'<ellipse cx="{sun_x}" cy="{HORIZON + 150}" rx="105" ry="165" '
      f'fill="url(#reflect)" filter="url(#softer)"/>')

    # 最前景一道明显的碎浪，给画面收口
    a(f'<path d="{wave_path(seed=9.7, base_y=H - 40, amp=46, segments=5)}" '
      f'fill="{darken(sea_deep, 0.14)}" opacity="0.94"/>')
    a(f'<ellipse cx="{W / 2}" cy="{H - 92}" rx="{W * 0.72:.0f}" ry="30" '
      f'fill="{lighten(foam, 0.7)}" opacity="0.30" filter="url(#softer)"/>')

    if petals:
        a('<g opacity="0.34">')
        rnd = 771
        for i in range(16):
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            x = (rnd % (W - 120)) + 60
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            y = (rnd % 560) + 140
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            rx = 4 + (rnd % 5)
            rot = rnd % 180
            a(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{max(2, rx // 2)}" '
              f'fill="{petals}" transform="rotate({rot} {x} {y})"/>')
        a('</g>')

    a('</svg>')

    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(s))
    return path, len('\n'.join(s))


THEMES = [
    # 破晓 · 晨雾海：天光刚从海平线渗出来，暖粉过渡到灰蓝
    dict(
        name='banner-ocean-dawn.svg',
        sky=[(0, '#fdf0e6'), (28, '#f9dccb'), (54, '#ecc6bd'), (78, '#c8cfdd'), (100, '#adbed2')],
        sun_color='#fff7f0', sun_glow='#f6c4ae',
        sea_shallow='#a8bed2', sea_deep='#4a6684',
        sun_x=1240, sun_y=386, sun_r=60, sun_rx=560, sun_ry=190,
        foam='#fff3e8', petals='#f3ae94',
        island=(1640, 210, 46, '#8896ac'),
    ),
    # 晴日 · 碧海：最通透的一张，正午的青蓝
    dict(
        name='banner-ocean-day.svg',
        sky=[(0, '#e8f6fc'), (32, '#c9e7f4'), (58, '#9fd0e8'), (80, '#82bcdc'), (100, '#74aed2')],
        sun_color='#ffffff', sun_glow='#b4e0f2',
        sea_shallow='#7fb8d6', sea_deep='#1f5c84',
        sun_x=1460, sun_y=190, sun_r=44, sun_rx=440, sun_ry=200,
        foam='#ffffff',
        island=(360, 190, 52, '#7d9cb4'),
    ),
    # 黄昏 · 落日海：橘金到靛蓝，情绪最浓
    dict(
        name='banner-ocean-dusk.svg',
        sky=[(0, '#f7e2cb'), (24, '#f5c493'), (46, '#e79b7e'), (66, '#b07e9a'), (84, '#6f6398'), (100, '#4b4d82')],
        sun_color='#fff3da', sun_glow='#f29f6c',
        sea_shallow='#8d7ba2', sea_deep='#262a52',
        sun_x=1180, sun_y=406, sun_r=72, sun_rx=600, sun_ry=170,
        foam='#ffe6cb',
        island=(1560, 240, 58, '#6b5f86'),
    ),
    # 月夜 · 静海：深蓝里一条月光，安静但耐看
    dict(
        name='banner-ocean-night.svg',
        sky=[(0, '#0d1830'), (32, '#152742'), (58, '#1d3557'), (80, '#254465'), (100, '#2d5474')],
        sun_color='#f4f8ff', sun_glow='#93bde4',
        sea_shallow='#27456a', sea_deep='#081226',
        sun_x=1380, sun_y=170, sun_r=38, sun_rx=400, sun_ry=230,
        foam='#d8e8f8', stars=True,
        island=(300, 200, 44, '#1b2c46'),
    ),
]

if __name__ == '__main__':
    for t in THEMES:
        p, n = build(**t)
        print(f'{os.path.basename(p):32s} {n / 1024:6.1f} KB')
