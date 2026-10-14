/**
 * 文章封面兜底池。
 *
 * 为什么单独抽一个模块而不是各处写一遍：
 *   这套池子原来散在 3 个文件里（PostCard / PostListItem / index），
 *   三份内容必须完全一致，否则同屏会出现「同一个位置换页后封面不一样」。
 *
 * ⚠️ 硬约束：封面池与壁纸池（banner-*）**不能有任何重叠**。
 *    一旦重叠，同一屏里就会出现「壁纸 = 某张卡片封面」的廉价撞图。
 *    这个坑在改版前踩过，靠不同目录隔离（covers/ vs wallpapers/）从源头避免。
 */

const PASTEL = [
  '/images/covers/cover-01.svg',
  '/images/covers/cover-02.svg',
  '/images/covers/cover-03.svg',
  '/images/covers/cover-04.svg',
  '/images/covers/cover-05.svg',
  '/images/covers/cover-06.svg',
  '/images/covers/cover-07.svg',
  '/images/covers/cover-08.svg',
];

export const COVER_POOLS: Record<string, string[]> = {
  default: PASTEL,
};

/**
 * 按索引取一张兜底封面。
 *
 * @param index 文章在列表里的位置（用来轮换，避免相邻撞图）
 * @param skin  皮肤 id（保留参数，将来再加皮肤不用改调用方）
 */
export function fallbackCover(index: number, skin?: string): string {
  const pool = COVER_POOLS[skin ?? 'default'] ?? PASTEL;
  return pool[index % pool.length];
}
