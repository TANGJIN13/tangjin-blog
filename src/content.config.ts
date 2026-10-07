import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/posts' }),
  schema: z.object({
      title: z.string(),
      description: z.string(),
      // 发布日期（YAML 里写字符串会自动转成 Date）
      published: z.coerce.date(),
      // 最后更新（可选，比发布日期新时显示）
      updated: z.coerce.date().optional(),
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
      date: z.coerce.date(),
      // 心情 emoji（可选）
      mood: z.string().optional(),
      // 配图（可选，相对 public 目录的路径数组）
      images: z.array(z.string()).default([]),
    }),
});

export const collections = { posts, says };
