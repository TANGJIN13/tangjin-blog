// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { remarkObsidian } from './remark-obsidian.mjs';

// https://astro.build/config
export default defineConfig({
  site: 'https://tangjin.xyz',
  output: 'static',
  compressHTML: true,
  markdown: {
    // Obsidian 语法兼容：![[图片]] 嵌入自动转成博客可渲染的图片；> [!标注] 转成引用块
    remarkPlugins: [remarkObsidian()],
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
