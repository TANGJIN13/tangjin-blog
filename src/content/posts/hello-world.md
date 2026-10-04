---
title: "你好，世界：这个博客是做什么的"
description: "用一篇短文说明这个自建博客的定位、技术栈，以及它和博客园的关系。"
published: 2026-10-04
tags: ["随笔", "建站"]
---

欢迎来到我的新家。这篇短文交代三件事：这里写什么、怎么搭的、以及为什么从博客园搬出来。

## 这里写什么

三个方向：

1. **CTF 题解**——踩过的坑、完整的复现思路，而不是只有 flag。
2. **漏洞复现**——Web 安全方向为主，记录环境搭建到利用链的完整过程。
3. **工具与笔记**——自己折腾过、验证有效的配置和方法论。

> 目标是让三个月后的自己能看懂，也让同路人少走弯路。

## 技术栈

这个站是**静态博客**，构建与托管链路如下：

```ts
// 内容层：Astro Content Collections
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
  schema: z.object({
    title: z.string(),
    published: z.coerce.date(),
    tags: z.array(z.string()).default([]),
  }),
});
```

- **框架**：Astro 7，静态输出，服务器只需 Nginx 发文件，内存占用近乎为零。
- **内容**：Markdown，源码用 git 管理，全站可回溯。
- **托管**：腾讯云轻量服务器，本地构建后 rsync 推送。

```bash
# 本地构建并预览
pnpm build
pnpm preview

# 推送到服务器
rsync -avz --delete dist/ tangjin:/var/www/blog/
```

## 为什么搬出来

博客园给了我很好的起点，但自定义空间始终受限——壁纸 banner、封面图、看板娘这些"做不到的清单"，自建之后全都有了。更重要的是：**站点的每一行代码都是自己的**，从里到外都可控，这对一个做安全的人来说，本身就是一种练习。
