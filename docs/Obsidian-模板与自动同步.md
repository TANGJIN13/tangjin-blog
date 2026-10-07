# Obsidian 写文 → 自动同步到博客

目标：**在 Obsidian 里新建笔记 → 弹出分类选择 → 写好保存 → 自动提交推送 → 博客自动上线**。
整套基于你已经装好的两个插件：**Templater**（模板 + 分类选择）和 **Obsidian Git**（自动提交推送）。

---

## 一、它怎么工作的

```
在 tangjin-blog/src/content/posts 里新建笔记
        │
        ├─ Templater 自动套用「博客文章」模板 → 弹窗问分类 / 标题 / 简介 / 标签
        │    └─ 生成 frontmatter（含 category）+ 规范文件名「日期-标题.md」
        │
        ├─ Ctrl+S 保存
        │
        ├─ Obsidian Git 检测到文件变化 → 自动 commit + push（约 2~3 分钟内）
        │
        └─ GitHub Actions 构建 → rsync 到服务器 → 博客上线（再 1~2 分钟）
```

---

## 二、已经帮你配置好的东西

### 1. 模板文件：`TANGJIN/Templates/博客文章.md`

新建笔记时会依次询问：

1. **分类**（下拉选择，Esc 默认「文章」）：文章 / 年度总结 / 工具使用
2. **标题**
3. **一句话简介**（可留空，但建议填，会显示在文章卡片上）
4. **标签**（逗号分隔，可留空）

然后自动生成：

```yaml
---
title: "你的标题"
description: "一句话简介"
published: 2026-10-06
category: article          # ← 分类 slug，博客据此显示徽章和分类页
tags: ["标签1", "标签2"]
---
```

并把文件名规范成 `2026-10-06-你的标题.md`（博客 URL 用它）。

### 2. Templater 设置（`TANGJIN/.obsidian/plugins/templater-obsidian/data.json`）

- `trigger_on_file_creation_mode` → `folder`（新建文件时按文件夹套模板）
- `folder_templates` → `tangjin-blog/src/content/posts` 绑定 `Templates/博客文章.md`

### 3. Obsidian Git 设置（`TANGJIN/.obsidian/plugins/obsidian-git/data.json`）

| 设置项 | 值 | 作用 |
| --- | --- | --- |
| `basePath` | `tangjin-blog` | **关键**：库根目录不是 git 仓库，这里告诉插件去管子目录里的博客仓库 |
| `autoBackupAfterFileChange` | `true` | 文件一改就自动提交推送（保存即上传） |
| `autoSaveInterval` | `2` | 兜底：每 2 分钟自动 commit |
| `autoPushInterval` | `3` | 兜底：每 3 分钟自动 push |
| `commitMessage` | `blog: {{date}}` | 提交信息 |

---

## 三、你需要做的：重启一次 Obsidian

⚠️ **重要**：我是直接改的配置文件，Obsidian 正在运行时不会重新读取。请**完全退出再打开 Obsidian**（不是只刷新），然后确认：

1. 设置 → 第三方插件 → **Templater** → Trigger Templater on new file creation = **Folder templates**，
   下方 Folder templates 里有 `tangjin-blog/src/content/posts → Templates/博客文章.md`
2. 设置 → 第三方插件 → **Git** → **Base path = `tangjin-blog`**，
   **Auto backup after file change = 打开**
3. 左侧应该能看到 Git 视图里有待提交的更改（如果显示「不是 git 仓库」，说明 basePath 没生效，手动填一次上面的值）

如果插件设置里这两项被旧配置覆盖了，手动填一次即可。

---

## 四、日常用法

1. 在 Obsidian 里打开 `tangjin-blog/src/content/posts` 文件夹，新建笔记；
2. 弹窗选分类 → 填标题 → 填简介 → 填标签；
3. 写正文，`Ctrl + S` 保存；
4. 等 2~3 分钟，去 GitHub 看提交记录，再过 1~2 分钟博客上就能看到了。

### 写一半不想发布

frontmatter 里加一行：

```yaml
draft: true
```

推送上去也不会在博客显示（`getPublishedPosts()` 会过滤草稿），写完删掉这行即可。

### 在库里别的地方写（比如日记里）

那篇笔记不在博客目录里，不会被自动推送。写完用发布脚本发：

```bash
cd tangjin-blog
./publish.sh "D:/apps/obsidian/note/TANGJIN/笔记/某篇.md"
```

---

## 五、排错

| 现象 | 原因 / 处理 |
| --- | --- |
| 新建笔记没弹分类选择 | **先完全退出 Obsidian 再打开**（不是关窗口）。若还不行，按下面「模板不弹窗的三层开关」逐条核对 |
| 模板确实没触发 | 手动补一次：`Ctrl+P` → `Templater: Open Insert Template Modal` → 选 `博客文章` |
| Git 插件显示「not a git repository」 | `basePath` 没填对，设为 `tangjin-blog` 后重启 |
| 保存了但 GitHub 上没提交 | 看 Obsidian 左下角 Git 状态；手动执行「Git: Commit-and-push」命令试试；确认 `git` 在系统 PATH 里 |
| 推送了但博客没更新 | 去 GitHub 仓库 → Actions 看流水线是否变绿（一般是构建报错） |
| 分类徽章没显示 | 检查 frontmatter 里 `category` 是不是这三个之一：`article` / `summary` / `tools` |
| 保存了但 GitHub 一直没动静 | 检查 `TANGJIN/.obsidian/community-plugins.json` 里有没有 `"obsidian-git"`——不在列表里就是插件没启用 |

---

## 六、模板不弹窗的三层开关

Templater 要在新建笔记时自动套模板，**三个条件必须同时满足**，缺一个就静默不触发：

1. **`trigger_on_file_creation: true`**（总开关，默认是 `false`）
2. **`trigger_on_file_creation_mode: "folder"`**（用文件夹模板模式）
3. **`folder_templates` 里有这一条**：
   ```json
   { "folder": "tangjin-blog/src/content/posts", "template": "Templates/博客文章.md" }
   ```

第 1 条最容易漏——只写 `trigger_on_file_creation_mode: "folder"` 是不够的，
Templater 内部的判断是 `trigger_on_file_creation && mode === "folder"`。

另外 Templater 只在**文件完全为空**时才套模板，所以要是新建时已经有内容，它也不会插手。

改完配置务必**完全退出 Obsidian**（任务管理器里确认没有 Obsidian 进程）再重开，
否则 Obsidian 退出时会用内存里的旧配置把你的改动覆盖回去。
