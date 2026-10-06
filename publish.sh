#!/usr/bin/env bash
# 发布 Obsidian 笔记到博客（支持分类）
# 用法: ./publish.sh <笔记路径>
# 示例: ./publish.sh ~/Documents/安全笔记/XSS复现.md

set -uo pipefail

PROJECT="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$(cd "$PROJECT" && pwd)"
POSTS_DIR="$PROJECT/src/content/posts"

NOTE_PATH="${1:-}"
if [ -z "$NOTE_PATH" ] || [ ! -f "$NOTE_PATH" ]; then
  echo "❌ 请提供笔记路径"
  echo "   用法: ./publish.sh /path/to/note.md"
  exit 1
fi

# 读取 frontmatter
TITLE=$(grep -m1 '^title:' "$NOTE_PATH" 2>/dev/null | sed 's/.*title:\s*["'\'']\(.*\)["'\'']/\1/' || echo '')
DESC=$(grep -m1 '^description:' "$NOTE_PATH" 2>/dev/null | sed 's/.*description:\s*["'\'']\(.*\)["'\'']/\1/' || echo '')
DATE=$(grep -m1 '^published:' "$NOTE_PATH" 2>/dev/null | sed 's/.*published:\s*//' | cut -dT -f1 || date +%Y-%m-%d)
TAGS=$(grep -m1 '^tags:' "$NOTE_PATH" 2>/dev/null | sed 's/.*tags:\s*//' || echo '[]')
CATEGORY=$(grep -m1 '^category:' "$NOTE_PATH" 2>/dev/null | sed 's/.*category:\s*//' || echo '')

if [ -z "$TITLE" ]; then
  FIRST_LINE=$(grep -m1 '^# ' "$NOTE_PATH" | sed 's/^# //' || echo '')
  TITLE="$FIRST_LINE"
fi

if [ -z "$TITLE" ]; then
  echo "❌ 找不到标题（frontmatter 里的 title 或第一行 # 标题）"
  exit 1
fi

# 生成文件名
SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | iconv -f utf-8 -t ascii//translit 2>/dev/null | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-\|-$//g')
[ -z "$SLUG" ] && SLUG=$(echo "$TITLE" | md5sum | cut -c1-8)
FILENAME="${DATE}-${SLUG}.md"

# 复制文件（frontmatter 原样保留，包含 category）
cp "$NOTE_PATH" "$POSTS_DIR/$FILENAME"

echo "✓ 标题: $TITLE"
echo "✓ 日期: $DATE"
[ -n "$CATEGORY" ] && echo "✓ 分类: $CATEGORY"
echo "✓ 文件: $FILENAME"

# 提交
cd "$PROJECT"
git add -A
git commit -q -m "post: $TITLE"
git push -q

echo "✓ 已推送，约 2 分钟后上线: https://tangjin.xyz"
