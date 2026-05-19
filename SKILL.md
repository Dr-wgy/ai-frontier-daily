---
name: ai-frontier-daily
description: >-
  每日 AI 前沿早报流水线：自动采集 RSS → LLM 摘要 → 渲染早报 Markdown → 飞书发布 + 群机器人 Webhook。
  工作流通过 Lobster 编排，所有参数由脚本从 config/secrets.json 自动读取。
disable-model-invocation: true
---

# AI 前沿早报（执行手册）

## 1. 首次使用

```bash
# 运行环境初始化脚本
./scripts/init_env.sh

# 配置 secrets.json
cp config/secrets.example.json config/secrets.json
# 编辑 secrets.json 填入实际配置
```

## 2. Lobster 工作流

> ⚠️ **必须严格使用 lobster 工具执行**，不可直接运行单个脚本文件。

```bash
lobster({ filePath: "<skill-path>/references/ai-frontier-daily.lobster" })
```

**步骤**：`news_frontier` → `render_wechat` → `publish2lark` → `push2group` → `final_report`

## 3. 产物

| 文件 | 职责 |
|------|------|
| `output/<DATE>/briefing.md` | 早报终稿 |
| `output/<DATE>/summary.json` | LLM 摘要（机器人推送用） |
| `output/<DATE>/filtered_ranked.json` | 筛选排序中间产物 |
| `output/<DATE>/ingested.jsonl` | 原始采集条目 |

## 4. 脚本说明

| 脚本 | 功能 |
|------|------|
| `scripts/init_env.sh` | 环境初始化（首次使用运行） |
| `scripts/news_frontier.py` | 主流水线（ingest → filter_rank → summarize → assemble） |
| `scripts/render_wechat.sh` | 微信公众号排版渲染 |
| `scripts/publish2lark.sh` | 飞书知识库发布（月份自动归档 + 同名去重） |
| `scripts/push2group.py` | 群机器人交互式卡片推送 |

详细流程见 [references/PIPELINE.md](./references/PIPELINE.md)。

## 5. 配置

**secrets.json**（gitignore）：

| 字段 | 说明 |
|------|------|
| `llm.api_key` | LLM API 认证 |
| `feishu.bot_webhook` | 群机器人 Webhook |
| `feishu.space_id` | 知识库 Space ID |
| `feishu.root_parent_token` | 知识库根目录 Token |

**业务配置**：`project-space/config/config.yaml`（可提交 Git）

## 6. 安全说明

- 敏感信息存储在 `config/secrets.json`，已加入 gitignore
- 不可将 secrets 内容暴露在对话、日志或注释中

## 7. 何时启用

| 场景 | 处理 |
|------|------|
| 每日定时 | ❌ 不需要，cron 自动执行 |
| 异常排查 | ✅ Agent 介入检查 |
| 补跑历史 | ✅ Agent 执行 |
| 手动撰写 | ❌ 不支持 |
