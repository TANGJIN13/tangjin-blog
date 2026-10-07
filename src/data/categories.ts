export interface Category {
  name: string;
  slug: string;
  description?: string;
  /** Icon 组件里的图标名 */
  icon?: string;
}

export const categories: Category[] = [
  { name: '文章', slug: 'article', description: '技术文章与笔记', icon: 'article' },
  { name: '年度总结', slug: 'summary', description: '年度回顾与总结', icon: 'calendar' },
  { name: '工具使用', slug: 'tools', description: '工具配置与使用心得', icon: 'terminal' },
];
