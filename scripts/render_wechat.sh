#!/bin/bash
set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
SECRETS_FILE="${PROJECT_ROOT}/config/secrets.json"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]    $(date '+%Y-%m-%d %H:%M:%S') $*${NC}" >&2; }
log_success() { echo -e "${GREEN}[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $*${NC}" >&2; }
log_error()   { echo -e "${RED}[ERROR]   $(date '+%Y-%m-%d %H:%M:%S') $*${NC}" >&2; }

# 支持两种调用方式：
#   ./render_wechat.sh /path/to/file.md      # 直接传 md 文件路径
#   ./render_wechat.sh 2026-05-19            # 传日期，自动拼接路径
#   ./render_wechat.sh                       # 默认今天

if [ -n "$1" ] && [[ "$1" == *.md ]]; then
    BRIEFING_FILE="$1"
    DATE=$(basename "$(dirname "$1")")
else
    DATE="${1:-$(date +%Y-%m-%d)}"
    BRIEFING_FILE="${PROJECT_ROOT}/output/${DATE}/briefing.md"
fi

RENDER_PROJECT=$(python3 -c "import json; print(json.load(open('${SECRETS_FILE}'))['weichat']['render_project'])")

if [ -z "$RENDER_PROJECT" ]; then
    log_error "secrets.json 中 weichat.render_project 未配置"
    exit 1
fi

if [ ! -f "$BRIEFING_FILE" ]; then
    log_error "早报文件不存在: ${BRIEFING_FILE}"
    exit 1
fi

log_info "渲染日期: ${DATE}"
log_info "早报文件: ${BRIEFING_FILE}"
log_info "渲染项目: ${RENDER_PROJECT}"

cd "$RENDER_PROJECT"
source .venv/bin/activate

log_info "开始渲染微信预览..."
python3 toolkit/cli.py preview "${BRIEFING_FILE}" --theme sspai

log_success "渲染完成"
