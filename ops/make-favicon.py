#!/usr/bin/env python3
"""
从头像生成站点图标。

设计要点：
  1. 圆形裁剪 —— 和侧边栏资料卡的圆形头像一致，语义清晰
  2. 轻微放大 —— 让主体在 16x16 下占比更大、更容易辨认
  3. 文件名带版本号 —— 换图标时改 VERSION 可强制浏览器重新拉取
     （浏览器对 favicon 的缓存极其顽固，改 URL 是最可靠的破缓存方式）

用法:
    python ops/make-favicon.py
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SRC = PUBLIC / "images" / "avatar.png"

# 改这个数字即可强制所有浏览器重新拉取图标
VERSION = 3

# 圆形裁剪后再放大一点，让主体更充满
ZOOM = 0.92

# 圆形外部是否填充纯色（None = 透明）
OUTSIDE_FILL = None


def center_square(img: Image.Image, zoom: float = 1.0) -> Image.Image:
    """裁成居中正方形；zoom<1 表示向内多切一点（主体显得更大）"""
    w, h = img.size
    side = int(min(w, h) * zoom)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def circular(img: Image.Image) -> Image.Image:
    """应用圆形遮罩"""
    size = img.size[0]
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    # 稍微内缩 1px，避免边缘锯齿
    draw.ellipse((1, 1, size - 2, size - 2), fill=255)

    out = Image.new("RGBA", (size, size), (0, 0, 0, 0) if OUTSIDE_FILL is None else OUTSIDE_FILL + (255,))
    out.paste(img, (0, 0), mask)
    return out


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"找不到源图: {SRC}")

    img = Image.open(SRC).convert("RGBA")
    print(f"源图      : {SRC.name}  {img.size[0]}x{img.size[1]}")

    sq = center_square(img, ZOOM)
    print(f"裁剪(zoom={ZOOM}): {sq.size[0]}x{sq.size[1]}")

    circ = circular(sq)
    print("已应用圆形遮罩")

    # 各尺寸 PNG（文件名带版本号以破缓存）
    outputs = [
        (16, f"icon-{VERSION}-16.png"),
        (32, f"icon-{VERSION}-32.png"),
        (180, "apple-touch-icon.png"),   # iOS 约定名，保持不变
    ]
    for size, name in outputs:
        out = circ.resize((size, size), Image.LANCZOS)
        path = PUBLIC / name
        out.save(path, "PNG", optimize=True)
        print(f"  {name:26} {size:>3}x{size:<3}  {path.stat().st_size / 1024:6.1f} KB")

    # 多尺寸 ICO（同尺寸取最大帧作为源，Pillow 会内嵌三帧）
    ico_name = f"icon-{VERSION}.ico"
    ico_path = PUBLIC / ico_name
    circ.resize((48, 48), Image.LANCZOS).save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print(f"  {ico_name:26}  16/32/48  {ico_path.stat().st_size / 1024:6.1f} KB")

    print(f"\n完成。记得同步更新 Base.astro 里的图标路径（版本 v{VERSION}）。")


if __name__ == "__main__":
    main()
