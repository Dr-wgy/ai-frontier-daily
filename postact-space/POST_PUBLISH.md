# 发布后流程（Post-Publish Workflow）

> 本文档描述早报脚本成功执行后的标准发布流程，可独立于主流水线使用。
> 主流水线说明参见 [SKILL.md](./SKILL.md)。

---

## 1. 飞书知识库发布

**发布前必读**：Agent 必须完整读取 `output/<DATE>/briefing.md` 文件，不要用摘要或对话复述代替全文发布。

**同名去重**：目标路径下标题 `AI 前沿早报（YYYY-MM-DD）` 只保留一篇，已存在则覆盖。

检索已有文档：
```bash
DATE='YYYY-MM-DD'
SPACE_ID='your_space_id'      # 由大模型根据上下文判断
PARENT_TOKEN='your_parent_token'  # 由大模型根据上下文判断
lark-cli wiki nodes list --as user \
  --params "{\"space_id\":\"${SPACE_ID}\",\"parent_node_token\":\"${PARENT_TOKEN}\",\"page_size\":50}" \
  --page-all \
  -q ".data.items[] | select(.title | contains(\"AI 前沿早报（${DATE}）\")) | {title, node_token, obj_edit_time}"
```

**新建并归档**（未命中时执行）：

| 顺序 | 动作 |
|------|------|
| 1 | `lark-cli docs +create --as user --doc-format markdown --content "# 占位"` → 得到文档 `TOKEN` |
| 2 | `lark-cli docs +update --as user --doc $TOKEN --mode overwrite --new-title "AI 前沿早报（$DATE）" --markdown - < 早报文件路径` |
| 3 | `lark-cli wiki +move --as user --obj-type docx --obj-token $TOKEN --target-space-id "$SPACE_ID" --target-parent-token "$PARENT_TOKEN"` |
| 4 | 返回文档链接给用户 |

**参数说明**：
- 文档标题：`AI 前沿早报（YYYY-MM-DD）`
- `space_id` / `parent_node_token`：由大模型根据对话上下文判断（非硬编码）
- 账号模式：`--as user`（勿用 Bot token）

---

## 2. 群机器人 Webhook 推送

发布完成后必须向群内推送交互式卡片通知：

```bash
cd /Users/huangxingbiao/.qclaw/skills/ai-frontier-daily
python3 project-space/push_feishu_bot.py \
  --date "YYYY-MM-DD" \
  --doc-url "https://xxx.feishu.cn/…"
```

**说明**：
- 从 `config/secrets.json` 的 `feishu.bot_webhook` 字段自动读取 Webhook
- 推送内容包含早报标题、各模块摘要（来自 `summary.json`）和「立即查看」按钮

---

## 3. 流程小结

| 步骤 | 动作 |
|------|------|
| 1 | 读取终稿确认内容 |
| 2 | 发布到飞书知识库 |
| 3 | 群机器人 Webhook 推送 |
| 4 | 返回文档链接给用户 |
