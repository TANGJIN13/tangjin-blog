#!/usr/bin/env bash
# 发布当前 Obsidian 笔记到博客
# 用法: 把这个脚本放到 Obsidian vault 里，在笔记右键 → 用终端打开 → 运行 ./publish.sh
# 或者设置 Obsidian 的 Shell Commands 插件调用这个脚本

set -uo pipefail

PROJECT="$(cd "$(dirname "$0")" && pwd)/tangjin-blog"
POSTS_DIR="$PROJECT/src/content/posts"

# 获取当前激活的笔记路径（从 Obsidian 传入）
NOTE_PATH="${1:-}"

if [ -z "$NOTE_PATH" ] || [ ! -f "$NOTE_PATH" ]; then
  echo "请在 Obsidian 中打开要发布的笔记，然后右键 → 用终端打开"
  exit 1
fi

BASENAME="$(basename "$NOTE_PATH" .md)"
TITLE="$(head -1 "$NOTE_PATH" | sed 's/^#\s*//')"
DATE="$(date +%Y-%m-%d)"
FILENAME="${DATE}-${BASENAME}.md"

# 读取 frontmatter（如果有）
if head -1 "$NOTE_PATH" | grep -q '^---'; then
  # 已有 frontmatter，直接复制
  cp "$NOTE_PATH" "$POSTS_DIR/$FILENAME"
else
  # 没有 frontmatter，自动补充
  {
    echo "---"
    echo "title: \"$TITLE\""
    echo "description: \"$TITLE\""
    echo "published: $DATE"
    echo "tags: []"
    echo "---"
    echo ""
    cat "$NOTE_PATH"
  } > "$POSTS_DIR/$FILENAME"
fi

echo "✓ 已发布: $FILENAME"

# 提交到 GitHub
cd "$PROJECT"
git add -A
git commit -m "post: $TITLE"
git push

echo "✓ 已推送到 GitHub，约 1-2 分钟后上线"
