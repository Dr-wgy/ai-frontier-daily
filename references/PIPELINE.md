# AI 前沿早报流水线 - 工作流说明

> 本文档描述 `ai-frontier-daily.lobster` 工作流的步骤设计、内部流程及数据流向。

---

## 1. 工作流总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ai-frontier-daily.lobster                                              │
│                                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐           │
│  │cleanup   │───▶│news_frontier │───▶│render_wechat │───▶│  publish2lark   │           │
│  └──────────┘    └──────────────┘    └──────────────┘    └─────────────────┘           │
│                                                                   │                    │
│                                                                   ▼                    │
│                                                          ┌───────────┐                 │
│                                                          │push2group │                 │
│                                                          └───────────┘                 │
│                                                                   │                    │
│                                                                   ▼                    │
│                                                          ┌─────────────────┐           │
│                                                          │publish2lark_base│           │
│                                                          └─────────────────┘           │
│                                                                   │                    │
│                                                                   ▼                    │
│                                                          ┌──────────────┐              │
│                                                          │final_report  │              │
│                                                          └──────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 步骤详解

### Step 0: `cleanup`

**功能**：清理临时文件，保障每次运行环境干净

**调用命令**：
```bash
rm -f /tmp/afinfo-*.txt
```

**说明**：删除上一次运行遗留的中间文件，避免脏数据干扰

---

### Step 1: `news_frontier`

**功能**：执行主流水线，生成 AI 前沿早报

**调用命令**：
```bash
$SKILL_DIR/scripts/base/run.sh python scripts/news_frontier.py --date $args.date
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
$SKILL_DIR/scripts/base/run.sh bash scripts/render_wechat.sh $args.date
```

---

### Step 3: `publish2lark`

**功能**：将早报发布到飞书知识库（按月份归档）

**调用命令**：
```bash
bash -c '$SKILL_DIR/scripts/base/run.sh python scripts/publish2lark.py --date $args.date > /tmp/afinfo-doc_url.txt'
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
- 标准输出重定向到 `/tmp/afinfo-doc_url.txt`
- 供后续 `push2group` 和 `final_report` 步骤使用

---

### Step 4: `push2group`

**功能**：向飞书群推送交互式卡片通知

**调用命令**：
```bash
bash -c 'DOC_URL=$(cat /tmp/afinfo-doc_url.txt) && $SKILL_DIR/scripts/base/run.sh python scripts/push2group.py --date $args.date --doc-url "$DOC_URL"'
```

**输入依赖**：
- `/tmp/afinfo-doc_url.txt`：上一步输出的文档链接
- `output/{DATE}/summary.json`：早报摘要数据

**卡片内容**：
- 标题：`AI 前沿早报（YYYY-MM-DD）`
- 正文：各模块摘要 + 热度标识（🔥）
- 按钮：「立即查看」→ 文档链接

**配置来源**：
- 从 `config/secrets.json` 读取 `feishu.bot_webhook`

---

### Step 5: `publish2lark_base`

**功能**：更新多维表格记录

**调用命令**：
```bash
bash -c '$SKILL_DIR/scripts/base/run.sh python scripts/publish2lark_base.py --date $args.date > /tmp/afinfo-base_url.txt'
```

**内部流程**（6 个子步骤）：

```
Step 1/6: create_base_if_not_exists ──▶ 创建/查找多维表格
    │
    ▼
Step 2/6: create_table_if_not_exists ──▶ 创建/查找数据表
    │
    ▼
Step 3/6: sync_fields ──▶ 同步字段（动态创建新字段）
    │
    ▼
Step 4/6: delete_today_records ──▶ 删除当天旧记录
    │
    ▼
Step 5/6: upload_records ──▶ 批量上传新记录
    │
    ▼
Step 6/6: output_url ──▶ 输出表格链接
```

**输出**：
- 标准输出重定向到 `/tmp/afinfo-base_url.txt`
- 供 `final_report` 步骤使用

---

### Step 6: `final_report`

**功能**：输出工作流完成报告

**调用命令**：
```bash
bash -c 'echo "✅ 完成！\n📄 文档：$(cat /tmp/afinfo-doc_url.txt)\n📊 表格：$(cat /tmp/afinfo-base_url.txt)"'
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
│render_wechat │              │ publish2lark│
│.sh           │              │ .py        │
│              │              │            │
│→ 微信格式    │              │→ 飞书文档   │
└──────────────┘              └──────┬─────┘
    │                               │
    │                               ▼
    │                        ┌────────────┐
    │                        │ push2group │
    │                        │ .py        │
    │                        │            │
    │                        │→ 群消息卡片 │
    │                        └──────┬─────┘
    │                               │
    │                               ▼
    │                        ┌─────────────────┐
    │                        │publish2lark_base│
    │                        │ .py             │
    │                        │                 │
    │                        │→ 多维表格记录    │
    │                        └─────────────────┘
    │
    ▼
┌──────────────┐
│final_report  │
│              │
│→ 完成报告    │
└──────────────┘
```

---

## 4. 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SKILL_DIR` | 项目根目录 | `ai-frontier-daily` |
| `args.date` | 早报日期参数 | `$(date +%Y-%m-%d)` |

**中间文件传递**：

| 文件 | 生产者 | 消费者 | 说明 |
|------|--------|--------|------|
| `/tmp/afinfo-doc_url.txt` | `publish2lark` | `push2group`, `final_report` | 飞书文档 URL |
| `/tmp/afinfo-base_url.txt` | `publish2lark_base` | `final_report` | 多维表格 URL |

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
│   ├── base/
│   │   ├── init_env.sh      # 环境初始化（首次使用运行）
│   │   └── run.sh           # 环境启动器（cd + venv + SSL + exec 透传）
│   ├── news_frontier.py     # 主流水线入口
│   ├── render_wechat.sh     # 微信格式渲染脚本
│   ├── publish2lark.py      # 飞书发布脚本
│   ├── publish2lark_base.py # 多维表格更新脚本
│   └── push2group.py        # 群机器人推送
├── project-space/            # 核心模块
│   ├── ingest.py
│   ├── filter_rank.py
│   ├── summarize.py
│   ├── assemble.py
│   └── utils/
│       ├── lark_commander.py # Lark 命令封装
│       ├── logger.py         # 统一日志
│       └── ...
├── output/
│   └── {DATE}/
│       ├── briefing.md        # 早报终稿
│       ├── summary.json       # LLM 摘要
│       ├── filtered_ranked.json
│       └── ingested.jsonl
├── references/
│   ├── ai-frontier-daily.example.lobster  # 工作流模板
│   └── PIPELINE.md           # 本文档
└── config/
    └── secrets.json          # 敏感配置
```
