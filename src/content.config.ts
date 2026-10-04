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
      // 封面图路径（相对 public 目录）；不填则用站点默认占位
      cover: z.string().optional(),
      category: z.string().optional(),
    }),
});

export const collections = { posts };
