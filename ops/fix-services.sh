#!/usr/bin/env bash
# 修复 Waline 端口映射 + MariaDB 容器访问
set -uo pipefail

DB_PASS="tangjin@2026"

echo "==> 1. MariaDB 绑定 0.0.0.0（容器通过 host.docker.internal 访问）"
sudo tee /etc/mysql/mariadb.conf.d/50-container-access.cnf > /dev/null <<'EOF'
[mysqld]
bind-address = 0.0.0.0
EOF
sudo systemctl restart mariadb
sleep 3
sudo systemctl is-active mariadb

echo "==> 2. 允许 waline/umami 用户从 Docker 网段连接"
mysql --protocol=socket -uroot -p"${DB_PASS}" <<'SQL'
CREATE USER IF NOT EXISTS 'waline'@'%' IDENTIFIED BY 'CHANGE_ME_WALINE_DB_PASSWORD';
GRANT ALL PRIVILEGES ON waline.* TO 'waline'@'%';
CREATE USER IF NOT EXISTS 'umami'@'%' IDENTIFIED BY 'CHANGE_ME_UMAMI_DB_PASSWORD';
GRANT ALL PRIVILEGES ON umami.* TO 'umami'@'%';
FLUSH PRIVILEGES;
SQL
echo "   用户已放行"

echo "==> 3. 验证容器网段能连 MariaDB"
mysql -h 127.0.0.1 -uwaline -pCHANGE_ME_WALINE_DB_PASSWORD -e "SELECT 'waline remote ok' AS s;" waline 2>&1 | tail -2
mysql -h 127.0.0.1 -uumami -pCHANGE_ME_UMAMI_DB_PASSWORD -e "SELECT 'umami remote ok' AS s;" umami 2>&1 | tail -2

echo "==> 4. 修正 Waline 端口映射（容器内 8360）"
sudo sed -i 's/8365:8365/8365:8360/' /opt/services/docker-compose.yml
grep -n '836' /opt/services/docker-compose.yml

echo "==> 5. 重启容器"
cd /opt/services && sudo docker compose up -d 2>&1 | tail -5

echo "==> 6. 等待启动并检查"
sleep 8
sudo docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "--- umami 日志 ---"
sudo docker logs umami 2>&1 | tail -6
echo "--- waline 健康 ---"
curl -s -o /dev/null -w 'Waline HTTP %{http_code}\n' http://127.0.0.1:8365/
echo "--- umami 健康 ---"
curl -s -o /dev/null -w 'Umami HTTP %{http_code}\n' http://127.0.0.1:3001/
