<%*
// 博客文章模板 —— Templater
// 安装 Templater 插件后，把这个文件放到 vault 的 Templates 文件夹
// 新建笔记时 → 插入模板 → 自动生成 frontmatter

// 获取标题（去掉文件扩展名）
const title = tp.file.title || "新文章";

// 今天日期
const today = tp.date.now("YYYY-MM-DD");

// 询问分类
const cat = await tp.system.suggester(
  ["Web 安全 (web-security)", "CTF (ctf)", "随笔 (essay)", "工具 (tools)", "其他 (custom)"],
  ["web-security", "ctf", "essay", "tools", "custom"],
  true,
  "选择分类"
);

// 如果选自定义，手动输入
let category = cat;
if (cat === "custom") {
  category = await tp.system.prompt("输入分类 slug（英文，如 reverse）", "");
}

// 询问标签
const tagsInput = await tp.system.prompt("标签（逗号分隔，如 Web安全,XSS）", "随笔");
const tags = tagsInput.split(/[,，]/).map(t => `"${t.trim()}"`).join(", ");

// 询问描述
const desc = await tp.system.prompt("文章摘要（一句话）", title);

// 生成文件名（日期-标题）
const slug = title.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]+/g, "-").replace(/^-|-$/g, "");
await tp.file.rename(`${today}-${slug}`);
%>
---
title: "<%= title %>"
description: "<%= desc %>"
published: <%= today %>
tags: [<%= tags %>]
category: <%= category %>
---

## 概述

<% tp.file.cursor() %>

## 详细内容

## 总结

---
> 发布: 保存后运行 `./publish.sh "<%= title %>.md"` 或等 Obsidian Git 自动同步
