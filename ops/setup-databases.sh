#!/usr/bin/env bash
# 为 Waline 和 Umami 创建数据库和用户
set -uo pipefail

DB_PASS="tangjin@2026"

echo "==> 创建 Waline 数据库和用户"
mysql --protocol=socket -uroot -p"${DB_PASS}" <<'SQL'
CREATE DATABASE IF NOT EXISTS waline CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'waline'@'localhost' IDENTIFIED BY 'CHANGE_ME_WALINE_DB_PASSWORD';
ALTER USER 'waline'@'localhost' IDENTIFIED BY 'CHANGE_ME_WALINE_DB_PASSWORD';
GRANT ALL PRIVILEGES ON waline.* TO 'waline'@'localhost';
FLUSH PRIVILEGES;
SQL
echo "   waline 数据库就绪"

echo "==> 创建 Umami 数据库和用户"
mysql --protocol=socket -uroot -p"${DB_PASS}" <<'SQL'
CREATE DATABASE IF NOT EXISTS umami CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'umami'@'localhost' IDENTIFIED BY 'CHANGE_ME_UMAMI_DB_PASSWORD';
ALTER USER 'umami'@'localhost' IDENTIFIED BY 'CHANGE_ME_UMAMI_DB_PASSWORD';
GRANT ALL PRIVILEGES ON umami.* TO 'umami'@'localhost';
FLUSH PRIVILEGES;
SQL
echo "   umami 数据库就绪"

echo "==> 验证"
mysql -uwaline -pCHANGE_ME_WALINE_DB_PASSWORD -e "SELECT 'waline ok' AS status;" waline 2>&1
mysql -uumami -pCHANGE_ME_UMAMI_DB_PASSWORD -e "SELECT 'umami ok' AS status;" umami 2>&1
