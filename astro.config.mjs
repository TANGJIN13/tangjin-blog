// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://tangjin.xyz',
  output: 'static',
  compressHTML: true,
  markdown: {
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
