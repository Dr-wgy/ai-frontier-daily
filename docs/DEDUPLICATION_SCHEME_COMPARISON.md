# 多维表格去重与选项管理方案对比

> 文档版本：v1.0  
> 日期：2026-05-22  
> 适用场景：AI 前沿日报 - 标签/分类字段的去重与选项管理

---

## 一、业务场景分析

### 1.1 当前问题

| 问题 | 现象 | 影响 |
|------|------|------|
| **数据重复** | 相同新闻多次入库 | 展示重复内容，用户体验差 |
| **标签不规范** | "LLM"、"llm"、"大模型"并存 | 统计不准确，筛选失效 |
| **选项不固定** | text 字段自由输入 | 前端无法提供选择列表 |
| **模糊匹配复杂** | 逗号拼接字段难以精确匹配 | 查询效率低，逻辑复杂 |

### 1.2 核心需求

1. **查询筛选**：根据条件（日期、板块、标签）查询数据
2. **选项管理**：前端需要获取固定的选项列表供用户选择
3. **数据去重**：确保返回的新闻记录不重复
4. **统计分析**：准确统计各分类/标签的数量

---

## 二、方案对比

### 2.1 方案总览

| 方案 | 数据存储方式 | 查询方式 | 去重机制 | 选项管理 | 适用场景 |
|------|--------------|----------|----------|----------|----------|
| **方案 A** | 纯文本存储 | 模糊匹配 | 前端去重 | 前端写死 | 快速上线、数据量小 |
| **方案 B** | 文本存储 | 后端聚合去重 | 后端去重 | 后端查询聚合 | 中等规模、需要灵活选项 |
| **方案 C** | 单选/多选字段 | 精确匹配 | 自动去重 | 多维表格配置 | 长期维护、数据量大 |
| **方案 D** | 逗号拼接 | 模糊匹配 | 前后端配合 | 手动维护 | 过渡方案、遗留系统 |

### 2.2 详细对比

#### 方案 A：前端写死选项 + 前端去重

**架构图**：
```
飞书多维表格（text字段）
        ↓
前端查询（无筛选）
        ↓
前端去重（Set/Map）
        ↓
前端展示
```

**实现代码**：
```typescript
// 前端写死选项
const MAIN_SECTIONS = [
  "AI 基石与算力",
  "大模型与核心技术", 
  "AI 智能体与交互",
  "AI+ 垂直应用",
  "AI 产业与观察"
];

const VERTICAL_TAGS = [
  "LLM", "Transformer", "算力", "芯片", "多模态", "Agent"
];

// 前端去重
function deduplicateByUrl(items: NewsItem[]): NewsItem[] {
  const seen = new Map<string, NewsItem>();
  for (const item of items) {
    const existing = seen.get(item.url);
    if (!existing || item.rank < existing.rank) {
      seen.set(item.url, item);
    }
  }
  return Array.from(seen.values());
}
```

**优缺点**：

| 维度 | 优点 | 缺点 |
|------|------|------|
| **实现难度** | 简单，无需修改后端 | - |
| **数据一致性** | 选项固定，不会出错 | 选项硬编码，维护麻烦 |
| **查询效率** | 简单查询 | 需要全量拉取再去重 |
| **扩展性** | 差 | 新增选项需要改代码重新部署 |
| **统计准确性** | 高（基于固定选项） | - |
| **适用规模** | 小 | 数据量大时性能差 |

---

#### 方案 B：后端聚合选项 + 后端去重

**架构图**：
```
飞书多维表格（text字段）
        ↓
后端查询聚合（SQL-like）
        ↓
后端去重（Map/Set）
        ↓
返回去重后数据 + 选项列表
        ↓
前端展示
```

**实现代码**：
```typescript
// 后端：获取所有不重复的标签
export async function getDistinctTags(): Promise<string[]> {
  const records = await fetchAllBitableRecords();
  const tags = new Set<string>();
  
  records.forEach(record => {
    const verticalTags = record.fields.vertical_tags;
    if (Array.isArray(verticalTags)) {
      verticalTags.forEach(tag => tags.add(tag));
    } else if (typeof verticalTags === 'string') {
      tags.add(verticalTags);
    }
  });
  
  return Array.from(tags).sort();
}

// 后端：查询并去重
export async function searchWithDedup(options: SearchOptions) {
  const records = await searchBitableRecords(options);
  
  // 去重
  const seen = new Map<string, typeof records.items[0]>();
  records.items.forEach(item => {
    const existing = seen.get(item.fields.url);
    if (!existing || item.fields.rank < existing.fields.rank) {
      seen.set(item.fields.url, item);
    }
  });
  
  return {
    items: Array.from(seen.values()),
    hasMore: false,
    pageToken: ''
  };
}
```

**优缺点**：

| 维度 | 优点 | 缺点 |
|------|------|------|
| **实现难度** | 中等 | 需要后端逻辑支持 |
| **数据一致性** | 动态获取，自动更新 | 可能包含脏数据 |
| **查询效率** | 需要两次 API 调用 | 全量拉取效率低 |
| **扩展性** | 好，选项自动更新 | - |
| **统计准确性** | 中等（可能有脏数据） | - |
| **适用规模** | 中 | 数据量大时性能差 |

---

#### 方案 C：使用单选/多选字段（推荐）

**架构图**：
```
飞书多维表格（单选/多选字段）
        ↓
前端查询（精确匹配）
        ↓
自动去重（字段特性）
        ↓
返回标准化数据
        ↓
前端展示
```

**字段配置**：

| 字段名 | 类型 | 选项配置 | 说明 |
|--------|------|----------|------|
| `main_section` | **单选** | AI 基石与算力、大模型与核心技术、AI 智能体与交互、AI+ 垂直应用、AI 产业与观察 | 主板块 |
| `vertical_tags` | **多选** | LLM、Transformer、算力、芯片、多模态、Agent、RAG、微调... | 垂类标签 |
| `hot_level` | **单选** | 🔥、🔥🔥、🔥🔥🔥、🔥🔥🔥🔥、🔥🔥🔥🔥🔥 | 热度等级 |

**查询代码**：
```typescript
// 精确匹配
const result = await searchBitableRecords({
  filter: {
    conjunction: 'and',
    conditions: [
      {
        field_name: 'main_section',
        operator: 'is',
        value: ['AI 基石与算力']
      },
      {
        field_name: 'vertical_tags',
        operator: 'contains',
        value: ['LLM']
      }
    ]
  },
  fields: ['title', 'url', 'main_section', 'vertical_tags']
});
```

**获取选项列表**：
```typescript
// 飞书 API：获取字段的选项配置
export async function getFieldOptions(tableId: string, fieldId: string) {
  const url = `${FEISHU_API_BASE}/bitable/v1/apps/${appToken}/tables/${tableId}/fields/${fieldId}`;
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const data = await res.json();
  
  // 返回选项列表
  return data.data.field.options.map(opt => opt.name);
}

// 使用
const sections = await getFieldOptions(tableId, 'fld_main_section');
const tags = await getFieldOptions(tableId, 'fld_vertical_tags');
```

**优缺点**：

| 维度 | 优点 | 缺点 |
|------|------|------|
| **实现难度** | 中等（需要配置多维表格） | 需要修改现有数据结构 |
| **数据一致性** | 完美（强制使用预定义选项） | - |
| **查询效率** | 最高（精确匹配 + 字段索引） | - |
| **扩展性** | 极好（在飞书界面配置，无需改代码） | - |
| **统计准确性** | 最高 | - |
| **适用规模** | 大 | - |

---

#### 方案 D：逗号拼接存储 + 模糊匹配

**架构图**：
```
飞书多维表格（text字段，逗号拼接）
        ↓
前端查询（模糊匹配）
        ↓
前端解析（split(',')）
        ↓
前端去重
        ↓
前端展示
```

**数据结构**：
```typescript
{
  "fields": {
    "vertical_tags": "LLM,Transformer,算力"  // 逗号拼接
  }
}
```

**查询代码**：
```typescript
// 模糊匹配（不准确）
const result = await searchBitableRecords({
  filter: {
    conjunction: 'and',
    conditions: [
      {
        field_name: 'vertical_tags',
        operator: 'contains',
        value: ['LLM']  // 可能匹配到 "LLM大模型" 等
      }
    ]
  }
});

// 前端解析
function parseTags(tagsStr: string): string[] {
  return tagsStr.split(',').map(tag => tag.trim()).filter(Boolean);
}
```

**优缺点**：

| 维度 | 优点 | 缺点 |
|------|------|------|
| **实现难度** | 简单 | - |
| **数据一致性** | 差（自由输入） | - |
| **查询效率** | 低（模糊匹配） | - |
| **扩展性** | 差 | - |
| **统计准确性** | 低 | - |
| **适用规模** | 不推荐 | - |

---

## 三、方案对比表

### 3.1 综合对比

| 维度 | 方案 A（前端写死） | 方案 B（后端聚合） | 方案 C（单选/多选） | 方案 D（逗号拼接） |
|------|-------------------|-------------------|--------------------|-------------------|
| **数据一致性** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **查询效率** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **实现难度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **扩展性** | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **统计准确性** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **维护成本** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| **推荐度** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |

### 3.2 适用场景建议

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| **快速原型** | A | 实现简单，快速验证 |
| **小数据量** | A/B | 数据量小，性能影响不大 |
| **中大型项目** | C | 数据一致性和查询效率优先 |
| **遗留系统迁移** | B → C | 先聚合去重，再逐步迁移 |
| **标签频繁变化** | C | 配置灵活，无需改代码 |

---

## 四、实施建议

### 4.1 方案 C 实施步骤

**步骤 1：修改多维表格字段类型**

| 原字段 | 原类型 | 新类型 | 选项配置 |
|--------|--------|--------|----------|
| `main_section` | 文本 | 单选 | AI 基石与算力、大模型与核心技术、AI 智能体与交互、AI+ 垂直应用、AI 产业与观察 |
| `vertical_tags` | 文本 | 多选 | LLM、Transformer、算力、芯片、多模态、Agent、RAG、微调、开源、商业化... |
| `general_tags` | 文本 | 多选 | 热门、新发布、重要、深度、速览... |
| `hot_level` | 文本 | 单选 | 🔥、🔥🔥、🔥🔥🔥、🔥🔥🔥🔥、🔥🔥🔥🔥🔥 |

**步骤 2：数据迁移**

```typescript
// 迁移脚本：将现有数据转换为新格式
async function migrateData() {
  const records = await fetchAllBitableRecords();
  
  for (const record of records) {
    const fields = record.fields;
    
    // 转换 main_section
    const normalizedSection = normalizeSection(fields.main_section);
    
    // 转换 vertical_tags（假设是逗号分隔）
    const tags = fields.vertical_tags 
      ? fields.vertical_tags.split(',').map(t => normalizeTag(t.trim()))
      : [];
    
    // 更新记录
    await updateRecord(record.record_id, {
      main_section: normalizedSection,
      vertical_tags: tags.filter(t => t)  // 过滤空值
    });
  }
}

function normalizeSection(section: string): string {
  const mappings: Record<string, string> = {
    'AI基石': 'AI 基石与算力',
    '基石': 'AI 基石与算力',
    '大模型': '大模型与核心技术',
    // ... 更多映射
  };
  return mappings[section] || section;
}

function normalizeTag(tag: string): string {
  const mappings: Record<string, string> = {
    'llm': 'LLM',
    '大模型': 'LLM',
    'transformer': 'Transformer',
    // ... 更多映射
  };
  return mappings[tag.toLowerCase()] || tag;
}
```

**步骤 3：修改前端代码**

```typescript
// 获取选项列表（从飞书 API）
export async function getSectionOptions(): Promise<string[]> {
  const fields = await getTableFields(tableId);
  const sectionField = fields.find(f => f.name === 'main_section');
  return sectionField.options.map(opt => opt.name);
}

// 查询（精确匹配）
export async function searchBySection(section: string) {
  return await searchBitableRecords({
    filter: {
      conjunction: 'and',
      conditions: [{
        field_name: 'main_section',
        operator: 'is',
        value: [section]
      }]
    },
    fields: ['title', 'url', 'summary']
  });
}
```

**步骤 4：更新写入逻辑**

```typescript
// 写入前验证
async function writeRecord(item: NewsItem) {
  // 验证主板块
  const validSections = await getSectionOptions();
  if (!validSections.includes(item.main_section)) {
    throw new Error(`无效的板块: ${item.main_section}`);
  }
  
  // 验证标签
  const validTags = await getTagOptions();
  const validItemTags = item.vertical_tags.filter(tag => 
    validTags.includes(tag)
  );
  
  return await createRecord({
    fields: {
      title: item.title,
      url: item.url,
      main_section: item.main_section,
      vertical_tags: validItemTags,
      // ... 其他字段
    }
  });
}
```

---

## 五、总结

### 5.1 方案选择建议

```
项目阶段 → 推荐方案
─────────────────────────────
快速原型   → 方案 A（前端写死）
中期迭代   → 方案 B（后端聚合）
长期维护   → 方案 C（单选/多选）
```

### 5.2 方案 C 的优势

1. **数据一致性**：强制使用预定义选项，避免数据脏污
2. **查询效率**：精确匹配，支持索引，查询速度快
3. **扩展性**：在飞书界面配置选项，无需修改代码
4. **维护成本**：低，选项管理可视化
5. **统计准确性**：完美，不会有重复或变体

### 5.3 推荐实施路径

```
当前状态（text字段）
        ↓
短期：方案 A（前端写死选项）
        ↓
中期：方案 B（后端聚合去重）
        ↓
长期：方案 C（单选/多选字段）
```

---

## 附录：飞书多维表格字段类型参考

| 字段类型 | 适用场景 | 是否支持选项 | 是否支持去重 |
|----------|----------|--------------|--------------|
| 文本 | 自由输入内容 | ❌ | ❌ |
| 单选 | 单一分类 | ✅ | ✅ |
| 多选 | 多个标签 | ✅ | ✅ |
| 数字 | 数值数据 | ❌ | ❌ |
| 日期 | 时间数据 | ❌ | ❌ |
| 人员 | 用户选择 | ✅ | ✅ |
| 公式 | 计算字段 | ❌ | ❌ |
| 查找引用 | 关联其他表格 | ✅ | ✅ |