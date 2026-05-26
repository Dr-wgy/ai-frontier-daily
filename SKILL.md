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
./scripts/base/init_env.sh

# 配置 secrets.json
cp config/secrets.example.json config/secrets.json
# 编辑 secrets.json 填入实际配置
```

## 2. Lobster 工作流

> ⚠️ **必须严格使用 lobster 工具执行**，不可直接运行单个脚本文件或 shell 命令。
>
> `lobster` 是 OpenClaw 的内置工具（tools），用于编排和运行多步骤工作流。

### 执行方式

调用 lobster 工具，参数如下：

| 参数 | 值 | 说明 |
|------|-----|------|
| `action` | `'run'` | 执行工作流 |
| `pipeline` | `<skill-path>/references/ai-frontier-daily.lobster` | 工作流文件路径 |
| `timeoutMs` | `300000` | 超时时间 5 分钟（采集 + LLM 调用耗时较长，不可设太短） |

**示例**：
```
lobster({
  action: 'run',
  pipeline: '<skill-path>/references/ai-frontier-daily.lobster',
  timeoutMs: 300000
})
```

### 注意事项

- **超时时间**：必须设置 `timeoutMs >= 300000`（5 分钟），默认超时可能不足以完成 LLM 摘要步骤
- **不可中断**：工作流运行期间不要发送新消息，等待工具返回结果
- **产物读取**：完成后从工具返回结果中提取飞书文档链接和多维表格链接
- **日期参数**：工作流内部使用 `$(date +%Y-%m-%d)` 自动获取当天日期，无需额外传入

## 3. 产物

### 确定产出

| 文件 | 职责 |
|------|------|
| `output/<DATE>/ingested.jsonl` | 原始采集条目 |
| `output/<DATE>/filtered_ranked.json` | 筛选排序中间产物 |
| `output/<DATE>/summary.json` | LLM 摘要（结构化数据） |

### 可选产出（由 Lobster 工作流配置决定）

后续分发环节按需启用，详见 [references/PIPELINE.md](./references/PIPELINE.md)：

| 分发渠道 | 产物 | 对应脚本 |
|----------|------|----------|
| 飞书知识库 | `briefing-feishu.md` → 在线文档 | `publish2lark.py` |
| 微信公众号 | `briefing-wechat.html` | `render_wechat.sh` |
| 小红书 | `redbook/*.html` → `redbook-png/*.png` | `screenshot-redbook.js` |
| 飞书多维表格 | Base 记录 | `publish2lark_base.py` |
| 群机器人 | 交互式卡片 | `push2group.py` |

## 4. 脚本说明

工作流分为**核心链路**（必执行）和**分发链路**（按需启用），详见 [references/PIPELINE.md](./references/PIPELINE.md)。

### 核心脚本（必执行）

| 脚本 | 功能 |
|------|------|
| `scripts/base/init_env.sh` | 环境初始化（首次使用运行） |
| `scripts/base/run.sh` | 环境启动器（cd + venv + SSL + exec 透传） |
| `scripts/news_frontier.py` | 主流水线（ingest → filter_rank → summarize → assemble） |

### 分发脚本（按需启用）

| 脚本 | 功能 | PIPELINE 章节 |
|------|------|---------------|
| `scripts/publish2lark.py` | 飞书知识库发布（月份自动归档 + 同名去重） | §3.1 |
| `scripts/push2group.py` | 群机器人交互式卡片推送 | §3.2 |
| `scripts/render_wechat.sh` | 微信公众号排版渲染 | §3.3 |
| `scripts/screenshot-redbook.js` | 小红书卡片批量截图 | §3.4 |
| `scripts/publish2lark_base.py` | 多维表格记录更新 | §3.5 |

## 5. 配置

**secrets.json**（gitignore）：

| 字段 | 说明 |
|------|------|
| `llm.api_key` | LLM API 认证 |
| `feishu.app_id` | 飞书应用 App ID |
| `feishu.app_secret` | 飞书应用 App Secret |
| `feishu.bot_webhook` | 群机器人 Webhook |
| `feishu.space_id` | 知识库 Space ID |
| `feishu.base_token` | 多维表格 Token（可选） |
| `feishu.table_id` | 数据表 ID（可选） |
| `feishu.chat_id` | 群聊 ID（可选） |

**飞书应用权限要求**：
- `wiki:wiki:readonly` - 获取知识库节点列表
- `wiki:wiki` - 创建和移动知识库节点
- `docx:document` - 创建和更新文档
- `bitable:app` - 创建多维表格
- `bitable:record` - 管理记录
- `im:message` - 发送消息

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
