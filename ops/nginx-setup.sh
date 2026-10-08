#!/usr/bin/env bash
# 配置 Nginx 站点：静态博客
set -uo pipefail

BLOG_ROOT="/var/www/blog"

echo "==> 1. 建站点目录"
sudo mkdir -p "$BLOG_ROOT"
sudo chown -R ubuntu:www-data "$BLOG_ROOT"

echo "==> 2. 备份并替换默认站点"
if [ ! -f /etc/nginx/sites-available/default.bak ]; then
  sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
  echo "   已备份为 default.bak"
fi

sudo tee /etc/nginx/sites-available/blog > /dev/null <<'EOF'
# 静态博客站点
# 说明：
#  - 未绑定域名时，直接用 http://<你的服务器IP> 访问（无 Host 或 IP 会命中 default_server）
#  - 域名 tangjin.xyz 解析到本机后，自动命中 server_name，无需改动
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name tangjin.xyz www.tangjin.xyz _;

    root /var/www/blog;
    index index.html;

    # 关闭服务器版本号暴露
    server_tokens off;

    # 安全响应头
    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    # gzip 压缩
    gzip on;
    gzip_min_length 1k;
    gzip_comp_level 5;
    gzip_types text/plain text/css application/json application/javascript
               application/xml application/xml+rss text/javascript image/svg+xml;

    # 静态资源缓存
    location ~* \.(?:css|js|svg|png|jpg|jpeg|gif|webp|ico|woff2?)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # 适配 Astro 输出的目录结构（/about/ -> /about/index.html）
    location / {
        try_files $uri $uri/ $uri.html =404;
    }

    # 404 页面
    error_page 404 /404.html;

    # ACME / certbot 验证目录
    location /.well-known/ {
        try_files $uri =404;
    }
}
EOF

echo "==> 3. 启用站点"
sudo ln -sf /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/blog
sudo rm -f /etc/nginx/sites-enabled/default
echo "   已启用 blog，移除 default"

echo "==> 4. 测试并重载"
sudo nginx -t
if [ $? -eq 0 ]; then
  sudo systemctl reload nginx
  echo "   nginx 已重载"
else
  echo "   nginx -t 失败，恢复默认站点备份"
  sudo cp /etc/nginx/sites-available/default.bak /etc/nginx/sites-available/default
  sudo ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
  exit 1
fi

echo "==> 完成。站点根目录: $BLOG_ROOT"
