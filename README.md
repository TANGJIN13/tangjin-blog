# tangjin.xyz —— 个人博客

基于 **Astro 7** 的静态博客站点，部署于腾讯云。

## 技术栈

| 层次 | 技术 |
|---|---|
| 框架 | Astro 7.3.5（Content Layer API） |
| 语言 | TypeScript |
| 样式 | 原生 CSS（oklch 配色） |
| 构建 | pnpm + Vite |
| 部署 | GitHub Actions → rsync → Nginx |
| 评论 | Giscus（GitHub Discussions） |
| 服务器 | 腾讯云 Ubuntu 24.04 |

## 功能

- 首页三栏布局（壁纸轮播 + 文章列表 + 侧栏）
- 文章页（横幅 + 目录 + 评论）
- 归档 / 分类 / 标签 / 友链 / 关于 / 搜索
- 本地音乐播放器（支持多曲切换）
- 深浅色主题切换
- 樱花特效 + 日历热力图
- 沉浸阅读模式
- RSS + Sitemap
- 自动部署（推 GitHub 即上线）

## 本地开发

```bash
# 克隆
git clone https://github.com/TANGJIN13/tangjin-blog.git
cd tangjin-blog

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建
pnpm build

# 预览构建结果
pnpm preview
```

## 目录结构

```
tangjin-blog/
├── .github/workflows/deploy.yml   # 自动部署工作流
├── public/                        # 静态资源（壁纸、头像、音乐）
├── src/
│   ├── site.ts                    # 站点配置
│   ├── content/posts/             # 文章 Markdown
│   ├── pages/                     # 页面路由
│   ├── components/                # 组件
│   ├── layouts/                   # 布局
│   └── styles/                    # 样式
├── deploy.ps1                     # 本地直传服务器脚本
├── publish.js                     # Obsidian 笔记发布脚本
└── astro.config.mjs               # Astro 配置
```

## 管理内容

### 写文章

在 `src/content/posts/` 新建 `.md` 文件：

```markdown
---
title: "文章标题"
description: "摘要"
published: 2026-10-05
tags: ["Web安全", "CTF"]
category: web-security
---

正文用 Markdown 写。
```

推送到 GitHub 即自动上线。

### 修改配置

编辑 `src/site.ts`：站点标题、座右铭、备案号、社交链接等。

### 添加音乐

将 MP3 文件放入 `public/music/`，编辑 `src/components/MusicPlayer.astro` 的 `tracks` 数组。

## 自动部署

推送 `main` 分支触发 GitHub Actions：

```
git add .
git commit -m "更新内容"
git push
```

约 1-2 分钟后 https://tangjin.xyz 自动更新。

## 许可证

MIT
