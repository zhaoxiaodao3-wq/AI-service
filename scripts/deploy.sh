#!/usr/bin/env bash
# 服务器端一键部署脚本（在服务器 /www/wwwroot/aigc 目录下执行）
# 用法：bash scripts/deploy.sh
set -euo pipefail

cd "$(dirname "$0")/.."
echo "[deploy] 部署目录: $(pwd)"

# 1) 检查 Docker
if ! command -v docker >/dev/null 2>&1; then
  echo "[deploy] 未检测到 Docker，请先在宝塔安装「Docker 管理器」"
  exit 1
fi

# 2) 检查 .env.prod
if [ ! -f .env.prod ]; then
  echo "[deploy] 缺少 .env.prod，请复制 .env.prod.example 并填写"
  exit 1
fi

# 3) 构建并启动
echo "[deploy] docker compose build + up ..."
docker compose -f docker-compose.prod.yml up -d --build

# 4) 等待健康检查
echo "[deploy] 等待后端健康检查 ..."
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8000/api/health >/dev/null 2>&1; then
    echo "[deploy] 后端健康检查通过"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "[deploy] 后端健康检查超时，请查看日志: docker logs aigc-backend"
    exit 1
  fi
  sleep 2
done

# 5) 验证容器状态
docker compose -f docker-compose.prod.yml ps

echo "[deploy] 完成。访问 http://服务器IP 即可（宝塔建站反代到 127.0.0.1:80 并配 HTTPS）"
