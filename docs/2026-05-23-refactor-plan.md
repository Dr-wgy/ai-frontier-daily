# AI 前沿早报项目重构计划

> 创建日期：2026-05-23
> 状态：待执行

---

## 概览

| # | 改造点 | 说明 | 涉及文件数 | 子任务数 | 依赖 |
|---|--------|------|-----------|----------|------|
| 1 | SummaryCluster 归置到 domain.py | 将 LLM 摘要后的新闻集群模型从业务脚本移至领域模型层 | 2 | 3 | 无 |
| 2 | Logger 工具化改造 | 统一日志模块，标准化路径和格式，消除各脚本重复实现 | 8 | 7 | 无 |
| 3 | 抽象 LarkCommander 命令执行器 | 封装 lark-cli 命令为链式调用对象，消除命令拼接和 subprocess 调用 | 4 | 5 | 第 2 点 |
| 4 | 提示词元信息简化 | 移除 LLM 不使用的冗余字段，减少 prompt token 消耗 | 4 | 4 | 无 |
| 5 | .lobster 工作流配置优化 | 环境配置抽离、全局参数定义、step 间文件传递，提升路径安全性 | 3 | 3 | 无 |
| 6 | 脚本路径调整 + 文档同步 | 同步更新 SKILL.md 等文档中的脚本路径引用，保持文档与代码一致 | 2 | 2 | 第 5 点 |

**执行顺序建议**：1 → 2 → 3 → 4 → 5 → 6（2 是 3 的前置依赖，5 是 6 的前置依赖）

---

## 第 1 点：SummaryCluster 归置到 domain.py

### 现状

- `SummaryCluster` 定义在 `summarize.py` 中（L15-60），是一个 LLM 摘要后的新闻集群包装类
- `domain.py` 中已有 `NewsCluster`、`SummaryItem` 等数据模型

### 判断

`SummaryCluster` 是 domain 模型，封装了 `NewsCluster` + LLM 返回数据，属于业务领域对象，应归置到 `domain.py`。

### 改造内容

- [ ] 1.1 将 `SummaryCluster` 类从 `summarize.py` 移动到 `domain.py`
  - 位置：放在 `NewsCluster` 类之后
  - 保持类定义不变，只改文件位置
- [ ] 1.2 在 `summarize.py` 中更新导入
  - 改为 `from utils.domain import SummaryCluster`
  - 删除原有的 `SummaryCluster` 类定义
- [ ] 1.3 检查是否有其他文件引用 `SummaryCluster`，同步更新导入路径
  - 搜索范围：`project-space/` 和 `scripts/`

---

## 第 2 点：Logger 工具化改造

### 现状

| 文件 | 日志方式 | 日志路径 |
|------|----------|----------|
| `work_module.py` | `self.log()` 同时写文件+stdout | `project-space/logs/{name}_{date}.log` |
| `push2group.py` | 独立 `_setup_logger()` | `output/{date}/tmp_push2group.log` |
| `publish2lark_base.py` | 独立 logger 设置 | `output/{date}/tmp_base.log` |
| `publish2lark.py` | 继承 `WorkModule.log()` | `project-space/logs/publish2lark_{date}.log` |

### 目标

- 新建统一的 `logger.py` 工具模块
- 日志路径统一为 `output/{date}/run.log`（一个日期下所有日志写入同一个文件）
- 通过日志格式中的 `%(name)s` 区分不同模块的日志
- 删除 `project-space/logs/` 目录
- 所有脚本都依赖 `get_logger()` 函数

### 改造内容

- [ ] 2.1 新建 `project-space/utils/logger.py`
  ```python
  import logging
  from pathlib import Path
  
  def get_logger(name: str, date: str) -> logging.Logger:
      """获取日志记录器
      
      Args:
          name: 模块名称（如 'publish2lark', 'push2group'），用于日志格式中标识来源
          date: 日期字符串（YYYY-MM-DD）
      
      Returns:
          配置好的 Logger 实例
      
      日志路径：output/{date}/run.log（所有模块共用一个文件，通过 name 区分）
      """
      project_root = Path(__file__).parent.parent.parent
      log_dir = project_root / 'output' / date
      log_dir.mkdir(parents=True, exist_ok=True)
      log_file = log_dir / 'run.log'
      
      logger = logging.getLogger(name)
      logger.setLevel(logging.INFO)
      logger.handlers.clear()
      
      handler = logging.FileHandler(log_file, encoding='utf-8')
      handler.setFormatter(logging.Formatter(
          '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s',
          datefmt='%Y-%m-%d %H:%M:%S'
      ))
      logger.addHandler(handler)
      
      return logger
  ```

- [ ] 2.2 改造 `project-space/utils/work_module.py`
  - 移除 `self.log()` 方法
  - 移除 `_log_file` 属性和 `_get_log_file()` 方法
  - 在 `__init__` 中改为：
    ```python
    from utils.logger import get_logger
    
    class WorkModule(ABC):
        def __init__(self, name: str, date: str = None):
            self.name = name
            self.date = date
            self.logger = get_logger(name, date) if date else None
            self._config_loaded = False
    ```
  - 保留 `load_jsonl/save_jsonl/load_json/save_json/clip_text` 等静态工具方法
  - 注意：`WorkModule` 的子类需要传入 `date` 参数

- [ ] 2.3 改造 `scripts/push2group.py`
  - 删除 `_setup_logger()` 函数和 `_LOG_FILE_NAME` 常量
  - 删除 `import logging`（如果不再需要）
  - 改为 `from utils.logger import get_logger`
  - `main()` 中：
    ```python
    logger = get_logger('push2group', args.date)
    ```
  - 移除 `FeishuBotPusher.__init__` 中的 `logger` 参数，改为内部初始化

- [ ] 2.4 改造 `scripts/publish2lark_base.py`
  - 删除 `_LOG_FILE_NAME` 常量
  - 删除类内 logger 初始化代码（`__init__` 中的 `logging.getLogger` 等）
  - 改为：
    ```python
    from utils.logger import get_logger
    
    class LarkBasePublisher:
        def __init__(self, date: str):
            self.date = date
            self.logger = get_logger('publish2lark_base', date)
            # ... 其他初始化
    ```

- [ ] 2.5 改造 `scripts/publish2lark.py`
  - `LarkWikiPublisher.__init__` 中，`super().__init__('publish2lark', date)` 传入 date
  - 将所有 `self.log(...)` 调用改为 `self.logger.info(...)` / `self.logger.warning(...)` / `self.logger.error(...)`
  - 注意 `self.log()` 的 `level` 参数映射：
    - `self.log(..., level='INFO')` → `self.logger.info(...)`
    - `self.log(..., level='WARNING')` → `self.logger.warning(...)`
    - `self.log(..., level='ERROR')` → `self.logger.error(...)`
    - `self.log(..., level='DEBUG')` → `self.logger.debug(...)`
  - 删除 `self._log_file` 引用（如 `self.log(f"全量执行日志将保存至: {self._log_file}")`）

- [ ] 2.6 改造 `project-space/` 下的其他模块
  - `ingest.py`、`filter_rank.py`、`summarize.py`、`assemble.py`
  - 确保 `super().__init__()` 调用传入 `date` 参数
  - 将所有 `self.log(...)` 调用改为 `self.logger.info(...)` 等

- [ ] 2.7 删除 `project-space/logs/` 目录（如果存在）

---

## 第 3 点：抽象 LarkCommander 命令执行器

### 设计思路

- 命令视为对象，使用链式调用：`LarkCmd.WIKI_NODE_CREATE.args(space_id=..., title=...).run()`
- 每个命令枚举值自带 `args()` 方法返回命令实例，命令实例的 `run()` 执行
- 外部脚本仅负责环境处理、流程控制，不直接拼接命令或调用 subprocess

### 改造内容

- [ ] 3.1 新建 `project-space/utils/lark_commander.py`
  ```python
  import subprocess
  from typing import Optional
  
  
  class _LarkCommand:
      """lark-cli 命令实例（由 LarkCmd.args() 创建）"""
      
      def __init__(self, template: list[str]):
          self._template = template
          self._kwargs: dict = {}
          self._input_text: Optional[str] = None
      
      def args(self, **kwargs) -> '_LarkCommand':
          """设置命令模板中的占位符参数"""
          self._kwargs.update(kwargs)
          return self
      
      def input(self, text: str) -> '_LarkCommand':
          """设置 stdin 输入内容（如文档正文）"""
          self._input_text = text
          return self
      
      def run(self) -> Optional[str]:
          """执行 lark-cli 命令
          
          Returns:
              命令执行成功返回 stdout（去除空白和 'null'），失败返回 None
          """
          cmd_args = [arg.format(**self._kwargs) for arg in self._template]
          
          result = subprocess.run(
              ['lark-cli'] + cmd_args,
              capture_output=True,
              text=True,
              encoding='utf-8',
              input=self._input_text
          )
          
          if result.returncode != 0:
              return None
          
          output = result.stdout.strip()
          return output if output and output != 'null' else None
  
  
  class LarkCmd:
      """lark-cli 命令模板（静态工厂）"""
      
      # === Wiki 命令 ===
      WIKI_NODE_LIST = _LarkCommand(['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--page-all', '-q', '{query}'])
      WIKI_NODE_LIST_BY_PARENT = _LarkCommand(['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--parent-node-token', '{parent_token}', '--page-all', '-q', '{query}'])
      WIKI_NODE_CREATE = _LarkCommand(['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--obj-type', 'docx', '--title', '{title}', '-q', '.data.node_token'])
      WIKI_NODE_CREATE_WITH_PARENT = _LarkCommand(['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--title', '{title}', '--parent-node-token', '{parent_token}', '-q', '.data.node_token'])
      WIKI_NODE_MOVE = _LarkCommand(['wiki', '+move', '--as', 'user', '--node-token', '{node_token}', '--target-parent-token', '{target_token}'])
      
      # === Docs 命令 ===
      DOC_UPDATE = _LarkCommand(['docs', '+update', '--api-version', 'v1', '--as', 'user', '--doc', '{doc_token}', '--new-title', '{title}', '--mode', 'overwrite', '--markdown', '-'])
      
      # === Base 命令 ===
      BASE_SEARCH = _LarkCommand(['base', '+base-search', '--keyword', '{keyword}', '--format', 'json', '-q', '.data.bases[0].base_token'])
      BASE_CREATE = _LarkCommand(['base', '+base-create', '--name', '{name}', '--time-zone', '{timezone}', '--format', 'json', '-q', '.data.base.base_token'])
      BASE_TABLE_LIST = _LarkCommand(['base', '+table-list', '--base-token', '{base_token}', '--format', 'json', '-q', '.data.tables'])
      BASE_TABLE_CREATE = _LarkCommand(['base', '+table-create', '--base-token', '{base_token}', '--json', '{table_json}', '--format', 'json', '-q', '.data.table.id'])
      BASE_FIELD_LIST = _LarkCommand(['base', '+field-list', '--base-token', '{base_token}', '--table-id', '{table_id}', '-q', '[.data.fields[] | {field_id: .id, name: .name, type: .type}]'])
      BASE_FIELD_CREATE = _LarkCommand(['base', '+field-create', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{field_json}', '-q', '.data.field.id'])
      BASE_RECORD_SEARCH = _LarkCommand(['base', '+record-search', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{search_json}', '--format', 'json'])
      BASE_RECORD_DELETE = _LarkCommand(['base', '+record-delete', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{delete_json}', '--yes', '-q', '.data.deleted_record_id_list'])
      BASE_RECORD_BATCH_CREATE = _LarkCommand(['base', '+record-batch-create', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{data_json}', '-q', '.data.record_id_list'])
      
      # === IM 命令 ===
      IM_MESSAGE_SEND = _LarkCommand(['im', '+messages-send', '--chat-id', '{chat_id}', '--msg-type', 'interactive', '--content', '{content}'])
  ```

- [ ] 3.2 改造 `scripts/publish2lark.py`
  - 删除 `run_lark_cli()` 函数
  - 删除所有 `CMD_*` 和 `QUERY_*` 类常量
  - 添加 `from utils.lark_commander import LarkCmd`
  - 改造示例：
    ```python
    # 改造前
    query = self.QUERY_NODE_BY_TITLE.format(title=title)
    cmd = [arg.format(space_id=self.space_id, query=query) for arg in self.CMD_NODE_LIST]
    token = run_lark_cli(cmd)
    
    # 改造后
    token = LarkCmd.WIKI_NODE_LIST.args(
        space_id=self.space_id,
        query=f'.data.nodes[] | select(.title == "{title}") | .node_token'
    ).run()
    
    # 创建节点
    token = LarkCmd.WIKI_NODE_CREATE.args(
        space_id=self.space_id,
        title=title
    ).run()
    ```
  - 文档写入需要传入 `input_text`：
    ```python
    result = LarkCmd.DOC_UPDATE.args(
        doc_token=node_token,
        title=title
    ).input(content).run()
    ```

- [ ] 3.3 改造 `scripts/publish2lark_base.py`
  - 删除 `run_lark_cli()` 函数
  - 添加 `from utils.lark_commander import LarkCmd`
  - 所有 `run_lark_cli(cmd)` 调用改为 `LarkCmd.XXX.args(**kwargs).run()`
  - 示例：
    ```python
    # 搜索 Base
    result = LarkCmd.BASE_SEARCH.args(keyword='AI前沿早报数据库').run()
    
    # 创建字段（需要 JSON 参数）
    result = LarkCmd.BASE_FIELD_CREATE.args(
        base_token=self.base_token,
        table_id=self.table_id,
        field_json=json.dumps({"name": field_name, "type": field_type}, ensure_ascii=False)
    ).run()
    ```

- [ ] 3.4 改造 `scripts/push2group.py`
  - `_send_via_lark_cli()` 改为使用 `LarkCmd`：
    ```python
    def _send_via_lark_cli(self, payload: dict) -> dict:
        chat_id = self.cfg.chat_id or self._load_chat_id_from_secrets()
        if not chat_id:
            raise ValueError('缺少 chat-id 配置')
        
        content = json.dumps(payload['card'], ensure_ascii=False)
        result = LarkCmd.IM_MESSAGE_SEND.args(
            chat_id=chat_id,
            content=content
        ).run()
        
        if result is None:
            raise RuntimeError('lark-cli 推送失败')
        
        return json.loads(result) if result else {}
    ```

- [ ] 3.5 统一日志路径（随第 2 点一起改造）
  - 确保所有脚本日志统一写入 `output/{date}/run.log`

---

## 第 4 点：提示词元信息简化

### 现状分析

#### `filter_ranker.j2.md` 中 `news_json` 结构

当前结构（来自 `filter_rank.py`）：
```json
[
  {
    "index": 0,
    "title": "...",
    "url": "...",
    "source": "...",
    "summary": "...",
    "pub_time": "..."
  }
]
```

**简化方案**：
- `index`：LLM 用于关联 `source_index`，**必须保留**
- `title`：LLM 筛选核心依据，**必须保留**
- `source`：LLM 判断来源可信度，**必须保留**
- `summary`：LLM 筛选核心依据，**必须保留**
- `url`：LLM 筛选时不使用，**可移除**
- `pub_time`：LLM 筛选时不使用，**可移除**

#### `summarizer.j2.md` 中 `news_json` 结构

当前结构（来自 `summarize.py`）：
```json
[
  {
    "cluster_index": 0,
    "cluster_id": "...",
    "keywords": ["..."],
    "main_section": "...",
    "sub_section": "...",
    "rank": 0,
    "merged_relevance": 0.0,
    "merged_hot_level": 0.0,
    "title": "...",
    "items": [{"index": 0, "title": "...", "url": "...", "summary": "...", "pub_time": "..."}],
    "sources": ["..."],
    "urls": ["..."],
    "merged_summary": "..."
  }
]
```

**简化方案**：
- `cluster_index`：LLM 关联输出，**必须保留**
- `keywords`：LLM 理解主题，**必须保留**
- `main_section` / `sub_section`：LLM 分类参考，**必须保留**
- `title`：LLM 参考，**必须保留**
- `items`：LLM 汇总核心数据，**必须保留**（但可简化内部字段）
- `merged_summary`：LLM 参考，**必须保留**
- `cluster_id`：LLM 不使用，**可移除**
- `rank` / `merged_relevance` / `merged_hot_level`：LLM 汇总时不使用，**可移除**
- `sources` / `urls`：LLM 不直接使用，**可移除**
- `items` 内部简化：只保留 `title`, `summary`（移除 `index`, `url`, `pub_time`）

### 改造内容

- [ ] 4.1 修改 `filter_rank.py` 中构建 `news_json` 的代码
  - 找到构建新闻条目的位置
  - 移除 `url` 和 `pub_time` 字段
  - 只保留 `index`, `title`, `source`, `summary`

- [ ] 4.2 修改 `summarize.py` 中 `_build_prompts()` 方法
  - 移除 `cluster_id`, `rank`, `merged_relevance`, `merged_hot_level`, `sources`, `urls`
  - `items` 内部只保留 `title`, `summary`
  - 保留 `cluster_index`, `keywords`, `main_section`, `sub_section`, `title`, `items`, `merged_summary`

- [ ] 4.3 验证提示词模板中是否引用了被移除的字段
  - 检查 `filter_ranker.j2.md` 和 `summarizer.j2.md`
  - 确保模板中使用的变量与新的 JSON 结构一致

- [ ] 4.4 运行测试验证 LLM 输出质量不受影响
  - 使用历史数据对比简化前后的 LLM 输出
  - 确认字段完整性、分类准确性

---

## 第 5 点：.lobster 工作流配置优化
> 详情 见：docs/lobster-介绍说明.md

### 文件归属说明

| 文件 | 归属 | 说明 |
|------|------|------|
| `references/ai-frontier-daily.example.lobster` | Git 仓库 | 示例配置，提交至版本控制 |
| `references/ai-frontier-daily.lobster` | 个人本地 | 实际运行配置，不提交 Git（含个人路径等敏感信息） |

### 现状

原始配置中：
- 每个 step 直接写完整命令路径（如 `./run.sh python scripts/xxx.py`）
- step 间通过 shell 变量或管道传递数据
- 环境配置（cd、venv、SSL）内嵌在每个命令中

### 目标

- 环境配置抽离为独立脚本 `scripts/base/run.sh`
- 全局参数统一在 `args` 块定义
- step 间通过 `/tmp/afinfo-*.txt` 文件传递数据

### 改造内容

- [ ] 5.1 新建 `scripts/base/run.sh` 环境启动脚本
  ```bash
  #!/bin/bash
  # 路径: $HOME/.qclaw/skills/ai-frontier-daily/run.sh

  # 1. 切换到项目根目录
  cd "$(dirname "$0")" || exit

  # 2. 激活虚拟环境 (如果存在)
  if [ -f ".venv/bin/activate" ]; then
      source .venv/bin/activate
  fi

  # 3. 注入 SSL 证书环境变量
  export SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())" 2>/dev/null)
  export REQUESTS_CA_BUNDLE=$SSL_CERT_FILE

  # 4. 透传并执行传入的任意命令
  exec "$@"
  ```

- [ ] 5.2 重构 `references/ai-frontier-daily.example.lobster` 配置文件结构
  ```yaml
  name: ai-frontier-daily
  description: AI前沿早报工作流 (路径安全版)

  args:
    date:
      default: $(date +%Y-%m-%d)

  env:
    # 核心：定义项目根目录，消灭相对路径不确定性
    SKILL_DIR: $HOME/.qclaw/skills/ai-frontier-daily

  steps:
    # 0. 清理临时文件 (保障每次运行环境干净)
    - id: cleanup
      command: bash -c 'mkdir -p $SKILL_DIR/tmp && rm -f /tmp/afinfo-*.txt'

    # 1. 新闻采集
    - id: news_frontier
      command: $SKILL_DIR/scripts/bin/run.sh python scripts/news_frontier.py --date $args.date

    # 2. 微信图文渲染
    - id: render_wechat
      command: $SKILL_DIR/scripts/bin/run.sh bash scripts/render_wechat.sh $args.date

    # 3. 发布飞书文档 (重定向到绝对路径下的 tmp 目录)
    - id: publish2lark
      command: bash -c '$SKILL_DIR/scripts/bin/run.sh python scripts/publish2lark.py --date $args.date > /tmp/afinfo-doc_url.txt'

    # 4. 推送飞书群 (从绝对路径读取文件)
    - id: push2group
      command: bash -c 'DOC_URL=$(cat /tmp/afinfo-doc_url.txt) && $SKILL_DIR/scripts/bin/run.sh python scripts/push2group.py --date $args.date --doc-url "$DOC_URL"'

    # 5. 更新多维表格
    - id: publish2lark_base
      command: bash -c '$SKILL_DIR/scripts/bin/run.sh python scripts/publish2lark_base.py --date $args.date > /tmp/afinfo-base_url.txt'

    # 6. 最终报告
    - id: final_report
      command: bash -c 'echo "✅ 完成！\n📄 文档：$(cat $SKILL_DIR/tmp/afinfo-doc_url.txt)\n📊 表格：$(cat $SKILL_DIR/tmp/afinfo-base_url.txt)"'
  ```

- [ ] 5.3 关键设计说明
  - **环境变量 `SKILL_DIR`**：统一定义项目根目录，所有 step 通过 `$SKILL_DIR/...` 引用路径
  - **`args.date`**：全局日期参数，所有 step 共享，支持 `--date YYYY-MM-DD` 覆盖
  - **`/tmp/afinfo-*.txt` 文件传递**：
    - `afinfo-doc_url.txt`：publish2lark → push2group / final_report
    - `afinfo-base_url.txt`：publish2lark_base → final_report
  - **cleanup step**：每次运行前清理 `/tmp/afinfo-*.txt`，避免脏数据
  - **`run.sh` 透传机制**：使用 `exec "$@"` 将参数原样传递给子命令，保持环境一致性
  - **文件分离策略**：`.example.lobster` 作为模板提交 Git，个人 `.lobster` 本地维护不提交

---

## 第 6 点：脚本路径调整 + 文档同步

### 现状

脚本目录结构调整：
- `scripts/init_env.sh` → `scripts/base/init_env.sh`
- 新增 `scripts/base/run.sh` 环境启动器
- `scripts/publish2lark.sh` → `scripts/publish2lark.py`（改为 Python 实现）
- 新增 `scripts/publish2lark_base.py` 多维表格更新脚本

### 改造内容

- [ ] 6.1 更新 `SKILL.md` 中的路径引用
  - `scripts/init_env.sh` → `scripts/base/init_env.sh`
  - 新增 `scripts/base/run.sh` 说明
  - 工作流步骤更新：增加 `cleanup` 和 `publish2lark_base`
  - 产物表增加 `/tmp/afinfo-*.txt` 中间文件说明

- [ ] 6.2 检查其他引用脚本路径的文档
  - 搜索 `references/` 目录下是否有引用旧路径的文件
  - 搜索 `docs/` 目录下是否有引用旧路径的文件
  - 同步更新所有路径引用

---

## 执行注意事项

1. **第 2 点是第 3 点的前置依赖**，必须先完成 Logger 改造
2. 每次改造后运行 `python -m py_compile <file>` 检查语法
3. 改造完成后运行现有测试（如有）
4. 建议按 1 → 2 → 3 → 4 顺序执行，每完成一点做一次 commit
5. 所有路径基于项目根目录：`/Users/han.qishu/Professional/ai-frontier-daily`
