#!/usr/bin/env python3
"""
从头像生成站点图标（favicon / apple-touch-icon）。

用法:
    python ops/make-favicon.py

输入:  public/images/avatar.png
输出:  public/favicon.ico            多尺寸 ICO（16/32/48）
       public/favicon-32x32.png
       public/favicon-16x16.png
       public/apple-touch-icon.png  180x180（iOS 添加到主屏）
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SRC = PUBLIC / "images" / "avatar.png"


def center_square(img: Image.Image) -> Image.Image:
    """裁成居中正方形，保证缩放后主体不被拉伸"""
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"找不到源图: {SRC}")

    img = Image.open(SRC).convert("RGBA")
    print(f"源图: {SRC.name}  {img.size[0]}x{img.size[1]}")

    sq = center_square(img)
    print(f"裁切后: {sq.size[0]}x{sq.size[1]}")

    # 各尺寸 PNG
    for size in (16, 32, 180):
        out = sq.resize((size, size), Image.LANCZOS)
        if size == 180:
            name = "apple-touch-icon.png"
        else:
            name = f"favicon-{size}x{size}.png"
        path = PUBLIC / name
        out.save(path, "PNG", optimize=True)
        print(f"  生成 {name:26} {size}x{size}  {path.stat().st_size / 1024:.1f} KB")

    # 多尺寸 ICO
    ico_path = PUBLIC / "favicon.ico"
    sq.resize((48, 48), Image.LANCZOS).save(
        ico_path,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print(f"  生成 {'favicon.ico':26} 16/32/48  {ico_path.stat().st_size / 1024:.1f} KB")

    print("\n完成。记得在 Base.astro 的 <head> 里引用这些文件。")


if __name__ == "__main__":
    main()
