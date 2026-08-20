#!/usr/bin/env bash
# 备份脚本：PostgreSQL 全量备份 + gzip 压缩 + 按日期留存最近 N 份
# 用法：在服务器上执行  bash scripts/backup.sh
# 推荐：宝塔面板「计划任务」→ shell 脚本，每天凌晨执行一次

set -euo pipefail

# ---------- 可配置项 ----------
BACKUP_DIR="${BACKUP_DIR:-/opt/aigc-backups}"   # 备份存放目录
KEEP_N="${KEEP_N:-7}"                            # 保留最近几份
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-aigc-postgres}"
POSTGRES_USER="${POSTGRES_USER:-aigc}"
POSTGRES_DB="${POSTGRES_DB:-aigc}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"       # 建议由 .env.prod 传入
# ------------------------------

mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="$BACKUP_DIR/aigc_${STAMP}.sql.gz"

echo "[backup] 开始备份 $POSTGRES_DB -> $OUT_FILE"

# 通过容器执行 pg_dump，压缩后写入宿主机备份目录
docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$POSTGRES_CONTAINER" \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges \
  | gzip > "$OUT_FILE"

echo "[backup] 完成: $(du -h "$OUT_FILE" | cut -f1)"

# 只保留最近 KEEP_N 份，删除更早的
ls -1t "$BACKUP_DIR"/aigc_*.sql.gz 2>/dev/null | tail -n +$((KEEP_N + 1)) | while read -r old; do
  echo "[backup] 清理旧备份: $old"
  rm -f "$old"
done

echo "[backup] 当前备份列表:"
ls -lht "$BACKUP_DIR" | head -n 10
