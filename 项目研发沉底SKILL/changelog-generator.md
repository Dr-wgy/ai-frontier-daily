# 变更日志生成 SKILL

> 用途：将 git diff 内容按规范生成结构化变更日志，追加至 CHANGELOG.md

---

## 触发条件

当用户说以下任意一种时触发：
- "生成变更日志"
- "写 changelog"
- "整理变更记录"
- "生成 CHANGELOG"

---

## 标准结构

### 目录层级

| 层级 | 格式 | 示例 |
|------|------|------|
| 一级 | 日期 | `### YYYY-MM-DD (commit: xxx)，作者：xxx` |
| 二级 | 大组分类 | `#### 研发工程 / Skill 框架 / 提示词工程` |
| 三级 | 改造点小组 | `##### 1. SummaryCluster 归置到 domain.py` |
| 四级 | 模块列表 | `- **模块名** - 精简描述` |

### 编写规范

1. **同一日期下多个 commit 用 `---` 分隔**
2. **描述控制在 15 字以内**，突出核心改造点
   - 改造内容较多、信息量大时，可不受字数限制：
     第一行高度汇总（主标题式），换行缩进后补充展开说明，逐点列举核心改动
3. **模块名使用 `**模块名**` 格式**，不含文件扩展名
4. **仅记录功能变更**，不涉及代码实现细节
5. **关键动作（新增/删除/重构）用词前置**
6. **相同改造点的模块合并为一行**，用顿号分隔模块名

---

## 执行步骤

> ⚠️ **必须逐项执行，不可跳过任何一步**

### Step 1：获取 Git Diff

```bash
git add .
git diff --cached --no-color > gitcmt.log.tmp
```

读取 `gitcmt.log.tmp` 内容作为变更依据。

### Step 2：读取改造计划文档

读取 `docs/YYYY-MM-DD-refactor-plan.md`（或用户指定的改造计划文档），获取：
- 改造点编号和名称
- 每个改造点涉及的模块/文件
- 改造点的分类归属（研发工程 or Skill 框架）

### Step 3：按改造点分组

根据改造计划文档，将 git diff 中的变更按改造点归类：
- 每个改造点对应一个 `#####` 三级标题
- 同一改造点下的模块变更合并展示（如 `**A、B、C** - 统一描述`）

### Step 4：构建变更日志

按以下模板构建：

```markdown
### YYYY-MM-DD (commit: -)，作者：xxx

#### 研发工程

##### 1. 改造点名称

- **模块A** - 变更描述
- **模块B、模块C** - 统一变更描述

##### 2. 改造点名称

- **模块D** - 变更描述

#### Skill 框架

##### 5. 改造点名称

- **配置文件** - 变更描述

##### 6. 改造点名称

- **文档A、文档B** - 变更描述
```

### Step 5：追加至 CHANGELOG.md

将构建好的变更日志追加至 `CHANGELOG.md` 文件顶部（在 `## 变更日志` 之后，其他日期记录之前）。

### Step 6：清理临时文件

```bash
rm -f gitcmt.log.tmp
```

---

## 大组分类规则

| 大组 | 包含内容 |
|------|----------|
| **研发工程** | 代码层面变更：新增模块、重构逻辑、修复 Bug、优化性能、调整路径等 |
| **Skill 框架** | 配置和文档层面变更：.lobster 工作流、SKILL.md、PIPELINE.md 等文档更新 |
| **提示词工程** | 提示词模板变更：filter_ranker.j2.md、summarizer.j2.md 等 prompt 调整 |

---

## 改造点映射示例

以 `docs/2026-05-23-refactor-plan.md` 为例：

| 改造点编号 | 改造点名称 | 归属大组 | 涉及模块 |
|-----------|-----------|---------|---------|
| 1 | SummaryCluster 归置到 domain.py | 研发工程 | domain |
| 2 | Logger 工具化改造 | 研发工程 | logger, work_module, llm_client, news_frontier, ingest, filter_rank, summarize, assemble |
| 3 | 抽象 LarkCommander 命令执行器 | 研发工程 | lark_commander, publish2lark, publish2lark_base, push2group |
| 4 | 提示词元信息简化 | 研发工程 | filter_rank, summarize |
| 5 | .lobster 工作流配置优化 | 研发工程 + Skill 框架 | run.sh（研发）, ai-frontier-daily.example.lobster（框架） |
| 6 | 脚本路径调整 + 文档同步 | 研发工程 + Skill 框架 | init_env.sh（研发）, PIPELINE.md, SKILL.md（框架） |

---

## 注意事项

1. **改造点编号必须与改造计划文档一致**
2. **跨大组的改造点（如第 5、6 点）需在两个大组下分别建立小组**
3. **模块名不含文件扩展名**（如 `logger` 而非 `logger.py`）
4. **描述使用动宾结构**（如 "新增统一日志模块"、"重构为 LarkCmd 链式调用"）
5. **生成完毕后必须删除 `gitcmt.log.tmp`**
