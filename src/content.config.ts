import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// YAML 里不带时区的日期（如 2026-10-07T16:34:22）会被 js-yaml 当成 UTC，
// 博客上显示会偏 8 小时。这里统一矫正：
// ① 字符串 → 直接补东八区偏移（最精确，模板里已给日期加引号走这条路）
// ② js-yaml 已解析成 Date 的（无时区时间戳按 UTC 解释）→ 平移回东八区钟表时间
// 注意：frontmatter 里请不要手写 Z / +08:00 等时区后缀，写本地时间即可。
const localDate = z.preprocess((v) => {
  if (typeof v === 'string') {
    const s = v.trim().replace(' ', 'T');
    if (/^\d{4}-\d{2}-\d{2}([T]\d{2}:\d{2}(:\d{2}(\.\d+)?)?)?$/.test(s)) {
      return s.length === 10 ? `${s}T00:00:00+08:00` : `${s}+08:00`;
    }
    return v;
  }
  if (v instanceof Date && !Number.isNaN(v.getTime())) {
    return new Date(v.getTime() - 8 * 3600 * 1000);
  }
  return v;
}, z.coerce.date());

const posts = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/posts' }),
  schema: z.object({
      title: z.string(),
      description: z.string(),
      // 发布日期（YAML 里写字符串会自动转成 Date）
      published: localDate,
      // 最后更新（可选，比发布日期新时显示）
      updated: localDate.optional(),
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false),
      // 置顶：首页/分类页浮到最前（归档页仍按日期倒序，不受影响）
      pinned: z.boolean().default(false),
      // 封面图路径（相对 public 目录）；不填则用站点默认占位
      cover: z.string().optional(),
      category: z.string().optional(),
    }),
});

const says = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/says' }),
  schema: z.object({
      // 发表时间（写在 frontmatter，便于精确排序）
      date: localDate,
      // 心情 emoji（可选）
      mood: z.string().optional(),
      // 配图（可选，相对 public 目录的路径数组）
      images: z.array(z.string()).default([]),
    }),
});

export const collections = { posts, says };
