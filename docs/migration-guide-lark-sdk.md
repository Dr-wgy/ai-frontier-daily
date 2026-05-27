# Lark CLI 迁移到 Python SDK 指南

---

## 1. 概述

本项目支持两种飞书 API 调用方式：

| 方式 | 描述 | 适用场景 |
|------|------|----------|
| **Lark CLI** | 通过命令行工具调用 | 开发调试、交互式操作 |
| **Python SDK** | 通过飞书官方 Python SDK 调用 | 生产环境、自动化脚本 |

默认使用 Lark CLI，可通过配置切换到 Python SDK。

---

## 2. 配置文件说明

### 2.1 secrets.json（推荐）

**位置**: `config/secrets.json`

```json
{
  "llm": {
    "api_key": "your_llm_api_key_here",
    "base_url": "https://api.deepseek.com",
    "model_name": "deepseek-chat"
  },
  "feishu": {
    "app_id": "cli_your_app_id_here",
    "app_secret": "your_app_secret_here",
    "user_access_token": "",
    "refresh_token": "",
    "redirect_uri": "https://your-domain.com/callback",
    "bot_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_token_here",
    "space_id": "your_space_id_here",
    "base_token": "your_base_token_here",
    "table_id": "your_table_id_here",
    "chat_id": "oc_your_chat_id_here",
    "use_sdk": false
  }
}
```

### 2.2 配置项详解

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_id` | string | 是 | 飞书应用的 App ID |
| `app_secret` | string | 是 | 飞书应用的 App Secret |
| `use_sdk` | boolean | 否 | `true` 使用 Python SDK，默认 `false` |
| `user_access_token` | string | 否 | 用户访问令牌（OAuth 授权后自动填充） |
| `refresh_token` | string | 否 | 刷新令牌（OAuth 授权后自动填充） |
| `redirect_uri` | string | 否 | OAuth 回调地址 |
| `bot_webhook` | string | 否 | 机器人 Webhook 地址 |
| `space_id` | string | 否 | 知识库空间 ID |
| `base_token` | string | 否 | 多维表格 Base Token |
| `table_id` | string | 否 | 表格 ID |
| `chat_id` | string | 否 | 群组 ID |

---

## 3. 快速开始

### 3.1 步骤 1：创建配置文件

```bash
cp config/secrets.example.json config/secrets.json
```

### 3.2 步骤 2：获取 App ID 和 App Secret

1. 登录 [飞书开放平台](https://open.feishu.cn/)
2. 进入「开发者后台」→「企业自建应用」
3. 创建或选择应用
4. 在「凭证与基础信息」中获取 `app_id` 和 `app_secret`

### 3.3 步骤 3：配置权限

在飞书开放平台为应用添加以下权限：

| 权限名称 | 权限标识 | 说明 |
|----------|----------|------|
| 文档只读 | `docs:document:readonly` | 读取文档 |
| 文档写入 | `docs:document:write` | 创建/更新文档 |
| 多维表格只读 | `bitable:app:readonly` | 读取表格数据 |
| 多维表格写入 | `bitable:app:write` | 创建/更新表格数据 |
| 知识库只读 | `wiki:space:readonly` | 读取知识库 |

### 3.4 步骤 4：启用 Python SDK

```json
{
  "feishu": {
    "use_sdk": true,
    "app_id": "cli_xxx",
    "app_secret": "xxx"
  }
}
```

---

## 4. OAuth 用户授权

### 4.1 什么是 OAuth

某些 API 需要用户级权限（如访问用户个人文档），需要通过 OAuth 获取 `user_access_token`。

### 4.2 使用授权助手

```bash
python project-space/tests/auth_helper.py
```

**操作流程**：
1. 脚本自动打开浏览器跳转到飞书授权页面
2. 登录飞书账号并授权
3. 将浏览器地址栏中的回调 URL 粘贴到命令行
4. 脚本自动保存令牌到 `secrets.json`

### 4.3 CI/CD 集成

```bash
SECRETS_FILE="${PROJECT_ROOT}/config/secrets.json"

if [ ! -f "$SECRETS_FILE" ]; then
    log_warning "未找到 secrets.json，请先根据 secrets.example.json 创建"
else
    HAS_REFRESH_TOKEN=$(python3 -c "import json, sys; d=json.load(open('$SECRETS_FILE')); print(1 if d.get('feishu', {}).get('refresh_token') else 0)" 2>/dev/null || echo 0)
    
    if [ "$HAS_REFRESH_TOKEN" -eq 1 ]; then
        log_success "飞书 SDK 已授权 (已发现 refresh_token)"
    else
        log_warning "未发现 refresh_token，即将运行授权助手..."
        python3 "${PROJECT_ROOT}/project-space/tests/auth_helper.py"
    fi
fi
```

---

## 5. Token 自动刷新机制

SDK 会自动处理 Token 过期问题：

```
┌─────────────────────────────────────────────────────────────┐
│                    Token 刷新流程                          │
├─────────────────────────────────────────────────────────────┤
│  1. 检查 user_access_token 是否即将过期（预留 5 分钟）      │
│                         ↓                                  │
│  2. 如果即将过期且存在 refresh_token                        │
│                         ↓                                  │
│  3. 调用 refresh_access_token API 获取新令牌               │
│                         ↓                                  │
│  4. 更新内存中的 token 和过期时间                          │
│                         ↓                                  │
│  5. 持久化到 secrets.json 文件                            │
│                         ↓                                  │
│  6. 如果 refresh_token 过期，提示重新授权                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 两种方式对比

| 特性 | Lark CLI | Python SDK |
|------|----------|------------|
| 依赖 | 需要安装 lark-cli | 需要安装 lark-oapi |
| 认证方式 | 用户级（--as user） | 应用级（app_id + app_secret） |
| 并发性能 | 较低（进程调用） | 较高（直接 API 调用） |
| 错误处理 | 解析命令行输出 | 结构化错误信息 |
| 日志级别 | 固定 | 可配置（DEBUG/INFO/WARN/ERROR） |
| Token 管理 | 手动管理 | 自动刷新 |
| 适用场景 | 开发调试 | 生产环境 |

---

## 7. 数据格式兼容性

### 7.1 搜索记录

**lark-cli 返回格式**：
```json
{
  "data": {
    "data": [["2026-05-26", "Article 1"], ...],
    "record_id_list": ["rec1", "rec2"],
    "field_id_list": ["fld1", "fld2"]
  }
}
```

**Python SDK 返回格式**（已转换为兼容格式）：
```json
{
  "data": {
    "data": [["2026-05-26", "Article 1"], ...],
    "record_id_list": ["rec1", "rec2"],
    "field_id_list": ["fld1", "fld2"]
  }
}
```

### 7.2 日期字段处理

创建记录时，日期字段会自动转换：

```python
# 输入
"2026-05-26"

# 输出（自动转换为 Unix 时间戳）
1779724800000
```

---

## 8. 故障排除

### 8.1 认证失败

```
{"code": 101001, "msg": "Invalid app_id or app_secret"}
```

**解决方案**：
- 检查 `app_id` 和 `app_secret` 是否正确
- 确保应用已发布上线
- 检查网络连接

### 8.2 权限不足

```
{"code": 101003, "msg": "Permission denied"}
```

**解决方案**：
- 在飞书开放平台为应用添加相应权限
- 确保权限已审批通过

### 8.3 日期字段格式错误

```
Invalid request parameter: 'records[0].fields.date.fieldValue.2026-05-26.fieldName.date'
```

**解决方案**：
- 确保传入 `field_types` 参数指定日期字段
- SDK 会自动将日期字符串转换为时间戳

### 8.4 refresh_token 过期

```
{"code": 20037, "msg": "refresh_token expired"}
```

**解决方案**：
- 重新运行授权助手获取新的 token
```bash
python project-space/tests/auth_helper.py
```

---

## 9. 回滚到 Lark CLI

如需回滚，只需修改配置：

```json
{
  "feishu": {
    "use_sdk": false
  }
}
```

---

## 10. 相关文件

| 文件 | 说明                             |
|------|--------------------------------|
| `config/secrets.json` | 敏感配置（app_id、app_secret、token 等） |
| `config/secrets.example.json` | secrets.json 模板                |
| `project-space/utils/lark_sdk_commander.py` | SDK 命令实现（包含 LarkClient）        |
| `project-space/utils/lark_commander.py` | CLI 命令实现（兼容层）                  |
| `project-space/tests/auth_helper.py` | OAuth 授权助手脚本，详见 [OAuth 配置指南](file:///Users/guanyu.wu/IdeaProjects/ai-frontier-daily/project-space/docs/oauth-setup-guide.md) |

---

**版本**: 2.0  
**日期**: 2026-05-26  
**适用版本**: ai-frontier-daily v2.0+
