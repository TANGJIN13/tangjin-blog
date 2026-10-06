# 搜索引擎提交指南（百度 / Google / Bing 等）

本项目的 sitemap 由 Astro 自动生成，链接推送也已接入 CI。
**自动化的部分已经做好了，你只需要完成一次性的「站点验证」和「填写 token」。**

---

## 一、已经自动化的部分（不用你管）

| 能力 | 实现方式 |
| --- | --- |
| sitemap 生成 | `@astrojs/sitemap`，构建时产出 `/sitemap-index.xml` + `/sitemap-0.xml` |
| robots.txt | `public/robots.txt`，声明了 Sitemap 地址、允许全部抓取 |
| 新文章自动提交 | GitHub Actions 部署成功后自动跑 `scripts/submit-urls.mjs` |
| 百度自动推送（JS） | 页面被访问即提交该 URL，官方 `push.js`，已注入 `Base.astro` |
| IndexNow 推送 | 提交给 Bing / Yandex / Seznam / Naver，密钥文件已放在站点根目录 |
| sitemap ping | 每次部署后 ping Bing / Google / 360 / 搜狗 |
| canonical / OG | 每页已带 `rel="canonical"` 与 Open Graph 元信息 |

每次 `git push` 到 main → 构建部署 → 自动推送全部链接，**新文章发出来就会被通知到搜索引擎**。

---

## 二、你需要做的 4 件事（各一次）

### 1. 百度搜索资源平台 —— 加站点 + 拿 token

1. 打开 <https://ziyuan.baidu.com/>，用百度账号登录；
2. 「用户中心 → 站点管理 → 添加网站」，填 `https://tangjin.xyz`；
3. **验证站点**：推荐用「HTML标签验证」，它会给你一个文件（如 `baidu_verify_abc123.html`），
   把文件原样放进 `public/` 目录，提交代码部署后点「完成验证」；
4. 验证通过后：左侧「资源提交 → 链接提交 → 自动提交 → 主动推送（实时）」，
   页面里会显示 **token**（形如 `xxxxxxxx`），复制它；
5. 到 GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret：
   - Name：`BAIDU_PUSH_TOKEN`
   - Value：刚才复制的 token
6. 建议同时在「sitemap」处填写 `https://tangjin.xyz/sitemap-index.xml`。

> 百度主动推送有每日配额，但咱博客文章不多，全量推送完全够用。

### 2. Google Search Console —— 加站点 + 提交 sitemap

1. 打开 <https://search.google.com/search-console>，用 Google 账号登录；
2. 右上角「添加资源」→ 选「网址前缀」→ 填 `https://tangjin.xyz`；
3. **验证**：推荐「HTML 文件」方式 —— 下载它给的 `googleXXXXXXXX.html`，
   放进 `public/` 目录，部署后点「验证」；
4. 验证通过后：左侧「站点地图」→ 添加 `sitemap-index.xml` → 提交。
   Google 之后会定期自己来抓，**新文章会跟着 sitemap 自动被发现**。

> Google 的「实时推送」需要 Indexing API + 服务账号，配置较重；
> 个人博客靠 sitemap + 百度 JS 推送 + IndexNow 已经足够，收录一般在一两天内。

### 3. Bing Webmaster Tools（顺带覆盖 ChatGPT 搜索 / Copilot）

1. 打开 <https://www.bing.com/webmasters>；
2. 可以选 **「从 Google Search Console 导入」**，一步导入站点（推荐）；
3. 或手动添加，用 IndexNow 密钥验证：密钥文件已生成在站点根目录
   `https://tangjin.xyz/indexnow-781d2b330f9aa92db5f554d380a4aa48.txt`；
4. 在「站点地图」里提交 `https://tangjin.xyz/sitemap-index.xml`。

### 4. 其他平台（可选）

- **360 搜索**：<https://zhanzhang.so.com/> 加站点 + sitemap
- **搜狗**：<https://zhanzhang.sogou.com/> 加站点 + sitemap
- **神马/头条**：<https://zhanzhang.toutiao.com/>（可选）

这些平台已被 `submit-urls.mjs` 的 ping 覆盖，只要登记了站点就会收到通知。

---

## 三、本地手动推送

```bash
pnpm build
node scripts/submit-urls.mjs              # 提交全部链接
node scripts/submit-urls.mjs --new-only   # 只提交新增链接
SEO_DRY_RUN=1 node scripts/submit-urls.mjs  # 只打印，不真发请求
```

需要的环境变量（可写进 `.env` 或临时导出）：

| 变量 | 说明 |
| --- | --- |
| `BAIDU_PUSH_TOKEN` | 百度主动推送 token，没有就跳过百度 |
| `INDEXNOW_KEY` | IndexNow 密钥，留空会自动从 `public/indexnow-*.txt` 读取 |
| `SEO_SITE` | 站点地址，默认 `https://tangjin.xyz` |

已提交过的链接记录在 `.seo/submitted-urls.txt`（已入库），配合 `--new-only` 可只推新增。

---

## 四、验证是否生效

```bash
# robots.txt
curl https://tangjin.xyz/robots.txt

# sitemap
curl https://tangjin.xyz/sitemap-index.xml

# IndexNow 密钥文件（内容应是一串 32 位字符）
curl https://tangjin.xyz/indexnow-781d2b330f9aa92db5f554d380a4aa48.txt
```

之后在百度「链接提交 → 主动推送」页面可以看到推送成功条数，
在 Google Search Console「网页」报告里可以看到收录情况。
