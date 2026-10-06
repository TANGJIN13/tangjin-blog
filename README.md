# tangjin.xyz —— 我的个人博客

[![构建并部署](https://github.com/TANGJIN13/tangjin-blog/actions/workflows/deploy.yml/badge.svg)](https://github.com/TANGJIN13/tangjin-blog/actions/workflows/deploy.yml)
[![Astro](https://img.shields.io/badge/Astro-7.3-BC52EE?logo=astro&logoColor=white)](https://astro.build)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 凡心所向，素履以往。生如逆旅，一苇以航。
>
> 一个从零手搓的静态博客：记录 Web 安全 / CTF 方向的复现、踩坑与思考。

**在线访问 👉 [https://tangjin.xyz](https://tangjin.xyz)**

![站点预览](docs/screenshot-home.png)

---

## 这是什么

这是我（[@TANGJIN13](https://github.com/TANGJIN13)，桂林电子科技大学 25 级网安学生）自己动手搭建的个人博客。没有使用现成主题，页面、组件、部署链路都是自己写的，算是一个"练手 + 自用"的项目。

- 写作在 **Obsidian** 里完成，一条命令发布上线
- 推送到 GitHub 后 **1~2 分钟自动部署**到腾讯云服务器
- 所有数据（文章、评论）都在自己的仓库里，不依赖第三方平台

## 功能特性

| 模块 | 说明 |
|---|---|
| 首页 | 壁纸轮播 + 文章列表 + 侧栏（日历 / 节假日 / 站点统计 / 活跃度热力图） |
| 文章页 | 顶部横幅 + 自动生成目录 + 文末分享（复制链接 / 微博 / QQ 空间） |
| 评论 | Giscus（GitHub Discussions 驱动，见下文） |
| 音乐播放器 | 本地 + 在线歌单双来源，滚动歌词（LRC 逐行高亮）、歌词时间微调、失效音源自动跳过 |
| 主题 | 亮色 / 暗色 / 跟随系统，评论框主题同步切换 |
| 特效 | 樱花飘落、沉浸阅读模式 |
| 其他 | 归档 / 分类 / 标签 / 友链 / 留言板 / 全文搜索 / RSS / Sitemap |
| 搜索引擎 | robots.txt + 自动 sitemap，部署后自动推送（百度主动推送 / IndexNow / 百度 JS 自动推送），详见 [SEO 文档](docs/SEO-搜索引擎提交.md) |

## 技术栈

| 层次 | 技术 |
|---|---|
| 框架 | Astro 7.3.5（Content Layer API） |
| 语言 | TypeScript |
| 样式 | 原生 CSS（oklch 色彩空间） |
| 构建 | pnpm + Vite |
| 评论 | Giscus + GitHub Discussions（[tangjin-blog-comments](https://github.com/TANGJIN13/tangjin-blog-comments)） |
| 部署 | GitHub Actions → rsync → 腾讯云 Ubuntu 24.04 → Nginx |

## 目录结构

```
tangjin-blog/
├── .github/workflows/deploy.yml   # 自动部署工作流（核心）
├── public/                        # 静态资源（壁纸、头像、音乐）
├── src/
│   ├── site.ts                    # 站点配置（标题、座右铭、社交链接等）
│   ├── content/posts/             # 文章 Markdown
│   ├── pages/                     # 页面路由
│   ├── components/                # 组件（音乐播放器、评论、热力图…）
│   ├── layouts/                   # 布局
│   └── styles/                    # 全局样式
├── publish.cjs / publish.sh       # Obsidian 笔记一键发布脚本
├── deploy.ps1                     # 本地直传服务器脚本（应急用）
└── astro.config.mjs               # Astro 配置
```

## 写作与发布

### 方式一：直接写 Markdown

在 `src/content/posts/` 新建 `.md` 文件，frontmatter 格式：

```markdown
---
title: "文章标题"
description: "摘要"
published: 2026-10-06
tags: ["Web安全", "CTF"]
category: web-security
---

正文用 Markdown 写。
```

然后 `git push`，自动上线。

### 方式二：Obsidian 一键发布（我的日常用法）

博客项目放在我的 Obsidian 笔记库内，写完笔记后：

```bash
./publish.sh <笔记路径>     # 单篇发布
node publish.cjs            # 批量发布 _publish/ 文件夹里的笔记
```

脚本会把笔记复制到 `src/content/posts/` 并自动 commit + push，触发部署。

## 评论系统

评论由 [Giscus](https://giscus.app) 驱动，原理很妙：

- 每条评论实际是对应文章在 [tangjin-blog-comments](https://github.com/TANGJIN13/tangjin-blog-comments) 仓库 **Discussions** 里的一条讨论
- 读者用 GitHub 账号登录即可评论、点赞、回复
- 博客本身零后端、零数据库，评论数据全在 GitHub 上
- 按页面路径（pathname）自动匹配讨论串

## 自动部署原理（GitHub Actions）

整条链路：**`git push` → GitHub Actions 构建 → rsync 同步 → Nginx 生效**，全部免人工干预。

```
本地 push main 分支
        │
        ▼
┌──────────────── GitHub Actions（ubuntu-latest）────────────────┐
│  1. 检出代码（actions/checkout）                                │
│  2. 安装 pnpm + Node.js 22，缓存依赖                            │
│  3. pnpm install --frozen-lockfile                              │
│  4. pnpm build        → 生成 dist/ 静态文件                     │
│  5. 校验 dist/index.html 存在                                   │
│  6. 把 Secret 里的私钥写入 ~/.ssh/deploy_key                    │
│  7. rsync -rltpz --delete dist/ → 服务器:/                      │
└────────────────────────────────────────────────────────────────┘
        │
        ▼
腾讯云服务器（49.232.251.198）
  · SSH 登录后被强制执行 rrsync -wo /var/www/blog（只写、只允许 rsync）
  · 文件落到 /var/www/blog，--delete 清理旧文件
        │
        ▼
Nginx 直接提供静态文件 → https://tangjin.xyz 更新
```

几个设计细节：

- **最小权限密钥**：部署用的 SSH 密钥在服务器 `authorized_keys` 里被限制为 `command="/usr/bin/rrsync -wo /var/www/blog",restrict`——这把钥匙**只能**通过 rsync 往站点目录写文件，不能执行任何 shell 命令、不能读取文件。即使 GitHub Secret 泄露，攻击者也无法登录服务器。
- **rrsync 白名单**：rrsync 对 rsync 选项有安全白名单，`--chmod`、`--no-group` 等选项会被拒绝，因此部署命令只使用 `-rltpz --delete` 这类白名单内的选项。
- **Secrets**：仓库只存一个机密 `SSH_PRIVATE_KEY`（部署私钥），服务器地址等非机密信息直接写在 workflow 里。
- **串行部署**：workflow 配置了 `concurrency`，同一时间只跑一个部署，避免并发写坏站点目录。

配置文件见 [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)。

## 本地开发

```bash
git clone git@github.com:TANGJIN13/tangjin-blog.git
cd tangjin-blog
pnpm install
pnpm dev        # 开发服务器
pnpm build      # 构建到 dist/
pnpm preview    # 预览构建结果
```

## 许可证

MIT — 代码随便参考，内容（文章）归我所有。
