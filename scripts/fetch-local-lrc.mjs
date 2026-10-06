// 一次性脚本：把本地歌曲的 LRC 抓下来存成静态文件 public/lrc/*.lrc
// 这样本地歌曲也有歌词，且不依赖第三方接口的 auth token（会过期）
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'https://api.i-meto.com/meting/api';

const SONGS = [
  { file: 'wo-zou-hou.lrc', cover: 'wo-zou-hou.jpg', query: '我走后 小咪' },
  { file: 'wo-hao-xiang-ni.lrc', cover: 'wo-hao-xiang-ni.jpg', query: '我好想你 苏打绿' },
];

async function json(u) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), 15000);
  const r = await fetch(u, { signal: c.signal });
  clearTimeout(t);
  return r.json();
}

await mkdir(resolve(root, 'public/lrc'), { recursive: true });

for (const s of SONGS) {
  try {
    const list = await json(`${base}?server=netease&type=search&id=${encodeURIComponent(s.query)}`);
    if (!Array.isArray(list) || !list.length) { console.log('✗ 搜不到:', s.query); continue; }
    const hit = list[0];
    if (!hit.lrc) { console.log('✗ 无歌词字段:', hit.title); continue; }
    const resp = await fetch(hit.lrc);
    if (!resp.ok) { console.log('✗ 歌词下载失败', resp.status, hit.title); continue; }
    const text = await resp.text();
    if (!/\[\d{1,3}:\d{1,2}/.test(text)) { console.log('✗ 内容不像 LRC:', hit.title); continue; }
    await writeFile(resolve(root, 'public/lrc', s.file), text, 'utf8');
    let cov = '';
    if (hit.pic && s.cover) {
      try {
        const pr = await fetch(hit.pic);
        if (pr.ok) {
          const buf = Buffer.from(await pr.arrayBuffer());
          if (buf.length > 1024) {
            await mkdir(resolve(root, 'public/music'), { recursive: true });
            await writeFile(resolve(root, 'public/music', s.cover), buf);
            cov = `，封面 ${s.cover}`;
          }
        }
      } catch (e) {}
    }
    console.log(`✓ ${s.file}  <-  ${hit.title} / ${hit.author}  (${text.length} 字节${cov})`);
  } catch (e) {
    console.log('✗', s.query, String(e.message || e).slice(0, 80));
  }
}
