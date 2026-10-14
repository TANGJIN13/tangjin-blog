# -*- coding: utf-8 -*-
"""
生成「大海」主题的文章封面（SVG）。

和壁纸的区别
------------
壁纸是**场景**（有地平线、有太阳、有纵深），要的是氛围；
封面是**内容缩略图**，会被裁成 16:9 小图挂在卡片上，所以：
  · 不能有明显的地平线 —— 缩到 140x96 时地平线会变成一条突兀的横线
  · 要更抽象：水波、气泡、光线、珊瑚剪影这类**无方向**的图形
  · 主体要居中偏下，因为卡片标题压在下半部分
  · 单张信息量要低，小尺寸下才读得出「这是一张海报」而不是一团糊

8 张各自不同，但共享同一套海洋色系，保证并排出现时是「一组」。
都带一点水面的光斑（caustics），这是"水下"最有效的视觉符号。

用法：python scripts/make-ocean-covers.py
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'public', 'images', 'covers-ocean')

W, H = 800, 450          # 16:9，和卡片比例一致


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, t):
    return mix(c, '#ffffff', t)


def darken(c, t):
    return mix(c, '#000000', t)


def prism(seed, amp, count, base, lead=-60, trail=W + 60):
    """
    一条平滑的波纹线（不闭合，用作装饰性水波）。
    正弦叠加，保证可复现。
    """
    span = trail - lead
    pts = []
    for i in range(count + 1):
        x = lead + i * span / count
        t = x / span
        y = base
        y += math.sin(t * math.pi * 2 + seed * 1.7) * amp
        y += math.sin(t * math.pi * 3.4 + seed * 0.8) * amp * 0.36
        pts.append((x, y))
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        cx = (x0 + x1) / 2
        d += f' C{cx:.1f} {y0:.1f} {cx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}'
    return d


def bubbles(rnd, n, amin, amax, ymax, color, op):
    """散布气泡。用 LCG 保证每次生成结果一致。"""
    out = []
    for _ in range(n):
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        x = (rnd % (W - 80)) + 40
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        y = (rnd % ymax) + 30
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        r = amin + (rnd % 1000) / 1000.0 * (amax - amin)
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        o = op * (0.5 + (rnd % 100) / 200.0)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="{color}" opacity="{o:.2f}"/>')
    return out


def caustics(color, op, seed=3):
    """
    水面光斑：几组模糊的斜向亮纹，模拟阳光在水里的折射网。
    这是让抽象图形"读起来像水下"的关键一笔。
    """
    parts = []
    rnd = seed * 7919
    for i in range(7):
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        x = (rnd % (W + 200)) - 100
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        w = 26 + (rnd % 60)
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        rot = -22 - (rnd % 16)
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        o = op * (0.35 + (rnd % 100) / 160.0)
        parts.append(
            f'<rect x="{x}" y="-120" width="{w}" height="{H + 240}" fill="{color}" '
            f'opacity="{o:.2f}" transform="rotate({rot} {x} {H / 2})"/>'
        )
    return parts


def build(name, top, bottom, accent, motif, seed=1, dark=False):
    """生成一张封面。"""
    s = []
    a = s.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
    a('<defs>')

    # 主背景：上浅下深，模拟水体
    a('<linearGradient id="bg" x1="0" y1="0" x2="0.25" y2="1">')
    a(f'<stop offset="0%" stop-color="{top}"/>')
    a(f'<stop offset="100%" stop-color="{bottom}"/>')
    a('</linearGradient>')

    # 右下角的暖色补光，避免整张图太闷
    a('<radialGradient id="warm" cx="50%" cy="50%" r="50%">')
    a(f'<stop offset="0%" stop-color="{accent}" stop-opacity="0.55"/>')
    a(f'<stop offset="100%" stop-color="{accent}" stop-opacity="0"/>')
    a('</radialGradient>')

    a('<filter id="b1" x="-30%" y="-30%" width="160%" height="160%">'
      '<feGaussianBlur stdDeviation="9"/></filter>')
    a('<filter id="b2" x="-40%" y="-40%" width="180%" height="180%">'
      '<feGaussianBlur stdDeviation="26"/></filter>')
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # 光斑（斜向亮纹）
    a('<g filter="url(#b2)">')
    for p in caustics(lighten(top, 0.5), 0.34, seed):
        a(p)
    a('</g>')

    # 右下暖色补光
    a(f'<ellipse cx="{W * 0.84:.0f}" cy="{H * 0.9:.0f}" rx="300" ry="220" fill="url(#warm)"/>')

    # ---- 主体图形：8 张各不同 ----
    if motif == 'waves':
        # 层叠水波：从下往上三条弧，越上越淡
        for i, (base, amp, tt, op) in enumerate([
            (H * 0.62, 16, 0.18, 0.5), (H * 0.74, 22, 0.44, 0.68), (H * 0.88, 28, 0.72, 0.9)
        ]):
            col = mix(top, bottom, tt)
            a(f'<path d="{prism(seed + i * 1.3, amp, 5, base)}" fill="none" '
              f'stroke="{col}" stroke-width="{10 + i * 5}" stroke-linecap="round" opacity="{op}"/>')
        a(f'<ellipse cx="{W / 2}" cy="{H * 0.8}" rx="330" ry="26" '
          f'fill="{lighten(top, 0.6)}" opacity="0.3" filter="url(#b2)"/>')

    elif motif == 'bubbles':
        for p in bubbles(seed * 977, 26, 3, 13, H - 40, lighten(top, 0.55), 0.5):
            a(p)
        a(f'<circle cx="{W * 0.72}" cy="{H * 0.34}" r="66" fill="none" '
          f'stroke="{lighten(top, 0.5)}" stroke-width="3" opacity="0.5"/>')
        a(f'<circle cx="{W * 0.72}" cy="{H * 0.34}" r="40" fill="{lighten(top, 0.72)}" opacity="0.22"/>')

    elif motif == 'rays':
        # 从上方斜射的光柱
        a('<g filter="url(#b1)">')
        rnd = seed * 331
        for i in range(5):
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            x = 90 + i * 160 + (rnd % 50)
            a(f'<rect x="{x}" y="-60" width="{34 + i * 7}" height="{H + 120}" '
              f'fill="{lighten(top, 0.62)}" opacity="0.3" '
              f'transform="rotate(-19 {x} {H / 2})"/>')
        a('</g>')
        a(f'<ellipse cx="{W / 2}" cy="{H * 0.42}" rx="150" ry="110" '
          f'fill="{lighten(top, 0.6)}" opacity="0.22" filter="url(#b2)"/>')

    elif motif == 'coral':
        # 珊瑚剪影：从底部升起的分叉
        a(f'<g fill="{darken(bottom, 0.18)}" opacity="0.5">')
        for cx, sc in [(150, 1.0), (300, 0.72), (520, 1.15), (668, 0.85)]:
            a(f'<path d="M{cx} {H} C{cx} {H - 70 * sc} {cx - 34 * sc} {H - 96 * sc} '
              f'{cx - 40 * sc} {H - 150 * sc} C{cx - 30 * sc} {H - 118 * sc} '
              f'{cx - 16 * sc} {H - 106 * sc} {cx - 12 * sc} {H - 74 * sc} '
              f'C{cx - 4 * sc} {H - 120 * sc} {cx + 16 * sc} {H - 132 * sc} '
              f'{cx + 14 * sc} {H - 176 * sc} C{cx + 30 * sc} {H - 122 * sc} '
              f'{cx + 22 * sc} {H - 62 * sc} {cx + 6 * sc} {H} Z"/>')
        a('</g>')
        for p in bubbles(seed * 613, 14, 3, 9, H - 140, lighten(top, 0.55), 0.4):
            a(p)

    elif motif == 'moon':
        # 月与海平线：唯一允许有"水平线"的一张，用得很淡
        a(f'<circle cx="{W * 0.68}" cy="{H * 0.3}" r="52" fill="{lighten(top, 0.72)}" opacity="0.85" filter="url(#b1)"/>')
        a(f'<ellipse cx="{W * 0.68}" cy="{H * 0.3}" rx="150" ry="150" fill="{lighten(top, 0.5)}" opacity="0.2" filter="url(#b2)"/>')
        a(f'<rect x="0" y="{H * 0.62:.0f}" width="{W}" height="{H}" fill="{darken(bottom, 0.2)}" opacity="0.5"/>')
        a(f'<ellipse cx="{W * 0.68}" cy="{H * 0.78:.0f}" rx="80" ry="90" '
          f'fill="{lighten(top, 0.4)}" opacity="0.22" filter="url(#b2)"/>')

    elif motif == 'jelly':
        # 水母：半透明伞盖 + 触须
        a(f'<g opacity="0.62">')
        a(f'<path d="M{W * 0.5 - 78:.0f} {H * 0.5:.0f} '
          f'C{W * 0.5 - 78:.0f} {H * 0.5 - 92:.0f} {W * 0.5 + 78:.0f} {H * 0.5 - 92:.0f} '
          f'{W * 0.5 + 78:.0f} {H * 0.5:.0f} Z" fill="{lighten(top, 0.55)}"/>')
        for i in range(7):
            x0 = W * 0.5 - 62 + i * 21
            a(f'<path d="M{x0:.0f} {H * 0.5:.0f} q{-9 + i * 3} 52 {3 - i} 104" '
              f'fill="none" stroke="{lighten(top, 0.45)}" stroke-width="4" stroke-linecap="round"/>')
        a('</g>')
        for p in bubbles(seed * 421, 12, 3, 8, H - 60, lighten(top, 0.6), 0.42):
            a(p)

    elif motif == 'swirl':
        # 漩涡/洋流：同心的弧
        a(f'<g fill="none" stroke="{lighten(top, 0.45)}" opacity="0.5">')
        for i in range(5):
            r = 40 + i * 30
            a(f'<path d="M{W * 0.46 + r:.0f} {H * 0.46:.0f} '
              f'A{r} {r} 0 1 1 {W * 0.46 - r:.0f} {H * 0.46:.0f}" stroke-width="{7 - i}"/>')
        a('</g>')
        a(f'<circle cx="{W * 0.46}" cy="{H * 0.46}" r="150" fill="{lighten(top, 0.6)}" opacity="0.12" filter="url(#b2)"/>')

    elif motif == 'fish':
        # 鱼群：一列小三角，指向同一方向
        a(f'<g fill="{darken(bottom, 0.1)}" opacity="0.46">')
        rnd = seed * 887
        for i in range(16):
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            x = 90 + (rnd % 560)
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            y = 90 + (rnd % 240)
            rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
            sc = 0.55 + (rnd % 100) / 160.0
            a(f'<path d="M{x} {y} l{20 * sc:.0f} {7 * sc:.0f} l{-20 * sc:.0f} {7 * sc:.0f} z" '
              f'transform="rotate({(rnd % 24) - 12} {x} {y})"/>')
        a('</g>')
        a(f'<ellipse cx="{W * 0.6}" cy="{H * 0.45}" rx="260" ry="150" '
          f'fill="{lighten(top, 0.55)}" opacity="0.14" filter="url(#b2)"/>')

    # 统一的收边暗角，让卡片上叠字时更稳
    a(f'<rect width="{W}" height="{H}" fill="none"/>')
    a('<radialGradient id="vig" cx="50%" cy="45%" r="72%">'
      '<stop offset="60%" stop-color="#000" stop-opacity="0"/>'
      '<stop offset="100%" stop-color="#000" stop-opacity="0.18"/>'
      '</radialGradient>')
    a(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')

    a('</svg>')

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(s))
    return path, len('\n'.join(s))


# 8 张，色相都在 195~245 之间（青蓝到靛蓝），共享同一套海洋色系。
# 明度刻意拉开：01/05 偏亮、04/08 偏深，并排时才有一组图的节奏。
COVERS = [
    dict(name='ocean-cover-01.svg', top='#a8d8ea', bottom='#2c6b93', accent='#f6c9a0', motif='waves',   seed=1),
    dict(name='ocean-cover-02.svg', top='#9fd0e8', bottom='#22557d', accent='#ffd9a8', motif='bubbles', seed=2),
    dict(name='ocean-cover-03.svg', top='#8fc6e2', bottom='#1d4a70', accent='#f2b98d', motif='rays',    seed=3),
    dict(name='ocean-cover-04.svg', top='#7fb2d2', bottom='#173d5e', accent='#e8a97e', motif='coral',   seed=4),
    dict(name='ocean-cover-05.svg', top='#b3dcea', bottom='#35789c', accent='#ffe0b0', motif='moon',    seed=5),
    dict(name='ocean-cover-06.svg', top='#95cbe0', bottom='#2a5f85', accent='#f7c4a4', motif='jelly',   seed=6),
    dict(name='ocean-cover-07.svg', top='#a4d4e6', bottom='#2f6a8e', accent='#fac9a0', motif='swirl',   seed=7),
    dict(name='ocean-cover-08.svg', top='#86bcd8', bottom='#1a4468', accent='#ebae86', motif='fish',    seed=8),
]

if __name__ == '__main__':
    for c in COVERS:
        p, n = build(**c)
        print(f'{os.path.basename(p):24s} {n / 1024:6.1f} KB')
