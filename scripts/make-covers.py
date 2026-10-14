# -*- coding: utf-8 -*-
"""
生成文章封面（SVG）—— 替换掉原来那批低饱和的灰粉图。

为什么要换
----------
测过原图：饱和度只有 0.02~0.10，平均色 #d1c7ca / #dacdce / #c8c5c4，
整组都是「灰扑扑的粉」，挂在玻璃卡片上既没有色彩、也没有焦点，看着像褪色了。
新的一组把饱和度拉到 0.3~0.55，同时保持雾紫主题的色相家族（270~330 + 少量暖橙做补色）。

怎么让抽象的图形"好看"
----------------------
单一个渐变块是没内容的。有四个东西能让几何图形读起来像"一张图"：

  ① 层次       —— 至少 3 层形状，靠透明度叠出纵深。一层是贴纸，三层才是画面。
  ② 焦点       —— 每张有一个视觉重心（太阳/月亮/最亮的那团），别均匀铺满。
  ③ 光感       —— 一层高光 + 一层暗部，画面才有体积。均匀亮度 = 平的。
  ④ 颗粒       —— 一层极淡的噪点。纯色渐变在屏幕上会有色带（banding），
                    噪点能把色带打散，顺带给出一点纸感/胶片感。

用法：python scripts/make-covers.py
"""
import os
import math
import random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'public', 'images', 'covers')

W, H = 800, 450   # 16:9，与卡片封面比例一致

# 雾紫家族的调色板：主色相 270~320，加一点暖橙（hue 25~40）做补色。
# 刻意让 8 张各自偏一个方向，并排出现时才是一组而不是复制粘贴。
PALETTES = [
    dict(name='cover-01', hi='#e9d5ff', mid='#b39ddb', lo='#7e57c2', glow='#ffd9ec', accent='#ffb3c7'),  # 紫粉
    dict(name='cover-02', hi='#dce7ff', mid='#8fa8e0', lo='#5468b8', glow='#ffe9c9', accent='#ffc48f'),  # 雾蓝紫
    dict(name='cover-03', hi='#ffe4ec', mid='#f0a0bd', lo='#c75d86', glow='#fff0d4', accent='#ffd08a'),  # 玫瑰
    dict(name='cover-04', hi='#e6dcff', mid='#9f8fd6', lo='#6553b0', glow='#c9f0e4', accent='#7fd6bd'),  # 紫青
    dict(name='cover-05', hi='#f6e3ff', mid='#c79ce0', lo='#8e5bb0', glow='#ffe2f0', accent='#ff9ec4'),  # 兰花紫
    dict(name='cover-06', hi='#ffeede', mid='#f2b99b', lo='#c2755f', glow='#e7dcff', accent='#b39ddb'),  # 暖杏 + 紫
    dict(name='cover-07', hi='#dfe9ff', mid='#93a7d8', lo='#5a6aa8', glow='#ffdcea', accent='#f79bc0'),  # 暮蓝 + 粉
    dict(name='cover-08', hi='#f3e6ff', mid='#a888d4', lo='#6d4e9c', glow='#ffe6c4', accent='#ffc27a'),  # 薰衣草
]

def build(p: dict, seed: int, motif: str):
    """motif: hills | aurora | waves | blobs | rings | sunset | mist | stars"""
    rnd = random.Random(seed)
    s = []
    a = s.append
    name, hi, mid, lo = p['name'], p['hi'], p['mid'], p['lo']
    glow, accent = p['glow'], p['accent']

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
    a('<defs>')

    a('<linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">')
    a(f'<stop offset="0%" stop-color="{hi}"/>')
    a(f'<stop offset="52%" stop-color="{mid}"/>')
    a(f'<stop offset="100%" stop-color="{lo}"/>')
    a('</linearGradient>')

    a('<radialGradient id="sun" cx="50%" cy="50%" r="50%">')
    a(f'<stop offset="0%" stop-color="{glow}" stop-opacity="1"/>')
    a(f'<stop offset="30%" stop-color="{glow}" stop-opacity="0.55"/>')
    a(f'<stop offset="100%" stop-color="{glow}" stop-opacity="0"/>')
    a('</radialGradient>')

    a('<filter id="soft" x="-40%" y="-40%" width="180%" height="180%">'
      '<feGaussianBlur stdDeviation="22"/></filter>')
    a('<filter id="softer" x="-50%" y="-50%" width="200%" height="200%">'
      '<feGaussianBlur stdDeviation="48"/></filter>')
    a('<pattern id="grain" patternUnits="userSpaceOnUse" width="180" height="180">'
      '<filter id="gn"><feTurbulence type="fractalNoise" baseFrequency="0.9" '
      'numOctaves="3" stitchTiles="stitch"/>'
      '<feColorMatrix type="saturate" values="0"/></filter>'
      '<rect width="180" height="180" filter="url(#gn)" opacity="0.055"/>'
      '</pattern>')
    a('</defs>')

    a(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

    # 焦点光团（每张都有，位置按 motif 微调）
    fx, fy = (rnd.randint(180, 620), rnd.randint(90, 250)) if motif not in ('sunset',) else (rnd.randint(480, 660), rnd.randint(210, 300))
    a(f'<circle cx="{fx}" cy="{fy}" r="{rnd.randint(150, 260)}" fill="url(#sun)"/>')

    if motif == 'hills':
        # 层叠山峦：由远及近，越近越深
        for i, (base, col, op) in enumerate([
            (H * 0.58, mid, 0.55), (H * 0.72, lo, 0.75), (H * 0.86, lo, 0.95),
        ]):
            pts = []
            seg = 7
            for k in range(seg + 1):
                x = -60 + k * (W + 120) / seg
                y = base + math.sin(k * 1.1 + seed * 0.7) * 34 - rnd.uniform(-8, 8)
                pts.append((x, y))
            d = f'M-60 {H + 40} L{pts[0][0]:.0f} {pts[0][1]:.0f}'
            for k in range(len(pts) - 1):
                cx = (pts[k][0] + pts[k + 1][0]) / 2
                d += f' C{cx:.0f} {pts[k][1]:.0f} {cx:.0f} {pts[k + 1][1]:.0f} {pts[k + 1][0]:.0f} {pts[k + 1][1]:.0f}'
            d += f' L{W + 60} {H + 40} Z'
            a(f'<path d="{d}" fill="{col}" opacity="{op}"/>')
        # 水面反光
        a(f'<ellipse cx="{fx}" cy="{H * 0.9:.0f}" rx="180" ry="34" fill="{glow}" opacity="0.28" filter="url(#soft)"/>')

    elif motif == 'aurora':
        # 极光：几条向上收的弧形色带
        a('<g filter="url(#softer)" opacity="0.8">')
        for i in range(5):
            bx = 40 + i * 165 + rnd.randint(-40, 40)
            hgt = rnd.randint(200, 330)
            a(f'<path d="M{bx} {H + 20} C{bx + 60} {H - hgt * 0.5:.0f} {bx - 30} {H - hgt * 0.8:.0f} {bx + 70} {20}" '
              f'stroke="{accent if i % 2 else glow}" stroke-width="{rnd.randint(46, 92)}" '
              f'stroke-linecap="round" fill="none" opacity="{rnd.uniform(0.28, 0.5):.2f}"/>')
        a('</g>')

    elif motif == 'waves':
        # 流动的波浪曲线
        for i in range(6):
            base = H * 0.32 + i * H * 0.11
            pts = []
            seg = 6
            for k in range(seg + 1):
                x = -40 + k * (W + 80) / seg
                y = base + math.sin(k * 0.95 + i * 0.8 + seed) * 26
                pts.append((x, y))
            d = f'M{pts[0][0]:.0f} {pts[0][1]:.0f}'
            for k in range(len(pts) - 1):
                cx = (pts[k][0] + pts[k + 1][0]) / 2
                d += f' C{cx:.0f} {pts[k][1]:.0f} {cx:.0f} {pts[k + 1][1]:.0f} {pts[k + 1][0]:.0f} {pts[k + 1][1]:.0f}'
            a(f'<path d="{d}" fill="none" stroke="{glow if i % 2 else accent}" '
              f'stroke-width="{2 + i * 1.1}" stroke-linecap="round" opacity="{0.3 + i * 0.1:.2f}"/>')

    elif motif == 'blobs':
        # 有机色块：几个不规则圆形叠在一起
        for i in range(5):
            cx = rnd.randint(90, 710)
            cy = rnd.randint(80, 370)
            r = rnd.randint(55, 135)
            col = [glow, accent, hi, mid, lo][i % 5]
            op = rnd.uniform(0.26, 0.5)
            a(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * rnd.uniform(0.72, 1.05):.2f}" '
              f'fill="{col}" opacity="{op:.2f}" filter="url(#soft)" '
              f'transform="rotate({rnd.randint(0, 90)} {cx} {cy})"/>')

    elif motif == 'rings':
        # 同心圆环
        cx, cy = rnd.randint(240, 560), rnd.randint(130, 320)
        for i in range(7):
            r = 34 + i * rnd.randint(22, 34)
            a(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
              f'stroke="{glow if i % 2 else accent}" stroke-width="{rnd.randint(2, 5)}" '
              f'opacity="{0.62 - i * 0.07:.2f}"/>')

    elif motif == 'sunset':
        # 落日：地平线 + 半沉的太阳
        horizon = H * rnd.uniform(0.58, 0.68)
        a(f'<rect x="0" y="{horizon:.0f}" width="{W}" height="{H - horizon:.0f}" fill="{lo}" opacity="0.72"/>')
        a(f'<circle cx="{fx}" cy="{horizon - 6:.0f}" r="62" fill="{glow}" opacity="0.9"/>')
        a(f'<rect x="0" y="{horizon - 3:.0f}" width="{W}" height="3" fill="{glow}" opacity="0.5"/>')
        for i in range(4):
            y = horizon + 26 + i * 22
            a(f'<rect x="0" y="{y:.0f}" width="{W}" height="2" fill="{glow}" opacity="{0.3 - i * 0.06:.2f}"/>')

    elif motif == 'mist':
        # 雾中树影：几条竖直的浅色细柱 + 大块模糊
        a('<g filter="url(#softer)">')
        for i in range(9):
            x = rnd.randint(40, 760)
            w = rnd.randint(6, 20)
            hgt = rnd.randint(140, 300)
            a(f'<rect x="{x}" y="{H - hgt}" width="{w}" height="{hgt}" fill="{lo}" '
              f'opacity="{rnd.uniform(0.14, 0.3):.2f}" rx="{w // 2}"/>')
        a('</g>')
        a(f'<rect x="0" y="{H * 0.6:.0f}" width="{W}" height="{H * 0.4:.0f}" fill="{glow}" opacity="0.16" filter="url(#softer)"/>')

    elif motif == 'stars':
        # 星空 + 星云
        a(f'<ellipse cx="{fx}" cy="{fy}" rx="260" ry="150" fill="{accent}" opacity="0.3" filter="url(#softer)"/>')
        for _ in range(46):
            x, y = rnd.randint(10, W - 10), rnd.randint(10, int(H * 0.78))
            r = rnd.uniform(0.8, 2.1)
            a(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#ffffff" opacity="{rnd.uniform(0.3, 0.95):.2f}"/>')
        # 一颗大星 + 十字光芒
        sx, sy = rnd.randint(280, 560), rnd.randint(90, 220)
        a(f'<circle cx="{sx}" cy="{sy}" r="3.4" fill="#ffffff"/>')
        a(f'<path d="M{sx - 22} {sy} h44 M{sx} {sy - 22} v44" stroke="#ffffff" '
          f'stroke-width="1" opacity="0.55" stroke-linecap="round"/>')

    # 颗粒：打散渐变色带，顺带一点纸感。
    # ⚠️ 这里用 <pattern> 而不是 data-URI 的 feTurbulence：
    #    fill="url("data:image/svg+xml,...")" 里外层双引号会被提前截断，
    #    整段 SVG 变成无效 XML —— 症状是 <img> 能加载（HTTP 200）但什么都不画，
    #    排查时很容易误以为是路径或 lazy-loading 的问题。
    a(f'<rect width="{W}" height="{H}" fill="url(#grain)"/>')
    a('</svg>')
    return '\n'.join(s)


MOTIFS = ['hills', 'aurora', 'waves', 'blobs', 'rings', 'sunset', 'mist', 'stars']

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for i, pal in enumerate(PALETTES):
        svg = build(pal, seed=i * 37 + 11, motif=MOTIFS[i % len(MOTIFS)])
        path = os.path.join(OUT, f"{pal['name']}.svg")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"{pal['name']}.svg  {len(svg)/1024:5.1f} KB  motif={MOTIFS[i % len(MOTIFS)]}")
