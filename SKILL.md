---
name: ai-frontier-daily
description: >-
  每日 AI 前沿早报流水线：自动采集 RSS → LLM 摘要 → 渲染早报 Markdown → 飞书发布 + 群机器人 Webhook。
  这是一个定时任务 Skill，通过 cron 自动执行，无需用户主动触发。
disable-model-invocation: true
---

# AI 前沿早报（执行手册）

---

## 0. 前置环境准备（首次使用必看）

### 0.1 确认 Python 与 pip 路径

每个人环境的 Python/pip 路径可能不同，请先确认：

```bash
# 检查 Python 版本
which python3
python3 --version

# 检查 pip 版本
which pip3
pip3 --version
```

### 0.2 安装项目依赖

```bash
cd ~/.qclaw/skills/ai-frontier-daily
pip3 install -r requirements.txt
```

### 0.3 安装 lark-cli

```bash
# 安装（如未安装）
brew install lark-cli

# 初始化配置
lark-cli config init --new

# 登录授权（用于 --as user 操作）
lark-cli auth login
```

**验证安装：**
```bash
lark-cli --version
lark-cli docs +create --as user --doc-format markdown --content "# 占位"
```

---

## 1. 何时启用 / 何时不用

| 场景 | 处理方式 |
|------|----------|
| **每日定时运行** | 不需要 Agent 介入，cron 自动执行 |
| **异常排查** | 日志显示失败，需 Agent 介入检查 |
| **指定日期补跑** | 用户说「重跑5月9日」，Agent 介入执行 |
| **手动撰写早报** | ❌ 不支持，内容由脚本生成 |
| **非 AI 类新闻汇总** | ❌ 不支持，本流水线仅处理 AI 前沿 |

---

## 2. 执行命令

### 2.1 一键执行（正常流程）

```bash
cd ~/.qclaw/skills/ai-frontier-daily
python3 project-space/pipeline.py --date "YYYY-MM-DD"
```

- 默认执行全部步骤：`ingest` → `filter_rank` → `summarize` → `assemble`
- 产物路径：`output/<DATE>/briefing.md`

### 2.2 分步执行（排错）

```bash
cd ~.qclaw/skills/ai-frontier-daily
python3 project-space/pipeline.py --steps ingest
python3 project-space/pipeline.py --steps filter_rank
python3 project-space/pipeline.py --steps summarize
python3 project-space/pipeline.py --steps assemble
```

### 2.3 补跑历史日期

```bash
# 例如重跑 5 月 9 日
python3 project-space/pipeline.py --date "2026-05-09"
```

---

## 3. 产物说明

| 文件 | 职责 | 必读 |
|------|------|------|
| `output/<DATE>/briefing.md` | 对外发布的终稿 | ✅ 是 |
| `output/<DATE>/summary.json` | LLM 合并结果，用于飞书机器人推送 | 发布时需要 |
| `output/<DATE>/filtered_ranked.json` | 筛选排序后的中间产物 | 排错时用 |
| `output/<DATE>/ingested.jsonl` | 原始采集条目 | 排错时用 |

---

## 4. 发布后流程（标准执行）

脚本成功后，按 **[POST_PUBLISH.md](./POST_PUBLISH.md)** 执行完整的发布后流程，包括：

1. 飞书知识库发布（同名去重 + 新建归档）
2. 群机器人 Webhook 推送

> 详细步骤、命令参数及注意事项见 [POST_PUBLISH.md](./POST_PUBLISH.md)。

---

## 5. 配置说明

所有配置分为两类：

| 配置类型 | 位置 | 是否可提交 Git |
|----------|------|----------------|
| **业务配置**（RSS 源、模块、去重策略等） | `project-space/config/config.json` | ✅ 是 |
| **敏感信息**（API Key、Webhook） | `config/secrets.json` | ❌ 否（已 gitignore） |
| **发布目标**（知识库 space_id、parent_token） | 对话上下文 | 由大模型自行判断 |

---

## 6. 异常速查

| 现象 | 建议 |
|------|------|
| 脚本非 0 退出 | 检查虚拟环境、依赖完整性；查看 stderr |
| `ingested.jsonl` 为空 | 当日源站无命中或网络失败；告知用户「暂无采集结果」 |
| `filter_rank` 失败 | 检查 `config/secrets.json` 中的 LLM 配置 |
| `summarize` 失败 | 检查 `config/secrets.json` 中的 LLM 配置；修复后重跑 |
| 无早报文件 | 按 §2.2 分步执行，定位中断步骤 |
| 飞书发布失败 | 确认大模型已正确识别目标知识库（space_id、parent_node_token）|
| Webhook 推送失败 | 检查 `config/secrets.json` 中的 `feishu.bot_webhook` |

---

## 7. 安全与敏感信息

| 配置项 | 用途 | 所在文件 |
|--------|------|----------|
| `llm.api_key` | LLM API 认证 | `config/secrets.json`（gitignore） |
| `feishu.bot_webhook` | 飞书群机器人推送 | `config/secrets.json`（gitignore） |
| 知识库 `space_id` / `parent_node_token` | 飞书知识库发布目标 | 大模型根据对话上下文自行判断 |
