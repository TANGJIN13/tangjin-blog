import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * Obsidian 语法兼容插件（Sätteri mdast 插件，构建时执行，不影响写作习惯）
 *
 * 1. ![[图片.png]] 嵌入 → 博客可渲染的图片：
 *    ① 图片和文章在同一目录       → 相对路径（走 Astro 图片管线，自动优化）
 *    ② 否则在 public/images/** 里按文件名找 → /images/... 绝对路径
 *    ③ 都找不到                  → 仍输出 /images/文件名（与 publish.cjs 的约定一致，构建不会报错）
 *
 * 2. > [!WARNING] / > [!TIP] 等 Obsidian 标注块 → 标准 blockquote（**WARNING:** 文字）
 *
 * 3. **段落内的单个换行 → `<br>`**（最重要的一条，见下方 text 访问器）
 *
 * 注意：[[笔记名]] 双链不是图片，这里不做转换（博客里会显示为普通文字）。
 */

/** 在 public/images 下递归找同名文件，返回相对 public 的路径（posix 风格），找不到返回 null */
function findInPublicImages(name) {
  const base = path.resolve(process.cwd(), 'public', 'images');
  let found = null;
  const walk = (dir) => {
    if (found) return;
    let entries;
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entries) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name === name) {
        found = path.relative(base, p).split(path.sep).join('/');
        return;
      }
    }
  };
  walk(base);
  return found;
}

/** 解析 ![[name]] 的最终 URL */
function resolveImageUrl(name, mdDir) {
  // ① 与文章同目录（相对路径，Astro 会自动优化）
  if (mdDir && name && fs.existsSync(path.join(mdDir, name))) {
    return './' + encodeURI(name);
  }
  // ② public/images 下按文件名找
  const rel = name ? findInPublicImages(name) : null;
  if (rel) return '/images/' + encodeURI(rel);
  // ③ 兜底（构建永不报错）
  return '/images/' + encodeURI(name);
}

/** 把文本里的 ![[xxx]] 换成标准 Markdown 图片语法 */
function convertEmbeds(text, mdDir) {
  return text.replace(/!\[\[([^\]]+)\]\]/g, (_, raw) => {
    const inner = raw.trim();
    const pipeIdx = inner.indexOf('|');
    const name = pipeIdx >= 0 ? inner.slice(0, pipeIdx).trim() : inner;
    const alt = pipeIdx >= 0 ? inner.slice(pipeIdx + 1).trim() : path.parse(name).name;
    const url = resolveImageUrl(name, mdDir);
    return `![${alt}](${url})`;
  });
}

export const obsidianCompatPlugin = {
  name: 'obsidian-compat',

  /** 引用块级处理：> [!TYPE] 文字 → > **TYPE:** 文字（Obsidian 标注块） */
  blockquote(node, ctx) {
    const children = Array.isArray(node.children) ? node.children : [];
    // 只处理「单段落、纯文本/图片」的简单标注块，复杂的保持原样
    if (children.length !== 1 || children[0]?.type !== 'paragraph') return;
    const kids = Array.isArray(children[0].children) ? children[0].children : [];
    if (kids.length === 0 || !kids.every((c) => c?.type === 'text' || c?.type === 'image')) return;

    const text = kids.map((c) => c.value ?? '').join('');
    const m = text.match(/^\[!(\w+)\][+-]?\s*/);
    if (!m) return;

    let mdDir = '';
    try {
      if (ctx?.fileURL) mdDir = path.dirname(fileURLToPath(ctx.fileURL));
    } catch {
      mdDir = '';
    }

    const type = m[1].toUpperCase();
    const rest = convertEmbeds(text.slice(m[0].length), mdDir);
    return { raw: `> **${type}:** ${rest}` };
  },

  /** 段落级处理：独立成段的 ![[图片]] → 重新解析成图片节点 */
  paragraph(node, ctx) {
    // 只处理「干净」的段落（纯文本/图片，避免破坏加粗、链接、行内代码等格式）
    const children = Array.isArray(node.children) ? node.children : [];
    const simple = children.every((c) => c?.type === 'text' || c?.type === 'image');
    if (!simple || children.length === 0) return;

    const text = children.map((c) => c.value ?? '').join('');
    if (typeof text !== 'string' || !text.includes('![[')) return;

    // 文章路径 → 所在目录（用于「同目录图片」的相对路径分支）
    let mdDir = '';
    try {
      if (ctx?.fileURL) mdDir = path.dirname(fileURLToPath(ctx.fileURL));
    } catch {
      mdDir = '';
    }

    const converted = convertEmbeds(text, mdDir);
    if (converted !== text) return { raw: converted };

    return;
  },

  /**
   * 文本级处理：段落内的**单个换行** → `<br>`（硬换行）。
   *
   * 为什么需要它：CommonMark 规定段落内的软换行渲染成**空格**，而 Obsidian 的
   * 阅读视图（"严格换行"关闭，也就是默认值）把它渲染成**换行**。用户是"一行一句"
   * 的写法（HTTP 头、curl 命令、路径列表各占一行），于是：
   *   Obsidian 里看到的是一行一条，博客上被合并成一大段、位置全乱。
   * 这条规则就是让博客和 Obsidian 的阅读视图一致 —— 等价于 remark-breaks 的语义。
   *
   * 实现要点：
   *   · 只处理 `text` 节点。代码块 / 行内代码的值在 `code` / `inlineCode` 节点上，
   *     不经过 text 访问器，所以**不会被误插 `<br>`**（这是最容易踩的地方）。
   *   · 表格单元格里不允许换行（HTML 表格里 `<br>` 会破坏对齐），直接跳过。
   *   · 拆完丢掉空片段，避免产生空 text 节点（`**粗体**\n后文` 这种，
   *     换行会落在下一个 text 节点的开头）。
   */
  text(node, ctx) {
    const value = node.value;
    if (typeof value !== 'string' || value.indexOf('\n') === -1) return;

    const parent = ctx.parent(node);
    if (parent && parent.type === 'tableCell') return;

    const parts = [];
    value.split('\n').forEach((seg, i) => {
      if (i > 0) parts.push({ type: 'break' });
      if (seg) parts.push({ type: 'text', value: seg });
    });
    if (parts.length <= 1) return;

    ctx.replaceNode(node, parts);
  },
};
