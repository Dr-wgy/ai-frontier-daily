#!/bin/bash
# 路径: ai-frontier-daily/scripts/base/run.sh

# 1. 切换到项目根目录 (run.sh 位于 scripts/base/，需上两级)
cd "$(dirname "$0")/../.." || exit

# 2. 激活虚拟环境 (如果存在)
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# 3. 注入 SSL 证书环境变量 (使用 venv 中的 python 获取路径)
export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())" 2>/dev/null)
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE

# 4. 核心魔法：使用 exec 透传并执行传入的任意命令及其参数
exec "$@"