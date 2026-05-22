# AI 前沿日报 - 项目技术文档

> 项目名称：AI Frontier Daily  
> 最后更新：2026-05-22  
> 文档版本：v1.0

---

## 📋 目录

- [1. 项目概述](#1-项目概述)
- [2. 技术栈](#2-技术栈)
- [3. 项目结构](#3-项目结构)
- [4. 编码规范](#4-编码规范)
- [5. 核心模块说明](#5-核心模块说明)
- [6. 数据流](#6-数据流)
- [7. 环境配置](#7-环境配置)
- [8. 开发工作流](#8-开发工作流)
- [9. 部署](#9-部署)
- [10. 常见问题](#10-常见问题)

---

## 1. 项目概述

### 1.1 项目简介

AI 前沿日报是一个自动化聚合中文 AI 领域要闻的 Web 应用，每日生成结构化的日报内容，涵盖大模型、智能体、算力、垂直应用、产业观察等板块。

### 1.2 核心特性

- ✅ **自动化生成**：基于 LLM 自动整理和分类新闻
- ✅ **多维表格存储**：使用飞书多维表格作为数据源
- ✅ **现代化前端**：Next.js 15 + Tailwind CSS 3
- ✅ **响应式设计**：完美适配移动端 / 平板 / 桌面端
- ✅ **深色模式**：支持系统主题切换
- ✅ **SEO 友好**：SSG 静态生成 + 元数据优化
- ✅ **高性能**：LCP < 1.5s，全局缓存策略

### 1.3 板块分类

| Key | 名称 | 说明 |
|-----|------|------|
| `foundation` | AI 基石与算力 | 芯片、算力、基础设施 |
| `core_tech` | 大模型与核心技术 | 模型架构、训练、推理 |
| `agent` | AI 智能体与交互 | Agent、多模态、交互 |
| `vertical` | AI+ 垂直应用 | 医疗、教育、金融等 |
| `industry` | AI 产业与观察 | 政策、投资、趋势 |

---

## 2. 技术栈

### 2.1 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Next.js** | 16.2.6 | React 框架，SSG/ISR 支持 |
| **React** | 19.2.4 | UI 库 |
| **TypeScript** | 5.x | 类型安全 |
| **Tailwind CSS** | 3.x | 原子化 CSS 框架 |
| **next-themes** | 0.4.6 | 深色模式支持 |
| **lucide-react** | 1.16.0 | 图标库 |
| **date-fns** | 4.2.1 | 日期处理 |
| **clsx** | 2.1.1 | 条件类名 |
| **tailwind-merge** | 3.6.0 | Tailwind 类名合并 |

### 2.2 后端/数据源

| 技术 | 用途 |
|------|------|
| **飞书多维表格 API** | 数据存储和查询 |
| **飞书开放平台** | 认证和授权 |

### 2.3 开发工具

| 工具 | 用途 |
|------|------|
| **pnpm** | 包管理器 |
| **ESLint** | 代码检查 |
| **TypeScript** | 类型检查 |
| **Vercel** | 部署平台 |

---

## 3. 项目结构

```
ai-frontier-daily/
├── web/                           # 前端项目
│   ├── src/
│   │   ├── app/                   # Next.js App Router
│   │   │   ├── layout.tsx         # 根布局
│   │   │   ├── page.tsx           # 首页（最新日报）
│   │   │   ├── [date]/            # 动态路由：日报详情页
│   │   │   │   └── page.tsx
│   │   │   ├── archive/           # 归档页
│   │   │   │   └── page.tsx
│   │   │   ├── globals.css        # 全局样式
│   │   │   └── favicon.ico
│   │   ├── components/            # React 组件
│   │   │   ├── BriefingCard.tsx   # 新闻卡片
│   │   │   ├── SectionNav.tsx     # 板块导航
│   │   │   ├── Header.tsx         # 页头
│   │   │   ├── Footer.tsx         # 页脚
│   │   │   ├── HotTag.tsx         # 热度标签
│   │   │   ├── ArchiveList.tsx    # 归档列表
│   │   │   └── ThemeToggle.tsx    # 主题切换
│   │   └── lib/                   # 工具库
│   │       ├── types.ts           # TypeScript 类型定义
│   │       ├── content.ts         # 内容获取和缓存
│   │       ├── feishu.ts          # 飞书 API 封装
│   │       ├── utils.ts           # 工具函数
│   │       └── mock-data.ts       # Mock 数据
│   ├── public/                    # 静态资源
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── postcss.config.mjs
│   └── tailwind.config.ts
├── project-space/                 # Python 数据处理
├── scripts/                       # 脚本工具
├── docs/                          # 文档
└── config/                        # 配置文件
```

---

## 4. 编码规范

### 4.1 TypeScript 规范

#### 4.1.1 类型定义

所有类型定义统一放在 `src/lib/types.ts`：

```typescript
// ✅ 正确：使用 interface 定义对象类型
export interface NewsItem {
  title: string;
  url: string;
  source: string;
  summary: string;
  // ...
}

// ✅ 正确：使用 type 定义联合类型
export type SectionKey =
  | "foundation"
  | "core_tech"
  | "agent"
  | "vertical"
  | "industry";

// ✅ 正确：使用 Record 定义映射类型
export const SECTION_LABELS: Record<SectionKey, string> = {
  foundation: "AI 基石与算力",
  core_tech: "大模型与核心技术",
  // ...
};
```

#### 4.1.2 函数类型

```typescript
// ✅ 正确：明确参数和返回类型
export async function getBriefingAsync(
  date: string
): Promise<Briefing | null> {
  const briefings = await getBriefingsMap();
  return briefings[date] ?? null;
}

// ✅ 正确：使用类型守卫
export function isBriefingSummary(
  item: BriefingSummary | null
): item is BriefingSummary {
  return item !== null;
}
```

### 4.2 React 组件规范

#### 4.2.1 组件结构

```typescript
// ✅ 正确的组件结构
import { ExternalLink } from "lucide-react";
import type { NewsItem } from "@/lib/types";
import { HotTag } from "./HotTag";

interface BriefingCardProps {
  item: NewsItem;
  index: number;
}

export function BriefingCard({ item, index }: BriefingCardProps) {
  // 1. 辅助函数
  function formatPubTime(pubTime: string): string {
    const match = pubTime.match(/(\d{2}:\d{2})/);
    return match ? match[1] : "";
  }

  // 2. 数据处理
  const time = formatPubTime(item.daily_report_time);
  const tags = [...(item.vertical_tags ?? []), ...(item.general_tags ?? [])];

  // 3. 渲染
  return (
    <article className="card group p-5 sm:p-6">
      {/* JSX 内容 */}
    </article>
  );
}
```

#### 4.2.2 Props 定义

```typescript
// ✅ 正确：使用 interface 定义 props
interface SectionNavProps {
  items: SectionNavItem[];
}

export function SectionNav({ items }: SectionNavProps) {
  // ...
}

// ✅ 正确：导出 props 类型供外部使用
export interface SectionNavItem {
  key: SectionKey | "all";
  label: string;
  count: number;
}
```

#### 4.2.3 客户端组件

```typescript
// ✅ 正确：使用 "use client" 标记客户端组件
"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  // ...
}
```

### 4.3 样式规范

#### 4.3.1 Tailwind CSS 类名

```typescript
// ✅ 正确：使用 cn() 合并类名
import { cn } from "@/lib/utils";

<div className={cn(
  "base-class",
  isActive && "active-class",
  "other-class"
)} />

// ✅ 正确：使用响应式前缀
<div className="text-sm sm:text-base lg:text-lg" />

// ✅ 正确：使用深色模式前缀
<div className="bg-white dark:bg-gray-900" />
```

#### 4.3.2 自定义类名

```typescript
// ✅ 正确：在 globals.css 中定义自定义类
.term-block {
  @apply overflow-hidden px-4 py-3.5 bg-surface-subtle border border-line-subtle;
}

// ✅ 正确：使用语义化类名
.card {
  @apply p-5 sm:p-6 border border-line-subtle rounded-lg;
}
```

### 4.4 命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 组件 | PascalCase | `BriefingCard`, `SectionNav` |
| 函数 | camelCase | `getBriefingAsync`, `formatDate` |
| 常量 | UPPER_SNAKE_CASE | `SECTION_ORDER`, `CACHE_TTL` |
| 接口/类型 | PascalCase | `NewsItem`, `BriefingSummary` |
| 文件名 | PascalCase (组件) / kebab-case (工具) | `BriefingCard.tsx`, `content.ts` |

### 4.5 注释规范

```typescript
// ✅ 单行注释：解释复杂逻辑
const CACHE_TTL = 5 * 60 * 1000; // 5 分钟缓存

// ✅ 多行注释：函数说明
/**
 * 将飞书记录转换为 NewsItem
 * @param record - 飞书多维表格记录
 * @returns 转换后的新闻项
 */
function mapRecordToNewsItem(record: { fields: BitableFields }): NewsItem {
  // ...
}

// ✅ 分区注释：代码组织
// ── 缓存：避免每次请求都调飞书 API ────────────────────────────────────
let _briefingsCache: Record<string, Briefing> | null = null;
```

---

## 5. 核心模块说明

### 5.1 类型系统 (`src/lib/types.ts`)

定义了所有核心数据类型：

```typescript
// 板块类型
export type SectionKey =
  | "foundation"
  | "core_tech"
  | "agent"
  | "vertical"
  | "industry";

// 新闻项
export interface NewsItem {
  title: string;
  url: string;
  source: string;
  summary: string;
  pub_time: string;
  daily_report_time: string;
  main_section: string;
  sub_section: string;
  relevance: number;
  hot_level: number;
  rank: number;
  headline: string;
  plain_explain: string;
  impacts: string[];
  digest_for_outline: string;
  vertical_tags: string[];
  general_tags: string[];
  hot: string;
}

// 日报
export interface Briefing {
  items: NewsItem[];
  blocks: BriefingBlocks;
}
```

### 5.2 内容获取 (`src/lib/content.ts`)

核心数据获取模块，支持飞书 API 和 Mock 数据：

```typescript
// 获取所有日期
export async function getAllDatesAsync(): Promise<string[]>

// 获取指定日期的日报
export async function getBriefingAsync(date: string): Promise<Briefing | null>

// 获取最新日报
export async function getLatestBriefingAsync(): Promise<Briefing | null>

// 按板块分组
export function groupBySection(items: NewsItem[]): Record<SectionKey, NewsItem[]>

// 获取日报摘要
export async function getBriefingSummaryAsync(date: string): Promise<BriefingSummary | null>
```

**缓存策略**：
- 内存缓存：5 分钟 TTL
- React cache：缓存函数调用结果
- Fallback：飞书 API 失败时使用 Mock 数据

### 5.3 飞书 API (`src/lib/feishu.ts`)

飞书多维表格 API 封装：

```typescript
// 获取访问令牌（带缓存）
async function getFeishuToken(): Promise<string>

// 获取记录列表
export async function fetchBitableRecords(options?: {
  viewId?: string;
  pageSize?: number;
  pageToken?: string;
}): Promise<{ items: any[]; hasMore: boolean; pageToken: string }>

// 一次性拉取所有分页数据
export async function fetchAllBitableRecords(options?: {
  viewId?: string;
}): Promise<any[]>
```

**环境变量**：
- `FEISHU_APP_ID`：飞书应用 ID
- `FEISHU_APP_SECRET`：飞书应用密钥
- `FEISHU_BITABLE_APP_TOKEN`：多维表格 app_token
- `FEISHU_BITABLE_TABLE_ID`：数据表 table_id
- `FEISHU_BITABLE_VIEW_ID`：视图 ID（可选）

### 5.4 组件库

#### 5.4.1 BriefingCard

新闻卡片组件，展示单条新闻：

```typescript
interface BriefingCardProps {
  item: NewsItem;  // 新闻数据
  index: number;   // 序号（用于显示排名）
}
```

**特性**：
- 终端风格序号徽章
- 热度标签（HotTag）
- 子板块标签
- 简要说明（plain_explain）
- 影响列表（impacts）
- 标签展示

#### 5.4.2 SectionNav

板块导航组件，支持滚动监听：

```typescript
interface SectionNavProps {
  items: SectionNavItem[];
}

interface SectionNavItem {
  key: SectionKey | "all";
  label: string;
  count: number;
}
```

**特性**：
- Intersection Observer 滚动监听
- 平滑滚动定位
- 响应式设计
- 计数徽章

#### 5.4.3 Header

页头组件，包含 Logo 和主题切换：

```typescript
export function Header() {
  // 包含 Logo、主题切换按钮
}
```

#### 5.4.4 Footer

页脚组件，显示版权信息：

```typescript
export function Footer() {
  // 包含版权、链接
}
```

#### 5.4.5 HotTag

热度标签组件，根据 hot_level 显示不同样式：

```typescript
interface HotTagProps {
  hot: string;      // 热度文本（如 "🔥 热度 3"）
  level: number;    // 热度等级（1-5）
}
```

---

## 6. 数据流

### 6.1 数据获取流程

```
用户请求页面
    ↓
getLatestBriefingAsync()
    ↓
getBriefingsMap() [检查缓存]
    ↓
缓存未命中 → fetchAllBitableRecords()
    ↓
飞书 API 调用
    ↓
buildBriefingsFromRecords() [数据转换]
    ↓
groupBySection() [按板块分组]
    ↓
渲染组件
```

### 6.2 数据转换

```typescript
// 飞书记录 → NewsItem
{
  fields: {
    title: "xxx",
    url: "xxx",
    // ...
  }
}
    ↓ mapRecordToNewsItem()
{
  title: "xxx",
  url: "xxx",
  main_section: "AI 基石与算力",
  // ...
}
    ↓ groupBySection()
{
  foundation: [NewsItem, ...],
  core_tech: [NewsItem, ...],
  // ...
}
```

### 6.3 缓存策略

| 层级 | 缓存位置 | TTL | 说明 |
|------|----------|-----|------|
| 飞书 Token | 内存变量 | expire - 300s | 提前 5 分钟过期 |
| 日报数据 | 内存变量 | 5 分钟 | 避免频繁调用 API |
| 函数调用 | React cache | 构建周期 | SSG 期间缓存结果 |

---

## 7. 环境配置

### 7.1 环境变量

在 `web/.env.local` 中配置：

```bash
# 飞书应用凭证
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 多维表格配置
FEISHU_BITABLE_APP_TOKEN=UViYwBDsqix41Skaldrcs8DbnGg
FEISHU_BITABLE_TABLE_ID=tbldczSnB4TNDAOc
FEISHU_BITABLE_VIEW_ID=vewUyeyQkO  # 可选
```

### 7.2 获取飞书凭证

1. **创建飞书应用**
   - 访问 [飞书开放平台](https://open.feishu.cn/)
   - 创建自建应用
   - 获取 `App ID` 和 `App Secret`

2. **配置权限**
   - 开启"根据条件搜索记录"权限
   - 或开启"查看、评论、编辑和管理 Base"权限

3. **获取多维表格信息**
   - 从多维表格 URL 提取：
     ```
     https://{tenant}.feishu.cn/wiki/{app_token}?table={table_id}&view={view_id}
     ```
   - `app_token`：`UViYwBDsqix41Skaldrcs8DbnGg`
   - `table_id`：`tbldczSnB4TNDAOc`
   - `view_id`：`vewUyeyQkO`（可选）

---

## 8. 开发工作流

### 8.1 本地开发

```bash
# 进入 web 目录
cd web

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 访问 http://localhost:3000
```

### 8.2 构建生产版本

```bash
# 构建静态站点
pnpm build

# 本地预览生产版本
pnpm start
```

### 8.3 代码检查

```bash
# 运行 ESLint
pnpm lint
```

### 8.4 Git 工作流

```bash
# 创建功能分支
git checkout -b feature/your-feature

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送分支
git push origin feature/your-feature

# 创建 Pull Request
```

**Commit 规范**：
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建/工具

---

## 9. 部署

### 9.1 Vercel 部署

1. **连接 GitHub 仓库**
   - 在 Vercel 中导入项目
   - 选择 `web` 目录作为根目录

2. **配置环境变量**
   - 在 Vercel 项目设置中添加环境变量
   - 参考第 7.1 节

3. **自动部署**
   - 推送到 main 分支自动触发部署
   - Vercel 提供 HTTPS 和全球 CDN

### 9.2 性能优化

| 优化项 | 说明 | 效果 |
|--------|------|------|
| SSG | 静态生成 HTML | 首屏加载快 |
| ISR | 增量静态再生成 | 内容更新快 |
| 缓存 | React cache + 内存缓存 | 减少 API 调用 |
| 图片优化 | Next.js Image | 自动优化图片 |
| 字体优化 | next/font | 自动优化字体 |

### 9.3 SEO 优化

```typescript
// layout.tsx 中的元数据配置
export const metadata: Metadata = {
  title: {
    default: "AI 前沿日报 · AI Frontier Daily",
    template: "%s · AI 前沿日报",
  },
  description: "每日聚合中文 AI 领域要闻...",
  keywords: ["AI 早报", "AI 日报", "大模型", ...],
  openGraph: {
    title: "AI 前沿日报",
    description: "每日聚合中文 AI 领域要闻...",
    type: "website",
    locale: "zh_CN",
  },
};
```

---

## 10. 常见问题

### 10.1 飞书 API 调用失败

**问题**：`飞书多维表格读取失败 (xxx): xxx`

**解决方案**：
1. 检查环境变量是否正确配置
2. 检查飞书应用权限是否开启
3. 检查多维表格是否对应用开放访问权限
4. 查看飞书开放平台日志

### 10.2 缓存问题

**问题**：数据更新后页面未刷新

**解决方案**：
1. 等待 5 分钟缓存过期
2. 重启开发服务器
3. 清除 Next.js 缓存：`rm -rf .next`

### 10.3 样式问题

**问题**：Tailwind 类名不生效

**解决方案**：
1. 检查 `tailwind.config.ts` 配置
2. 检查 `postcss.config.mjs` 配置
3. 重启开发服务器
4. 检查类名拼写是否正确

### 10.4 类型错误

**问题**：TypeScript 类型检查失败

**解决方案**：
1. 检查 `types.ts` 中类型定义
2. 使用 `as` 类型断言（谨慎使用）
3. 检查飞书 API 返回的数据结构
4. 运行 `pnpm lint` 查看详细错误

---

## 附录

### A. 相关文档

- [前端设计文档](./frontend-design.md)
- [飞书多维表格 API 指南](./feishu-bitable-api-guide.md)
- [关键词去重设计](./keyword-dedup-design.md)

### B. 外部资源

- [Next.js 文档](https://nextjs.org/docs)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [飞书开放平台](https://open.feishu.cn/)
- [TypeScript 文档](https://www.typescriptlang.org/docs/)

### C. 联系方式

如有问题，请联系项目维护者。