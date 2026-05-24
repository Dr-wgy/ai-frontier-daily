"""
domain — AI-Froniteer-Daily 数据模型层

数据流程：
    ingested.jsonl (RSS原始)
        ↓
    filtered_ranked.json (筛选+分类+排序)
        ↓
    summary.json (LLM摘要增强，集群模式)
        ↓
    briefing.md (最终简报)

核心类：
    NewsItem → FilteredItem → NewsCluster → SummaryCluster
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass(frozen=True)
class NewsItem:
    """RSS 抓取的原始新闻条目"""
    title: str
    url: str
    source: str
    summary: str
    pub_time: str
    _feed_url: str = field(default='', compare=False)

    @staticmethod
    def from_dict(d: dict) -> 'NewsItem':
        return NewsItem(
            title=d.get('title', ''),
            url=d.get('url', ''),
            source=d.get('source', ''),
            summary=d.get('summary', ''),
            pub_time=d.get('pub_time', ''),
            _feed_url=d.get('_feed_url', ''),
        )


@dataclass(frozen=True)
class FilteredItem(NewsItem):
    """筛选+分类+排序后的新闻条目"""
    main_section: str = ''
    sub_section: str = ''
    relevance: float = 0.0
    hot_level: float = 0.0
    rank: int = 0
    keywords: List[str] = field(default_factory=list)

    @staticmethod
    def from_dict(d: dict) -> 'FilteredItem':
        keywords = d.get('keywords', [])
        if isinstance(keywords, str):
            keywords = [keywords] if keywords else []
        
        return FilteredItem(
            title=d.get('title', ''),
            url=d.get('url', ''),
            source=d.get('source', ''),
            summary=d.get('summary', ''),
            pub_time=d.get('pub_time', ''),
            _feed_url=d.get('_feed_url', ''),
            main_section=d.get('main_section', ''),
            sub_section=d.get('sub_section', ''),
            keywords=keywords,
            relevance=float(d.get('relevance', 0)),
            hot_level=float(d.get('hot_level', 0)),
            rank=int(d.get('rank', 0)),
        )

    @staticmethod
    def from_llm_response(data: dict) -> List[Dict[str, Any]]:
        """从 LLM 响应中提取 items 字典（不做过滤）"""
        if not isinstance(data, dict):
            return []

        items = []
        for row in data.get('items', []):
            if not isinstance(row, dict):
                continue

            si = row.get('source_index')
            if si is None:
                continue
            try:
                si_int = int(si)
            except (ValueError, TypeError):
                continue

            items.append({
                'source_index': si_int,
                'main_section': row.get('main_section', ''),
                'sub_section': row.get('sub_section', ''),
                'keywords': row.get('keywords', []),
                'relevance': float(row.get('relevance', 0)),
                'hot_level': float(row.get('hot_level', 0)),
            })

        return items

    @classmethod
    def from_news_and_llm(cls, news_item: NewsItem, llm_result: Dict[str, Any], rank: int) -> 'FilteredItem':
        """从 NewsItem 和 LLM 结果合并创建 FilteredItem"""
        keywords = llm_result.get('keywords', [])
        if isinstance(keywords, str):
            keywords = [keywords] if keywords else []
        
        return cls(
            title=news_item.title,
            url=news_item.url,
            source=news_item.source,
            summary=news_item.summary,
            pub_time=news_item.pub_time,
            _feed_url=news_item._feed_url,
            main_section=llm_result.get('main_section', ''),
            sub_section=llm_result.get('sub_section', ''),
            keywords=keywords,
            relevance=float(llm_result.get('relevance', 0)),
            hot_level=float(llm_result.get('hot_level', 0)),
            rank=rank,
        )


@dataclass(frozen=True)
class NewsCluster:
    """新闻集群（基于关键词聚合的新闻集）"""
    cluster_id: str
    keywords: List[str]
    items: List[FilteredItem]
    merged_relevance: float
    merged_hot_level: float
    main_section: str
    sub_section: str
    rank: int

    @property
    def title(self) -> str:
        """集群标题（取最相关新闻的标题）"""
        if not self.items:
            return ''
        return max(self.items, key=lambda x: x.relevance).title

    @property
    def url(self) -> List[str]:
        """集群URL（取最相关新闻的URL）"""
        if not self.items:
            return ''
        return max(self.items, key=lambda x: x.relevance).url

    @property
    def source(self) -> List[str]:
        """集群来源（取最相关新闻的来源）"""
        if not self.items:
            return ''
        return max(self.items, key=lambda x: x.relevance).source

    @property
    def urls(self) -> List[str]:
        """集群包含的所有URL"""
        return [item.url for item in self.items]

    @property
    def sources(self) -> List[str]:
        """集群包含的所有来源"""
        return list(set(item.source for item in self.items))

    @property
    def merged_summary(self) -> str:
        """合并摘要（取最相关新闻的摘要）"""
        if not self.items:
            return ''
        return max(self.items, key=lambda x: x.relevance).summary

    @staticmethod
    def from_dict(d: dict) -> 'NewsCluster':
        """从字典创建 NewsCluster 对象"""
        items = [FilteredItem.from_dict(it) for it in d.get('items', [])]
        return NewsCluster(
            cluster_id=d.get('cluster_id', ''),
            keywords=d.get('keywords', []),
            items=items,
            merged_relevance=float(d.get('merged_relevance', 0)),
            merged_hot_level=float(d.get('merged_hot_level', 0)),
            main_section=d.get('main_section', ''),
            sub_section=d.get('sub_section', ''),
            rank=int(d.get('rank', 0)),
        )


@dataclass(frozen=True)
class SummaryCluster:
    """摘要后的新闻集群（自管理所有属性，不依赖 NewsCluster）"""
    cluster_id: str = ''
    cluster_index: int = 0
    keywords: list = field(default_factory=list)
    items: list = field(default_factory=list)
    title: str = ''
    url: str = ''
    source: str = ''
    urls: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    summary: str = ''
    relevance: float = 0.0
    hot_level: float = 0.0
    rank: int = 0
    headline: str = ''
    plain_explain: str = ''
    impacts: list = field(default_factory=list)
    digest_for_outline: str = ''
    main_section: str = ''
    sub_section: str = ''
    vertical_tags: list = field(default_factory=list)
    general_tags: list = field(default_factory=list)
    hot: str = ''

    @classmethod
    def from_cluster_and_llm(cls, cluster: 'NewsCluster', llm_data: dict) -> 'SummaryCluster':
        """从 NewsCluster 和 LLM 数据构建 SummaryCluster（仅用于构建）"""
        return cls(
            cluster_id=cluster.cluster_id,
            cluster_index=llm_data.get('cluster_index', 0),
            keywords=cluster.keywords,
            items=cluster.items,
            title=cluster.title,
            url=cluster.url,
            source=cluster.source,
            urls=cluster.urls,
            sources=cluster.sources,
            summary=cluster.merged_summary,
            relevance=cluster.merged_relevance,
            hot_level=cluster.merged_hot_level,
            rank=cluster.rank,
            headline=llm_data.get('headline', ''),
            plain_explain=llm_data.get('plain_explain', ''),
            impacts=llm_data.get('impacts', []) if isinstance(llm_data.get('impacts'), list) else [],
            digest_for_outline=llm_data.get('digest_for_outline', ''),
            main_section=llm_data.get('main_section', cluster.main_section),
            sub_section=llm_data.get('sub_section', cluster.sub_section),
            vertical_tags=llm_data.get('vertical_tags', []) if isinstance(llm_data.get('vertical_tags'), list) else [],
            general_tags=llm_data.get('general_tags', []) if isinstance(llm_data.get('general_tags'), list) else [],
            hot=llm_data.get('hot', ''),
        )

    @classmethod
    def from_dict(cls, d: dict) -> 'SummaryCluster':
        """从字典创建 SummaryCluster"""
        return cls(
            cluster_id=d.get('cluster_id', ''),
            cluster_index=d.get('cluster_index', 0),
            keywords=d.get('keywords', []),
            items=d.get('items', []),
            title=d.get('title', ''),
            url=d.get('url', ''),
            source=d.get('source', ''),
            urls=d.get('urls', []),
            sources=d.get('sources', []),
            summary=d.get('summary', ''),
            relevance=float(d.get('relevance', 0)),
            hot_level=float(d.get('hot_level', 0)),
            rank=int(d.get('rank', 0)),
            headline=d.get('headline', ''),
            plain_explain=d.get('plain_explain', ''),
            impacts=d.get('impacts', []) if isinstance(d.get('impacts'), list) else [],
            digest_for_outline=d.get('digest_for_outline', ''),
            main_section=d.get('main_section', ''),
            sub_section=d.get('sub_section', ''),
            vertical_tags=d.get('vertical_tags', []) if isinstance(d.get('vertical_tags'), list) else [],
            general_tags=d.get('general_tags', []) if isinstance(d.get('general_tags'), list) else [],
            hot=d.get('hot', ''),
        )

    def to_dict(self) -> dict:
        return {
            'cluster_id': self.cluster_id, 'cluster_index': self.cluster_index,
            'urls': self.urls, 'sources': self.sources,
            'title': self.title, 'url': self.url, 'source': self.source,
            'summary': self.summary,
            'headline': self.headline, 'hot': self.hot,
            'main_section': self.main_section, 'sub_section': self.sub_section,
            'vertical_tags': self.vertical_tags, 'general_tags': self.general_tags,
            'digest_for_outline': self.digest_for_outline,
            'plain_explain': self.plain_explain,
            'impacts': self.impacts,
            'keywords': self.keywords,
            'relevance': self.relevance, 'hot_level': self.hot_level,
            'rank': self.rank
        }


@dataclass(frozen=True)
class FilterStats:
    """筛选统计信息"""
    input_count: int = 0
    output_count: int = 0
    dropped_count: int = 0
    top_topics: List[str] = field(default_factory=list)

    @staticmethod
    def from_counts(
        input_count: int,
        output_count: int,
        section_counts: Dict[str, int],
        top_n: int = 5,
    ) -> 'FilterStats':
        """从统计计数创建 FilterStats"""
        return FilterStats(
            input_count=input_count,
            output_count=output_count,
            dropped_count=input_count - output_count,
            top_topics=sorted(section_counts.keys(), key=lambda x: section_counts[x], reverse=True)[:top_n],
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'input_count': self.input_count,
            'output_count': self.output_count,
            'dropped_count': self.dropped_count,
            'top_topics': self.top_topics,
        }

