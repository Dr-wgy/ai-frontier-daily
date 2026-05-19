name: ai-frontier-daily
description: AI前沿早报工作流 - 自动采集、LLM摘要、飞书发布
steps:
  - id: news_frontier
    command: bash -c 'cd $HOME/Professional/ai-frontier-daily && source .venv/bin/activate && export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())") && export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE && python scripts/news_frontier.py --date "${DATE:-$(date +%Y-%m-%d)}"'

  - id: render_wechat
    command: bash -c 'cd $HOME/Professional/ai-frontier-daily && source .venv/bin/activate && scripts/render_wechat.sh "${DATE:-$(date +%Y-%m-%d)}"'

  - id: publish2lark
    command: bash -c 'cd $HOME/Professional/ai-frontier-daily && source .venv/bin/activate && export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())") && export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE && python scripts/publish2lark.py --date "${DATE:-$(date +%Y-%m-%d)}"'

  - id: push2group
    command: bash -c 'cd $HOME/Professional/ai-frontier-daily && source .venv/bin/activate && export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())") && export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE && python scripts/push2group.py --date "${DATE:-$(date +%Y-%m-%d)}" --doc-url "${DOC_URL:-$publish2lark.stdout}"'
    stdin: $publish2lark.stdout

  - id: final_report
    command: bash -c 'echo "AI前沿早报发布完成！日期：${DATE:-$(date +%Y-%m-%d)}，文档链接：${DOC_URL:-$publish2lark.stdout}"'