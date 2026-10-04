import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'posts'>;

/** 拿全部已发布文章，按发布日期倒序 */
export async function getPublishedPosts(): Promise<Post[]> {
  const posts = await getCollection('posts');
  return posts
    .filter((p) => !p.data.draft)
    .sort((a, b) => b.data.published.valueOf() - a.data.published.valueOf());
}

/** 按标签分组，返回 { tag, count } 列表，按数量倒序 */
export async function getTags(): Promise<{ tag: string; count: number }[]> {
  const posts = await getPublishedPosts();
  const map = new Map<string, number>();
  for (const p of posts) {
    for (const t of p.data.tags) {
      map.set(t, (map.get(t) ?? 0) + 1);
    }
  }
  return [...map.entries()]
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag));
}

const dateFmt = new Intl.DateTimeFormat('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});

/** 把 Date 格式化成「2026年10月4日」 */
export function formatDate(d: Date): string {
  return dateFmt.format(d);
}

/** 把 Date 格式化成 ISO 日期（sitemap / RSS 用） */
export function toISODate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

/** 文章阅读时长估算（中文约 400 字/分钟） */
export function readingTime(body: string | undefined): number {
  if (!body) return 1;
  const chars = body.replace(/\s/g, '').length;
  return Math.max(1, Math.round(chars / 400));
}
