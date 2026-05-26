# AI 前沿早报流水线 - 工作流说明

> 本文档描述工作流的步骤设计、内部流程及数据流向。
> 工作流分为**核心链路**（必执行）和**分发链路**（按需启用）两部分。

---

## 1. 工作流总览

```
┌─────────────────────────────────────────────────────────────┐
│  核心链路（必执行）                                           │
│                                                             │
│  cleanup ──▶ news_frontier                                  │
│                │                                            │
│                ├── ingest ──▶ ingested.jsonl                │
│                ├── filter_rank ──▶ filtered_ranked.json     │
│                ├── summarize ──▶ summary.json               │
│                └── assemble ──▶ briefing-feishu.md          │
│                           └──▶ briefing-wechat.html         │
│                           └──▶ redbook/*.html               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  分发链路（按需启用，由 Lobster 配置决定）                     │
│                                                             │
│  briefing-feishu.md ──▶ publish2lark ──▶ 飞书知识库文档       │
│                              │                              │
│                              ▼                              │
│                        push2group ──▶ 飞书群卡片               │
│                                                             │
│  briefing-wechat.html ──▶ render_wechat ──▶ 微信公众号排版     │
│                                                             │
│  redbook/*.html ──▶ screenshot_redbook ──▶ redbook-png/*.png │
│                                                             │
│  summary.json ──▶ publish2lark_base ──▶ 多维表格记录          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 核心链路（必执行）

### Step 0: `cleanup`

**功能**：清理临时文件，保障每次运行环境干净

**说明**：删除上一次运行遗留的中间文件，避免脏数据干扰

---

### Step 1: `news_frontier`

**功能**：执行主流水线，完成 AI 前沿早报的采集、筛选、摘要、拼版

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
| `assemble` | `AssembleModule` | `summary.json` | 多平台产物 | 拼版渲染，产出飞书/微信/小红书三套内容 |

**assemble 输出**：

| 平台 | 产物 | 说明 |
|------|------|------|
| 飞书 | `briefing-feishu.md` | Markdown 格式，用于飞书知识库发布 |
| 微信 | `briefing-wechat.html` | HTML 格式，用于微信公众号排版 |
| 小红书 | `redbook/*.html` | 独立卡片 HTML，用于后续截图 |

**数据产物**：

| 文件 | 用途 |
|------|------|
| `output/{DATE}/ingested.jsonl` | 原始采集条目 |
| `output/{DATE}/filtered_ranked.json` | 筛选排序中间产物 |
| `output/{DATE}/summary.json` | LLM 摘要结果（结构化数据） |
| `output/{DATE}/briefing-feishu.md` | 飞书早报终稿 |
| `output/{DATE}/briefing-wechat.html` | 微信公众号 HTML |
| `output/{DATE}/redbook/*.html` | 小红书卡片源文件 |

---

## 3. 分发链路（按需启用）

分发链路由 Lobster 工作流配置决定，可按需增删。每个分发 step 独立运行，互不依赖（除 `push2group` 依赖 `publish2lark` 输出的文档链接外）。

### 3.1 飞书知识库发布

**脚本**：`scripts/publish2lark.py`

**功能**：将早报发布到飞书知识库，按月份自动归档

**输入**：`output/{DATE}/briefing-feishu.md`

**内部流程**：
```
find_or_create_month_folder ──▶ 查找/创建 YYYY-MM 文件夹
    │
    ▼
check_output ──▶ 验证早报文件存在
    │
    ▼
clean_duplicates ──▶ 同名文档移入回收站
    │
    ▼
publish ──▶ 创建节点 + 写入内容
    │
    ▼
输出文档 URL（stdout）
```

**配置**：`config/secrets.json` → `feishu.space_id`

---

### 3.2 飞书群推送

**脚本**：`scripts/push2group.py`

**功能**：向飞书群推送交互式卡片通知

**输入**：
- 文档 URL（来自 `publish2lark` 的 stdout）
- `output/{DATE}/summary.json`（早报摘要）

**卡片内容**：标题 + 各模块摘要 + 热度标识（🔥）+ 「立即查看」按钮

**配置**：`config/secrets.json` → `feishu.bot_webhook`

---

### 3.3 微信公众号渲染

**脚本**：`scripts/render_wechat.sh`

**功能**：将 Markdown 早报转为微信公众号兼容的 HTML 排版

**输入**：`output/{DATE}/briefing-feishu.md`

**输出**：渲染后的 HTML（用于第三方公众号编辑器导入）

---

### 3.4 小红书卡片截图

**脚本**：`scripts/screenshot-redbook.js`

**功能**：批量将小红书卡片 HTML 截图为 PNG 图片

**输入**：`output/{DATE}/redbook/*.html`

**输出**：`output/{DATE}/redbook-png/*.png`

**流程**：
```
打开 HTML ──▶ 检测卡片类型 ──▶ 获取卡片尺寸
    │
    ▼
设置视口（宽 450px，高自适应）──▶ 刷新页面
    │
    ▼
截图（quality 95）──▶ 保存 PNG
```

---

### 3.5 多维表格更新

**脚本**：`scripts/publish2lark_base.py`

**功能**：将早报数据写入飞书多维表格

**输入**：`output/{DATE}/summary.json`

**内部流程**：
```
create_base_if_not_exists ──▶ 创建/查找多维表格
    │
    ▼
create_table_if_not_exists ──▶ 创建/查找数据表
    │
    ▼
sync_fields ──▶ 同步字段定义
    │
    ▼
delete_today_records ──▶ 删除当天旧记录
    │
    ▼
upload_records ──▶ 批量上传新记录
    │
    ▼
输出表格 URL（stdout）
```

---

## 4. 数据流图

```
RSS 源
  │
  ▼
┌──────────────────────────────────────────┐
│ 核心链路：news_frontier.py               │
│                                          │
│  ingest ──▶ ingested.jsonl               │
│     │                                    │
│     ▼                                    │
│  filter_rank ──▶ filtered_ranked.json    │
│     │                                    │
│     ▼                                    │
│  summarize ──▶ summary.json              │
│     │                                    │
│     ▼                                    │
│  assemble ──┬─▶ briefing-feishu.md       │
│             ├─▶ briefing-wechat.html      │
│             └─▶ redbook/*.html            │
└──────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────┐
│ 分发链路（按需启用）                       │
│                                          │
│  briefing-feishu.md ──▶ publish2lark     │
│                            │             │
│                            ▼             │
│                       push2group          │
│                                          │
│  briefing-wechat.html ──▶ render_wechat  │
│                                          │
│  redbook/*.html ──▶ screenshot_redbook   │
│                                          │
│  summary.json ──▶ publish2lark_base      │
└──────────────────────────────────────────┘
```

---

## 5. 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SKILL_DIR` | 项目根目录 | `ai-frontier-daily` |
| `args.date` | 早报日期参数 | `$(date +%Y-%m-%d)` |

---

## 6. 配置文件

**路径**：`config/secrets.json`

| 字段 | 说明 |
|------|------|
| `llm.api_key` | LLM API Key |
| `llm.base_url` | LLM API 基础 URL |
| `llm.model_name` | LLM 模型名称 |
| `feishu.space_id` | 飞书知识库 Space ID |
| `feishu.bot_webhook` | 群机器人 Webhook 地址 |

---

## 7. 目录结构

```
ai-frontier-daily/
├── scripts/
│   ├── base/
│   │   ├── init_env.sh          # 环境初始化（首次使用运行）
│   │   └── run.sh               # 环境启动器（cd + venv + SSL + exec 透传）
│   ├── news_frontier.py         # 核心链路入口
│   ├── render_wechat.sh         # [分发] 微信公众号渲染
│   ├── publish2lark.py          # [分发] 飞书知识库发布
│   ├── publish2lark_base.py     # [分发] 多维表格更新
│   ├── push2group.py            # [分发] 群机器人推送
│   └── screenshot-redbook.js    # [分发] 小红书卡片截图
├── project-space/               # 核心模块
│   ├── ingest.py
│   ├── filter_rank.py
│   ├── summarize.py
│   ├── assemble.py
│   └── utils/
│       ├── lark_commander.py    # Lark 命令封装
│       ├── base_config.py       # 模板与文件名常量
│       └── ...
├── output/
│   └── {DATE}/
│       ├── briefing-feishu.md       # 飞书早报终稿
│       ├── briefing-wechat.html     # 微信公众号 HTML
│       ├── summary.json             # LLM 摘要
│       ├── filtered_ranked.json     # 筛选中间产物
│       ├── ingested.jsonl           # 原始采集条目
│       ├── redbook/                 # 小红书卡片源文件
│       │   ├── card-001.html
│       │   └── ...
│       └── redbook-png/             # 小红书卡片截图
│           ├── card-001.png
│           └── ...
├── references/
│   ├── ai-frontier-daily.lobster    # 工作流配置
│   └── PIPELINE.md                  # 本文档
└── config/
    ├── secrets.json                 # 敏感配置（gitignore）
    └── config.yaml                  # 业务配置
```
