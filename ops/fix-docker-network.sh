#!/usr/bin/env bash
# 修复 Docker 默认地址池耗尽问题
set -uo pipefail

echo "==> 1. 备份当前 daemon.json"
sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak 2>/dev/null

echo "==> 2. 写入扩大的地址池配置"
sudo tee /etc/docker/daemon.json > /dev/null <<'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.1panel.live"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-address-pools": [
    { "base": "172.17.0.0/16", "size": 24 },
    { "base": "172.18.0.0/16", "size": 24 },
    { "base": "172.19.0.0/16", "size": 24 },
    { "base": "10.20.0.0/16", "size": 24 }
  ],
  "live-restore": true
}
EOF

echo "==> 3. 校验并重启 docker"
sudo dockerd --validate --config-file=/etc/docker/daemon.json 2>&1 | tail -2
sudo systemctl restart docker
sleep 4
sudo systemctl is-active docker

echo "==> 4. 清理残留的失败网络"
sudo docker network ls 2>/dev/null

echo "==> 5. 重新启动 waline + umami"
cd /opt/services && sudo docker compose up -d 2>&1 | tail -6

echo "==> 6. 最终状态"
sudo docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}' 2>&1
