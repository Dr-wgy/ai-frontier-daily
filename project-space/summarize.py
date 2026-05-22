#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summarize.py — LLM 摘要模块（支持新闻集群汇总）
"""

from __future__ import annotations

import json
from typing import List, Sequence

from utils import AppConfig, LLMClient, WorkModule, PromptLoader, TEMPLATE_SUMMARIZE
from utils.domain import FilteredItem, NewsCluster


class SummaryCluster:
    """摘要后的新闻集群"""
    def __init__(self, cluster: NewsCluster, llm_data: dict):
        self.cluster = cluster
        self.cluster_index = llm_data.get('cluster_index', 0)
        self.headline = llm_data.get('headline', '')
        self.plain_explain = llm_data.get('plain_explain', '')
        self.impacts = llm_data.get('impacts', []) if isinstance(llm_data.get('impacts'), list) else []
        self.digest_for_outline = llm_data.get('digest_for_outline', '')
        self.main_section = llm_data.get('main_section', cluster.main_section)
        self.sub_section = llm_data.get('sub_section', cluster.sub_section)
        self.vertical_tags = llm_data.get('vertical_tags', []) if isinstance(llm_data.get('vertical_tags'), list) else []
        self.general_tags = llm_data.get('general_tags', []) if isinstance(llm_data.get('general_tags'), list) else []
        self.hot = llm_data.get('hot', '')

    @property
    def cluster_id(self) -> str:
        return self.cluster.cluster_id

    @property
    def keywords(self) -> List[str]:
        return self.cluster.keywords

    @property
    def items(self) -> List[FilteredItem]:
        return self.cluster.items

    @property
    def title(self) -> str:
        return self.cluster.title

    @property
    def urls(self) -> List[str]:
        return self.cluster.urls

    @property
    def sources(self) -> List[str]:
        return self.cluster.sources

    def to_dict(self) -> dict:
        return {
            'cluster_id': self.cluster_id,
            'cluster_index': self.cluster_index,
            'headline': self.headline,
            'title': self.title,  # 兼容旧字段
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
            'merged_summary': self.cluster.merged_summary,  # 合并摘要
        }


class SummarizeModule(WorkModule):
    """LLM 摘要（支持新闻集群汇总）"""

    def __init__(self, config: AppConfig):
        super().__init__('summarize')
        self.llm_client = LLMClient(config.llm_client_cfg)
        self._app_config = config

    def _load_clusters(self, input_file: str) -> List[NewsCluster]:
        """加载输入文件，支持从 clusters 字段加载新闻集群"""
        data = self.load_json(input_file)
        if data is not None and isinstance(data, dict):
            # 优先从 clusters 字段加载（阶段二输出格式）
            if 'clusters' in data:
                return [NewsCluster.from_dict(it) for it in data.get('clusters', [])]
            # 兼容旧格式（阶段一输出格式）
            if 'items' in data:
                items = [FilteredItem.from_dict(it) for it in data.get('items', [])]
                # 将单个新闻转换为单条新闻的集群
                clusters = []
                for i, item in enumerate(items):
                    clusters.append(NewsCluster(
                        cluster_id=f"cluster_{i}",
                        keywords=item.keywords,
                        items=[item],
                        merged_relevance=item.relevance,
                        merged_hot_level=item.hot_level,
                        main_section=item.main_section,
                        sub_section=item.sub_section,
                        rank=i + 1
                    ))
                return clusters
        
        # 尝试 JSONL 格式
        raw_items = self.load_jsonl(input_file)
        clusters = []
        for i, raw in enumerate(raw_items):
            item = FilteredItem.from_dict(raw)
            clusters.append(NewsCluster(
                cluster_id=f"cluster_{i}",
                keywords=item.keywords,
                items=[item],
                merged_relevance=item.relevance,
                merged_hot_level=item.hot_level,
                main_section=item.main_section,
                sub_section=item.sub_section,
                rank=i + 1
            ))
        return clusters

    def _build_prompts(self, clusters: Sequence[NewsCluster]) -> tuple:
        """构建 system/user 提示词（针对新闻集群）"""
        item_cap = int(self._app_config.links.llm.summarize_item_cap)
        
        rows = []
        for i, cluster in enumerate(clusters):
            # 为每个集群构建包含多条新闻的数据结构
            news_items = []
            for j, item in enumerate(cluster.items):
                body = self.clip_text(item.summary, item_cap)
                news_items.append({
                    'index': j,
                    'title': item.title,
                    'source': item.source,
                    'url': item.url,
                    'summary': body,
                    'pub_time': item.pub_time
                })
            
            rows.append({
                'cluster_index': i,
                'cluster_id': cluster.cluster_id,
                'keywords': cluster.keywords,
                'main_section': cluster.main_section,
                'sub_section': cluster.sub_section,
                'rank': cluster.rank,
                'merged_relevance': cluster.merged_relevance,
                'merged_hot_level': cluster.merged_hot_level,
                'news_items': news_items,
                'title': cluster.title,
                'sources': cluster.sources,
                'urls': cluster.urls,
                'merged_summary': self.clip_text(cluster.merged_summary, item_cap * 3)
            })

        self.log(f"构建 {len(rows)} 个新闻集群的提示词")
        
        return PromptLoader().load_with_config(
            TEMPLATE_SUMMARIZE,
            self._app_config.protocols,
            news_json=json.dumps(rows, ensure_ascii=False, indent=2),
        )

    def _extract_cluster_articles(self, data: dict) -> tuple:
        """从 LLM 响应中提取 articles（针对集群格式）和 drop_indices"""
        if not isinstance(data, dict):
            return {}, set()

        by_cluster = {}
        for a in data.get('articles', []):
            if not isinstance(a, dict):
                continue
            ci = a.get('cluster_index')
            if ci is None:
                continue
            try:
                by_cluster[int(ci)] = a
            except (ValueError, TypeError):
                continue

        drop = set()
        for x in data.get('deduplication', {}).get('drop_indices', []):
            try:
                drop.add(int(x))
            except (ValueError, TypeError):
                continue

        return by_cluster, drop

    def run(self, input_file: str, output_file: str) -> dict:
        """执行完整流程（支持新闻集群）"""
        self.log("开始执行摘要模块")
        
        assembly_cfg = self._app_config.modules.assembly
        max_items = min(max(1, int(assembly_cfg.summary_unified_max_items)), 500)

        # 加载新闻集群
        clusters = self._load_clusters(input_file)[:max_items]
        n_clusters = len(clusters)
        
        self.log(f"加载到 {n_clusters} 个新闻集群")

        if n_clusters == 0:
            self.save_json(output_file, {'clusters': [], 'blocks': {}})
            return {'count': 0, 'api_calls': 0, 'unified': True}

        # 构建提示词并调用 LLM
        system, user = self._build_prompts(clusters)
        self.log("调用 LLM 进行集群汇总...")
        data = self.llm_client.call_json(system, user)

        # 提取 LLM 返回的集群摘要数据
        by_cluster, drop = self._extract_cluster_articles(data)
        
        # 调试：打印 LLM 响应的原始统计
        raw_articles = data.get('articles', []) if isinstance(data, dict) else []
        self.log(f"输入 {len(clusters)} 个集群，LLM 返回 {len(raw_articles)} 条 articles", level='DEBUG')
        self.log(f"有效 cluster_index 匹配 {len(by_cluster)} 个，drop_indices 包含 {len(drop)} 个", level='DEBUG')

        # 生成输出结果
        out_clusters = []
        self.log(f"预计保留: {len(by_cluster)} 个集群（LLM 返回且不在 drop_indices 中）", level='DEBUG')
        
        for i, cluster in enumerate(clusters):
            if i in drop:
                self.log(f"跳过集群 {i} (在 drop_indices 中)", level='DEBUG')
                continue
            if i not in by_cluster:
                self.log(f"跳过集群 {i} (LLM 未返回该集群数据)", level='DEBUG')
                continue
            
            llm_data = by_cluster.get(i, {})
            summary_cluster = SummaryCluster(cluster, llm_data)
            out_clusters.append(summary_cluster)

        # 保存输出
        result = {
            'clusters': [sc.to_dict() for sc in out_clusters],
            'blocks': data.get('blocks', {}) if isinstance(data, dict) else {}
        }
        
        self.save_json(output_file, result)
        
        self.log(f"摘要模块执行完成，输出 {len(out_clusters)} 个集群")
        
        return {'count': len(out_clusters), 'api_calls': 1, 'unified': True}
