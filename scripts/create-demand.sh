#!/usr/bin/env bash
set -eu
(set -o pipefail) 2>/dev/null && set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SUPERPOWERS_BASE="$PROJECT_ROOT/docs/superpowers"

VALID_TYPES=(feature ui-style api-adapter fix)

source "$SCRIPT_DIR/lib/resolve-superpowers-version.sh"

usage() {
  cat <<'EOF'
用法:
  ./scripts/create-demand.sh --type <feature|ui-style|api-adapter|fix> --name "<中文模块名>"
  ./scripts/create-demand.sh --init-version [--version v1.0.0]

选项:
  --type           业务分类（必填，除非 --init-version）
  --name           中文业务模块名（必填，除非 --init-version）
  --version        版本目录，默认解析 current
  --init-version   仅初始化版本骨架（四大分类空目录）
  -h, --help       显示帮助
EOF
}

is_valid_type() {
  local t="$1"
  for v in "${VALID_TYPES[@]}"; do
    [[ "$v" == "$t" ]] && return 0
  done
  return 1
}

mkdir_if_missing() {
  local dir="$1"
  if [[ -d "$dir" ]]; then
    echo "  已存在，跳过: $dir"
  else
    mkdir -p "$dir"
    echo "  已创建: $dir"
  fi
}

init_version_skeleton() {
  local version="$1"
  local version_dir="$SUPERPOWERS_BASE/$version"
  echo "初始化版本骨架: $version_dir"
  for t in "${VALID_TYPES[@]}"; do
    mkdir_if_missing "$version_dir/$t"
  done
}

create_module_dirs() {
  local version="$1"
  local type="$2"
  local name="$3"
  local module_root="$SUPERPOWERS_BASE/$version/$type/$name"

  echo "创建模块目录: $module_root"
  mkdir_if_missing "$module_root/requirements"
  mkdir_if_missing "$module_root/archive"
  mkdir_if_missing "$module_root/specs"
  mkdir_if_missing "$module_root/plans"

  echo ""
  echo "完成。模块根目录:"
  echo "  $module_root"
}

TYPE=""
NAME=""
VERSION=""
INIT_VERSION=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --type) TYPE="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    --init-version) INIT_VERSION=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1"; usage; exit 1 ;;
  esac
done

if [[ $INIT_VERSION -eq 1 ]]; then
  VERSION="${VERSION:-$(resolve_superpowers_version "$SUPERPOWERS_BASE")}"
  VERSION="$(normalize_superpowers_version "$VERSION")"
  init_version_skeleton "$VERSION"
  exit 0
fi

if [[ -z "$TYPE" || -z "$NAME" ]]; then
  echo "错误: --type 和 --name 为必填"
  usage
  exit 1
fi

if ! is_valid_type "$TYPE"; then
  echo "错误: 非法分类 '$TYPE'。允许: ${VALID_TYPES[*]}"
  exit 1
fi

VERSION="${VERSION:-$(resolve_superpowers_version "$SUPERPOWERS_BASE")}"
VERSION="$(normalize_superpowers_version "$VERSION")"
VERSION_DIR="$(resolve_superpowers_version_dir "$SUPERPOWERS_BASE" "$VERSION")"
init_version_skeleton "$VERSION_DIR"
create_module_dirs "$VERSION_DIR" "$TYPE" "$NAME"
