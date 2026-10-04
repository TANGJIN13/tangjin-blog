#!/usr/bin/env bash
# 给 /admin/ 路径加 HTTP Basic 认证
# 用法: sudo bash nginx-admin-auth.sh '用户名' '密码'
set -euo pipefail

USERNAME="${1:-tj}"
PASSWORD="${2:?需要提供密码}"

HTPASSWD="/etc/nginx/.htpasswd-admin"
CONF="/etc/nginx/sites-available/blog"
SNIPPET="/etc/nginx/snippets/admin-auth.conf"

echo "==> 1. 生成密码文件"
install -d -m 755 /etc/nginx/snippets
# openssl passwd -apr1 生成 Apache MD5 格式，nginx 支持
HASH=$(openssl passwd -apr1 "$PASSWORD")
printf '%s:%s\n' "$USERNAME" "$HASH" | sudo tee "$HTPASSWD" > /dev/null
sudo chmod 640 "$HTPASSWD"
sudo chown root:www-data "$HTPASSWD"
echo "   已写入 $HTPASSWD (用户: $USERNAME)"
ls -l "$HTPASSWD"

echo
echo "==> 2. 写入认证配置片段"
sudo tee "$SNIPPET" > /dev/null <<'EOF'
# /admin/ 后台访问认证
auth_basic "Restricted: Blog Admin";
auth_basic_user_file /etc/nginx/.htpasswd-admin;
EOF
echo "   已写入 $SNIPPET"

echo
echo "==> 3. 在站点配置里引入（幂等）"
if sudo grep -q 'admin-auth.conf' "$CONF"; then
  echo "   已经引入过了，跳过"
else
  sudo cp "$CONF" "${CONF}.bak-$(date +%s)"
  # 在 443 的 server 块里，location / 之前插入 /admin/ 块
  sudo python3 - "$CONF" <<'PY'
import re, sys
path = sys.argv[1]
src = open(path, encoding='utf-8').read()

admin_block = '''
    # ---- 后台：需要登录 ----
    location = /admin { return 301 /admin/; }
    location /admin/ {
        include /etc/nginx/snippets/admin-auth.conf;
        try_files $uri $uri/ =404;
    }

'''

# 找到第二个 server 块（443 那个）里的 "location / {"
idx = src.find('listen 443')
if idx < 0:
    sys.exit('找不到 443 server 块')
loc = src.find('    location / {', idx)
if loc < 0:
    sys.exit('在 443 块里找不到 location /')
src = src[:loc] + admin_block.lstrip('\n') + src[loc:]
open(path, 'w', encoding='utf-8').write(src)
print('   已在 443 server 块插入 /admin/ 认证')
PY
fi

echo
echo "==> 4. 校验并重载"
sudo nginx -t
sudo systemctl reload nginx
echo "   nginx 已重载"

echo
echo "==> 5. 验证"
echo -n "   不带凭证访问 /admin/ : HTTP "
curl -s -o /dev/null -w '%{http_code}' -H 'Host: tangjin.xyz' -k https://127.0.0.1/admin/ || true
echo
echo -n "   带凭证访问 /admin/   : HTTP "
curl -s -o /dev/null -w '%{http_code}' -H 'Host: tangjin.xyz' -k -u "$USERNAME:$PASSWORD" https://127.0.0.1/admin/ || true
echo
echo -n "   首页（应仍为 200）   : HTTP "
curl -s -o /dev/null -w '%{http_code}' -H 'Host: tangjin.xyz' -k https://127.0.0.1/ || true
echo
