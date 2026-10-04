#!/usr/bin/env bash
# 测试 rrsync 下 rsync 目标路径的正确写法
set -uo pipefail

TESTKEY=/tmp/pathkey
AUTH=/home/ubuntu/.ssh/authorized_keys
TARGET=/var/www/blog

rm -f "$TESTKEY" "$TESTKEY.pub"
ssh-keygen -t ed25519 -f "$TESTKEY" -N '' -C 'path-test' -q
PUB=$(cat "$TESTKEY.pub")
grep -v 'path-test' "$AUTH" > /tmp/a.new; cat /tmp/a.new > "$AUTH"
echo "command=\"/usr/bin/rrsync -wo $TARGET\",restrict $PUB" >> "$AUTH"
chmod 600 "$AUTH"

mkdir -p /tmp/psrc && echo "path test" > /tmp/psrc/z.txt
SSHOPT="ssh -i $TESTKEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no"

echo "==> 写法 A: 目标写 / （受限目录的根）"
rsync -az --delete -e "$SSHOPT" /tmp/psrc/ localhost:/ 2>&1 | sed 's/^/   /' | head -3
[ -f "$TARGET/z.txt" ] && echo "   → 文件落在 $TARGET/z.txt  ✓" || echo "   → 没写进去 ✗"
rm -f "$TARGET/z.txt"

echo
echo "==> 写法 B: 目标写完整绝对路径 /var/www/blog/"
rsync -az -e "$SSHOPT" /tmp/psrc/ localhost:/var/www/blog/ 2>&1 | sed 's/^/   /' | head -3
[ -f "$TARGET/z.txt" ] && echo "   → 落在 $TARGET/z.txt" || echo "   → 没落在预期位置"
# 检查是不是被当成相对路径了
if [ -d "$TARGET/var/www/blog" ]; then
  echo "   ⚠ 被解释成了相对路径，实际落在 $TARGET/var/www/blog/"
  rm -rf "$TARGET/var"
fi
rm -f "$TARGET/z.txt"

echo
echo "==> 写法 C: 目标写 ./ （显式相对当前）"
rsync -az -e "$SSHOPT" /tmp/psrc/ localhost:./ 2>&1 | sed 's/^/   /' | head -3
[ -f "$TARGET/z.txt" ] && echo "   → 文件落在 $TARGET/z.txt  ✓" || echo "   → 没写进去"
rm -f "$TARGET/z.txt"

echo
echo "==> 写法 D: 带子目录（确认子目录可用）"
mkdir -p /tmp/psrc/sub && echo "sub file" > /tmp/psrc/sub/s.txt
rsync -az -e "$SSHOPT" /tmp/psrc/sub/ localhost:/sub/ 2>&1 | sed 's/^/   /' | head -3
[ -f "$TARGET/sub/s.txt" ] && echo "   → 子目录可用: $TARGET/sub/s.txt ✓" || echo "   → 子目录写入失败"
rm -rf "$TARGET/sub"

echo
echo "==> 清理"
grep -v 'path-test' "$AUTH" > /tmp/a.new; cat /tmp/a.new > "$AUTH"
rm -f "$TESTKEY" "$TESTKEY.pub" /tmp/a.new
rm -rf /tmp/psrc
echo "   完成"
echo
echo "==> 目标目录现状"
ls -la "$TARGET" | head -6
