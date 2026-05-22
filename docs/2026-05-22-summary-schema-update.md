# Summary Schema 更新记录

**日期**：2026-05-22  
**文件**：`project-space/summarize.py`

---

## 变更 1：输出结构调整

### 变更内容

| 类型 | 变更 |
|------|------|
| 剔除字段 | `items` - 新闻集群内的原始条目列表 |
| 字段重命名 | `merged_relevance` → `relevance` |
| 字段重命名 | `merged_hot_level` → `hot_level` |
| 字段重命名 | `merged_summary` → `summary` |

### 修改前

```python
def to_dict(self) -> dict:
    return {
        'cluster_id': self.cluster_id,
        'cluster_index': self.cluster_index,
        'headline': self.headline,
        'title': self.title,
        'plain_explain': self.plain_explain,
        'impacts': self.impacts,
        'digest_for_outline': self.digest_for_outline,
        'main_section': self.main_section,
        'sub_section': self.sub_section,
        'vertical_tags': self.vertical_tags,
        'general_tags': self.general_tags,
        'hot': self.hot,
        'keywords': self.keywords,
        'items': [it.__dict__.copy() for it in self.items],
        'urls': self.urls,
        'sources': self.sources,
        'rank': self.cluster.rank,
        'merged_relevance': self.cluster.merged_relevance,
        'merged_hot_level': self.cluster.merged_hot_level,
        'merged_summary': self.cluster.merged_summary,
    }
```

### 修改后

```python
def to_dict(self) -> dict:
    return {
        'cluster_id': self.cluster_id,
        'cluster_index': self.cluster_index,
        'urls': self.urls,
        'sources': self.sources,

        'headline': self.headline,
        'title': self.title,
        'digest_for_outline': self.digest_for_outline,
        'plain_explain': self.plain_explain,
        'summary': self.cluster.merged_summary,
        'impacts': self.impacts,
        'keywords': self.keywords,

        'relevance': self.cluster.merged_relevance,
        'hot_level': self.cluster.merged_hot_level,

        'main_section': self.main_section,
        'sub_section': self.sub_section,
        'vertical_tags': self.vertical_tags,
        'general_tags': self.general_tags,
        'hot': self.hot,
        'rank': self.cluster.rank
    }
```

---

## 变更 2：剔除兼容性代码

### 变更内容

| 位置 | 变更 |
|------|------|
| `_load_clusters()` | 剔除阶段一旧格式兼容（`items` 字段加载） |
| `_load_clusters()` | 剔除 JSONL 格式兼容（`load_jsonl()` 调用） |

### 修改前

```python
def _load_clusters(self, input_file: str) -> List[NewsCluster]:
    """加载输入文件，支持从 clusters 字段加载新闻集群"""
    data = self.load_json(input_file)
    if data is not None and isinstance(data, dict):
        if 'clusters' in data:
            return [NewsCluster.from_dict(it) for it in data.get('clusters', [])]
        if 'items' in data:  # 阶段一旧格式兼容
            items = [FilteredItem.from_dict(it) for it in data.get('items', [])]
            clusters = []
            for i, item in enumerate(items):
                clusters.append(NewsCluster(
                    cluster_id=f"cluster_{i}", keywords=item.keywords, items=[item],
                    merged_relevance=item.relevance, merged_hot_level=item.hot_level,
                    main_section=item.main_section, sub_section=item.sub_section, rank=i + 1
                ))
            return clusters
    raw_items = self.load_jsonl(input_file)  # JSONL 格式兼容
    clusters = []
    for i, raw in enumerate(raw_items):
        item = FilteredItem.from_dict(raw)
        clusters.append(NewsCluster(
            cluster_id=f"cluster_{i}", keywords=item.keywords, items=[item],
            merged_relevance=item.relevance, merged_hot_level=item.hot_level,
            main_section=item.main_section, sub_section=item.sub_section, rank=i + 1
        ))
    return clusters
```

### 修改后

```python
def _load_clusters(self, input_file: str) -> List[NewsCluster]:
    """加载输入文件，从 clusters 字段加载新闻集群"""
    data = self.load_json(input_file)
    if data is not None and isinstance(data, dict) and 'clusters' in data:
        return [NewsCluster.from_dict(it) for it in data.get('clusters', [])]
    return []
```

---

## 变更原因

1. **剔除 `items`**：输出已包含 `urls` 和 `sources`，原始条目信息非必要
2. **简化命名**：`merged_` 前缀冗余
3. **不兼容历史版本**：统一使用 `clusters` 字段作为唯一输入格式


## 变更 3：.lobster配置文件调整（已完成）

### 变更内容

- 新增「ai-frontier-daily.example.lobster」文件，并将其他「.lobster」文件ignore掉（同时移除其在git仓库的记录）