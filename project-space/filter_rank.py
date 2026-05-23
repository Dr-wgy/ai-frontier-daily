#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
filter_rank.py — 智能筛选与优先级排序模块（支持关键词聚类与历史去重）

步骤二：对 ingest 输出的原始新闻进行智能筛选、排名、关键词聚类和历史去重
"""

from __future__ import annotations

import json
from typing import Sequence, List, Tuple
from collections import defaultdict

from utils import AppConfig, LLMClient, WorkModule, PromptLoader, TEMPLATE_FILTER_RANK, FN_SUMMARY
from utils.domain import NewsItem, FilteredItem, NewsCluster


class KeywordClusterer:
    """关键词聚类器 - 基于关键词相似度对新闻进行聚类"""

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold

    def cluster_by_keywords(
        self,
        items: List[FilteredItem],
        max_items_per_cluster: int = 5
    ) -> List[NewsCluster]:
        """基于关键词聚类新闻"""
        if not items:
            return []

        # 按主板块分组
        by_section = defaultdict(list)
        for item in items:
            by_section[item.main_section].append(item)

        clusters = []
        cluster_counter = 0

        for section, section_items in by_section.items():
            section_clusters = self._cluster_section_items(
                section_items,
                section,
                cluster_counter,
                max_items_per_cluster
            )
            clusters.extend(section_clusters)
            cluster_counter += len(section_clusters)

        # 按综合得分排序
        clusters.sort(
            key=lambda c: c.merged_relevance * c.merged_hot_level,
            reverse=True
        )

        # 重新分配排名
        for i, cluster in enumerate(clusters):
            # 使用 object.__setattr__ 因为 NewsCluster 是 frozen dataclass
            object.__setattr__(cluster, '_NewsCluster__rank', i + 1)

        return clusters

    def _cluster_section_items(
        self,
        items: List[FilteredItem],
        section: str,
        start_cluster_id: int,
        max_items_per_cluster: int
    ) -> List[NewsCluster]:
        """对同一板块内的新闻进行聚类"""
        if not items:
            return []

        # 按相关性排序
        sorted_items = sorted(items, key=lambda x: x.relevance, reverse=True)

        clusters = []
        used_indices = set()

        for i, item in enumerate(sorted_items):
            if i in used_indices:
                continue

            # 创建新集群
            cluster_items = [item]
            used_indices.add(i)

            # 查找相似新闻
            for j in range(i + 1, len(sorted_items)):
                if j in used_indices:
                    continue

                other_item = sorted_items[j]
                if len(cluster_items) >= max_items_per_cluster:
                    break

                # 计算关键词相似度
                similarity = self._calculate_keyword_similarity(
                    item.keywords,
                    other_item.keywords
                )

                if similarity >= self.similarity_threshold:
                    cluster_items.append(other_item)
                    used_indices.add(j)

            # 创建集群对象
            cluster_id = f"cluster_{start_cluster_id + len(clusters)}"
            cluster = NewsCluster(
                cluster_id=cluster_id,
                keywords=self._merge_keywords(cluster_items),
                items=cluster_items,
                merged_relevance=max(it.relevance for it in cluster_items),
                merged_hot_level=max(it.hot_level for it in cluster_items),
                main_section=section,
                sub_section=cluster_items[0].sub_section,
                rank=0  # 稍后统一分配
            )
            clusters.append(cluster)

        return clusters

    def _calculate_keyword_similarity(
        self,
        keywords1: List[str],
        keywords2: List[str]
    ) -> float:
        """计算两组关键词的相似度（Jaccard相似度）"""
        if not keywords1 or not keywords2:
            return 0.0

        # 使用 Jaccard 相似度
        set1 = set(k.lower() for k in keywords1)
        set2 = set(k.lower() for k in keywords2)

        intersection = set1 & set2
        union = set1 | set2

        if not union:
            return 0.0

        jaccard = len(intersection) / len(union)

        # 如果有直接匹配的关键词，提高相似度
        direct_match = len(intersection) / max(len(set1), len(set2))

        # 综合评分
        return jaccard * 0.6 + direct_match * 0.4

    def _merge_keywords(self, items: List[FilteredItem]) -> List[str]:
        """合并多条新闻的关键词（去重并保留顺序）"""
        all_keywords = []
        for item in items:
            all_keywords.extend(item.keywords)

        # 去重并保留顺序
        seen = set()
        unique_keywords = []
        for kw in all_keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_keywords.append(kw)

        return unique_keywords


class HistoricalKeywordDedup:
    """历史关键词去重器 - 基于历史数据中的关键词进行去重"""

    def __init__(self, config: AppConfig):
        self._config = config
        self._keyword_dedup_cfg = config.modules.keyword_dedup

    def load_recent_keywords(self, days: int = None) -> List[List[str]]:
        """加载最近N天的关键词历史（从 summary.json 读取）

        与 ingest.py 中的 dedup_recent 保持一致：
        - 读取经过 LLM 汇总后的 summary.json，而非中间产物 filtered_ranked.json
        - 因为 summary.json 是真正发布的最终内容，代表了真正有效的历史数据

        数据来源优先级：
        1. clusters[].keywords（阶段一改造后的格式）
        2. items[].keywords（旧格式，兼容）
        3. 从 title + summary 字段提取关键词（兜底策略）

        Args:
            days: 读取近几天的数据，默认从配置读取

        Returns:
            关键词列表的列表，每个内部列表代表一天的关键词集合
        """
        if days is None:
            days = getattr(self._keyword_dedup_cfg, 'recent_days', 3)

        # 获取近N天的 output 目录
        recent_dirs = self._config.paths.get_recent_output_dirs(days)

        all_keywords = []
        for output_dir in recent_dirs:
            # 读取 summary.json（最终发布的汇总结果），而非 filtered_ranked.json
            summary_file = output_dir / FN_SUMMARY
            if summary_file.is_file():
                try:
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                        # 优先级1：从 clusters 中提取关键词（阶段一改造后的格式）
                        if 'clusters' in data:
                            for cluster in data['clusters']:
                                if 'keywords' in cluster and cluster['keywords']:
                                    all_keywords.append(cluster['keywords'])

                        # 优先级2：从 items 中提取关键词（旧格式兼容）
                        elif 'items' in data:
                            for item in data['items']:
                                if 'keywords' in item and item['keywords']:
                                    all_keywords.append(item['keywords'])

                except (json.JSONDecodeError, IOError):
                    continue

        return all_keywords

    def dedup_by_history(
        self,
        clusters: List[NewsCluster],
        similarity_threshold: float = None
    ) -> Tuple[List[NewsCluster], List[str]]:
        """基于历史关键词去重"""
        if not clusters:
            return [], []

        if similarity_threshold is None:
            similarity_threshold = getattr(
                self._keyword_dedup_cfg,
                'history_similarity_threshold',
                0.6
            )

        history_keywords = self.load_recent_keywords()
        if not history_keywords:
            return clusters, []

        kept_clusters = []
        dropped_cluster_ids = []

        for cluster in clusters:
            is_duplicate = False

            for hist_keywords in history_keywords:
                similarity = self._calculate_similarity(
                    cluster.keywords,
                    hist_keywords
                )

                if similarity >= similarity_threshold:
                    is_duplicate = True
                    dropped_cluster_ids.append(
                        f"{cluster.cluster_id} (similarity: {similarity:.2f})"
                    )
                    break

            if not is_duplicate:
                kept_clusters.append(cluster)

        return kept_clusters, dropped_cluster_ids

    def _calculate_similarity(
        self,
        keywords1: List[str],
        keywords2: List[str]
    ) -> float:
        """计算关键词相似度（Jaccard相似度）"""
        if not keywords1 or not keywords2:
            return 0.0

        set1 = set(k.lower() for k in keywords1)
        set2 = set(k.lower() for k in keywords2)

        intersection = set1 & set2
        union = set1 | set2

        if not union:
            return 0.0

        return len(intersection) / len(union)


class FilterRankModule(WorkModule):
    """智能筛选与优先级排序（支持关键词聚类与历史去重）"""

    def __init__(self, config: AppConfig):
        super().__init__('filter_rank', config.date_str)
        self.llm_client = LLMClient(config.llm_client_cfg, self.date)
        self._app_config = config
        self.valid_main_sections = [
            getattr(m, 'name', '') for m in config.protocols.classification.main_sections
        ]
        self.max_news_per_topic = config.modules.filter_rank.max_news_per_topic

        # 初始化聚类器和历史去重器
        keyword_dedup_cfg = config.modules.keyword_dedup
        self.clusterer = KeywordClusterer(
            similarity_threshold=getattr(keyword_dedup_cfg, 'similarity_threshold', 0.7)
        )
        self.historical_dedup = HistoricalKeywordDedup(config)

    def _build_prompts(self, items: Sequence[NewsItem]) -> tuple:
        """构建 system/user 提示词"""
        rows = [
            {
                'index': i,
                'title': it.title,
                'source': it.source,
                'summary': it.summary,
            } for i, it in enumerate(items)
        ]

        return PromptLoader().load_with_config(
            TEMPLATE_FILTER_RANK,
            self._app_config.protocols,
            news_json=json.dumps(rows, ensure_ascii=False, indent=2),
        )

    def run(self, input_file: str, output_file: str) -> dict:
        """执行完整流程"""
        self.logger.info(f"开始执行筛选排序模块，输入文件: {input_file}")
        
        raw_items = self.load_jsonl(input_file)
        news_items = [NewsItem.from_dict(it) for it in raw_items]
        n_input = len(news_items)
        self.logger.info(f"加载输入数据完成，共 {n_input} 条新闻")

        if n_input == 0:
            self.logger.info("输入数据为空，直接输出空结果")
            self.save_json(
                output_file,
                {'clusters': [], 'stats': {'input_count': 0, 'output_count': 0}}
            )
            return {'count': 0, 'api_calls': 0, 'input_count': 0}

        # Step 1: LLM 筛选和关键词提取
        self.logger.info("Step 1: 开始 LLM 筛选和关键词提取")
        system, user = self._build_prompts(news_items)
        data = self.llm_client.call_json(system, user)
        llm_items = FilteredItem.from_llm_response(data)
        self.logger.info(f"LLM 筛选完成，通过 {len(llm_items)} 条")

        # Step 2: 构建带关键词的 FilteredItem
        self.logger.info("Step 2: 构建带关键词的 FilteredItem")
        filtered_items = []
        for row in llm_items:
            si = row['source_index']
            if not (0 <= si < n_input):
                continue

            main_section = row['main_section']
            if main_section not in self.valid_main_sections:
                main_section = 'AI 产业与观察'

            sub_section = row['sub_section']
            if not sub_section:
                sub_section = '其他'

            row['main_section'] = main_section
            row['sub_section'] = sub_section

            original = news_items[si]
            rank = len(filtered_items) + 1
            filtered_item = FilteredItem.from_news_and_llm(original, row, rank)
            filtered_items.append(filtered_item)
        self.logger.info(f"构建 FilteredItem 完成，共 {len(filtered_items)} 条")

        # Step 3: 关键词聚类
        self.logger.info("Step 3: 开始关键词聚类")
        clusters = self.clusterer.cluster_by_keywords(
            filtered_items,
            max_items_per_cluster=getattr(
                self._app_config.modules.keyword_dedup,
                'max_items_per_cluster',
                5
            )
        )
        self.logger.info(f"关键词聚类完成，生成 {len(clusters)} 个集群")

        # Step 4: 历史关键词去重
        self.logger.info("Step 4: 开始历史关键词去重")
        clusters, dropped_ids = self.historical_dedup.dedup_by_history(clusters)
        self.logger.info(f"历史去重完成，保留 {len(clusters)} 个集群，丢弃 {len(dropped_ids)} 个")
        if dropped_ids:
            self.logger.debug(f"丢弃的集群: {dropped_ids}")

        # Step 5: 板块数量控制
        self.logger.info("Step 5: 执行板块数量控制")
        section_counts = {}
        final_clusters = []
        for cluster in clusters:
            if section_counts.get(cluster.main_section, 0) < self.max_news_per_topic:
                final_clusters.append(cluster)
                section_counts[cluster.main_section] = section_counts.get(cluster.main_section, 0) + 1
        self.logger.info(f"板块数量控制完成，最终保留 {len(final_clusters)} 个集群")

        # 重新分配排名
        for i, cluster in enumerate(final_clusters):
            object.__setattr__(cluster, '_NewsCluster__rank', i + 1)

        # 构建统计信息
        stats = {
            'input_count': n_input,
            'filtered_count': len(filtered_items),
            'clustered_count': len(clusters),
            'output_count': len(final_clusters),
            'dropped_by_history': dropped_ids,
            'top_topics': sorted(
                section_counts.keys(),
                key=lambda x: section_counts[x],
                reverse=True
            )[:5]
        }

        # 输出结果
        result = {
            'clusters': [self._cluster_to_dict(c) for c in final_clusters],
            'stats': stats
        }

        self.save_json(output_file, result)
        self.logger.info(f"筛选排序模块执行完成，输出到: {output_file}")
        
        return {
            'count': len(final_clusters),
            'input_count': n_input,
            'api_calls': 1
        }

    def _cluster_to_dict(self, cluster: NewsCluster) -> dict:
        """将集群对象转换为字典"""
        return {
            'cluster_id': cluster.cluster_id,
            'keywords': cluster.keywords,
            'items': [it.__dict__.copy() for it in cluster.items],
            'merged_relevance': cluster.merged_relevance,
            'merged_hot_level': cluster.merged_hot_level,
            'main_section': cluster.main_section,
            'sub_section': cluster.sub_section,
            'rank': cluster.rank,
            'title': cluster.title,
            'urls': cluster.urls,
            'sources': cluster.sources,
            'merged_summary': cluster.merged_summary
        }
