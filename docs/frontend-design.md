# AI 前沿日报 - 前端网站技术设计文档

> 分支：`feat/frontend-website`  
> 日期：2026-05-20  
> 状态：Draft

---

## 1. 项目概述

为 AI 前沿日报（ai-frontier-daily）构建一个现代化的 Web 展示页面，将每日生成的 Markdown 简报以美观、交互友好的方式呈现给用户，同时提供历史日报的浏览、搜索和订阅能力。

### 1.1 核心目标

- **快速首屏加载**：LCP < 1.5s（国内 CDN + SSG）
- **SEO 友好**：搜索引擎可索引每日日报内容
- **响应式**：移动端 / 平板 / 桌面端全适配
- **极简运维**：静态站点部署，零服务器成本

### 1.2 功能范围

| P0（MVP） | P1（增强） | P2（远期） |
|-----------|-----------|-----------|
| 每日日报展示 | 全文搜索（标题/摘要） | RSS 输出 |
| 历史日报归档 | 按板块筛选 | 邮件订阅 |
| 板块导航（5 大板块） | 深色模式 | 阅读量统计 |
| 响应式布局 | 热度排行 | 多语言 |
| | PWA 离线支持 | |

---

## 2. 技术选型

### 2.1 推荐方案：Next.js 15 (App Router) + Tailwind CSS

| 层面 | 选型 | 理由 |
|------|------|------|
| **框架** | Next.js 15 (App Router) | SSG 静态生成 + ISR 增量更新，SEO 天然支持 |
| **样式** | Tailwind CSS 4 | 原子化 CSS，零运行时，开发效率高 |
| **部署** | Vercel / Cloudflare Pages | 免费 HTTPS + 全球 CDN + 自动部署 |
| **内容源** | summary.json（现有产物） | 直接复用 Pipeline 输出，无需新增 CMS |
| **语言** | TypeScript | 类型安全 |
| **包管理** | pnpm | 快速、省磁盘 |

### 2.2 数据流

```
Pipeline 产出 (output/{DATE}/summary.json)
        ↓
  scripts/build-index.ts  ← 新增：扫描所有 summary.json，生成索引
        ↓
  content/index.json  ← 全量索引（日期列表、板块统计、搜索索引）
        ↓
  Next.js SSG  ← 构建时读取 content/index.json
        ↓
  静态 HTML + JSON  ← 部署到 CDN
```

### 2.3 为什么不用其他方案？

| 方案 | 不选原因 |
|------|---------|
| Nuxt.js | Python 生态为主，Node.js 社区更大（Vercel 部署更顺） |
| Astro | 功能够用但生态稍小，Next.js ISR 对日报场景更实用 |
| 纯静态 HTML | 无组件化，维护成本高，搜索/筛选难做 |
| WordPress / CMS | 杀鸡用牛刀，内容源已有 JSON 产物 |

---

## 3. 系统架构

### 3.1 目录结构

```
web/
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── public/
│   ├── favicon.ico
│   └── og/                    # OG 图片模板
├── content/
│   └── index.json             # 构建时生成的索引文件
├── src/
│   ├── app/
│   │   ├── layout.tsx         # 根布局（Header / Footer）
│   │   ├── page.tsx           # 首页（最新日报）
│   │   ├── archive/
│   │   │   └── page.tsx       # 历史归档页
│   │   ├── [date]/
│   │   │   └── page.tsx       # 每日日报详情页（SSG）
│   │   └── api/
│   │       └── search/
│   │           └── route.ts   # 搜索 API（ISR 期间可用）
│   ├── components/
│   │   ├── BriefingCard.tsx   # 新闻卡片
│   │   ├── SectionNav.tsx     # 板块导航
│   │   ├── HotTag.tsx         # 热度标签 🔥
│   │   ├── SearchBar.tsx      # 搜索框
│   │   ├── ArchiveList.tsx    # 归档列表
│   │   └── Footer.tsx         # 页脚
│   ├── lib/
│   │   ├── content.ts         # 读取 summary.json 的工具函数
│   │   ├── types.ts           # TypeScript 类型定义
│   │   └── search.ts          # 搜索索引（FlexSearch / MiniSearch）
│   └── styles/
│       └── globals.css
├── scripts/
│   └── build-index.ts         # 扫描 output/ 生成 content/index.json
└── tests/
    └── build-index.test.ts
```

### 3.2 页面路由

| 路由 | 说明 | 渲染方式 |
|------|------|---------|
| `/` | 首页，展示最新日报 | SSG + ISR（每小时） |
| `/[date]` | 日报详情页（如 `/2026-05-20`） | SSG（按日期生成） |
| `/archive` | 历史归档列表 | SSG + ISR |
| `/api/search?q=xxx` | 搜索接口 | API Route |

---

## 4. 核心模块设计

### 4.1 内容索引构建（build-index.ts）

负责扫描 `output/*/summary.json`，生成统一索引：

```typescript
// content/index.json 结构
interface ContentIndex {
  dates: string[];                    // 所有日报日期，倒序
  latest: string;                     // 最新日期
  stats: {
    totalArticles: number;
    totalDates: number;
    sectionStats: Record<string, number>;
  };
  articles: ArticleMeta[];            // 用于搜索的轻量索引
}

interface ArticleMeta {
  date: string;
  title: string;
  headline: string;
  main_section: string;
  sub_section: string;
  source: string;
  hot: string;
  url: string;
  vertical_tags: string[];
  general_tags: string[];
}
```

### 4.2 数据类型定义（types.ts）

直接映射现有 `SummaryItem` 的数据结构：

```typescript
interface SummaryItem {
  title: string;
  headline: string;
  url: string;
  source: string;
  summary: string;
  plain_explain: string;
  impacts: string[];
  digest_for_outline: string;
  main_section: string;
  sub_section: string;
  vertical_tags: string[];
  general_tags: string[];
  hot: string;              // 🔥 / 🔥🔥 / 🔥🔥🔥
  relevance: number;
  hot_level: number;
  rank: number;
  pub_time: string;
}

interface BriefingData {
  date: string;
  items: SummaryItem[];
  header: {
    date_str: string;
    coverage_line: string;
    data_sources: string;
    header_tag: string;
  };
  footer: Record<string, string[]>;
}
```

### 4.3 页面设计

#### 首页（/）

```
┌─────────────────────────────────────────────┐
│  🤖 AI 前沿日报                    🔍 搜索   │
├─────────────────────────────────────────────┤
│                                             │
│  📅 2026-05-20 · AI 前沿早报               │
│  数据来源：36氪 · 雷锋网 · IT之家 ...        │
│                                             │
│  ┌─── 板块导航 ───────────────────────┐     │
│  │ 全部 | AI基石 | 大模型 | 智能体 | ...│     │
│  └────────────────────────────────────┘     │
│                                             │
│  ┌─ 新闻卡片 ────────────────────────┐     │
│  │ 1.1 标题 🔥🔥                     │     │
│  │ #垂类标签 #通用标签                │     │
│  │ 概要...                           │     │
│  │ 🌱 白话解释...                    │     │
│  │ 🎯 影响：... / ...                │     │
│  │ [来源：标题 → 原文链接]            │     │
│  └────────────────────────────────────┘     │
│                                             │
│  ... 更多卡片 ...                           │
│                                             │
│  📅 历史日报                                │
│  [2026-05-19] [2026-05-18] [2026-05-17]     │
│                                             │
├─────────────────────────────────────────────┤
│  GitHub · RSS · 关于                         │
└─────────────────────────────────────────────┘
```

### 4.4 搜索方案

使用 **MiniSearch**（纯前端，< 10KB gzip），在客户端做全文搜索：

- 构建时生成搜索索引（articles 数组）
- 首页加载后初始化 MiniSearch
- 支持中文分词（simple tokenizer + 前缀匹配）
- 搜索范围：标题 + 概要 + 白话解释 + 标签

---

## 5. 部署方案

### 5.1 CI/CD 流程

```
Pipeline 完成 (news_frontier.py)
    ↓
  output/{DATE}/summary.json 产出
    ↓
  GitHub Push / Webhook 触发
    ↓
  Vercel Build:
    1. scripts/build-index.ts → content/index.json
    2. next build (SSG)
    ↓
  Vercel Deploy → CDN
    ↓
  ISR: 首页每小时重新验证
```

### 5.2 部署配置

```typescript
// next.config.ts
const nextConfig = {
  output: 'export',              // 纯静态导出（可选，也可用 Vercel 原生）
  images: { unoptimized: true }, // 静态导出时关闭图片优化
};
```

### 5.3 域名建议

- 主域名：`daily.yourdomain.com` 或 `ai-daily.yourdomain.com`
- GitHub Pages 备选：`yourname.github.io/ai-frontier-daily`

---

## 6. 性能优化策略

| 策略 | 说明 | 预期效果 |
|------|------|---------|
| **SSG** | 构建时生成 HTML，零服务器渲染 | LCP < 1s |
| **ISR** | 首页每小时增量更新 | 内容及时 |
| **图片懒加载** | Next.js Image + loading="lazy" | 减少 FCP |
| **代码分割** | App Router 自动按路由分割 | JS bundle < 100KB |
| **字体优化** | next/font 自动子集化 | CLS = 0 |
| **Gzip/Brotli** | CDN 自动压缩 | 传输大小 -70% |

---

## 7. 开发计划

### Phase 1：MVP（1-2 周）

1. 项目初始化（Next.js + Tailwind + TypeScript）
2. 实现 `build-index.ts`（读取 summary.json 生成索引）
3. 实现日报详情页 `/[date]`
4. 实现首页 `/`（最新日报展示）
5. 板块导航 + 响应式布局
6. 部署到 Vercel

### Phase 2：增强（第 3 周）

1. 客户端全文搜索（MiniSearch）
2. 历史归档页
3. 深色模式
4. OG 图片自动生成
5. SEO meta tags

### Phase 3：远期

1. RSS 输出
2. PWA 离线支持
3. 邮件订阅
4. 多语言

---

## 8. 关键文件对应关系

| 现有 Pipeline 产物 | 前端使用方式 |
|-------------------|-------------|
| `output/{DATE}/summary.json` | 页面数据源，`content.ts` 读取 |
| `output/{DATE}/briefing.md` | 可选，用于 SEO meta description |
| `project-space/config/config.yaml` | 板块定义、标签白名单（构建时读取） |
| `project-space/utils/domain.py` | `types.ts` 的类型映射参考 |

---

## 9. 数据源配置

### 9.1 飞书多维表格（当前数据源）

项目现已从飞书多维表格读取数据，数据源信息：

| 参数 | 值 | 说明 |
|------|-----|------|
| **多维表格 URL** | `https://ucni7p523jc2.feishu.cn/wiki/UViYwBDsqix41Skaldrcs8DbnGg` | 多维表格入口 |
| **app_token** | `UViYwBDsqix41Skaldrcs8DbnGg` | 多维表格应用标识 |
| **table_id** | `tbldczSnB4TNDAOc` | 数据表标识 |
| **view_id** | `vewUyeyQkO` | 默认视图标识 |

### 9.2 环境变量配置

在 `web/.env.local` 文件中配置：

```bash
# 飞书应用凭证（必填）
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 多维表格配置（必填）
FEISHU_BITABLE_APP_TOKEN=UViYwBDsqix41Skaldrcs8DbnGg
FEISHU_BITABLE_TABLE_ID=tbldczSnB4TNDAOc

# 可选配置
FEISHU_BITABLE_VIEW_ID=vewUyeyQkO          # 默认视图 ID
FEISHU_API_TIMEOUT=30000                   # API 请求超时时间
FEISHU_TOKEN_CACHE_TTL=7200000             # Token 缓存时间（2小时）
```

**如何获取飞书凭证**：

1. 在飞书开发者平台创建应用
2. 申请 `bitable:app` 和 `bitable:table:readonly` 权限
3. 在多维表格中添加应用为协作者
4. 复制 `App ID` 和 `App Secret`

---

## 10. 快速启动

```bash
# 1. 进入 web 目录
cd web

# 2. 安装依赖
pnpm install

# 3. 配置环境变量
cp .env.local.example .env.local
# 编辑 .env.local，填入飞书凭证

# 4. 启动开发服务器
pnpm dev

# 5. 打开 http://localhost:3000
```

---

## 11. 附录：技术栈版本

| 依赖 | 版本 |
|------|------|
| Next.js | 15.x |
| React | 19.x |
| TypeScript | 5.x |
| Tailwind CSS | 4.x |
| MiniSearch | 7.x |
| pnpm | 9.x |
| Node.js | >= 20 |
