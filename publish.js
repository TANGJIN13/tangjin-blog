#!/usr/bin/env node
/**
 * 发布 Obsidian 笔记到博客
 * 用法: node publish.js "笔记文件名.md"
 * 或者直接: node publish.js （发布所有新增/修改的文章）
 * 
 * 功能：
 * 1. 读取 Obsidian 笔记
 * 2. 转换 frontmatter 到博客格式
 * 3. 复制到 src/content/posts/
 * 4. 提交到 GitHub 并部署
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PROJECT = path.resolve(__dirname);
const POSTS_DIR = path.join(PROJECT, 'src/content/posts');
const OBSIDIAN_VAULT = process.env.OBSIDIAN_VAULT || '' ; // 可选：Obsidian vault 路径

// 博客文章 frontmatter 模板
function makeFrontmatter(title, description, tags = []) {
  const date = new Date().toISOString().slice(0, 10);
  return `---
title: "${title}"
description: "${description}"
published: ${date}
tags: ${JSON.stringify(tags)}
---

`;
}

// 转换 Obsidian frontmatter 到博客格式
function convertNote(content) {
  // 提取 Obsidian 的 frontmatter（如果有）
  const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!fmMatch) {
    // 没有 frontmatter，用文件名作为标题
    return null;
  }
  
  const obsFM = fmMatch[1];
  const body = fmMatch[2];
  
  // 解析 Obsidian frontmatter
  const titleMatch = obsFM.match(/title:\s*"?([^"\n]+)"?/);
  const descMatch = obsFM.match(/description:\s*"?([^"\n]+)"?/);
  const tagsMatch = obsFM.match(/tags:\s*\[([^\]]+)\]/)
    || obsFM.match(/tags:\s*\n((?:\s*-\s*.+\n?)+)/);
  
  const title = titleMatch ? titleMatch[1].trim() : '';
  const desc = descMatch ? descMatch[1].trim() : '';
  let tags = [];
  if (tagsMatch) {
    if (tagsMatch[1].includes(',')) {
      tags = tagsMatch[1].split(',').map(t => t.trim().replace(/"/g, ''));
    } else {
      tags = tagsMatch.slice(2).map(t => t.replace(/^\s*-\s*/, '').trim()).filter(Boolean);
    }
  }
  
  // 转换 Obsidian 语法到标准 Markdown
  let converted = body;
  
  // [[wiki-links]] → 纯文本或转为博客链接
  converted = converted.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, link, alias) => {
    const text = alias || link;
    const slug = link.toLowerCase().replace(/\s+/g, '-');
    return `[${text}/](/posts/${slug}/)`;
  });
  
  // ![[embed]] → 图片
  converted = converted.replace(/!\[\[([^\]]+)\]\]/g, (_, img) => {
    const name = path.parse(img).name;
    return `![${name}](/images/${name})`;
  });
  
  // 调用 callouts（Obsidian > [!INFO] → 标准 blockquote）
  converted = converted.replace(/^> \[!(\w+)\]\s*(.+)$/gm, (_, type, text) => {
    return `> **${type}**: ${text}`;
  });
  
  // 移除 Obsidian 特有的 %%comments%%
  converted = converted.replace(/%%[^%]*%%/g, '');
  
  return makeFrontmatter(title, desc, tags) + converted;
}

function publishNote(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const basename = path.basename(filePath, '.md');
  
  const converted = convertNote(content);
  if (!converted) {
    const title = basename.replace(/-/g, ' ');
    const output = makeFrontmatter(title, basename) + content;
    const outFile = path.join(POSTS_DIR, basename + '.md');
    fs.writeFileSync(outFile, output, 'utf8');
    console.log(`✓ 已发布: ${basename}.md (无 frontmatter，自动补充)`);
    return outFile;
  }
  
  const outFile = path.join(POSTS_DIR, basename + '.md');
  fs.writeFileSync(outFile, converted, 'utf8');
  console.log(`✓ 已发布: ${basename}.md`);
  return outFile;
}

function main() {
  const target = process.argv[2];
  
  if (target) {
    // 发布指定文件
    const filePath = path.isAbsolute(target) ? target : path.resolve(target);
    if (!fs.existsSync(filePath)) {
      console.error('文件不存在:', filePath);
      process.exit(1);
    }
    publishNote(filePath);
  } else if (OBSIDIAN_VAULT) {
    // 发布 Obsidian vault 中所有 _publish 文件夹的文章
    const publishDir = path.join(OBSIDIAN_VAULT, '_publish');
    if (!fs.existsSync(publishDir)) {
      console.error('找不到 _publish 文件夹:', publishDir);
      console.log('在 Obsidian vault 里创建 _publish 文件夹，把要发布的笔记放进去');
      process.exit(1);
    }
    const files = fs.readdirSync(publishDir).filter(f => f.endsWith('.md'));
    if (files.length === 0) {
      console.log('_publish 文件夹里没有文章');
      return;
    }
    files.forEach(f => publishNote(path.join(publishDir, f)));
  } else {
    console.log('用法:');
    console.log('  node publish.js "笔记.md"     — 发布指定文件');
    console.log('  node publish.js                — 发布 Obsidian vault _publish 文件夹里的所有文章');
    console.log('');
    console.log('提示: 设置环境变量 OBSIDIAN_VAULT 指向你的 vault 路径');
    console.log('  然后在 vault 里创建 _publish 文件夹，写完笔记放进去');
  }
}

main();
