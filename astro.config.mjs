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
    // ![[图片]] 自动转成博客可渲染的图片；> [!标注] 转成引用块；段内单个换行转 <br>
    processor: satteri({
      mdastPlugins: [obsidianCompatPlugin],
    }),
    // 关掉「智能标点」（smartypants）。
    // 它会把 -- 变成 –（en dash）、把 ' 变成 '、... 变成 …，
    // 对**技术博客是灾难**：文章里 curl --http1.1 -sSi 会被渲染成 curl –http1.1 -sSi，
    // 读者复制出去就是一条错命令。Obsidian 默认也不做这个转换，
    // 关掉之后「编辑器里看到什么，站上就是什么」。
    smartypants: false,
    shikiConfig: {
      // 双主题：浅色用 latte、深色用 mocha。
      // 单主题时 Shiki 会把颜色写成**内联样式**，内联优先级高于样式表，
      // 暗色下代码块就会顶着浅色底 + 浅色 token（怎么改 CSS 都盖不掉）。
      // 双主题会改成输出 --shiki-light / --shiki-dark 变量，再由 global.css 按主题切换。
      themes: { light: 'catppuccin-latte', dark: 'catppuccin-mocha' },
      wrap: true,
    },
  },
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/draft'),
    }),
  ],
});
