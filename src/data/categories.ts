export interface Category {
  name: string;
  slug: string;
  description?: string;
  /** Icon 组件里的图标名 */
  icon?: string;
}

export const categories: Category[] = [
  { name: 'Web 安全', slug: 'web-security', description: 'Web 安全相关文章', icon: 'lock' },
  { name: 'CTF', slug: 'ctf', description: 'CTF 题解与笔记', icon: 'flag' },
  { name: '随笔', slug: 'essay', description: '日常随笔与思考', icon: 'text' },
  { name: '工具', slug: 'tools', description: '工具使用与配置', icon: 'terminal' },
];
