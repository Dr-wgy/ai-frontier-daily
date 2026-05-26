# Chrome CDP 截图模块设计

## 概述

用 Chrome headless + Chrome DevTools Protocol (CDP) 替换原有的 `agent-browser` CLI 方案，实现小红书卡片 HTML → PNG 的批量截图。

**核心优势：**
- 零第三方依赖（仅 Node.js 内置模块）
- 精确获取卡片渲染后尺寸，截图尺寸与原方案一致
- 单个 Chrome 进程复用，批量处理效率高

## 架构分层

```
─────────────────────────────────────────────┐
│  RedbookScreenshot  (业务层)                 │
│  仅感知：打开 → 量尺寸 → 截图                 │
├─────────────────────────────────────────────┤
│  HeadlessBrowser  (浏览器层)                  │
│  Chrome 进程管理 + CDP 操作封装               │
│  接口：launch / open / queryRect /           │
│        screenshot / close                    │
├─────────────────────────────────────────────┤
│  CDPClient  (通信层)                          │
│  纯 WebSocket 收发 CDP JSON 消息              │
│  接口：connect / send / close                │
└─────────────────────────────────────────────┘
```

## 模块说明

### CDPClient — WebSocket 通信层

| 方法 | 说明 |
|------|------|
| `connect()` | 建立 WebSocket 连接到 Chrome 调试端口 |
| `send(method, params)` | 发送 CDP 命令，返回 Promise |
| `close()` | 关闭连接 |

**实现要点：**
- 使用 Node.js 内置 `net` 模块手写 WebSocket 帧解析/组装
- 客户端帧需 masking（RFC 6455），服务端帧无需 unmask
- 通过 `msg.id` 匹配请求与响应，15 秒超时

### HeadlessBrowser — 浏览器层

| 方法 | 说明 |
|------|------|
| `launch()` | 启动 Chrome headless 进程，建立 CDP 连接 |
| `open(fileUrl)` | 导航到指定 URL（file://） |
| `queryRect(selector)` | 执行 JS 获取 DOM 元素的 getBoundingClientRect |
| `screenshot(rect, outputPath)` | 设视口 + clip 精确裁剪截图，写 PNG 文件 |
| `close()` | 关闭 CDP 连接 + kill Chrome 进程 |

**关键 CDP 命令：**
- `Page.navigate` — 页面导航
- `Runtime.evaluate` — 执行 JS，获取卡片尺寸
- `Emulation.setDeviceMetricsOverride` — 设置视口和 deviceScaleFactor
- `Page.captureScreenshot` — 截图，带 `clip` 参数精确裁剪

### RedbookScreenshot — 业务层

| 方法 | 说明 |
|------|------|
| `validate()` | 校验目录、Chrome 路径、HTML 文件列表 |
| `logSummary()` | 打印任务摘要 |
| `processOne(browser, htmlFile, index, total)` | 处理单个文件 |
| `run()` | 主流程：启动浏览器 → 遍历文件 → 关闭 |

**工作流链路：**
```
validate() → launch() → [open → queryRect → screenshot] × N → close()
```

## 截图流程（单文件）

```
1. browser.open("file://xxx.html")
       ↓ Page.navigate + sleep 500ms
2. browser.queryRect("section.quick-view-card")
       ↓ Runtime.evaluate → getBoundingClientRect()
       ↓ 返回 { x, y, width, height }
3. browser.screenshot(rect, outputPath)
       ↓ Emulation.setDeviceMetricsOverride(宽视口 1200px, 高度足够)
       ↓ Page.captureScreenshot(clip={x, y, w, h})
       ↓ base64 → 写文件
```

## 截图策略：宽视口 + clip 裁剪

**核心思想：** 保持宽视口（1200px）让页面正常渲染，不破坏布局；用 `clip` 参数精确裁剪卡片区域（含留白）。

```
┌─────────────────────────────────────────────────────┐  ← 视口 1200px
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  卡片区域 (card)                               │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │  内容                                     │  │  │
│  │  │  ...                                     │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  │  ↑ PADDING                                     │  │
│  │  ↓ PADDING                                     │  │
│  ───────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
         ↑ clip 裁剪区域（含左右/上下留白）
```

**clip 参数计算：**
- `clipX = rect.x - PADDING` — 左留白
- `clipY = rect.y - PADDING` — 上留白
- `clipW = rect.width + 2*PADDING` — 宽度 + 左右留白
- `clipH = rect.height + 2*PADDING` — 高度 + 上下留白

## 常量配置

### Config 类统一管理

| 常量 | 值 | 说明 |
|------|------|------|
| `CHROME_BIN` | `/Applications/Google Chrome.app/.../Google Chrome` | Chrome 路径 |
| `CARD_WIDTH` | `460` | 卡片宽度（px） |
| `DEVICE_SCALE` | `2` | @2x 高清截图 |
| `PADDING` | `5` | 上下留白（px），clipY 和 clipH 共用 |
| `CLIP_X_OFFSET` | `5` | 左留白（px），clipX 偏移 |
| `CLIP_W_EXTRA` | `10` | 右留白（px），clipW 额外宽度 |
| `VIEWPORT_WIDTH` | `1200` | 视口宽度（px），保持页面正常渲染 |
| `VIEWPORT_MIN_HEIGHT` | `2000` | 视口最小高度（px） |
| `VIEWPORT_EXTRA_HEIGHT` | `20` | 视口额外高度（px） |
| `WINDOW_SIZE` | `1200,1200` | Chrome 窗口尺寸 |
| `HEADLESS` | `true` | 是否无头模式 |
| `CDP_TIMEOUT` | `15000` | CDP 命令超时（ms） |
| `CHROME_READY_RETRIES` | `60` | Chrome 启动重试次数 |
| `CHROME_READY_INTERVAL` | `500` | Chrome 启动重试间隔（ms） |
| `PAGE_NAVIGATE_WAIT` | `500` | 页面导航后等待（ms） |
| `SCREENSHOT_WAIT` | `200` | 截图前等待（ms） |

## 卡片选择器

按优先级遍历：
1. `section.quick-view-card`
2. `section.news-card`

首个匹配到的即为当前页面的卡片类型。
