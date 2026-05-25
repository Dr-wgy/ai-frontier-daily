#!/bin/bash
set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "${SCRIPT_DIR}/.." && pwd)
VENV_DIR="${PROJECT_ROOT}/.venv"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]    $(date '+%Y-%m-%d %H:%M:%S') $*${NC}" >&2; }
log_success() { echo -e "${GREEN}[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $*${NC}" >&2; }
log_error()   { echo -e "${RED}[ERROR]   $(date '+%Y-%m-%d %H:%M:%S') $*${NC}" >&2; }
log_warning() { echo -e "${YELLOW}[WARNING] $(date '+%Y-%m-%d %H:%M:%S') $*${NC}" >&2; }

echo "=== AI 前沿早报 - 环境初始化 ===" >&2

log_info "[1/5] 检查 Python 3..."
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 未安装"
    exit 1
fi
log_success "Python $(python3 --version)"

log_info "[2/5] 创建/激活虚拟环境..."
if [ -d "$VENV_DIR" ]; then
    log_info "虚拟环境已存在，激活中..."
else
    log_info "创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    log_success "虚拟环境创建完成"
fi
source "${VENV_DIR}/bin/activate"
log_success "虚拟环境已激活"

log_info "[3/5] 安装项目依赖..."
if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    pip install -r "${PROJECT_ROOT}/requirements.txt"
    log_success "依赖安装完成"
else
    log_warning "未找到 requirements.txt"
fi

log_info "[4/5] 检查/安装 lark-cli..."
if command -v lark-cli &> /dev/null; then
    log_success "lark-cli 已安装 ($(lark-cli --version))"
else
    log_info "安装 lark-cli..."
    brew install lark-cli
    log_success "lark-cli 安装完成"
fi

log_info "[5/6] 初始化 lark-cli 配置..."
if ! lark-cli config show &> /dev/null; then
    log_warning "请运行以下命令完成配置:"
    echo "    lark-cli config init --new" >&2
    echo "    lark-cli auth login" >&2
else
    log_success "lark-cli 已配置"
fi

log_info "[6/6] 检查飞书 SDK 授权 (OAuth)..."
SECRETS_FILE="${PROJECT_ROOT}/config/secrets.json"
if [ ! -f "$SECRETS_FILE" ]; then
    log_warning "未找到 secrets.json，请先根据 secrets.example.json 创建并填入 app_id/app_secret"
else
    # 使用 Python 检查 secrets.json 中是否有 refresh_token
    HAS_REFRESH_TOKEN=$(python3 -c "import json, sys; d=json.load(open('$SECRETS_FILE')); print(1 if d.get('feishu', {}).get('refresh_token') else 0)" 2>/dev/null || echo 0)
    
    if [ "$HAS_REFRESH_TOKEN" -eq 1 ]; then
        log_success "飞书 SDK 已授权 (已发现 refresh_token)"
    else
        log_warning "未发现 refresh_token，即将运行授权助手..."
        python3 "${PROJECT_ROOT}/project-space/tests/auth_helper.py"
    fi
fi

echo "" >&2
echo "=== 环境检查完成 ===" >&2
echo "" >&2
echo "下一步:" >&2
echo "  1. 确认配置: 检查 config/secrets.json 是否包含有效的 app_id/app_secret" >&2
echo "  2. 运行工作流: lobster({ filePath: \"<skill-path>/references/ai-frontier-daily.lobster\" })" >&2
echo "" >&2
echo "提示: 后续运行项目时，请先激活虚拟环境:" >&2
echo "      source ${VENV_DIR}/bin/activate" >&2
