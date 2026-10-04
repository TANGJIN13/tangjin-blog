#!/usr/bin/env bash
# 把部署密钥限制为「只能 rrsync 写 /var/www/blog」
set -euo pipefail

AUTH=/home/ubuntu/.ssh/authorized_keys
TARGET=/var/www/blog
MARKER='github-actions-deploy@tangjin.xyz'

echo "==> 1. 备份 authorized_keys"
cp "$AUTH" "$AUTH.bak-$(date +%s)"
echo "   已备份"

echo
echo "==> 2. 修改前的部署密钥行"
grep "$MARKER" "$AUTH" | cut -c1-120 || true

echo
echo "==> 3. 应用 rrsync 限制"
python3 - "$AUTH" "$TARGET" "$MARKER" <<'PY'
import sys
auth, target, marker = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(auth, encoding='utf-8').read().splitlines()
out = []
changed = False
for ln in lines:
    # 只处理部署密钥那一行，且跳过已加过限制的
    if marker in ln and 'rrsync' not in ln:
        # 剥掉可能已有的 command= 前缀，取纯公钥部分
        parts = ln.split()
        # 找到 ssh- 开头的位置
        try:
            idx = next(i for i, p in enumerate(parts) if p.startswith('ssh-') or p.startswith('ecdsa-'))
        except StopIteration:
            out.append(ln); continue
        pubkey = ' '.join(parts[idx:])
        newline = f'command="/usr/bin/rrsync -wo {target}",restrict {pubkey}'
        out.append(newline)
        changed = True
    else:
        out.append(ln)
open(auth, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('   已应用限制' if changed else '   无需修改（可能已应用过）')
PY
chmod 600 "$AUTH"

echo
echo "==> 4. 修改后的部署密钥行"
grep "$MARKER" "$AUTH" | cut -c1-140

echo
echo "==> 5. 当前 authorized_keys 全部条目（只显示类型与备注）"
awk '{print "   ", $1, $NF}' "$AUTH"
