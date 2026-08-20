#!/usr/bin/env bash
# 恢复脚本：把指定备份文件恢复到 PostgreSQL
# 用法：bash scripts/restore.sh /opt/aigc-backups/aigc_20260820_030000.sql.gz
# 注意：会覆盖目标库现有数据，请先确认。

set -euo pipefail

BACKUP_FILE="${1:-}"
if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
  echo "用法: bash scripts/restore.sh <备份文件路径>"
  exit 1
fi

POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-aigc-postgres}"
POSTGRES_USER="${POSTGRES_USER:-aigc}"
POSTGRES_DB="${POSTGRES_DB:-aigc}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

echo "[restore] 从 $BACKUP_FILE 恢复 $POSTGRES_DB ..."

# 先清空旧数据再导入，避免残留表冲突
docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$POSTGRES_CONTAINER" \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

gunzip -c "$BACKUP_FILE" | docker exec -i -e PGPASSWORD="$POSTGRES_PASSWORD" "$POSTGRES_CONTAINER" \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "[restore] 完成。建议重启后端让 Alembic 自动对齐版本：docker compose -f docker-compose.prod.yml restart backend worker"
