---
title: "<%= tp.file.title %>"
description: "<%= tp.system.prompt('文章摘要（一句话）') %>"
published: "<%= tp.date.now('YYYY-MM-DD') %>"
tags: [<%= tp.system.prompt('标签（逗号分隔，如 Web安全,CTF）').split(',').map(t => '"' + t.trim() + '"').join(',') %>]
category: <%= await tp.system.suggester(['文章 article', '年度总结 summary', '工具使用 tools'], ['article', 'summary', 'tools'], true, '选择分类') %>
---

## 概述

<%= tp.file.cursor() %>

## 详细内容

## 总结

---
> 发布: 保存后约 2 分钟自动上线 https://tangjin.xyz
