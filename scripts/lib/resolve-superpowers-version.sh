#!/usr/bin/env bash
# scripts/lib/resolve-superpowers-version.sh
# 用法: source 后调用 resolve_superpowers_version <docs/superpowers 绝对或相对路径>

# 规范化为三位版本号：v1.2 -> v1.2.0，v1.2.0 不变
normalize_superpowers_version() {
  local ver="${1:?version required}"
  if [[ "$ver" =~ ^v[0-9]+\.[0-9]+$ ]]; then
    printf '%s.0' "$ver"
    return 0
  fi
  printf '%s' "$ver"
}

# 解析当前活跃版本（始终返回三位）
resolve_superpowers_version() {
  local base="${1:?base dir required}"
  local raw=""
  base="${base%/}"

  if [[ -L "$base/current" ]]; then
    raw="$(readlink "$base/current")"
    raw="${raw#./}"
  elif [[ -f "$base/current-version.txt" ]]; then
    raw="$(tr -d '\r\n' < "$base/current-version.txt")"
  else
    raw="v1.0.0"
  fi

  normalize_superpowers_version "$raw"
}

# 解析磁盘上实际存在的版本目录名（兼容旧两位目录）
resolve_superpowers_version_dir() {
  local base="${1:?base dir required}"
  local ver="${2:?version required}"
  base="${base%/}"
  ver="$(normalize_superpowers_version "$ver")"

  if [[ -d "$base/$ver" ]]; then
    printf '%s' "$ver"
    return 0
  fi

  if [[ "$ver" =~ ^v([0-9]+)\.([0-9]+)\.0$ ]]; then
    local legacy="v${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
    if [[ -d "$base/$legacy" ]]; then
      printf '%s' "$legacy"
      return 0
    fi
  fi

  printf '%s' "$ver"
}
