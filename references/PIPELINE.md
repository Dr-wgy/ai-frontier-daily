# AI 前沿早报流水线 - 工作流说明

> 本文档描述 `ai-frontier-daily.lobster` 工作流的步骤设计、内部流程及数据流向。

---

## 1. 工作流总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ai-frontier-daily.lobster                                              │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐           │
│  │news_frontier │───▶│render_wechat │───▶│  publish2lark   │           │
│  └──────────────┘    └──────────────┘    └─────────────────┘           │
│                                                   │                    │
│                                                   ▼                    │
│                                          ┌───────────┐                 │
│                                          │push2group │───▶ final_report│
│                                          └───────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 步骤详解

### Step 0: 环境准备

**功能**：激活虚拟环境并配置 SSL 证书

**配置命令**：
```bash
cd /Users/han.qishu/Professional/ai-frontier-daily
source .venv/bin/activate
export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")
export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE
```

---

### Step 1: `news_frontier`

**功能**：执行主流水线，生成 AI 前沿早报

**调用命令**：
```bash
cd /Users/han.qishu/Professional/ai-frontier-daily && python3 scripts/news_frontier.py --date "${DATE}"
```

**内部流程**（4 个子阶段）：

| 子阶段 | 模块 | 输入 | 输出 | 说明 |
|--------|------|------|------|------|
| `ingest` | `IngestModule` | RSS 源列表 | `output/{DATE}/ingested.jsonl` | RSS 抓取、去重（标题/URL/时间窗口） |
| `filter_rank` | `FilterRankModule` | `ingested.jsonl` | `output/{DATE}/filtered_ranked.json` | LLM 智能筛选，判断新闻相关性与质量，排序 |
| `summarize` | `SummarizeModule` | `filtered_ranked.json` | `output/{DATE}/summary.json` | LLM 摘要生成，统一格式 |
| `assemble` | `AssembleModule` | `summary.json` | `output/{DATE}/briefing.md` | 拼版渲染 Markdown 终稿 |

**数据产物**：

| 文件 | 用途 | 必读 |
|------|------|------|
| `output/{DATE}/briefing.md` | 早报终稿，用于飞书发布 | ✅ 是 |
| `output/{DATE}/summary.json` | LLM 摘要结果，用于机器人推送 | 发布时需要 |
| `output/{DATE}/filtered_ranked.json` | 筛选排序中间产物 | 排错时用 |
| `output/{DATE}/ingested.jsonl` | 原始采集条目 | 排错时用 |

---

### Step 2: `render_wechat`

**功能**：渲染微信公众号格式的早报

**调用命令**：
```bash
DATE="${DATE}"; /Users/han.qishu/Professional/ai-frontier-daily/scripts/render_wechat.sh "$DATE"
```

---

### Step 3: `publish2lark`

**功能**：将早报发布到飞书知识库（按月份归档）

**调用命令**：
```bash
DATE="${DATE}"; python3 /Users/han.qishu/Professional/ai-frontier-daily/scripts/publish2lark.py --date "$DATE"
```

**内部流程**（5 个子步骤）：

```
Step 1/5: find_or_create_month_folder
    │
    ▼
Step 2/5: check_output
    │
    ▼
Step 3/5: clean_duplicates ──▶ 将重复文档移入回收站
    │
    ▼
Step 4/5: publish ──▶ 创建节点 + 写入内容
    │
    ▼
Step 5/5: get_doc_url ──▶ 输出文档链接
```

**子步骤详解**：

| 步骤 | 函数 | 说明 |
|------|------|------|
| 1/5 | `_find_or_create_month_folder` | 在知识库根目录下查找 `YYYY-MM` 文件夹，不存在则创建 |
| 2/5 | `_check_output` | 验证 `output/{DATE}/briefing.md` 是否存在 |
| 3/5 | `_clean_duplicates` | 查找重复文档并移入「回收站」文件夹 |
| 4/5 | `_publish` | 创建新文档节点并写入早报内容 |
| 5/5 | `_publish` | 输出文档链接到标准输出 |

**配置读取**：
- 从 `config/secrets.json` 读取 `feishu.space_id`

**同名去重逻辑**：
```
IF 知识库中存在 "AI 前沿早报（YYYY-MM-DD）"
  THEN 将重复文档移入「回收站」文件夹
  ELSE 创建新文档
```

**输出**：
- 标准输出最后一行：文档链接 URL (`https://my.feishu.cn/wiki/{node_token}`)
- 供后续 `push2group` 步骤使用

---

### Step 4: `push2group`

**功能**：向飞书群推送交互式卡片通知

**调用命令**：
```bash
DATE="${DATE}"; DOC_URL="${DOC_URL:-$publish2lark.stdout}"; python3 scripts/push2group.py --date "${DATE}" --doc-url "${DOC_URL}"
```

**输入依赖**：
- `$publish2lark.stdout`：上一步输出的文档链接（自动获取）
- `output/{DATE}/summary.json`：早报摘要数据

**卡片内容**：
- 标题：`AI 前沿早报（YYYY-MM-DD）`
- 正文：各模块摘要 + 热度标识（🔥）
- 按钮：「立即查看」→ 文档链接

**配置来源**：
- 从 `config/secrets.json` 读取 `feishu.bot_webhook`

---

### Step 5: `final_report`

**功能**：输出工作流完成报告

**调用命令**：
```bash
echo "AI前沿早报发布完成！日期：${DATE}，文档链接：${DOC_URL}"
```

---

## 3. 数据流图

```
RSS 源列表
    │
    ▼
┌─────────────────────────────────────┐
│ news_frontier.py: ingest           │
│  → ingested.jsonl                   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ news_frontier.py: filter_rank      │
│  → filtered_ranked.json            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ news_frontier.py: summarize        │
│  → summary.json                    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ news_frontier.py: assemble         │
│  → briefing.md                     │
└─────────────────────────────────────┘
    │
    ├─────────────────────────────────┤
    ▼                                 ▼
┌──────────────┐              ┌────────────┐
│render_wechat │              │ push2group │
│.sh           │              │ .py        │
│              │◀─────────────┤            │
│→ 微信格式    │  summary.json │            │
└──────────────┘              └──────┬─────┘
    │                               │
    ▼                               ▼
┌──────────────┐              ┌────────────┐
│publish2lark  │              │ final_     │
│.py           │              │ report     │
│              │              │            │
│→ 飞书文档    │              │            │
└──────────────┘              └────────────┘
```

---

## 4. 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATE` | 早报日期 | `$(date +%Y-%m-%d)` |
| `DOC_URL` | 文档链接 | `$publish2lark.stdout` |

---

## 5. 配置文件

**路径**：`config/secrets.json`

| 字段 | 说明 |
|------|------|
| `feishu.space_id` | 飞书知识库 Space ID |
| `feishu.bot_webhook` | 群机器人 Webhook 地址 |
| `llm.api_key` | LLM API Key |
| `llm.base_url` | LLM API 基础 URL |
| `llm.model_name` | LLM 模型名称 |

---

## 6. 目录结构

```
ai-frontier-daily/
├── scripts/
│   ├── news_frontier.py      # 主流水线入口
│   ├── render_wechat.sh      # 微信格式渲染脚本
│   ├── publish2lark.py       # 飞书发布脚本
│   └── push2group.py         # 群机器人推送
├── project-space/            # 核心模块
│   ├── ingest.py
│   ├── filter_rank.py
│   ├── summarize.py
│   ├── assemble.py
│   └── utils/
├── output/
│   └── {DATE}/
│       ├── briefing.md        # 早报终稿
│       ├── summary.json       # LLM 摘要
│       ├── filtered_ranked.json
│       └── ingested.jsonl
└── config/
    └── secrets.json          # 敏感配置
```
