#!/usr/bin/env bash
# 修正博客目录权限：ubuntu 可写（部署用），www-data 可读（nginx 用）
set -uo pipefail

ROOT="/var/www/blog"

echo "==> 修正 $ROOT 归属与权限"
sudo chown -R ubuntu:www-data "$ROOT"
sudo find "$ROOT" -type d -exec chmod 755 {} +
sudo find "$ROOT" -type f -exec chmod 644 {} +
echo "   owner=ubuntu group=www-data  dir=755 file=644"

echo
echo "==> 验证：ubuntu 可写"
touch "$ROOT/.write-test" && echo "   写: OK" && rm -f "$ROOT/.write-test" || echo "   写: 失败"

echo "==> 验证：nginx 可读首页"
if sudo -u www-data test -r "$ROOT/index.html"; then echo "   读: OK"; else echo "   读: 失败"; fi

echo
echo "==> 目录状态"
ls -ld "$ROOT"
ls -la "$ROOT" | head -8

echo
echo "==> 确认 ubuntu 有免密 sudo（部署时可能需要 reload nginx）"
sudo -n true 2>/dev/null && echo "   免密 sudo: 可用" || echo "   免密 sudo: 不可用"
