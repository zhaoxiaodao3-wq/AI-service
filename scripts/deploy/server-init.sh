#!/usr/bin/env bash
# ============================================================
# AI-agent 阿里云 ECS 初始化：Docker + Compose 插件 + 镜像加速
# 用法: sudo bash server-init.sh
# ============================================================
set -euo pipefail

echo "==> [1/4] apt 更新并安装基础依赖"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg git

echo "==> [2/4] 安装 Docker CE + compose 插件"
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
# shellcheck disable=SC1091
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "==> [3/4] 设置开机自启并启动"
systemctl enable --now docker

echo "==> [4/4] 配置 Docker 镜像加速（国内拉取镜像用，可替换为阿里云个人加速器地址）"
mkdir -p /etc/docker
if [ ! -f /etc/docker/daemon.json ]; then
  cat > /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1ms.run"
  ]
}
EOF
  systemctl restart docker
fi

echo "==> 完成！验证："
docker --version
docker compose version
