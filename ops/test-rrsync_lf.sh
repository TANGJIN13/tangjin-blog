#!/usr/bin/env bash
# 隔离测试 rrsync：验证受限密钥只能写指定目录、不能执行命令
set -uo pipefail

TESTKEY=/tmp/rrtest
TESTKEY_PUB=/tmp/rrtest.pub
AUTH=/home/ubuntu/.ssh/authorized_keys
TARGET=/var/www/blog

echo "==> 1. 生成测试密钥"
rm -f "$TESTKEY" "$TESTKEY_PUB"
ssh-keygen -t ed25519 -f "$TESTKEY" -N '' -C 'rrsync-test' -q
echo "   已生成"

echo
echo "==> 2. 以受限方式加入 authorized_keys"
PUB=$(cat "$TESTKEY_PUB")
ENTRY="command=\"/usr/bin/rrsync -wo $TARGET\",restrict $PUB"
# 先删掉可能存在的旧测试项
grep -v 'rrsync-test' "$AUTH" > /tmp/auth.new && cat /tmp/auth.new > "$AUTH"
echo "$ENTRY" >> "$AUTH"
chmod 600 "$AUTH"
echo "   已添加:"
echo "   $ENTRY" | cut -c1-100

echo
echo "==> 3. 测试 A：能否执行任意命令（应该被拒绝）"
OUT=$(ssh -i "$TESTKEY" -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o BatchMode=yes localhost 'whoami' 2>&1)
echo "   ssh localhost whoami  →  $OUT"

echo
echo "==> 4. 测试 B：能否用 rsync 写入目标目录（应该成功）"
mkdir -p /tmp/rrsrc
echo "rrsync test $(date)" > /tmp/rrsrc/probe.txt
rsync -az -e "ssh -i $TESTKEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no" \
      /tmp/rrsrc/ localhost:/ 2>&1 | sed 's/^/   /'
if [ -f "$TARGET/probe.txt" ]; then
  echo "   ✓ 文件已写入 $TARGET/probe.txt"
  cat "$TARGET/probe.txt" | sed 's/^/     /'
else
  echo "   ✗ 文件没写进去"
fi

echo
echo "==> 5. 测试 C：能否写到目标目录之外（应该被拒绝）"
rsync -az -e "ssh -i $TESTKEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no" \
      /tmp/rrsrc/ localhost:/../etc/ 2>&1 | sed 's/^/   /' | head -5

echo
echo "==> 6. 测试 D：能否读取目标目录（-wo 是只写，读应该被拒）"
rsync -az -e "ssh -i $TESTKEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=no" \
      localhost:/index.html /tmp/readback/ 2>&1 | sed 's/^/   /' | head -3

echo
echo "==> 7. 清理测试痕迹"
rm -f "$TARGET/probe.txt"
grep -v 'rrsync-test' "$AUTH" > /tmp/auth.new && cat /tmp/auth.new > "$AUTH"
rm -f "$TESTKEY" "$TESTKEY_PUB" /tmp/auth.new
rm -rf /tmp/rrsrc /tmp/readback
echo "   已清理测试密钥和文件"
echo "   剩余密钥:"
cut -d' ' -f3 "$AUTH" | sed 's/^/     /'
