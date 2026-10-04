/**
 * 站点级配置 —— 全局唯一事实来源。
 * 改这里的值，全站（head、页脚、RSS、sitemap）都会跟着变。
 */
export const site = {
  url: 'https://tangjin.xyz',
  title: 'tj',
  titleSuffix: ' · 安全笔记',
  description: 'Web 安全与 CTF 方向的个人博客，记录复现、踩坑与思考。',
  author: 'tj',
  lang: 'zh-CN',

  /**
   * 首屏壁纸上的那句「座右铭」—— 会在页面顶部大字显示。
   * 想换句子只改这一行即可。
   */
  motto: '凡心所向，素履以往',
  /** 座右铭下面的小字注解（留空则不显示） */
  mottoSub: '生如逆旅，一苇以航',

  heroImage: '/images/hero.svg',
  avatar: '/images/avatar.png',
  icp: '',
  footer: {
    since: 2026,
  },
  links: [
    { label: 'GitHub', href: 'https://github.com/TANGJIN13' },
  ],
} as const;
