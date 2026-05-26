# 新闻板块截图功能 — 小红书卡片自动化

> 创建日期：2026-05-25
> 状态：已实现

---

## 概览

将 AI 前沿早报的每条新闻和"今日速览"模块拆分为独立的 HTML 卡片页面，通过 Agent Browser 工具自动截图，生成适合小红书平台发布的 PNG 图片。整个流程集成到每日工作流尾部，实现从数据采集到多平台发布的完整闭环。

---

## 背景

### 现状

- 每日早报产出为完整的 Markdown / HTML 文档，适合飞书文档和微信公众号
- 小红书平台需要**单条卡片式图片**，每条新闻独立成图，风格统一
- 手动截图效率低、尺寸不一致、排版易出错

### 目标

| 维度 | 目标 |
|------|------|
| 内容拆分 | 每条新闻 + 今日速览 → 独立 HTML 页面 |
| 截图自动化 | Agent Browser 打开页面 → 自动检测卡片 → 精准裁剪截图 |
| 工作流集成 | 作为每日 pipeline 的最后一步，自动产出所有卡片截图 |

---

## 方案设计

### 1. 模板拆分

#### 1.1 合并截图模板

将 news card 和 quick-view card 合并为单一模板 `briefing-template-redbook.html.j2`，通过 `card_type` 参数控制渲染类型：

```
card_type = 'news'       → 渲染新闻卡片
card_type = 'quick_view' → 渲染今日速览卡片
```

**模板特点**：
- 宽度固定 450px，适合小红书竖版比例
- 卡片居中显示（`min-height: 100vh` + flex 居中）
- 仅保留截图所需的 CSS，剔除页脚、分区标题等冗余样式
- CSS 按选择器分组，每行一个规则，保持可读性

#### 1.2 输出目录结构

```
output/{date}/
├── briefing-feishu.md             # 飞书文档（Markdown）
├── briefing-wechat.html           # 微信公众号（HTML）
└── redbook/                       # 小红书卡片源文件
    ├── quick-view.html            # 今日速览
    ├── card-001.html              # 第 1 条新闻
    ├── card-002.html              # 第 2 条新闻
    └── ...
```

### 2. 截图流程

#### 2.1 核心类设计

```
BrowserSession          — 封装 agent-browser CLI 操作
  ├── open(filePath)    — 打开本地 HTML 并等待加载完成
  ├── detectCardType()  — 自动识别卡片类型（news-card / quick-view-card）
  ├── getRect(type)     — 获取卡片元素的 bounding rect
  ├── fitViewport(rect) — 根据卡片尺寸计算并设置视口
  ├── capture(path)     — 全屏截图
  └── close()           — 关闭浏览器会话

RedbookScreenshot       — 主流程编排
  ├── validate()        — 校验 redbook/ 目录和 HTML 文件
  ├── processOne()      — 处理单个 HTML：打开 → 识别 → 截图
  └── run()             — 遍历所有文件，输出到 redbook-png/
```

#### 2.2 截图输出

```
output/{date}/
└── redbook-png/               # 截图结果
    ├── quick-view.png
    ├── card-001.png
    ├── card-002.png
    └── ...
```

#### 2.3 截图步骤

1. **打开页面** — `agent-browser open file://...` + `wait --load networkidle`
2. **检测卡片类型** — `eval` 检测 `section.news-card` / `section.quick-view-card`
3. **获取位置尺寸** — `eval` 调用 `getBoundingClientRect()`
4. **计算视口** — `viewport = rect.x * 2 + rect.width + padding`
5. **设置视口并刷新** — `set viewport W H` + `reload`
6. **截图** — `screenshot --full output.png`

### 3. 工作流集成

#### 3.1 assemble.py 三块输出

`run()` 方法按平台拆分为三个清晰模块：

```python
# === 1. 飞书：Markdown 文件 ===
md = renderer.render(TEMPLATE_BRIEFING, ctx)
→ output/{date}/briefing-feishu.md

# === 2. 微信：HTML 文件 ===
html = renderer.render(TEMPLATE_BRIEFING_WECHAT, ctx)
→ output/{date}/briefing-wechat.html

# === 3. 小红书：目录（多个 HTML）===
redbook_paths = render_redbook_cards(clusters, footer, output_dir)
→ output/{date}/redbook/*.html
```

#### 3.2 工作流尾部接入

在 `.lobster` 工作流中，截图步骤放在发布之后：

```yaml
steps:
  # ... 前面的采集、渲染、发布步骤 ...

  # 生成小红书卡片 HTML
  - id: assemble_redbook
    command: $SKILL_DIR/scripts/base/run.sh python project-space/assemble.py --date $args.date

  # 批量截图
  - id: screenshot_redbook
    command: $SKILL_DIR/scripts/base/run.sh node scripts/screenshot-redbook.js $args.date
```

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `project-space/config/briefing-template-redbook.html.j2` | 小红书截图模板（合并 news + quick_view） |
| `project-space/config/briefing-template-wechat.html.j2` | 微信公众号 HTML 模板 |
| `project-space/assemble.py` | 拼版渲染模块，新增 `_render_redbook_cards()` |
| `project-space/utils/base_config.py` | 模板常量：`FN_BRIEFING_FEISHU`、`FN_BRIEFING_WECHAT`、`FN_REDBOOK`、`TEMPLATE_BRIEFING_WECHAT`、`TEMPLATE_BRIEFING_REDBOOK` |
| `scripts/screenshot-redbook.js` | OOP 风格的截图脚本（BrowserSession + RedbookScreenshot） |
| `scripts/screenshot-cards.sh` | Bash 版截图脚本（备用） |

---

## 后续优化方向

1. **截图质量** — 考虑增加设备像素比（DPR）设置，提升 Retina 屏幕截图清晰度
2. **并发截图** — 当前串行处理，可改为并发打开多个页面提升速度
3. **样式主题** — 小红书卡片可增加多种配色主题，通过参数切换
4. **水印/署名** — 截图底部自动添加来源水印
5. **失败重试** — 截图失败时自动重试，避免整批中断
