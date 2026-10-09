# tangjin-blog

[![构建并部署](https://github.com/TANGJIN13/tangjin-blog/actions/workflows/deploy.yml/badge.svg)](https://github.com/TANGJIN13/tangjin-blog/actions/workflows/deploy.yml)
[![Astro](https://img.shields.io/badge/Astro-7.3-BC52EE?logo=astro&logoColor=white)](https://astro.build)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 一个从零手搓的 **Astro 静态博客**：文章 / 说说 / 相册 / 归档 / 全文搜索 / 深浅主题 / 评论 / 音乐播放器，推送到 GitHub 即自动部署上线。
>
> 它既是作者的个人站点源码，也当作一个可参考、可 Fork 的博客项目开源。

**在线预览 👉 [https://tangjin.xyz](https://tangjin.xyz)**

📘 内容写作与功能使用手册：[使用指南.md](使用指南.md)

![首页预览](docs/screenshot-home.png)

---

## ✨ 特性

| 模块 | 说明 |
|---|---|
| 首页 | 分类入口 + 文章卡片网格（16:9 封面 / 日期 / 分类 / 摘要 / 标签）+ 标签区 + 侧栏（日历 / 节假日 / 站点统计 / 活跃度热力图），移动端侧栏自动堆叠 |
| 文章页 | 顶部横幅 + 自动生成目录 + 阅读进度条 + 上一篇/下一篇 + 文末分享；配图点击放大（再点一下切 1:1 原始尺寸，可拖动看细节） |
| 说说 | `/says/` 短动态，按时间倒序，支持心情 emoji 与配图；草稿用 `draft: true` 暂不公开 |
| 相册 | `/album/` 瀑布流照片墙，点击开大图灯箱（← / → 翻页、Esc 关闭） |
| 关于页 | `/about/` 名片 + 自动统计（篇数 / 天数 / 字数）+ 技能卡 + 时间线 |
| 评论 | 文章页 / 关于页用 **Giscus**，留言板用自建 **Waline**（免登录匿名留言），见下文 |
| 音乐播放器 | 本地 + 在线歌单双来源，滚动歌词（LRC 逐行高亮）、失效音源自动跳过 |
| 主题 | 亮色 / 暗色 / 跟随系统，切换时底部提示当前模式，评论框主题同步 |
| 特效 | 进入文章时樱花飘落约 10 秒、沉浸阅读模式 |
| 全站壁纸横幅 | 多张壁纸自动轮播（每隔几秒淡入切换，换页接着上一张继续）。**每个页面顶部都有**：首页大图（88vh），内页压到 35vh 并把页面标题压在壁纸上（电脑端；手机端内页自动隐藏，避免多滑一屏） | |
| 资源库 | `/downloads/` 文件下载页：文件放 `public/files/`、在 `src/data/downloads.json` 登记一条即可，大小 / 日期 / 图标自动生成，支持外部网盘链接 |
| 搜索 | `/search/` 全文搜索：文章（标题 / 描述 / 标签 / 分类）+ 资源库文件都能搜到，资源条目点击直接下载 |
| 归档 | 按年份竖向时间线展示，含总字数统计 |
| 其他 | 归档 / 分类 / 标签 / 友链 / 留言板 / RSS / Sitemap |
| SEO | `robots.txt` + 自动 sitemap，部署后自动推送（百度主动推送 / IndexNow），详见 [SEO 文档](docs/SEO-搜索引擎提交.md) |

## 🧱 技术栈

| 层次 | 技术 |
|---|---|
| 框架 | Astro 7.3（Content Layer API） |
| 语言 | TypeScript |
| 样式 | 原生 CSS（oklch 色彩空间） |
| 构建 | pnpm + Vite |
| 评论 | Giscus（GitHub Discussions）+ 自建 Waline |
| 部署 | GitHub Actions → rsync → Nginx |

## 🚀 快速开始

环境要求：**Node.js ≥ 22**、**pnpm ≥ 11**

```bash
git clone https://github.com/TANGJIN13/tangjin-blog.git
cd tangjin-blog
pnpm install
pnpm dev        # 开发服务器  http://localhost:4321
pnpm build      # 构建到 dist/
pnpm preview    # 本地预览构建结果
```

## ⚙️ 配置说明

全站配置集中在少数几个文件里，改完重新构建即可生效：

| 想改什么 | 改哪里 |
|---|---|
| 站点名 / 座右铭 / 备案号 / 社交链接 / 建站日期 / 评论服务地址 | [`src/site.ts`](src/site.ts) |
| 关于页（自我介绍、技能、时间线、联系方式） | [`src/data/profile.ts`](src/data/profile.ts) |
| 分类列表 | [`src/data/categories.ts`](src/data/categories.ts) |
| 相册清单 | [`src/data/album.json`](src/data/album.json) |
| 资源库（可下载的工具 / 资料） | 清单 [`src/data/downloads.json`](src/data/downloads.json)，文件本体放 `public/files/` |
| 首页头像 / 壁纸 | `public/images/avatar.png`、`src/site.ts` 的 `heroImage` |
| 顶部轮播壁纸（换图在这里） | 图片放 `public/images/wallpapers/`，列表写在 [`src/components/WallpaperBanner.astro`](src/components/WallpaperBanner.astro) 顶部的 `images` 数组 |
| 文章 / 说说 | `src/content/posts/`、`src/content/says/` |

## 💬 评论系统

- **文章页 + 关于页 —— Giscus**：由 GitHub Discussions 驱动，读者用 GitHub 账号登录即可评论、点赞、回复。评论数据存在另一个仓库（[tangjin-blog-comments](https://github.com/TANGJIN13/tangjin-blog-comments)）的 Discussions 里，博客本身**零后端、零数据库**，按页面路径（pathname）自动匹配讨论串。组件见 [`src/components/GiscusComments.astro`](src/components/GiscusComments.astro)。
- **留言板 —— 自建 Waline**：读者**无需登录**，填个昵称即可留言（邮箱选填）。前端随仓库自带（`src/vendor/waline.js|css`），服务端部署在同域 `/waline/` 下，地址在 `src/site.ts` 的 `waline.serverURL` 配置。组件见 [`src/components/WalineComments.astro`](src/components/WalineComments.astro)。

## 🚢 部署（可选）

默认工作流 [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) 的链路是：

```
push main → GitHub Actions 构建 dist/ → rsync 同步到服务器 → Nginx 直接提供静态文件
```

想复刻这套全自动部署，需要：

1. 一台装了 Nginx 的服务器，站点根目录如 `/var/www/blog`；
2. 生成一对**部署专用** SSH 密钥，公钥写进服务器 `authorized_keys`，并**强烈建议**用
   `command="/usr/bin/rrsync -wo /var/www/blog",restrict` 把它限制为「只能 rsync 写入站点目录」——这样即使密钥泄露也无法登录服务器；
3. 仓库 **Settings → Secrets and variables → Actions** 添加 `SSH_PRIVATE_KEY`（部署私钥全文），并把 workflow 里的 `SSH_HOST` / `SSH_USER` / `DEPLOY_PATH` 改成你自己的值。

> **不需要自动部署？** 直接删掉 `.github/workflows/deploy.yml`，手动 `pnpm build` 后把 `dist/` 传到任意静态托管即可（Vercel / Netlify / Cloudflare Pages / GitHub Pages）。

## 📁 目录结构

```
tangjin-blog/
├── .github/workflows/deploy.yml   # 自动部署工作流
├── public/                        # 静态资源（壁纸、头像、相册照片、音乐、兜底封面）
├── src/
│   ├── site.ts                    # 站点配置（标题、座右铭、社交链接、备案号等）
│   ├── data/                      # 站点数据（关于页资料 / 分类 / 相册清单 / 资源库清单）
│   ├── content/posts/             # 文章 Markdown（配图也放同目录）
│   ├── content/says/              # 说说 Markdown
│   ├── pages/                     # 页面路由（首页 / 文章 / 归档 / 说说 / 相册 / 关于 / 留言板…）
│   ├── components/                # 组件（音乐播放器、评论、热力图…）
│   ├── layouts/                   # 布局
│   └── styles/                    # 全局样式
├── docs/                          # 补充文档（SEO 提交、Obsidian 教程等）
├── 使用指南.md                     # 内容添加手册（怎么写、怎么发、去哪改）
├── ops/                           # 服务器运维脚本（Nginx / 部署密钥限制等）
└── astro.config.mjs               # Astro 配置
```

## 📝 写作与发布

完整图文手册见 [使用指南.md](使用指南.md)，这里给个速览。在 `src/content/posts/` 新建 `.md`：

```markdown
---
title: "文章标题"
description: "摘要"
published: 2026-10-06
tags: ["Web安全", "CTF"]
category: article      # essay / article / summary / tools 四选一
---

正文用 Markdown 写。
```

然后 `git push`，GitHub Actions 会自动构建并上线。

## 📦 分享文件（资源库）

想给访客提供可下载的工具 / 资料：

1. 把文件放进 `public/files/`（超过 50MB 建议放网盘，走外链）；
2. 在 [`src/data/downloads.json`](src/data/downloads.json) 里加一条：

```json
{ "name": "工具名", "file": "/files/xxx.zip", "desc": "一句话说明", "tags": ["安全"] }
```

3. 保存推送，一分钟内 `/downloads/` 页面更新，大小 / 日期 / 图标自动生成，`/search/` 搜索页也能直接搜到并点击下载。

## 📄 License

[MIT](LICENSE) —— 代码可自由参考、修改、分发；**文章内容版权归作者所有**。

## 🙏 致谢

感谢 [Astro](https://astro.build)、[Waline](https://waline.js.org)、[Giscus](https://giscus.app) 以及所有开源项目。