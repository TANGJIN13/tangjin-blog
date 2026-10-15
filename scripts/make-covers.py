# -*- coding: utf-8 -*-
"""
生成文章封面（SVG）—— 目标是「看起来像一张照片」。

为什么要换掉上一版
------------------
上一版是抽象几何（色块/圆环/波浪线），用户评价"太丑"。
参考站 c1everf0x.cn 的封面是**真实照片**：自然光影、上亮下暗、
柔和体积感、饱和度中等。但直接用别人的照片有版权问题。

所以这一版的目标：**用代码画出"像照片"的画面** —— 不是照片，
但要有照片的三个视觉特征：

  ① 光照体积感 —— 不是均匀渐变，而是"光从某个方向照进来"：
                      一个亮源 + 一片受光面 + 一片阴影面。
  ② 自然色相过渡 —— 真实天空/水面不会是一条直线渐变，
                     而是暖→冷、深→浅的复杂过渡。
  ③ 胶片颗粒 + 轻微暗角 —— 这两样是"照片"而不是"插画"的指纹。

每张都给一个「可联想的情景」：晨雾山谷 / 夕阳湖面 / 星夜海洋 /
雨后天空 / 熔金云海 …… 让人一眼能说出"这是哪儿"，而不是"这是个图案"。

用法：python scripts/make-covers.py
"""
import os
import math
import random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'public', 'images', 'covers')

W, H = 800, 450   # 16:9，与卡片封面比例一致


def gradient(colors, stops):
    """colors: [(offset%, #hex), ...]  → linearGradient 字符串"""
    out = ['<linearGradient id="sky" x1="0" y1="0" x2="0.08" y2="1">']
    for off, col in colors:
        out.append(f'<stop offset="{off}%" stop-color="{col}"/>')
    out.append('</linearGradient>')
    return '\n'.join(out)


def build(seed, name, sky, haze, sun, sun_r=46, sun_pos=(0.72, 0.32),
          ridges=None, water=False, stars=0, spray=0, vignette=0.24):
    rnd = random.Random(seed)
    s = []
    a = s.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
    a('<defs>')

    # 天空：主渐变（上→下）
    a('<linearGradient id="sky" x1="0" y1="0" x2="0.08" y2="1">')
    for off, col in sky:
        a(f'<stop offset="{off}%" stop-color="{col}"/>')
    a('</linearGradient>')

    # 地平线附近的辉光（暖/亮）
    a('<radialGradient id="glow" cx="50%" cy="50%" r="50%">')
    a(f'<stop offset="0%" stop-color="{sun}" stop-opacity="0.95"/>')
    a(f'<stop offset="30%" stop-color="{sun}" stop-opacity="0.5"/>')
    a(f'<stop offset="100%" stop-color="{sun}" stop-opacity="0"/>')
    a('</radialGradient>')

    # 云雾/雾气：极淡的大面积渐变
    a('<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">')
    a(f'<stop offset="0%" stop-color="{haze}" stop-opacity="0"/>')
    a(f'<stop offset="100%" stop-color="{haze}" stop-opacity="0.5"/>')
    a('</linearGradient>')

    a('<filter id="soft" x="-40%" y="-40%" width="180%" height="180%">'
      '<feGaussianBlur stdDeviation="16"/></filter>')
    a('<filter id="softer" x="-50%" y="-50%" width="200%" height="200%">'
      '<feGaussianBlur stdDeviation="42"/></filter>')
    # 胶片颗粒：pattern 的 feTurbulence，比 data-URI 安全
    a('<pattern id="grain" patternUnits="userSpaceOnUse" width="160" height="160">'
      '<filter id="gn"><feTurbulence type="fractalNoise" baseFrequency="0.85" '
      'numOctaves="3" stitchTiles="stitch"/>'
      '<feColorMatrix type="saturate" values="0"/></filter>'
      '<rect width="160" height="160" filter="url(#gn)" opacity="0.045"/>'
      '</pattern>')
    a('</defs>')

    # ---------- 天空 ----------
    a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

    # 星星（夜间）
    if stars:
        a('<g fill="#ffffff">')
        for _ in range(stars):
            x = rnd.randint(10, W - 10)
            y = rnd.randint(6, int(H * 0.55))
            r = rnd.uniform(0.6, 1.6)
            a(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>')
        a('</g>')

    # ---------- 太阳/月亮光晕 ----------
    sx, sy = int(W * sun_pos[0]), int(H * sun_pos[1])
    a(f'<circle cx="{sx}" cy="{sy}" r="{sun_r + 90}" fill="url(#glow)"/>')
    a(f'<circle cx="{sx}" cy="{sy}" r="{sun_r}" fill="{sun}" opacity="0.92" filter="url(#soft)"/>')

    # ---------- 云层（soft 大模糊椭圆，错落排布）----------
    a('<g filter="url(#softer)">')
    for _ in range(rnd.randint(5, 8)):
        cx = rnd.randint(0, W)
        cy = rnd.randint(int(H * 0.05), int(H * 0.42))
        rx = rnd.randint(90, 260)
        ry = rnd.randint(14, 38)
        col = '#ffffff' if rnd.random() < 0.5 else haze
        a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    a('</g>')

    # ---------- 地平线 + 远景山脊/海面 ----------
    horizon = H * rnd.uniform(0.52, 0.62)
    if ridges:
        # 山脊：由远及近 2-3 层，颜色渐深，顶部被雾盖住
        for i, (base, dark) in enumerate(ridges):
            col = dark
            pts = []
            seg = 8
            for k in range(seg + 1):
                x = -40 + k * (W + 80) / seg
                y = horizon + math.sin(k * 0.9 + i * 1.7 + seed) * (26 + i * 10)
                pts.append((x, y))
            d = f'M-40 {H + 40} L{pts[0][0]:.0f} {pts[0][1]:.0f}'
            for k in range(len(pts) - 1):
                cx = (pts[k][0] + pts[k + 1][0]) / 2
                d += f' C{cx:.0f} {pts[k][1]:.0f} {cx:.0f} {pts[k + 1][1]:.0f} {pts[k + 1][0]:.0f} {pts[k + 1][1]:.0f}'
            d += f' L{W + 40} {H + 40} Z'
            a(f'<path d="{d}" fill="{col}" opacity="{0.9 - i * 0.12:.2f}"/>')
    else:
        # 海面/地面：单块渐变
        a(f'<rect x="0" y="{horizon:.0f}" width="{W}" height="{H - horizon:.0f}" '
          f'fill="{sky[-1][1]}" opacity="0.92"/>')

    # ---------- 水面反光（如果有水）----------
    if water:
        # 太阳在水面的纵向光柱
        a(f'<rect x="{sx - 26}" y="{horizon:.0f}" width="52" height="{H - horizon:.0f}" '
          f'fill="{sun}" opacity="0.18" filter="url(#soft)"/>')
        # 几条横波纹
        for i in range(rnd.randint(3, 5)):
            y = horizon + 20 + i * rnd.randint(18, 30)
            a(f'<rect x="0" y="{y:.0f}" width="{W}" height="2" fill="{sun}" '
              f'opacity="{0.28 - i * 0.05:.2f}"/>')

    # ---------- 雾气：把地平线处的山脚/海面柔化 ----------
    a(f'<rect x="0" y="{horizon - 40:.0f}" width="{W}" height="90" fill="url(#haze)"/>')

    # ---------- 前景飞沫/光斑（增加"空气感"）----------
    if spray:
        a('<g filter="url(#soft)">')
        for _ in range(spray):
            x = rnd.randint(0, W)
            y = rnd.randint(int(horizon), H)
            r = rnd.uniform(2, 7)
            a(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#ffffff" opacity="{rnd.uniform(0.12, 0.3):.2f}"/>')
        a('</g>')

    # ---------- 胶片颗粒 ----------
    a(f'<rect width="{W}" height="{H}" fill="url(#grain)"/>')

    # ---------- 暗角（照片感）----------
    a('<radialGradient id="vig" cx="50%" cy="46%" r="72%">'
      '<stop offset="55%" stop-color="#000" stop-opacity="0"/>'
      f'<stop offset="100%" stop-color="#000" stop-opacity="{vignette}"/>'
      '</radialGradient>')
    a(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
    a('</svg>')
    return '\n'.join(s)


# 8 张，各自一个"情景"，色相覆盖紫/蓝/青/粉/暖橙（都偏雾紫家族，和站点配色一路）
SCENES = [
    # 晨雾山谷 —— 淡紫→灰蓝，山脊被雾截断
    dict(seed=11, name='cover-01.svg',
         sky=[(0, '#e9e2f6'), (38, '#cfc9ea'), (62, '#a9b3d9'), (82, '#8a9ac4'), (100, '#7182ad')],
         haze='#dfd7f0', sun='#f8f3ff', sun_r=44, sun_pos=(0.66, 0.36),
         ridges=[(0.56, '#8a9ac4'), (0.62, '#6f7fae')], water=False, stars=0, spray=0),
    # 夕阳湖面 —— 暖橙→深紫，水面反光
    dict(seed=22, name='cover-02.svg',
         sky=[(0, '#fdeef0'), (26, '#f8c9cf'), (48, '#e89ab2'), (70, '#b97a9e'), (100, '#7a5380')],
         haze='#f6d9de', sun='#ffd9c2', sun_r=52, sun_pos=(0.62, 0.4),
         ridges=None, water=True, stars=0, spray=0),
    # 雨后天空 —— 青蓝→黛蓝，几片残余云
    dict(seed=33, name='cover-03.svg',
         sky=[(0, '#e3f2f9'), (30, '#b8dcee'), (55, '#8fc4e2'), (78, '#5e9cc4'), (100, '#3f7ba3')],
         haze='#d4ecf5', sun='#ffffff', sun_r=40, sun_pos=(0.75, 0.3),
         ridges=None, water=True, stars=0, spray=0),
    # 熔金云海 —— 金色晚霞铺在云上
    dict(seed=44, name='cover-04.svg',
         sky=[(0, '#fdf3e0'), (24, '#f9d9a8'), (46, '#f0b878'), (70, '#c98f6d'), (100, '#8a5a5e')],
         haze='#fbe9c8', sun='#fff3d0', sun_r=60, sun_pos=(0.55, 0.5),
         ridges=None, water=False, stars=0, spray=0),
    # 星夜海洋 —— 深蓝夜空 + 海面 + 星星
    dict(seed=55, name='cover-05.svg',
         sky=[(0, '#0e1830'), (30, '#17273f'), (55, '#233a5a'), (78, '#2f5072'), (100, '#3a6185')],
         haze='#22365a', sun='#f2f6ff', sun_r=34, sun_pos=(0.68, 0.22),
         ridges=None, water=True, stars=42, spray=0),
    # 晨光海洋 —— 粉紫天 + 深蓝海
    dict(seed=66, name='cover-06.svg',
         sky=[(0, '#f7e8f4'), (28, '#e8cde8'), (52, '#c4a8d6'), (76, '#8f7ab8'), (100, '#5f548f')],
         haze='#e6d3ec', sun='#ffe9f6', sun_r=48, sun_pos=(0.7, 0.38),
         ridges=None, water=True, stars=0, spray=0),
    # 雾中山峰 —— 冷灰紫，主峰轮廓
    dict(seed=77, name='cover-07.svg',
         sky=[(0, '#eef0f7'), (36, '#d4d9ea'), (58, '#b3bcd4'), (78, '#93a0bf'), (100, '#7686a5')],
         haze='#e2e6f2', sun='#fdfdff', sun_r=42, sun_pos=(0.72, 0.34),
         ridges=[(0.55, '#93a0bf'), (0.6, '#7787a6')], water=False, stars=0, spray=0),
    # 雨后云隙 —— 光从云缝漏下来
    dict(seed=88, name='cover-08.svg',
         sky=[(0, '#dfe9f5'), (26, '#b4cce8'), (50, '#8aacd0'), (74, '#6687ad'), (100, '#4c6890')],
         haze='#c9dbf0', sun='#ffffff', sun_r=36, sun_pos=(0.6, 0.28),
         ridges=None, water=False, stars=0, spray=26),
]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for sc in SCENES:
        svg = build(**sc)
        path = os.path.join(OUT, sc['name'])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"{sc['name']}  {len(svg)/1024:5.1f} KB")
