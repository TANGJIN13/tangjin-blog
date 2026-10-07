# Obsidian 写文章 → 发布到博客 完整教程

> 从零开始，写完一篇文章 30 秒，2 分钟后自动上线。

---

## 第一部分：一次性设置

### 1. 安装两个插件

打开 Obsidian → 左下角 **设置** → **社区插件** → **浏览**

| 插件名 | 作用 |
|---|---|
| **Obsidian Git** | 自动同步笔记到 GitHub |
| **Templater** | 新建笔记时自动生成模板 |

两个都安装并启用。

### 2. 设置 Obsidian Git

设置 → Obsidian Git → 修改以下项：

| 设置项 | 值 |
|---|---|
| Auto commit interval | `5` |
| Auto push interval | `5` |
| Commit message | 留空（自动生成）|

### 3. 设置 Templater

设置 → Templater → **Template folder location** → 填：`Templates`

### 4. 放入模板文件

在你的 Obsidian vault 里新建文件夹 `Templates`，把以下内容保存为 `博客文章.md`：

```
---
title: "<%= tp.file.title %>"
description: "<%= tp.system.prompt('文章摘要') %>"
published: "<%= tp.date.now('YYYY-MM-DD') %>"
tags: [<%= tp.system.prompt('标签（逗号分隔）').split(',').map(t => '"' + t.trim() + '"').join(',') %>]
category: <%= tp.system.suggester(['文章 article','年度总结 summary','工具使用 tools'], ['article','summary','tools']) %>
---

<%
const cat = await tp.system.suggester(
  ['文章 article','年度总结 summary','工具使用 tools'],
  ['article','summary','tools'],
  true,
  '选择分类'
);
%>
```

等等，Templater 模板里不能直接写 frontmatter 动态生成。让我用更简单的方式。

---

## 第二部分：日常写文章

### 方法 A：用模板（推荐）

1. **新建笔记** `Ctrl + N`
2. **插入模板** `Ctrl + P` → Insert Template → 选"博客文章模板"
3. **填写弹窗**：选分类 → 填标签 → 填摘要
4. **写正文**
5. **保存** `Ctrl + S`
6. **等 2 分钟**自动上线

### 方法 B：不用模板

新建笔记，直接复制这个开头：

```markdown
---
title: "文章标题"
description: "一句话摘要"
published: 2026-10-05
tags: ["Web安全"]
category: article
---

## 正文

保存后自动上线。
```

---

## 分类对照表

| 想写什么 | category 填 |
|---|---|
| 技术文章、教程 | `article` |
| 年终总结、回顾 | `summary` |
| 软件推荐、配置 | `tools` |

---

## 怎么发布到博客？

### 原理

```
Obsidian 保存
    ↓
Obsidian Git 插件自动 commit（5分钟内）
    ↓
自动 push 到 GitHub
    ↓
GitHub Actions 自动构建
    ↓
rsync 推送到你的服务器
    ↓
约 2 分钟后 https://tangjin.xyz 更新
```

### 你需要做的

只需要 **写文章 → 保存**，其他全自动。

---

## 常见问题

| 问题 | 解决 |
|---|---|
| 没自动同步 | 检查 Obsidian Git 是否启用，Auto push 是否设为 5 |
| 文章没上线 | 去 github.com/TANGJIN13/tangjin-blog/actions 看构建状态 |
| 改分类 | 修改 frontmatter 里的 `category: xxx`，保存 |
| 删文章 | 删掉 .md 文件，保存，自动同步删除 |
| 改标题 | 修改 frontmatter 里的 `title:`，保存 |
| 想预览 | Obsidian 里按 `Ctrl + E` 切换预览模式 |

---

## 模板文件（直接复制）

在你的 Obsidian vault 里新建 `Templates/博客文章.md`，内容：

```markdown
---
title: "<%= tp.file.title %>"
description: "<%= tp.system.prompt('文章摘要（一句话）') %>"
published: "<%= tp.date.now('YYYY-MM-DD') %>"
tags: [<%= tp.system.prompt('标签（逗号分隔，如 Web安全,CTF）').split(',').map(t => '"' + t.trim() + '"').join(',') %>]
category: <%= await tp.system.suggester(['文章 article','年度总结 summary','工具使用 tools'], ['article','summary','tools'], true, '选择分类') %>
---

## 概述

<%= tp.file.cursor() %>

## 详细内容

## 总结

---
> 发布: 保存后约 2 分钟自动上线 https://tangjin.xyz
```

---

## 一图总结

```
┌─────────────────────────────────────────┐
│  Obsidian 新建笔记                       │
│     ↓ Ctrl+P → Insert Template          │
│     ↓ 选分类 → 填标签 → 填摘要           │
│     ↓ 写正文                            │
│     ↓ Ctrl+S 保存                       │
│     ↓ Obsidian Git 自动 commit          │
│     ↓ 自动 push 到 GitHub               │
│     ↓ GitHub Actions 构建               │
│     ↓ 推送到服务器                       │
│     ↓ 2分钟后 ✅ 上线                   │
└─────────────────────────────────────────┘
```

---

**就这么简单。写好保存就行，其他全自动。**
