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

  /**
   * 段落级处理：
   * - 独立成段的 ![[图片]] → 重新解析成图片节点
   * - 引用块里的 [!TYPE] 标注头 → **TYPE:**
   */
  paragraph(node, ctx) {
    // 只处理「干净」的段落（纯文本/图片，避免破坏加粗、链接、行内代码等格式）
    const children = Array.isArray(node.children) ? node.children : [];
    const simple = children.every((c) => c?.type === 'text' || c?.type === 'image');
    if (!simple || children.length === 0) return;

    const text = children.map((c) => c.value ?? '').join('');
    if (typeof text !== 'string' || !text) return;

    // 文章路径 → 所在目录（用于「同目录图片」的相对路径分支）
    let mdDir = '';
    try {
      if (ctx?.fileURL) mdDir = path.dirname(fileURLToPath(ctx.fileURL));
    } catch {
      mdDir = '';
    }

    // ① Obsidian 图片嵌入
    if (text.includes('![[')) {
      const converted = convertEmbeds(text, mdDir);
      if (converted !== text) return { raw: converted };
    }

    // ② 标注块：> [!TYPE] 文字（在 blockquote 里的段落）
    const m = text.match(/^\[!(\w+)\][+-]?\s*/);
    if (m && ctx?.parent?.type === 'blockquote') {
      const type = m[1].toUpperCase();
      const rest = text.slice(m[0].length);
      return { raw: `**${type}:** ${rest}` };
    }

    return;
  },
};
