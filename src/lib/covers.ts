/**
 * 文章封面兜底池 —— 按皮肤分组。
 *
 * 为什么单独抽一个模块而不是各处写一遍：
 *   这套池子原来散在 3 个文件里（PostCard / PostListItem / index），
 *   三份内容必须完全一致，否则同屏会出现「同一个位置换页后封面不一样」。
 *   加皮肤之后变成 2 组 = 6 份，再各写一遍必然会漂。
 *
 * ⚠️ 硬约束：封面池与壁纸池（banner-*）**不能有任何重叠**。
 *    一旦重叠，同一屏里就会出现「壁纸 = 某张卡片封面」的廉价撞图。
 *    这个坑在改版前踩过，这里用目录隔离（covers/ 与 covers-ocean/）从源头避免。
 */

/** 默认（雾紫）皮肤：暖粉水彩插画 */
const PASTEL = [
  '/images/covers/cover-01.jpg',
  '/images/covers/cover-02.jpg',
  '/images/covers/cover-03.jpg',
  '/images/covers/cover-04.jpg',
  '/images/covers/cover-05.jpg',
  '/images/covers/cover-06.jpg',
  '/images/covers/cover-07.jpg',
  '/images/covers/cover-08.jpg',
];

/** 大海皮肤：青蓝抽象海景（SVG，单张 2~4KB） */
const OCEAN = [
  '/images/covers-ocean/ocean-cover-01.svg',
  '/images/covers-ocean/ocean-cover-02.svg',
  '/images/covers-ocean/ocean-cover-03.svg',
  '/images/covers-ocean/ocean-cover-04.svg',
  '/images/covers-ocean/ocean-cover-05.svg',
  '/images/covers-ocean/ocean-cover-06.svg',
  '/images/covers-ocean/ocean-cover-07.svg',
  '/images/covers-ocean/ocean-cover-08.svg',
];

export const COVER_POOLS: Record<string, string[]> = {
  default: PASTEL,
  ocean: OCEAN,
};

/**
 * 按索引取一张兜底封面。
 *
 * @param index 文章在列表里的位置（用来轮换，避免相邻撞图）
 * @param skin  皮肤 id（默认皮肤传 undefined / 'default'）
 */
export function fallbackCover(index: number, skin?: string): string {
  const pool = COVER_POOLS[skin ?? 'default'] ?? PASTEL;
  return pool[index % pool.length];
}

/**
 * 取「另一套皮肤」的同位置封面。
 *
 * 用途：封面也要跟着皮肤切换，但不能用 JS 换 src（会有解码延迟、闪一下）。
 *   所以两组图都渲染进 DOM，用 CSS 按 data-skin 控制显隐 —— 这需要
 *   每个位置同时知道两套皮肤各自的图。见 PostListItem / PostCard 的用法。
 */
export function coverPair(index: number, skin?: string): { primary: string; alt: string } {
  const active = COVER_POOLS[skin ?? 'default'] ?? PASTEL;
  const other = skin === 'ocean' ? PASTEL : OCEAN;
  return {
    primary: active[index % active.length],
    alt: other[index % other.length],
  };
}
