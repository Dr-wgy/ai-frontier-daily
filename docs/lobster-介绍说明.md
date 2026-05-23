# 🦞 OpenClaw Lobster 工作流引擎指南

## 一、 Lobster 基础介绍

**Lobster** 是 OpenClaw 网关内嵌的一款轻量级工作流编排工具。它的核心设计哲学是 **"Small CLI + JSON Pipes"（小型命令行 + JSON 管道）**。

### 1. 核心目标
将多步骤的工具调用序列，打包成**一次确定性调用**，并内置审批机制和可恢复状态，从而让 AI Agent 能够安全、低成本地执行复杂任务。

### 2. 解决的核心痛点
* **降本增效**：将复杂工作流封装为一次调用，大幅减少 LLM 的 Token 消耗。
* **安全可控**：内置人工审批（Human-in-the-loop）机制，拦截高危副作用操作（如发邮件、删库）。
* **断点恢复**：流程中断后无需重头执行，通过 `resumeToken` 即可从暂停点继续。

### 3. 核心工作原理
```text
🔄 OpenClaw 触发 Lobster 引擎
   ↓
📦 解析 .lobster 配置文件 (YAML/JSON)
   ↓
⚙️ 按顺序执行 CLI 命令管道，传递 JSON 数据
   ↓
⏸️ 遇到 approval 节点 -> 冻结状态 -> 返回 resumeToken
   ↓
✅ 外部审批通过 -> resume 恢复执行 -> 返回最终 JSON 信封
```

---

## 二、 `.lobster` 配置文件语法详解

`.lobster` 文件采用 YAML 格式，是一种声明式的领域特定语言（DSL）。

### 1. 顶层核心结构
```yaml
name: string        # 必填：工作流唯一标识（如 ai-frontier-daily）
description: string # 可选：工作流描述
env: object         # 可选：全局环境变量注入
args: object        # 可选：定义接收的外部参数
steps: array        # 必填：按顺序执行的步骤列表
```

### 2. 参数传递 (`args`)
允许工作流接收外部变量，提高复用性。
```yaml
args:
  date:
    default: $(date +%Y-%m-%d) # 支持 Shell 命令作为默认值
  limit:
    default: 10
```
*触发方式*：在调用时通过 `argsJson: "{\"date\":\"2026-05-23\"}"` 覆盖默认值。在步骤中通过 `$args.date` 引用。

### 3. 步骤编排 (`steps`)
每个 Step 包含以下关键属性：

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :---: | :--- |
| `id` | string | ✅ | 步骤唯一 ID，用于后续引用（如 `$collect`）。 |
| `command` | string | ✅ | 要执行的 Shell 命令或 CLI 工具。 |
| `stdin` | string | ❌ | 数据管道。将之前步骤的输出作为当前命令的标准输入。 |
| `approval` | string | ❌ | 设为 `required` 时，流程暂停等待人工审批。 |
| `condition` | string | ❌ | 条件执行门控。如 `$step.approved` 或 `!$step.approved`。 |

### 4. 数据流转的两种模式（核心）

#### 模式 A：纯管道流 (适合线性、单一数据流)
利用 `stdin` 将上一步的 `stdout` 直接喂给下一步。
```yaml
- id: fetch
  command: curl -s api.example.com/data.json
- id: process
  command: jq '.items'
  stdin: $fetch.stdout  # 数据在内存中流转，不落盘
```

#### 模式 B：纯文件流 (适合多对一汇聚、复杂状态管理) ⭐推荐
利用重定向 `>` 写文件，`cat` 读文件。完美解决 `stdin` 只能接收一个前置步骤的限制。
```yaml
- id: task_a
  command: bash -c 'python a.py > $SKILL_DIR/tmp/a_result.txt'
- id: task_b
  command: bash -c 'python b.py > $SKILL_DIR/tmp/b_result.txt'
- id: final_report
  # 轻松汇聚两个不同步骤的输出
  command: bash -c 'echo "A: $(cat $SKILL_DIR/tmp/a_result.txt), B: $(cat $SKILL_DIR/tmp/b_result.txt)"'
```

---

## 三、 工程实践：注意事项与最佳建议

### 1. 路径安全：永远不要假设当前工作目录 (CWD)
直接使用 `./run.sh` 等相对路径极易因引擎触发位置不同而报错。
* **最佳实践**：在 `env` 中定义全局根目录变量，并在所有命令中使用绝对路径。
```yaml
env:
  SKILL_DIR: $HOME/.qclaw/skills/ai-frontier-daily
steps:
  - id: run_task
    command: $SKILL_DIR/run.sh python main.py
```

### 2. 环境隔离：使用通用 Wrapper 脚本 (`run.sh`)
不要在 `.lobster` 中写冗长的环境准备代码（如激活 venv、导出证书）。将其封装到 `run.sh` 中，并使用 `exec "$@"` 透传命令。
```bash
#!/bin/bash
cd "$(dirname "$0")" || exit
[ -f ".venv/bin/activate" ] && source .venv/bin/activate
export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())" 2>/dev/null)
# 核心魔法：完美透传任意命令、保留参数边界、传递退出码
exec "$@" 
```
*在 `.lobster` 中调用*：`command: $SKILL_DIR/run.sh python script.py`

### 3. 命令执行机制：何时使用 `bash -c '...'`
Lobster 底层默认使用 `exec` 直接执行程序。如果命令中包含 Shell 特有语法，**必须**使用 `bash -c` 召唤 Shell 解释器。

| 包含以下语法时 | 必须使用 `bash -c`？ | 示例 |
| :--- | :---: | :--- |
| 仅可执行文件+普通参数 | ❌ 不需要 | `python main.py --port 80` |
| 重定向 (`>`, `>>`) | ✅ **必须** | `echo "log" > app.log` |
| 管道 (`\|`) | ✅ **必须** | `cat data.json \| jq '.'` |
| 逻辑控制 (`&&`, `\|\|`) | ✅ **必须** | `make build && make test` |
| 变量赋值/读取 (`=`, `$VAR`) | ✅ **必须** | `URL=$(cat file) && echo $URL` |

⚠️ **引号陷阱**：使用 `bash -c` 时，**最外层强烈建议使用单引号 `'`**，防止外层系统过早解析内部的 `$VAR` 或 `$(cmd)`。

### 4. 临时文件管理
如果使用“纯文件流”模式，务必在 `steps` 的最开始增加一个清理步骤，防止旧数据干扰。
```yaml
- id: cleanup
  command: bash -c 'mkdir -p $SKILL_DIR/tmp && rm -f $SKILL_DIR/tmp/*.txt'
```

---

## 四、 扩展延伸知识点

### 1. 底层利器：`tee` 命令 (数据分流器)
`tee` 从 stdin 读取数据，同时输出到 stdout 和文件。在混合流模式中，常用于“既要把数据传给下一步，又要存一份留作最终汇总”。
```bash
# 数据既会顺着管道流给 jq，又会保存到 raw.json
curl -s api.com | tee raw.json | jq '.'
```

### 2. Shell 技巧：`$(cat)` 读取标准输入
在 `bash -c` 中，使用 `VAR=$(cat)` 是接收管道（stdin）数据的黄金法则。
* **对比 `read VAR`**：`$(cat)` 能完美读取**多行文本**（如完整的 JSON），且不受 Bash `IFS` 分隔符的影响，比 `read` 更安全、更彻底。
```bash
# 将 stdin 中的多行 JSON 完整赋值给 DATA 变量
DATA=$(cat) && python process.py --payload "$DATA"
```

### 3. 真实世界的同类工具参考
Lobster 的设计吸收了业界优秀的编排理念。如果您想进一步深入学习工作流编排，可以参考以下真实存在的开源/商业产品官方文档：
* **GitHub Actions**：学习其 YAML 语法、`steps` 设计和上下文变量传递。
* **Temporal.io**：学习其极强的状态恢复能力、长时运行工作流和 Signal（类似审批）机制。
* **Dagger (dagger.io)**：学习其将复杂 CI/CD 管道封装为代码、强调管道和容器化执行的理念。
* **Prefect / Airflow**：学习 Python 生态下的数据管道编排和 DAG（有向无环图）依赖管理。