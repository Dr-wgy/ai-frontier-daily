# 微信公众号前端开发规范

---

## 第一部分：整体兼容要求

> 运行环境基线：`Browserslist: iOS >= 14, Android >= 9, Chrome >= 85, Safari >= 14`

### 渲染引擎说明

| 平台 | 引擎 | 等效环境 |
|------|------|----------|
| **iOS** | WKWebView (WebKit) | Safari 14+ |
| **Android** | 腾讯 X5 内核 (Chromium/Blink 深度定制) | Chrome 85+ |
| **PC/Mac** | 微信 XWeb 引擎 / Edge WebView2 (Blink) | 现代 Chromium |

*无需兼容 IE、老旧 Android 4.x 或 iOS 12 以下的设备。*

---

### 1. CSS 与布局规范

| 问题 | 规范要求 |
|------|----------|
| **1px 边框** | 高分屏下禁止直接用 `border: 1px`，改用 `transform: scaleY(0.5)` 伪元素方案或 `box-shadow` |
| **底部安全区** | 底部固定元素必须加 `padding-bottom: env(safe-area-inset-bottom)` 适配全面屏 |
| **Fixed 定位** | iOS 键盘弹起时 `fixed` 易抖动，优先改用 `sticky`；必须用 `fixed` 时，需将滚动容器设为独立 `overflow-y: auto` 元素而非 body |
| **iOS 橡皮筋** | 全屏弹窗/游戏类页面根容器加 `overscroll-behavior: none` |
| **字体缩放** | 全局加 `-webkit-text-size-adjust: 100%` 防止横屏或系统字体设置导致排版崩溃 |
| **点击高亮** | 全局加 `-webkit-tap-highlight-color: transparent` 去除 iOS 点击灰色遮罩 |

---

### 2. JavaScript 与交互规范

| 问题 | 规范要求 |
|------|----------|
| **滚动穿透** | 弹出全屏遮罩时，用 `body { overflow: hidden }` + JS 记录并恢复 `scrollTop`；或对 `touchmove` 调用 `preventDefault()`（注意 passive event 限制） |
| **点击事件** | 现代微信已无 300ms 延迟，统一使用标准 `click` 事件；触摸反馈优化可加 `touch-action: manipulation` |
| **内存泄漏** | 页面卸载（`pagehide` / `unload`）时必须移除全局事件监听（`resize`、`scroll` 等）、清除定时器、解绑 WebSocket/EventSource |
| **时间解析** | iOS WebKit 不支持 `new Date('2026-05-24 10:00:00')`，必须改为斜杠格式 `new Date('2026/05/24 10:00:00')` 或直接使用时间戳 |

---

### 3. 多媒体与表单规范

**视频同层播放（Android X5）**

Android 微信中 `<video>` 默认会被强制全屏并遮挡页面 UI，必须添加以下属性：

```html
<video
  playsinline
  webkit-playsinline
  x5-video-player-type="h5"
  x5-video-player-fullscreen="true"
  x5-video-orientation="portraint">
</video>
```

**图片长按菜单**

不需要用户长按保存/识别的图片，添加：`-webkit-touch-callout: none; user-select: none;`

**输入框**

iOS 微信中关闭首字母自动大写与自动纠错：

```html
<input type="text" autocapitalize="off" autocomplete="off" autocorrect="off" />
```

---

### 4. 性能与工程化规范

| 项目 | 规范要求 |
|------|----------|
| **图片格式** | 优先使用 WebP，通过 `<picture>` 标签或 CSS 降级提供 JPEG/PNG fallback |
| **图片懒加载** | 长列表图片使用 `IntersectionObserver` 或原生 `loading="lazy"` |
| **CSS 变量** | `var(--color)` 在当前基线（Chrome 85+/Safari 14+）已完全支持，可放心使用 |
| **配色重构** | 换色任务只修改 CSS/样式，不改动 DOM 结构与 JS 逻辑；色值统一使用 CSS 变量管理，避免硬编码；文字与背景对比度需 ≥ 4.5:1 |

---

## 第二部分：微信公众号实践经验

> 通过实际测试对比 `create.html`（原始 HTML）与公众号编辑器粘贴后的转换结果整理。

---

### 1. `<style>` 标签处理

| 行为 | 说明 |
|------|------|
| **`<style>` 被删除** | 粘贴后 `<head>` 为空，所有 `<style>` 内容被移除 |
| **自动内联** | 公众号会尝试将 `<style>` 中的 CSS 类名属性**内联**到对应元素上 |
| **内联不完整** | 简单属性（font-size、color、background、border、padding、margin）会被内联；复杂属性（flex 布局、伪元素、gap）可能丢失 |
| **class 属性无效** | `<style>` 被删除后所有 `class=` 定义的样式均失效，不要依赖 class 控制视觉 |

**结论**：
- 面向公众号的 HTML，**不要保留 `<style>` 和 `class`**，所有样式必须内联
- 若同时需要浏览器预览，可单独维护一个 `preview.html` 使用 class 写法

---

### 2. 标签转换规则

| 原始标签 | 公众号转换后 | 说明 |
|----------|-------------|------|
| `<main>` | `<section>` | 语义化标签被转换 |
| `<article>` | `<section>` | 语义化标签被转换 |
| `<html>` / `<head>` / `<body>` | 被剥离 | 公众号只保留 body 内容，无需写完整页面结构 |
| `<div>` 包含纯文本 | `<p>` | 导致 flex 等布局失效 |
| `<div>` 包含 flex 布局 | `<p>` | **flex 失效**，容器样式丢失 |
| `<div>` 作为容器（有子元素） | 可能保留或转为 `<section>` | 取决于内容复杂度 |
| `<section>` | `<section>` | ✅ 保留，推荐用于容器 |
| `<p>` 正文段落 | `<p>` | 保留，但 `line-height` 等样式可能被覆盖，建议改用 `<section>` |

**结论**：
- **不要用 `<div>` 作为布局容器**，改用 `<section>`
- **正文段落建议用 `<section>` 替代 `<p>`**，`<p>` 的行间距在公众号中容易失效
- `<section>` 是公众号最稳定的容器标签
- 面向公众号输出时，**不需要 `<!DOCTYPE html>`、`<html>`、`<head>`、`<body>`**，直接从内容标签开始

---

### 3. CSS 属性兼容性

#### ✅ 完全支持（会被内联保留）

| 属性 | 示例 |
|------|------|
| `font-size` | `14px`, `0.85rem` |
| `font-weight` | `700`, `600` |
| `color` | `#hex` → 自动转为 `rgb()` |
| `background` | 纯色 `#hex` → 自动转为 `rgb()` |
| `border` | `1px solid #hex` |
| `border-radius` | `12px`, `999px` |
| `padding` / `margin` | 各方向值 |
| `display: flex` | ✅ 保留（需元素是 `<section>`） |
| `display: inline-flex` | ✅ 保留 |
| `display: block` | ✅ 保留 |
| `justify-content` | `space-between`, `center` |
| `align-items` | `flex-start`, `center` |
| `flex-shrink` | `0` |
| `flex: 1` | ✅ 保留 |
| `line-height` | **建议用 `px` 固定值**（如 `22px`），无单位倍数（`1.6`）在 `<p>` 标签中可能失效 |
| `letter-spacing` | `0.02em` |
| `list-style: none` | ✅ 保留 |
| `position: relative` | ✅ 保留 |
| `text-align` | ✅ 保留 |
| `white-space` | ✅ 保留 |
| `font-family` | ✅ 保留，**但必须内联**，`<style>` 中定义的字体不生效 |

#### ❌ 不支持 / 会被丢弃

| 属性 | 说明 |
|------|------|
| `rgba()` 颜色 | **被完全丢弃**，改用纯色 `#hex` |
| `gap` | 内联了但渲染可能不一致，建议用 `margin` 替代 |
| `gap` 在 flex 容器中 | 公众号会保留 `gap` 属性，但值可能被调整（如 `gap:6px` 可能转为 `gap: 6px;`），建议写完整单位 |
| `transform` | 不支持（如 `rotate(45deg)`） |
| `box-shadow` | 部分支持，但可能被简化 |
| `background-image` | 不支持渐变 `linear-gradient()` |
| `opacity` | 可能不支持 |
| `transition` / `animation` | 不支持 |

#### ⚠️ 伪元素

| 伪元素 | 说明 |
|--------|------|
| `::before` / `::after` | **不支持**，自定义圆点、装饰线等无法渲染 |
| `:last-child` 等伪类 | 不支持，需手动处理最后一个元素 |

---

### 4. 颜色处理

| 原始格式 | 公众号转换后 |
|----------|-------------|
| `#fef2f2` | `rgb(254, 242, 242)` |
| `#dc2626` | `rgb(220, 38, 38)` |
| `rgba(158, 192, 219, 0.12)` | **被丢弃** |

**结论**：
- 所有颜色用 `#hex` 格式，公众号会自动转 `rgb()`
- **不要用 `rgba()`**，改用纯色或降低饱和度的纯色替代

---

### 5. 文字内容处理

| 原始 | 公众号转换后 |
|------|-------------|
| 文字内容 | 自动包裹 `<span leaf="">文字</span>` |
| emoji 🔥 | 转为 Unicode 编码 `&#55357;&#56613;` |
| `&` | 转为 `&amp;` |
| `·` | 转为 `&middot;` |

**结论**：
- 所有文字内容应预先包裹 `<span leaf="" style="box-sizing:border-box;">文字</span>`
- 标题、段落、标签、列表项内的文字都需要包裹
- 列表项 `<li>` 内的文字需额外包裹 `<section style="box-sizing:border-box;"><span leaf="" style="box-sizing:border-box;">文字</span></section>`

---

### 6. 字体处理

| 场景 | 说明 |
|------|------|
| 正文字体（`font-family`） | 必须内联到最外层容器（如顶层 `<section>`），依靠继承向下传递 |
| 标题宋体 | 必须在每个 `<h2>`、`<h3>` 上单独内联 `font-family:'Songti SC','SimSun',Georgia,serif;` |
| `<style>` 中的字体定义 | **完全无效**，粘贴后被删除 |

**结论**：
- 正文容器加 `font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;`
- 宋体标题逐个加 `font-family:'Songti SC','SimSun',Georgia,serif;`

---

### 7. 行间距（line-height）最佳实践

| 写法 | 结果 |
|------|------|
| `line-height:1.6`（无单位倍数）放在 `<p>` | **可能失效**，公众号对 `<p>` 有默认样式覆盖 |
| `line-height:22px`（px 固定值）放在 `<p>` | 生效概率更高 |
| `line-height:22px` 放在 `<section>` | ✅ **最稳定** |

**结论**：
- 正文段落用 `<section>` 替代 `<p>`，配合 `line-height:22px`（px 值）
- 避免在 `<p>` 上依赖 `line-height`，若必须用 `<p>`，改用 px 值

---

### 8. 间距控制建议

| 场景 | 推荐值 |
|------|--------|
| 卡片内 padding | `10px 14px`（紧凑）/ `14px 18px`（宽松） |
| 卡片间 margin-bottom | `10px`～`16px` |
| 卡片内子块 margin-bottom | `6px`～`10px` |
| 标题与正文间距 | `margin-bottom:10px`（不要低于 `8px`，公众号转换后标题行高可能压缩） |
| **行内元素间距（如标签间距）** | ❌ 不要用空内容 `<span style="width:5px;">` 撑间距，公众号会忽略空标签的宽度；✅ 直接在已有 `<span>` 上加 `margin-right` 或 `margin-left` |

---

### 9. 公众号自动添加的样式与标签

公众号会在所有内联 `style` 中自动补充 `box-sizing: border-box` 及继承的 `font-family`、`color`、`font-size` 等属性。提前写死 `box-sizing:border-box` 可减少转换差异。

| 自动添加 | 说明 |
|----------|------|
| `<span leaf="">` 包裹文字 | 所有文本节点都会被包裹 |
| `<span leaf="">` 加 `style="box-sizing:border-box;"` | 每个 leaf span 都有 |
| `<section>` inside `<li>` 加 `style="box-sizing:border-box;"` | 列表项内容器 |
| `class="list-paddingleft-1"` | `<ul>` 自动添加 |
| `flex: 1 1 0%` | `flex:1` 会被展开 |
| `padding: 10px 0px` | 单位补全（`0` → `0px`） |
| `margin: 0px` | 替代 `margin:0` |
| `<a class="wx_topic_link">` | `#话题` 标签会被转为话题链接 |

---

### 10. 推荐写法模板

#### 布局容器

```html
<section style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;background:#f5f5f0;border-radius:8px;padding:6px 12px;">
  <span style="font-size:14px;font-weight:700;color:#475569;"><span leaf="" style="box-sizing:border-box;">标题</span></span>
  <span style="flex-shrink:0;font-size:16px;"><span leaf="" style="box-sizing:border-box;">🔥</span></span>
</section>
```

#### 正文段落（替代 `<p>`）

```html
<section style="box-sizing:border-box;margin-bottom:16px;font-size:14px;line-height:22px;color:#3f3f46;">
  <span leaf="" style="box-sizing:border-box;">正文内容……</span>
</section>
```

#### 卡片/盒子

```html
<section style="box-sizing:border-box;background:#e8f0f5;border:1px dashed #9EC0DB;border-radius:12px;padding:10px 14px;margin-bottom:10px;">
  <p style="box-sizing:border-box;font-size:14px;font-weight:700;margin-bottom:6px;color:#0d9488;"><span leaf="" style="box-sizing:border-box;">☁️ 白话版</span></p>
  <p style="box-sizing:border-box;font-size:14px;line-height:22px;color:#3f3f46;font-weight:400;margin:0px;"><span leaf="" style="box-sizing:border-box;">内容</span></p>
</section>
```

#### 标签列表（含标签间距）

```html
<section style="box-sizing:border-box;display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">
  <span style="box-sizing:border-box;display:inline-flex;align-items:center;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:500;background:#fef2f2;color:#dc2626;border:1px solid #fecaca;"><span leaf="" style="box-sizing:border-box;">#标签</span></span>
</section>
```

> **标签间距说明**：若容器 `gap` 不可靠，直接在标签 `<span>` 上用 `margin-right:5px` 控制间距。❌ 不要插入空内容的 `<span style="width:5px;">` ，公众号会忽略无文字内容的空标签宽度。

```html
<!-- ✅ 正确：margin 直接加在标签元素上 -->
<span style="...;margin-right:5px;"><span leaf="" style="box-sizing:border-box;">#标签A</span></span>
<span style="..."><span leaf="" style="box-sizing:border-box;">#标签B</span></span>

<!-- ❌ 错误：空 span 撑间距，公众号不生效 -->
<span style="..."><span leaf="" style="box-sizing:border-box;">#标签A</span></span>
<span style="display:inline-block;width:5px;"></span>
<span style="..."><span leaf="" style="box-sizing:border-box;">#标签B</span></span>
```

#### 宋体标题

```html
<h3 style="box-sizing:border-box;margin-bottom:10px;font-size:20px;font-weight:700;line-height:1.25;color:#0a0a0a;text-decoration:underline;font-family:'Songti SC','SimSun',Georgia,serif;">
  <span leaf="" style="box-sizing:border-box;">标题文字</span>
</h3>
```

---

### 11. 不推荐写法

```html
<!-- ❌ 不要用 <div> 作为 flex 容器 -->
<div style="display:flex;justify-content:space-between;">

<!-- ❌ 不要用 rgba() -->
<section style="background:rgba(158,192,219,0.12);">

<!-- ❌ 不要依赖伪元素 -->
<style>.item::before { content: '·'; }</style>

<!-- ❌ 不要只用 class 不写内联（公众号删除 <style> 后 class 失效） -->
<div class="card">

<!-- ❌ 不要在 <p> 上用无单位 line-height -->
<p style="line-height:1.6;">

<!-- ❌ 不要保留完整 HTML 页面结构 -->
<!DOCTYPE html><html><head>...</head><body>...</body></html>

<!-- ❌ 不要用 font-family 只写在 <style> 中 -->
<style>h3 { font-family: 'Songti SC'; }</style>

<!-- ❌ 不要用空内容 span 撑行内间距 -->
<span style="display:inline-block;width:5px;"></span>

<!-- ❌ 不要用纯装饰性 span 包裹 emoji，直接内联到文本即可 -->
<div class="insight-label"><span class="insight-icon">☁️</span> 白话版</div>
<!-- ✅ 应改为 -->
<section style="...">☁️ 白话版</section>
```

---

### 12. 文件结构建议

| 文件 | 用途 |
|------|------|
| `create.html` | 面向公众号，纯内联样式，无 `<html>`/`<head>`/`<body>`/`<style>`/`class` |
| `preview.html` | 面向浏览器预览，完整 HTML 结构 + `<style>` + class 写法，方便开发调试 |

---

### 13. 测试流程

1. 在浏览器中打开 `preview.html` 预览效果
2. 全选复制 `create.html` 内容
3. 粘贴到微信公众号编辑器
4. 对比公众号渲染效果，调整不兼容的样式
5. 重点关注：flex 布局、背景色、边框、圆角、字体、行间距

---

### 14. Jinja2 模板工程实践（.j2）

当 `create.html` 需要由数据动态生成时，推荐维护一个 `.html.j2` 模板文件，通过 Jinja2 渲染输出最终的公众号内联 HTML。

**三层文件结构**：

| 文件 | 用途 |
|------|------|
| `briefing.html` | 面向浏览器预览，完整 HTML + `<link>` 引用 `style.css` + class 写法 |
| `create.html` | 面向公众号，纯内联样式，无 `<html>`/`<head>`/`<body>`/`<style>`/`class`，可手动维护 |
| `briefing-template-wechat-inline.html.j2` | 面向自动化生成，Jinja2 模板，输出与 `create.html` 等价的内联 HTML |

**模板编写要点**：

- 所有样式仍然遵循内联规范（无 `class`、无 `<style>`、无 `rgba()`、无 `gap`）
- 标签间距通过在 `<span>` 上传入 `extra_style` 参数（如 `margin-right:5px`）控制，不插入空节点
- Jinja2 macro 中使用 `loop.cycle()` 交替颜色，使用 `loop.first` / `loop.last` 控制边界间距

```jinja
{%- macro tag_span(label, color, extra_style='') -%}
<span style="...;{{ extra_style }}"><span leaf="" style="box-sizing:border-box;">#{{ label }}</span></span>
{%- endmacro -%}

{%- for tag in it.vertical_tags -%}
{{ tag_span(tag, loop.cycle('blue', 'green'), 'margin-right:5px;' if not loop.last else '') }}
{%- endfor -%}
```
