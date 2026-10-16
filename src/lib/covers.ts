/**
 * 文章封面兜底池。
 *
 * 简化后：PostCard 默认不显示封面，只有 post.data.cover 显式写了路径才显示左侧小缩略图。
 * 这套池子保留下来供「想让文章有封面的用户」在 frontmatter 里引用，例：
 *   cover: /images/covers/cover-01.jpg
 *
 * ⚠️ 硬约束：封面池与壁纸池（banner-*）**不能有任何重叠**。
 *    一旦重叠，同一屏里就会出现「壁纸 = 某张卡片封面」的廉价撞图。
 *    这个坑在改版前踩过，靠不同目录隔离（covers/ vs wallpapers/）从源头避免。
 *
 * 2026-10-16 用户挑选：从原有 7 张里**只留 3 张水彩风**（原 C6 林中小屋 / C4 粉橘云层 /
 * C5 圆月雪山），已重编号为 01/02/03；其余 4 张物理删除（备份在 .shots/backup-covers/）。
 */

const POOL = [
  '/images/covers/cover-01.jpg',
  '/images/covers/cover-02.jpg',
  '/images/covers/cover-03.jpg',
  '/images/covers/cover-04.jpg',
  '/images/covers/cover-05.jpg',
  '/images/covers/cover-06.jpg',
  '/images/covers/cover-07.jpg',
  '/images/covers/cover-08.jpg',
  '/images/covers/cover-09.jpg',
  '/images/covers/cover-10.jpg',
  '/images/covers/cover-11.jpg',
  '/images/covers/cover-12.jpg',
];

export const COVER_POOLS: Record<string, string[]> = {
  default: POOL,
};

/**
 * 按索引取一张兜底封面。
 * 当前 PostCard 不再自动展示兜底封面（保持极简文本卡），仅当调用方需要时使用。
 */
export function fallbackCover(index: number, skin?: string): string {
  const pool = COVER_POOLS[skin ?? 'default'] ?? POOL;
  return pool[index % pool.length];
}
