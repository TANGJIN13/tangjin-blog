/**
 * 关于页的个人资料 —— 改这里就能改「关于我」页面，不用碰 HTML。
 *
 * 注意：icon 字段必须是 src/components/Icon.astro 里已有的名字，
 * 写错了会退化成占位图标。可用的有：
 * lock flag code terminal mail github link sparkle chart calendar person
 * book text image moon wave archive folder tag search send copy sun monitor
 */

export interface Skill {
  name: string;
  icon: string;
  /** 鼠标悬停时显示的一句说明 */
  note?: string;
}

export interface TimelineItem {
  /** 显示在卡片左上角，比如「2026」或「2026.03」 */
  date: string;
  title: string;
  desc: string;
  icon?: string;
}

export const profile = {
  /** 头像旁边那行身份标签 */
  headline: '桂林电子科技大学 · 25级网安 · Web 安全',

  /**
   * 「我是谁」下面的自我介绍。数组里每一项是一个段落，
   * 可以用 HTML（比如 <strong>加粗</strong>）。
   */
  intro: [
    '你好，我是 <strong>tj</strong>。桂林电子科技大学 25 级网络安全专业，安网阁社团的一员，目前主要往 <strong>Web 安全</strong>方向摸索,现在还是一个只会点鼠标的猴子。',
    '这个站是我自己人机协同搭的，主要放两类东西：一是 CTF 打完之后的<strong>复现和复盘</strong>，二是学习路上踩过的坑。',
    '如果你也在学安全，或者对某篇文章有不同看法，欢迎在下面留言——我都会看。',
    '如果你想联系我，可以通过 <strong>2020556277@qq.com</strong> 或 <strong>GitHub</strong> 找到我。',
  ],

  /**
   * 技能卡片 —— 全部按「正在学」展示（虚线卡片）。
   * 想分「能上手 / 正在学」两组的话，把部分条目移回下面的 skills 即可。
   */
  skills: [] as Skill[],

  /** 正在啃的 */
  learning: [
    { name: 'Web 安全', icon: 'lock', note: 'SQL 注入 / XSS / 文件上传' },
    { name: 'Python', icon: 'code', note: '写脚本、跑 PoC' },
    { name: 'Linux', icon: 'terminal', note: '日常环境' },
    { name: 'Docker', icon: 'monitor', note: '搭靶场用' },
    { name: 'JavaScript', icon: 'code', note: '前端审计' },
    { name: '内网渗透', icon: 'lock', note: '还在入门' },
    { name: 'Astro', icon: 'sparkle', note: '就是这个站' },
  ] as Skill[],

  /** 时间线，从上到下按顺序显示 */
  timeline: [
    {
      date: '2026.10',
      title: '这个博客上线',
      desc: '用 Astro 从零搭起来，配好 GitHub Actions 自动部署。',
      icon: 'sparkle',
    },
    {
      date: '2025',
      title: '开始打 CTF',
      desc: '跟着队伍参加比赛，赛后把题目复现写下来。',
      icon: 'flag',
    },
    {
      date: '2025',
      title: '网安专业入学 · 虽然专业不是自己预期的但最后也是挺感兴趣的。',
      desc: '进入桂林电子科技大学网络安全专业。',
      icon: 'book',
    },
  ] as TimelineItem[],

  /** 页面最后那句自己想说的话 */
  quote: '安全是一场没有终点的旅程。',
};
