# 飞书多维表格查询接口技术指南

> 文档版本：v1.0  
> 日期：2026-05-22  
> 适用场景：AI 前沿日报前端数据查询

---

## 1. 当前数据结构分析

### 1.1 数据源信息

根据提供的 URL 提取关键配置：

| 参数 | 值 | 说明 |
|------|-----|------|
| **Base URL** | `https://ucni7p523jc2.feishu.cn/wiki/UViYwBDsqix41Skaldrcs8DbnGg` | 多维表格入口 |
| **app_token** | `UViYwBDsqix41Skaldrcs8DbnGg` | 多维表格应用标识 |
| **table_id** | `tbldczSnB4TNDAOc` | 数据表标识 |
| **view_id** | `vewUyeyQkO` | 默认视图标识 |

### 1.2 数据字段概览

基于项目现有代码和典型日报数据结构，表格包含以下关键字段：

| 字段名 | 类型 | 说明 | 查询价值 |
|--------|------|------|----------|
| `date` / `pub_time` | string (YYYY-MM-DD) | 发布日期 | **高** - 按日期查询 |
| `main_section` | string | 主板块（AI基石/大模型/智能体/垂直应用/产业观察） | **高** - 按板块筛选 |
| `sub_section` | string | 子板块 | 中 |
| `vertical_tags` | array/string | 垂类标签 | **高** - 标签筛选 |
| `general_tags` | array/string | 通用标签 | **高** - 标签筛选 |
| `hot` | string | 热度等级（🔥/🔥🔥/🔥🔥🔥） | **高** - 热度筛选 |
| `hot_level` | number | 热度数值 | **高** - 热度排序 |
| `relevance` | number | 相关度 | 中 |
| `rank` | number | 排序序号 | 中 |
| `source` | string | 数据来源 | **中** - 按来源筛选 |
| `title` | string | 标题 | **高** - 全文搜索 |

---

## 2. 飞书多维表格查询 API 详解

### 2.1 核心接口对比

飞书提供两种记录查询方式：

| 接口 | 适用场景 | 优势 |
|------|----------|------|
| **列出记录**（旧） | 简单遍历、全量拉取 | 接口简单，支持视图筛选 |
| **搜索记录**（新） | 关键词搜索、复杂筛选 | 支持复杂过滤、排序、字段选择 |

**推荐使用：搜索记录 API**（功能更强大，官方推荐）

---

### 2.2 搜索记录 API（推荐）

**接口地址**：`POST /open-apis/bitable/v1/apps/:app_token/tables/:table_id/records/search`

**官方文档**：https://open.feishu.cn/document/docs/bitable-v1/app-table-record/search

**核心特性**：
- ✅ 复杂过滤条件（`filter`）
- ✅ 自定义排序（`sort`）
- ✅ 分页支持（`page_size` / `page_token`）
- ✅ 字段选择（`field_names`）
- ✅ 支持视图筛选（`view_id`）

**频控限制**：20 次/秒

**权限要求**（开启任一即可）：
- 根据条件搜索记录
- 查看、评论、编辑和管理 Base
- 查看、评论和导出 Base

#### 请求参数

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `app_token` | string | 是 | 多维表格应用唯一标识符 |
| `table_id` | string | 是 | 数据表唯一标识符 |

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id_type` | string | 否 | 用户 ID 类型（open_id/union_id/user_id） |
| `page_token` | string | 否 | 分页标记 |
| `page_size` | int | 否 | 每页条数（最大 500，默认 20） |

**请求体参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `view_id` | string | 否 | 视图 ID（自动应用视图筛选规则） |
| `filter` | string | 否 | 筛选条件（JSON 字符串） |
| `sort` | string[] | 否 | 排序规则 |
| `field_names` | string[] | 否 | 指定返回字段 |

#### 筛选条件（filter）语法

**基础结构**：
```json
{
  "filter": {
    "conjunction": "and",
    "conditions": [
      {
        "field_name": "main_section",
        "operator": "is",
        "value": ["AI 基石与算力"]
      }
    ]
  }
}
```

**支持的操作符**：

| 操作符 | 说明 | 适用类型 |
|--------|------|----------|
| `is` | 等于 | 所有类型 |
| `isNot` | 不等于 | 除日期外 |
| `contains` | 包含 | 除日期外 |
| `doesNotContain` | 不包含 | 除日期外 |
| `isEmpty` | 为空 | 所有类型 |
| `isNotEmpty` | 不为空 | 所有类型 |
| `isGreater` | 大于 | 数字 |
| `isGreaterEqual` | 大于等于 | 除日期外 |
| `isLess` | 小于 | 数字 |
| `isLessEqual` | 小于等于 | 除日期外 |
| `like` | LIKE 匹配 | 文本 |
| `in` | IN 集合 | 暂未支持 |

**逻辑连接词**（`conjunction`）：
- `"and"`：所有条件都满足
- `"or"`：任一条件满足

**嵌套条件**（支持一层 children）：
```json
{
  "filter": {
    "conjunction": "and",
    "children": [
      {
        "conjunction": "or",
        "conditions": [
          { "field_name": "职位", "operator": "is", "value": ["高级销售员"] },
          { "field_name": "职位", "operator": "is", "value": ["初级销售员"] }
        ]
      },
      {
        "conjunction": "or",
        "conditions": [
          { "field_name": "销售额", "operator": "is", "value": ["10000"] },
          { "field_name": "销售额", "operator": "is", "value": ["20000"] }
        ]
      }
    ]
  }
}
```

#### 排序（sort）语法

```json
{
  "sort": ["hot_level DESC", "rank ASC"]
}
```

**说明**：
- 支持多字段排序，按顺序逐层排序
- `DESC`：降序，`ASC`：升序
- 不支持对公式字段和关联字段排序
- 参数长度不超过 1000 字符

---

### 2.3 列出记录 API（旧版，不推荐）

**接口地址**：`GET /bitable/v1/apps/:app_token/tables/:table_id/records`

**官方文档**：https://open.feishu.cn/document/server-docs/docs/bitable-v1/record/list

**说明**：该接口为历史接口，已不推荐使用，建议使用**搜索记录**接口替代。

**适用场景**：
- 简单遍历所有记录
- 使用预定义视图筛选

**参数**：
- `view_id`：视图 ID（自动应用视图的筛选规则）
- `filter`：筛选条件（格式参考下方筛选参数说明）
- `sort`：排序规则
- `field_names`：指定返回字段
- `page_size`：每页条数（1-500）

---

## 3. 推荐查询维度与实现方案

### 3.1 查询维度优先级

| 优先级 | 维度 | 典型场景 | API 参数 |
|--------|------|----------|----------|
| P0 | **按日期查询** | 获取某天的日报 | `filter: {date = "2026-05-22"}` |
| P0 | **按板块筛选** | 查看 AI 基石板块 | `filter: {main_section = "AI 基石与算力"}` |
| P1 | **按标签筛选** | 查看 LLM 相关内容 | `filter: {vertical_tags contains "LLM"}` |
| P1 | **按热度筛选** | 只看热门内容 | `filter: {hot_level >= 2}` |
| P2 | **按来源筛选** | 查看特定媒体来源 | `filter: {source = "36氪"}` |
| P2 | **全文搜索** | 搜索标题/摘要 | 需前端实现 |

### 3.2 接口设计建议

**方案一：通用查询接口（推荐）**

```typescript
interface BitableQueryOptions {
  // 基础筛选
  date?: string;                    // 精确日期 YYYY-MM-DD
  dateRange?: { start: string; end: string };  // 日期范围
  
  // 分类筛选
  mainSection?: string;             // 主板块
  subSection?: string;              // 子板块
  verticalTags?: string[];          // 垂类标签（包含任一）
  generalTags?: string[];           // 通用标签（包含任一）
  
  // 热度筛选
  minHotLevel?: number;             // 最小热度等级
  hotLevel?: number;                // 精确热度等级
  
  // 来源筛选
  source?: string;
  
  // 分页排序
  pageSize?: number;
  pageToken?: string;
  sortBy?: string;                  // 排序字段
  sortOrder?: 'asc' | 'desc';       // 排序方向
  
  // 字段选择
  fields?: string[];                // 只返回指定字段
}
```

---

## 4. 代码实现参考

### 4.1 环境变量配置

在项目根目录的 `.env.local` 文件中配置飞书多维表格的访问凭证：

```bash
# 飞书应用凭证
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 多维表格配置
FEISHU_BITABLE_APP_TOKEN=UViYwBDsqix41Skaldrcs8DbnGg
FEISHU_BITABLE_TABLE_ID=tbldczSnB4TNDAOc
```

**如何获取 app_token 和 table_id**：
1. 从飞书多维表格 URL 中提取
   - URL 格式：`https://{tenant}.feishu.cn/wiki/{app_token}?table={table_id}&view={view_id}`
   - 例如：`https://ucni7p523jc2.feishu.cn/wiki/UViYwBDsqix41Skaldrcs8DbnGg?table=tbldczSnB4TNDAOc`
   - `app_token` = `UViYwBDsqix41Skaldrcs8DbnGg`
   - `table_id` = `tbldczSnB4TNDAOc`

### 4.2 增强版查询函数（使用搜索 API）

```typescript
const FEISHU_API_BASE = 'https://open.feishu.cn/open-apis';

interface SearchOptions {
  // 基础筛选
  date?: string;                    // 精确日期 YYYY-MM-DD
  dateRange?: { start: string; end: string };  // 日期范围
  
  // 分类筛选
  mainSection?: string;             // 主板块
  subSection?: string;              // 子板块
  verticalTags?: string[];          // 垂类标签（包含任一）
  generalTags?: string[];           // 通用标签（包含任一）
  
  // 热度筛选
  minHotLevel?: number;             // 最小热度等级
  hotLevel?: number;                // 精确热度等级
  
  // 来源筛选
  source?: string;
  
  // 分页排序
  pageSize?: number;                // 每页条数（最大 500）
  pageToken?: string;               // 分页标记
  sortBy?: string;                  // 排序字段
  sortOrder?: 'asc' | 'desc';       // 排序方向
  
  // 字段选择
  fields?: string[];                // 只返回指定字段
  
  // 视图筛选
  viewId?: string;                  // 视图 ID（自动应用视图筛选规则）
}

interface FilterCondition {
  field_name: string;
  operator: string;
  value: string[];
}

interface Filter {
  conjunction: 'and' | 'or';
  conditions: FilterCondition[];
  children?: Filter[];
}

export async function searchBitableRecords(
  app_token: string,
  table_id: string,
  options: SearchOptions
): Promise<{
  items: any[];
  hasMore: boolean;
  pageToken: string;
}> {
  const token = await getFeishuToken();
  
  // 构建筛选条件
  const conditions: FilterCondition[] = [];
  
  // 日期筛选
  if (options.date) {
    conditions.push({
      field_name: 'pub_time',
      operator: 'contains',
      value: [options.date]
    });
  }
  
  if (options.dateRange) {
    conditions.push({
      field_name: 'pub_time',
      operator: 'isGreaterEqual',
      value: [options.dateRange.start]
    });
    conditions.push({
      field_name: 'pub_time',
      operator: 'isLessEqual',
      value: [options.dateRange.end]
    });
  }
  
  // 板块筛选
  if (options.mainSection) {
    conditions.push({
      field_name: 'main_section',
      operator: 'is',
      value: [options.mainSection]
    });
  }
  
  // 标签筛选（OR 关系，使用 children 嵌套）
  if (options.verticalTags && options.verticalTags.length > 0) {
    const tagConditions: FilterCondition[] = options.verticalTags.map(tag => ({
      field_name: 'vertical_tags',
      operator: 'contains',
      value: [tag]
    }));
    
    // 使用 children 实现 OR 逻辑
    // 注意：需要在顶层 filter 中处理
  }
  
  // 热度筛选
  if (options.minHotLevel !== undefined) {
    conditions.push({
      field_name: 'hot_level',
      operator: 'isGreaterEqual',
      value: [String(options.minHotLevel)]
    });
  }
  
  // 构建 filter
  let filter: Filter | undefined;
  if (conditions.length > 0) {
    filter = {
      conjunction: 'and',
      conditions
    };
  }
  
  // 构建排序
  const sort: string[] = [];
  if (options.sortBy) {
    sort.push(`${options.sortBy} ${options.sortOrder === 'desc' ? 'DESC' : 'ASC'}`);
  }
  
  // 构建请求体
  const requestBody: any = {
    view_id: options.viewId,
    filter: filter ? JSON.stringify(filter) : undefined,
    sort: sort.length > 0 ? sort : undefined,
    field_names: options.fields?.length ? options.fields : undefined
  };
  
  // 移除 undefined 字段
  Object.keys(requestBody).forEach(key => {
    if (requestBody[key] === undefined) {
      delete requestBody[key];
    }
  });
  
  // 构建 URL
  const url = new URL(`${FEISHU_API_BASE}/bitable/v1/apps/${app_token}/tables/${table_id}/records/search`);
  url.searchParams.set('page_size', String(Math.min(options.pageSize || 20, 500)));
  if (options.pageToken) {
    url.searchParams.set('page_token', options.pageToken);
  }
  
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json; charset=utf-8',
    },
    body: JSON.stringify(requestBody),
  });
  
  const data = await res.json();
  if (data.code !== 0) {
    throw new Error(`飞书搜索 API 错误 (${data.code}): ${data.msg}`);
  }
  
  return {
    items: data.data.items ?? [],
    hasMore: data.data.has_more ?? false,
    pageToken: data.data.page_token || '',
  };
}
```

### 4.3 使用示例

```typescript
// 示例 1：查询指定日期的日报
const result = await searchBitableRecords(
  {
    date: '2026-05-22',
    sortBy: 'rank',
    sortOrder: 'asc',
    pageSize: 100,
    fields: ['title', 'url', 'hot', 'summary', 'rank']
  }
);

// 示例 2：查询 AI 基石板块的热门内容
const result = await searchBitableRecords(
  {
    mainSection: 'AI 基石与算力',
    minHotLevel: 2,
    sortBy: 'hot_level',
    sortOrder: 'desc',
    pageSize: 20,
    fields: ['title', 'url', 'hot', 'summary', 'hot_level']
  }
);

// 示例 3：使用视图筛选（推荐）
// 在飞书多维表格中创建视图，设置筛选条件为"板块 = AI 基石与算力"
// 然后将视图 ID 添加到环境变量 FEISHU_BITABLE_VIEW_ID
const result = await searchBitableRecords(
  {
    viewId: process.env.FEISHU_BITABLE_VIEW_ID,  // 自动应用视图的筛选规则
    sortBy: 'rank',
    sortOrder: 'asc',
    pageSize: 100
  }
);

// 示例 4：分页查询所有记录
async function fetchAllRecords() {
  const allRecords: any[] = [];
  let pageToken: string | undefined;
  
  do {
    const result = await searchBitableRecords(
      {
        pageSize: 500,  // 最大 500
        pageToken,
        fields: ['title', 'url', 'pub_time']
      }
    );
    
    allRecords.push(...result.items);
    pageToken = result.hasMore ? result.pageToken : undefined;
  } while (pageToken);
  
  return allRecords;
}

// 示例 5：复杂筛选（多条件 AND）
const result = await searchBitableRecords(
  {
    mainSection: '大模型与核心技术',
    minHotLevel: 2,
    dateRange: {
      start: '2026-05-01',
      end: '2026-05-31'
    },
    sortBy: 'hot_level',
    sortOrder: 'desc',
    pageSize: 50,
    fields: ['title', 'url', 'hot', 'summary', 'pub_time']
  }
);
```

### 4.4 筛选参数填写说明

根据飞书官方文档，不同字段类型的 value 填写规则：

| 字段类型 | value 示例 | 说明 |
|----------|-----------|------|
| 多行文本 | `["文本内容"]` | 单元素数组 |
| 数字 | `["23.4"]` | 字符串格式 |
| 日期 | `["1702449755000"]` | 毫秒时间戳 |
| 单选/多选 | `["选项 1"]` | 选项文本 |
| 人员 | `["ou_xxxxx"]` | Open ID |

**注意事项**：
1. 不支持对"人员"及"关联字段"的属性进行筛选
2. 筛选条件参数长度不超过 2000 字符
3. 排序条件参数长度不超过 1000 字符
4. 不支持对公式字段和关联字段排序

---

## 5. 性能优化建议

### 5.1 查询优化策略

| 策略 | 说明 | 实现方式 |
|------|------|----------|
| **字段裁剪** | 只请求需要的字段 | 使用 `fields` 参数 |
| **分页查询** | 避免一次性拉取全部 | 前端分页 + `pageSize` |
| **视图预筛选** | 利用飞书视图的筛选规则 | 使用 `view_id` 参数 |
| **缓存策略** | 减少重复请求 | 按查询条件缓存结果 |
| **时间范围限制** | 限制查询的时间窗口 | 使用 `dateRange` 参数 |

### 5.2 缓存方案设计

```typescript
interface QueryCache {
  key: string;
  data: any[];
  expiresAt: number;
}

const queryCache = new Map<string, QueryCache>();
const CACHE_TTL = 5 * 60 * 1000; // 5分钟

function getCacheKey(options: QueryOptions): string {
  return JSON.stringify(options);
}

async function queryWithCache(options: QueryOptions): Promise<any[]> {
  const cacheKey = getCacheKey(options);
  const cached = queryCache.get(cacheKey);
  
  if (cached && Date.now() < cached.expiresAt) {
    return cached.data;
  }
  
  const result = await queryBitableRecords(options);
  queryCache.set(cacheKey, {
    key: cacheKey,
    data: result.items,
    expiresAt: Date.now() + CACHE_TTL
  });
  
  // 清理过期缓存
  queryCache.forEach((value, key) => {
    if (Date.now() > value.expiresAt) {
      queryCache.delete(key);
    }
  });
  
  return result.items;
}
```

---

## 6. 错误处理与降级方案

### 6.1 错误类型

| 错误码 | 含义 | 处理策略 |
|--------|------|----------|
| 1001 | 参数错误 | 校验参数格式 |
| 1010 | 权限不足 | 提示用户配置权限 |
| 400 | 请求格式错误 | 检查 JSON 序列化 |
| 401 | Token 过期 | 自动刷新 Token |
| 500 | 服务器错误 | 重试或降级 |
| 800004135 | API 调用超限 | 限制调用频率 |

### 6.2 降级方案

```typescript
async function getRecordsWithFallback(options: QueryOptions): Promise<any[]> {
  try {
    return await queryWithCache(options);
  } catch (error) {
    console.warn('[Bitable] 查询失败，使用 mock 数据:', error);
    // 返回空数组或 mock 数据
    return [];
  }
}
```

---

## 7. 安全注意事项

1. **敏感信息保护**：`app_id`、`app_secret` 必须通过环境变量配置，禁止硬编码
2. **Token 安全**：`tenant_access_token` 有效期 2 小时，需妥善缓存，避免频繁请求
3. **API 调用限制**：飞书 API 有调用频率限制，需实现合理的请求间隔
4. **数据过滤**：前端展示前需对数据进行清洗和验证，防止 XSS 攻击

---

## 附录：飞书多维表格 URL 解析规则

```
https://{tenant}.feishu.cn/wiki/{app_token}?table={table_id}&view={view_id}
                  ↑                      ↑              ↑             ↑
              租户域名              多维表格标识    数据表标识    视图标识
```

**提取脚本**：
```typescript
function parseBitableUrl(url: string) {
  const match = url.match(/https:\/\/([^.]+)\.feishu\.cn\/wiki\/([^?]+)\?table=([^&]+)&view=([^&]+)/);
  if (!match) return null;
  
  return {
    tenant: match[1],
    app_token: match[2],
    table_id: match[3],
    view_id: match[4]
  };
}
```
