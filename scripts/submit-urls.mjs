#!/usr/bin/env node
/**
 * 把站点链接提交给搜索引擎
 *
 * 用法（在 pnpm build 之后跑，脚本会读 dist/sitemap*.xml）：
 *   node scripts/submit-urls.mjs              # 提交全部链接
 *   node scripts/submit-urls.mjs --new-only   # 只提交上次之后新增的链接
 *
 * 支持渠道：
 *   1. 百度「主动推送（实时）」—— 需要 BAIDU_PUSH_TOKEN（百度搜索资源平台获取）
 *   2. IndexNow（必应 Bing / Yandex / Seznam / Naver）—— 需要 INDEXNOW_KEY，
 *      留空时会从 public/indexnow-<key>.txt 自动识别
 *   3. 各家 sitemap ping（Bing / Google / 360 / 搜狗）—— 无需凭据
 *
 * 环境变量：
 *   SEO_SITE          站点地址，默认 https://tangjin.xyz
 *   BAIDU_PUSH_TOKEN  百度主动推送 token（没有就跳过百度）
 *   BAIDU_SITE        百度登记的站点域名，默认 tangjin.xyz
 *   INDEXNOW_KEY      IndexNow 密钥（留空则自动识别）
 *   SEO_DRY_RUN=1     只打印要提交的链接，不真的请求
 */

import fs from 'node:fs';
import path from 'node:path';

const SITE = (process.env.SEO_SITE || 'https://tangjin.xyz').replace(/\/+$/, '');
const DIST = process.env.SEO_DIST || 'dist';
const STATE_FILE = '.seo/submitted-urls.txt';
const ONLY_NEW = process.argv.includes('--new-only');
const DRY_RUN = process.env.SEO_DRY_RUN === '1';

const log = (...a) => console.log(...a);

/* ---------- 1. 从 sitemap 里取出所有页面链接 ---------- */
function collectUrls() {
  if (!fs.existsSync(DIST)) {
    console.error(`找不到 ${DIST}/，请先运行 pnpm build`);
    process.exit(1);
  }
  const files = fs
    .readdirSync(DIST)
    .filter((f) => /^sitemap.*\.xml$/.test(f));

  const urls = new Set();
  for (const f of files) {
    const xml = fs.readFileSync(path.join(DIST, f), 'utf8');
    for (const m of xml.matchAll(/<loc>([^<]+)<\/loc>/g)) {
      const u = m[1].trim();
      if (!u.endsWith('.xml')) urls.add(u); // 排除 sitemap-index 里的子 sitemap
    }
  }
  return [...urls].sort();
}

/* ---------- 2. 读取「已提交过」的记录 ---------- */
function readSubmitted() {
  try {
    return new Set(
      fs.readFileSync(STATE_FILE, 'utf8').split('\n').map((s) => s.trim()).filter(Boolean)
    );
  } catch {
    return new Set();
  }
}

function saveSubmitted(urls) {
  fs.mkdirSync(path.dirname(STATE_FILE), { recursive: true });
  fs.writeFileSync(STATE_FILE, urls.join('\n') + '\n', 'utf8');
}

/* ---------- 3. 百度主动推送（实时） ---------- */
async function baiduPush(urls) {
  const token = process.env.BAIDU_PUSH_TOKEN;
  if (!token) {
    log('· 百度主动推送：跳过（未设置 BAIDU_PUSH_TOKEN）');
    return false;
  }
  if (!urls.length) { log('· 百度主动推送：无新链接'); return true; }

  const site = process.env.BAIDU_SITE || new URL(SITE).host;
  const endpoint = `http://data.zz.baidu.com/urls?site=${encodeURIComponent(site)}&token=${encodeURIComponent(token)}`;

  if (DRY_RUN) { log(`· 百度主动推送：[dry-run] ${urls.length} 条 → ${endpoint}`); return true; }

  try {
    const resp = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: urls.join('\n'),
    });
    const text = await resp.text();
    log(`· 百度主动推送：HTTP ${resp.status} ${text.slice(0, 200)}`);
    return resp.ok;
  } catch (e) {
    log('· 百度主动推送：失败', e.message);
    return false;
  }
}

/* ---------- 4. IndexNow（Bing / Yandex …） ---------- */
function findIndexNowKey() {
  if (process.env.INDEXNOW_KEY) return process.env.INDEXNOW_KEY;
  try {
    const f = fs
      .readdirSync('public')
      .find((n) => /^indexnow-[A-Za-z0-9_-]{8,128}\.txt$/.test(n));
    if (!f) return '';
    return fs.readFileSync(path.join('public', f), 'utf8').trim();
  } catch {
    return '';
  }
}

async function indexNow(urls) {
  const key = findIndexNowKey();
  if (!key) { log('· IndexNow：跳过（没找到密钥文件 public/indexnow-*.txt）'); return false; }
  if (!urls.length) { log('· IndexNow：无新链接'); return true; }

  const host = new URL(SITE).host;
  const body = JSON.stringify({
    host,
    key,
    keyLocation: `${SITE}/indexnow-${key}.txt`,
    urlList: urls,
  });

  if (DRY_RUN) { log(`· IndexNow：[dry-run] ${urls.length} 条，key=${key.slice(0, 8)}…`); return true; }

  let ok = false;
  for (const ep of ['https://api.indexnow.org/IndexNow', 'https://www.bing.com/indexnow']) {
    try {
      const resp = await fetch(ep, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body,
      });
      log(`· IndexNow ${new URL(ep).host}：HTTP ${resp.status}`);
      if (resp.ok || resp.status === 202) ok = true;
    } catch (e) {
      log(`· IndexNow ${new URL(ep).host}：失败 ${e.message}`);
    }
  }
  return ok;
}

/* ---------- 5. 各家 sitemap ping ---------- */
async function pingSitemap() {
  const sitemap = `${SITE}/sitemap-index.xml`;
  const endpoints = [
    `https://www.bing.com/ping?sitemap=${encodeURIComponent(sitemap)}`,
    `https://www.google.com/ping?sitemap=${encodeURIComponent(sitemap)}`,
    `https://www.so.com/ping?sitemap=${encodeURIComponent(sitemap)}`,
    `https://www.sogou.com/ping?url=${encodeURIComponent(sitemap)}`,
  ];
  if (DRY_RUN) { log('· sitemap ping：[dry-run] 跳过'); return; }
  for (const ep of endpoints) {
    try {
      const resp = await fetch(ep);
      log(`· ping ${new URL(ep).host}：HTTP ${resp.status}`);
    } catch (e) {
      log(`· ping ${new URL(ep).host}：失败 ${e.message}`);
    }
  }
}

/* ---------- 主流程 ---------- */
const all = collectUrls();
const submitted = readSubmitted();
const targets = ONLY_NEW ? all.filter((u) => !submitted.has(u)) : all;

log(`站点：${SITE}`);
log(`sitemap 链接总数：${all.length}，本次提交：${targets.length}${ONLY_NEW ? '（仅新增）' : '（全部）'}`);
targets.slice(0, 20).forEach((u) => log('  - ' + u));
if (targets.length > 20) log(`  … 还有 ${targets.length - 20} 条`);

if (!targets.length) {
  log('没有需要提交的链接，结束。');
  process.exit(0);
}

await baiduPush(targets);
await indexNow(targets);
await pingSitemap();

if (!DRY_RUN) {
  saveSubmitted([...new Set([...submitted, ...all])]);
  log(`已记录到 ${STATE_FILE}`);
}
log('完成。');
