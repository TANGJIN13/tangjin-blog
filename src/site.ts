/**
 * 站点级配置 —— 全局唯一事实来源。
 * 改这里的值，全站（head、页脚、RSS、sitemap）都会跟着变。
 */
export const site = {
  url: 'https://tangjin.xyz',
  /** 导航栏左上角显示的名字 */
  title: "Tj's Blog",
  /** 浏览器标签页标题（首页显示这个；内页显示「页面名 - 这个」） */
  tabTitle: "tj's Blog",
  description: 'Web 安全与 CTF 方向的个人博客，记录复现、踩坑与思考。',
  author: 'tj',
  lang: 'zh-CN',

  /**
   * 首屏横幅上轮换浮现的句子 —— 每隔几秒淡入换一句。
   * 想换句子 / 加句子只改这个数组即可（sub 是下面的小字注解，可省略）。
   */
  mottos: [
    { text: '凡心所向，素履以往', sub: '生如逆旅，一苇以航' },
    { text: '路漫漫其修远兮', sub: '吾将上下而求索' },
    { text: '星光不问赶路人', sub: '时光不负有心人' },
    { text: '但行好事，莫问前程', sub: '前路漫漫亦灿灿' },
    { text: '心之所向，无问西东', sub: '慢慢来，会比较快' },
    { text: '山高路远，看世界，也找自己', sub: '尽情体验，不问归期' },
  ],

  heroImage: '/images/hero.svg',
  avatar: '/images/avatar.png',
  /** 备案号 —— 显示在页脚，链接到工信部 */
  icp: '桂ICP备2026005024号-1',
  /**
   * 建站日期（YYYY-MM-DD）—— 首页「运行时长」从这一天开始算。
   * 想改成实际的建站日，改这一行即可。
   */
  startDate: '2026-10-04',
  /**
   * 留言板评论服务（自建 Waline，部署在同域 /waline/ 下）。
   * 读者无需登录任何账号，填个昵称就能留言。
   */
  waline: {
    serverURL: '/waline/',
  },
  /**
   * 搜索引擎站长平台的「站点归属验证」代码。
   * 在各平台拿到验证串后填到对应字段，提交部署即自动通过验证（留空则不输出该标签）。
   *   - Google：Search Console → 添加资源 → 「HTML 标记」，取 google-site-verification 的 content
   *   - 百度：搜索资源平台 → 站点管理 → 「HTML标签验证」，取 baidu-site-verification 的 content
   *   - Bing：Webmaster Tools → 验证，取 msvalidate.01 的 content
   */
  verify: {
    google: 'cYpQxk3oM8jvwlu2tnr4CY0A9_UNELFV9zr5FibRGR4',
    baidu: '',
    bing: '',
  },
  footer: {
    since: 2026,
  },
  links: [
    { label: 'GitHub', href: 'https://github.com/TANGJIN13' },
  ],
} as const;
