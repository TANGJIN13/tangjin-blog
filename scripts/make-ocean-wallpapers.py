# -*- coding: utf-8 -*-
"""
生成「大海」主题壁纸（SVG）。

沿用站点既有的插画语言（见 wallpaper-01.svg）：
分层渐变 + 柔和模糊的浪沫分隔 + 远处的光晕。

设计要点：
  · 1920x800，preserveAspectRatio="xMidYMid slice"，和既有壁纸一致
  · 天空渐变承载情绪，海面用 5 层色带做出纵深
  · 每层色带顶部压一条高斯模糊的亮线 —— 这是「浪沫」的关键，
    没有它色带之间就是生硬的色阶断层
  · 越靠前越暗越饱和，模拟真实海面的远近关系
  · 中心区域保持干净，因为要压座右铭文字

用法：python scripts/make-ocean-wallpapers.py
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'public', 'images', 'wallpapers')

W, H = 1920, 800
HORIZON = 470          # 海平线高度


def mix(c1, c2, t):
    """线性插值两个 #rrggbb 颜色。"""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, t):
    return mix(c, '#ffffff', t)


def darken(c, t):
    return mix(c, '#000000', t)


def wave_path(seed, base_y, amp, segments=7, lead=-120, trail=W + 120):
    """
    生成一条起伏的海浪轮廓线。

    用正弦叠加而不是随机数，好处是同一条曲线可复现、
    且相邻两层只要改 seed 就能得到「呼应但不重复」的形态。
    """
    pts = []
    span = trail - lead
    step = span / segments
    for i in range(segments + 1):
        x = lead + i * step
        # 三组不同频率的正弦叠加，模拟自然海面
        t = x / span
        y = base_y
        y += math.sin(t * math.pi * 2.0 + seed * 1.7) * amp
        y += math.sin(t * math.pi * 3.0 + seed * 0.9) * amp * 0.42
        y += math.sin(t * math.pi * 5.0 + seed * 2.3) * amp * 0.18
        pts.append((x, y))

    # 用三次贝塞尔平滑连接，避免折线感
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cx = (x0 + x1) / 2
        d += f' C{cx:.1f} {y0:.1f} {cx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}'
    d += f' L{trail:.1f} {H + 40:.1f} L{lead:.1f} {H + 40:.1f} Z'
    return d


def build(name, sky, sun_color, sun_glow, sea_deep, sea_shallow,
          sun_x=1305, sun_y=272, sun_r=58, sun_rx=430, sun_ry=300,
          foam='#ffffff', extra='', stars=False, petals=None):
    """生成一张壁纸 SVG 文本。"""
    s = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
    a('<defs>')

    # —— 天空渐变 ——
    a('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">')
    for off, col in sky:
        a(f'<stop offset="{off}%" stop-color="{col}"/>')
    a('</linearGradient>')

    # —— 海面渐变（上浅下深）——
    a('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{sea_shallow}"/>')
    a(f'<stop offset="100%" stop-color="{sea_deep}"/>')
    a('</linearGradient>')

    # —— 太阳/月亮的光晕 ——
    a('<radialGradient id="glow" cx="50%" cy="50%" r="50%">')
    a(f'<stop offset="0%" stop-color="{sun_color}" stop-opacity="0.95"/>')
    a(f'<stop offset="32%" stop-color="{sun_glow}" stop-opacity="0.55"/>')
    a(f'<stop offset="100%" stop-color="{sun_glow}" stop-opacity="0"/>')
    a('</radialGradient>')

    # —— 水面上的垂直光柱（日/月倒影）——
    a('<linearGradient id="reflect" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{lighten(sun_color, 0.3)}" stop-opacity="0.62"/>')
    a(f'<stop offset="100%" stop-color="{lighten(sun_color, 0.3)}" stop-opacity="0"/>')
    a('</linearGradient>')

    a('<filter id="soft" x="-25%" y="-25%" width="150%" height="150%">'
      '<feGaussianBlur stdDeviation="16"/></filter>')
    a('<filter id="softer" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="36"/></filter>')
    a('</defs>')

    # —— 天空 ——
    a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

    if stars:
        a('<g fill="#ffffff">')
        rnd = 20261014
        for i in range(46):
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            x = (rnd % (W - 80)) + 40
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            y = (rnd % 300) + 24
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            r = 0.9 + (rnd % 100) / 100.0 * 1.5
            o = 0.28 + (rnd % 100) / 100.0 * 0.5
            a(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" opacity="{o:.2f}"/>')
        a('</g>')

    # —— 日/月光晕 + 本体 ——
    a(f'<ellipse cx="{sun_x}" cy="{sun_y}" rx="{sun_rx}" ry="{sun_ry}" fill="url(#glow)"/>')
    a(f'<circle cx="{sun_x}" cy="{sun_y}" r="{sun_r}" fill="{sun_color}" opacity="0.9" filter="url(#soft)"/>')

    # —— 高空薄云：模糊的长椭圆，横向拉开做卷云 ——
    a('<g filter="url(#softer)">')
    for i, (cx, cy, rx, ry, op) in enumerate([
        (420, 150, 480, 22, 0.5),
        (1380, 108, 560, 19, 0.42),
        (930, 218, 450, 15, 0.36),
        (1690, 232, 380, 13, 0.32),
        (240, 300, 420, 16, 0.26),
    ]):
        a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
          f'fill="{lighten(sky[0][1], 0.36)}" opacity="{op}"/>')
    a('</g>')

    # —— 海面：5 层色带，由远及近 ——
    # 每层 = 一条浪形轮廓 + 顶部一条模糊亮线（浪沫）
    layers = [
        # (基准y, 振幅, 混色比例, 透明度, 浪沫透明度)
        (HORIZON + 6, 10, 0.02, 0.70, 0.40),
        (HORIZON + 62, 16, 0.20, 0.80, 0.44),
        (HORIZON + 128, 22, 0.42, 0.87, 0.46),
        (HORIZON + 196, 28, 0.66, 0.92, 0.50),
        (HORIZON + 262, 34, 0.88, 0.96, 0.54),
    ]

    # 日/月在水面的倒影，压在海面之下、色带之上
    a(f'<ellipse cx="{sun_x}" cy="{HORIZON + 130}" rx="120" ry="150" '
      f'fill="url(#reflect)" filter="url(#softer)"/>')

    for i, (by, amp, t, op, foam_op) in enumerate(layers):
        col = mix(sea_shallow, sea_deep, t)
        a(f'<path d="{wave_path(seed=i * 1.31 + 0.4, base_y=by, amp=amp)}" '
          f'fill="{col}" opacity="{op}"/>')
        # 浪沫：贴着浪尖压一条模糊亮线，制造「水花/碎浪」的过渡
        a(f'<ellipse cx="{W / 2}" cy="{by:.0f}" rx="{W * 0.75:.0f}" ry="{18 + i * 3}" '
          f'fill="{lighten(foam, 0.6)}" opacity="{foam_op * 0.62:.2f}" filter="url(#softer)"/>')

    # —— 最前景：一道明显的碎浪，给画面收口 ——
    a(f'<path d="{wave_path(seed=9.7, base_y=H - 52, amp=22, segments=6)}" '
      f'fill="{darken(sea_deep, 0.12)}" opacity="0.9"/>')
    a(f'<ellipse cx="{W / 2}" cy="{H - 58}" rx="{W * 0.7:.0f}" ry="26" '
      f'fill="{lighten(foam, 0.72)}" opacity="0.34" filter="url(#softer)"/>')

    if petals:
        a(f'<g opacity="0.42">')
        rnd = 771
        for i in range(16):
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            x = (rnd % (W - 120)) + 60
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            y = (rnd % 620) + 120
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            rx = 4 + (rnd % 5)
            rot = rnd % 180
            a(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{max(2, rx // 2)}" '
              f'fill="{petals}" transform="rotate({rot} {x} {y})"/>')
        a('</g>')

    a(extra)
    a('</svg>')

    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(s))
    return path, len('\n'.join(s))


THEMES = [
    # 1) 破晓 · 晨雾海 —— 天光刚从海平线渗出来
    dict(
        name='banner-ocean-dawn.svg',
        sky=[(0, '#fdf1ea'), (30, '#f8ddd0'), (58, '#ecc9c4'), (80, '#cfd3de'), (100, '#b9c6d6')],
        sun_color='#fff6ef', sun_glow='#f7c9b4',
        sea_shallow='#b8c9d8', sea_deep='#5d7794',
        sun_x=1180, sun_y=352, sun_r=52, sun_rx=520, sun_ry=250,
        foam='#fff3ea', petals='#f6b9a0',
    ),
    # 2) 晴日 · 碧海 —— 最通透的一张，正午的青蓝
    dict(
        name='banner-ocean-day.svg',
        sky=[(0, '#eaf6fb'), (34, '#cfe9f4'), (62, '#a8d4e8'), (84, '#8dc0dc'), (100, '#7fb2d2')],
        sun_color='#ffffff', sun_glow='#bfe4f2',
        sea_shallow='#8fc0da', sea_deep='#2d6c92',
        sun_x=1420, sun_y=214, sun_r=46, sun_rx=460, sun_ry=230,
        foam='#ffffff',
    ),
    # 3) 黄昏 · 落日海 —— 橘金到靛蓝，情绪最浓
    dict(
        name='banner-ocean-dusk.svg',
        sky=[(0, '#f6e3d0'), (26, '#f4c79b'), (48, '#e79f84'), (68, '#b4829c'), (86, '#7a6a9c'), (100, '#54558a')],
        sun_color='#fff2d8', sun_glow='#f4a878',
        sea_shallow='#9c86a8', sea_deep='#33355f',
        sun_x=1260, sun_y=392, sun_r=66, sun_rx=560, sun_ry=210,
        foam='#ffe9d2',
    ),
    # 4) 月夜 · 静海 —— 深蓝里一条月光，安静但耐看
    dict(
        name='banner-ocean-night.svg',
        sky=[(0, '#101c36'), (34, '#172a4c'), (62, '#1f3a63'), (84, '#27496f'), (100, '#2f5b7d')],
        sun_color='#f2f7ff', sun_glow='#9dc4e8',
        sea_shallow='#2a4a6e', sea_deep='#0c1730',
        sun_x=1340, sun_y=188, sun_r=40, sun_rx=420, sun_ry=250,
        foam='#dceaf8', stars=True,
    ),
]

if __name__ == '__main__':
    for t in THEMES:
        p, n = build(**t)
        print(f'{os.path.basename(p):32s} {n / 1024:6.1f} KB')
