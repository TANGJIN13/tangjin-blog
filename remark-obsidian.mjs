import fs from 'node:fs';
import path from 'node:path';

/**
 * Obsidian 语法兼容插件（构建时执行，不影响写作习惯）
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

/** 把一段文本按 ![[xxx]] 拆开，替换成 图片+文字 混合节点；有嵌入返回 true */
function replaceEmbedsInText(text, mdDir, newNodes) {
  const re = /!\[\[([^\]]+)\]\]/g;
  let last = 0;
  let m;
  let matched = false;
  while ((m = re.exec(text)) !== null) {
    matched = true;
    if (m.index > last) {
      newNodes.push({ type: 'text', value: text.slice(last, m.index) });
    }
    const raw = m[1].trim();
    // ![[img.png|说明文字]] → alt 取竖线后面的部分
    const pipeIdx = raw.indexOf('|');
    const name = pipeIdx >= 0 ? raw.slice(0, pipeIdx).trim() : raw;
    const alt = pipeIdx >= 0 ? raw.slice(pipeIdx + 1).trim() : path.parse(name).name;

    let url = null;
    // ① 与文章同目录
    if (mdDir && name && fs.existsSync(path.join(mdDir, name))) {
      url = './' + encodeURI(name);
    }
    // ② public/images 下按文件名找
    if (!url) {
      const rel = name ? findInPublicImages(name) : null;
      if (rel) url = '/images/' + encodeURI(rel);
    }
    // ③ 兜底：/images/文件名（构建永不报错）
    if (!url) url = '/images/' + encodeURI(name);

    newNodes.push({ type: 'image', url, alt, title: null });
    last = m.index + m[0].length;
  }
  if (!matched) return false;
  if (last < text.length) newNodes.push({ type: 'text', value: text.slice(last) });
  return true;
}

export function remarkObsidian() {
  return (tree, file) => {
    const mdPath = file?.history?.[0] || file?.path || '';
    const mdDir = mdPath ? path.dirname(mdPath) : '';

    const visit = (node) => {
      if (!node || typeof node !== 'object') return;

      // ① 标注块：> [!TYPE] 文字 → > **TYPE:** 文字
      if (node.type === 'blockquote' && Array.isArray(node.children)) {
        const first = node.children[0];
        if (first?.type === 'paragraph' && Array.isArray(first.children)) {
          const t = first.children[0];
          if (t?.type === 'text') {
            const m = t.value.match(/^\[!(\w+)\][+-]?\s*/);
            if (m) {
              const type = m[1].toUpperCase();
              const rest = t.value.slice(m[0].length);
              first.children.splice(
                0,
                1,
                { type: 'strong', children: [{ type: 'text', value: type }] },
                { type: 'text', value: ': ' + rest },
              );
            }
          }
        }
      }

      if (Array.isArray(node.children)) {
        // 先递归处理子节点
        for (const child of node.children) visit(child);
        // 再在父级展开：文本节点里的 ![[...]] → 图片节点序列
        const hasEmbed = node.children.some(
          (c) => c?.type === 'text' && typeof c.value === 'string' && c.value.includes('![['),
        );
        if (hasEmbed) {
          const expanded = [];
          for (const c of node.children) {
            if (c?.type === 'text' && typeof c.value === 'string' && c.value.includes('![[')) {
              const out = [];
              if (replaceEmbedsInText(c.value, mdDir, out) && out.length) expanded.push(...out);
              else expanded.push(c);
            } else {
              expanded.push(c);
            }
          }
          node.children = expanded;
        }
      }
    };

    visit(tree);
  };
}
