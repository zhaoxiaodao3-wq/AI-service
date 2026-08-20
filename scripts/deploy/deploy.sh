#!/usr/bin/env bash
# ============================================================
# 服务器端部署：解包 + 生成根 .env + docker compose 构建启动
# 用法: bash deploy.sh [/path/to/aigc-agent.tar.gz]
# 环境: APP_DIR=/opt/aigc-agent（可用环境变量覆盖）
# ============================================================
set -euo pipefail

PKG="${1:-}"
APP_DIR="${APP_DIR:-/opt/aigc-agent}"
COMPOSE_F="-f docker-compose.yml -f scripts/deploy/docker-compose.prod.yml"

mkdir -p "$APP_DIR"
cd "$APP_DIR"

if [ -n "$PKG" ] && [ -f "$PKG" ]; then
  echo "==> 解包 $PKG -> $APP_DIR"
  tar -xzf "$PKG" -C "$APP_DIR"
fi

echo "==> 检查/生成根 .env"
if [ ! -f .env ]; then
  if [ -f scripts/deploy/.env.production.example ]; then
    cp scripts/deploy/.env.production.example .env
    echo "已从模板生成 .env，请修改 POSTGRES_PASSWORD 后重跑本脚本"
    exit 1
  fi
fi

echo "==> 检查 backend/.env"
if [ ! -f backend/.env ]; then
  echo "ERROR: 缺少 backend/.env"
  echo "  本地执行: scp backend/.env root@<IP>:$APP_DIR/backend/.env"
  echo "  或按 backend/.env.example 填写后重跑"
  exit 1
fi

echo "==> docker compose 构建并启动"
docker compose $COMPOSE_F up -d --build

echo "==> 状态"
docker compose $COMPOSE_F ps
echo "==> 健康检查"
sleep 5
curl -fsS http://127.0.0.1/api/health && echo "" || echo "（后端尚未就绪，稍后重试）"
