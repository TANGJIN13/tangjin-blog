// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { satteri } from '@astrojs/markdown-satteri';
import { obsidianCompatPlugin } from './remark-obsidian.mjs';

// 统一按北京时间（东八区）渲染日期。
// 构建机时区不同（GitHub Actions 默认 UTC）会让页面时间比实际早 8 小时，这里显式固定。
process.env.TZ = 'Asia/Shanghai';

// https://astro.build/config
export default defineConfig({
  site: 'https://tangjin.xyz',
  output: 'static',
  compressHTML: true,
  markdown: {
    // Astro 7 默认的 Sätteri 处理器 + Obsidian 语法兼容插件：
    // ![[图片]] 自动转成博客可渲染的图片；> [!标注] 转成引用块
    processor: satteri({
      mdastPlugins: [obsidianCompatPlugin],
    }),
    shikiConfig: {
      theme: 'catppuccin-latte',
      wrap: true,
    },
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/draft'),
    }),
  ],
});
