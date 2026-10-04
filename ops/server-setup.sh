#!/usr/bin/env bash
# 服务器端配置：Nginx 站点 + 目录权限
set -uo pipefail

BLOG_ROOT="/var/www/blog"

echo "==> 1. 建站点目录"
sudo mkdir -p "$BLOG_ROOT"
sudo chown -R ubuntu:www-data "$BLOG_ROOT"

echo "==> 2. 备份默认站点"
if [ ! -f /etc/nginx/sites-available/default.bak ]; then
  sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak
  echo "   已备份"
fi

echo "==> 3. 写入 Nginx 配置"
sudo tee /etc/nginx/sites-available/blog > /dev/null <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name tangjin.xyz www.tangjin.xyz _;

    root /var/www/blog;
    index index.html;
    server_tokens off;

    add_header X-Content-Type-Options nosniff always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    gzip on;
    gzip_min_length 1k;
    gzip_comp_level 5;
    gzip_types text/plain text/css application/json application/javascript
               application/xml application/xml+rss text/javascript image/svg+xml;

    location ~* \.(?:css|js|svg|png|jpg|jpeg|gif|webp|ico|woff2?|mp3)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    location / {
        try_files $uri $uri/ $uri.html =404;
    }

    error_page 404 /404.html;

    location /.well-known/ {
        try_files $uri =404;
    }
}
EOF

echo "==> 4. 启用站点"
sudo ln -sf /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/blog
sudo rm -f /etc/nginx/sites-enabled/default

echo "==> 5. 测试并重载"
sudo nginx -t && sudo systemctl reload nginx

echo "==> 完成"
