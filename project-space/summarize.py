#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
summarize.py — LLM 摘要模块（支持新闻集群汇总）
"""

from __future__ import annotations

import json
from typing import List, Sequence

from utils import AppConfig, LLMClient, WorkModule, PromptLoader, TEMPLATE_SUMMARIZE
from utils.domain import NewsCluster, SummaryCluster


class SummarizeModule(WorkModule):
    """LLM 摘要（支持新闻集群汇总）"""

    def __init__(self, config: AppConfig):
        super().__init__('summarize', config.date_str)
        self.llm_client = LLMClient(config.llm_client_cfg, self.date)
        self._app_config = config

    def _load_clusters(self, input_file: str) -> List[NewsCluster]:
        """加载输入文件，从 clusters 字段加载新闻集群"""
        data = self.load_json(input_file)
        if data is not None and isinstance(data, dict) and 'clusters' in data:
            return [NewsCluster.from_dict(it) for it in data.get('clusters', [])]
        return []

    def _build_prompts(self, clusters: Sequence[NewsCluster]) -> tuple:
        """构建 system/user 提示词（针对新闻集群）"""
        item_cap = int(self._app_config.links.llm.summarize_item_cap)
        
        rows = []
        for i, cluster in enumerate(clusters):
            # 为每个集群构建包含多条新闻的数据结构
            news_items = []
            for item in cluster.items:
                body = self.clip_text(item.summary, item_cap)
                news_items.append({
                    'title': item.title,
                    'summary': body,
                })
            
            rows.append({
                'cluster_index': i,
                'keywords': cluster.keywords,
                'main_section': cluster.main_section,
                'sub_section': cluster.sub_section,
                'news_items': news_items,
                'title': cluster.title,
                'merged_summary': self.clip_text(cluster.merged_summary, item_cap * 3)
            })

        self.logger.info(f"构建 {len(rows)} 个新闻集群的提示词")
        
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
        self.logger.info("开始执行摘要模块")
        
        assembly_cfg = self._app_config.modules.assembly
        max_items = min(max(1, int(assembly_cfg.summary_unified_max_items)), 500)

        # 加载新闻集群
        clusters = self._load_clusters(input_file)[:max_items]
        n_clusters = len(clusters)
        
        self.logger.info(f"加载到 {n_clusters} 个新闻集群")

        if n_clusters == 0:
            self.save_json(output_file, {'clusters': [], 'blocks': {}})
            return {'count': 0, 'api_calls': 0, 'unified': True}

        # 构建提示词并调用 LLM
        system, user = self._build_prompts(clusters)
        max_tokens = self._app_config.links.llm.summarize_max_tokens
        self.logger.info("调用 LLM 进行集群汇总...")
        data = self.llm_client.call_json(system, user, max_tokens=max_tokens)

        # 提取 LLM 返回的集群摘要数据
        by_cluster, drop = self._extract_cluster_articles(data)
        
        # 调试：打印 LLM 响应的原始统计
        raw_articles = data.get('articles', []) if isinstance(data, dict) else []
        self.logger.debug(f"输入 {len(clusters)} 个集群，LLM 返回 {len(raw_articles)} 条 articles")
        self.logger.debug(f"有效 cluster_index 匹配 {len(by_cluster)} 个，drop_indices 包含 {len(drop)} 个")

        # 生成输出结果
        out_clusters = []
        self.logger.debug(f"预计保留: {len(by_cluster)} 个集群（LLM 返回且不在 drop_indices 中）")
        
        for i, cluster in enumerate(clusters):
            if i in drop:
                self.logger.debug(f"跳过集群 {i} (在 drop_indices 中)")
                continue
            if i not in by_cluster:
                self.logger.debug(f"跳过集群 {i} (LLM 未返回该集群数据)")
                continue
            
            llm_data = by_cluster.get(i, {})
            summary_cluster = SummaryCluster.from_cluster_and_llm(cluster, llm_data)
            out_clusters.append(summary_cluster)

        # 保存输出
        result = {
            'clusters': [sc.to_dict() for sc in out_clusters],
            'blocks': data.get('blocks', {}) if isinstance(data, dict) else {}
        }
        
        self.save_json(output_file, result)
        
        self.logger.info(f"摘要模块执行完成，输出 {len(out_clusters)} 个集群")
        
        return {'count': len(out_clusters), 'api_calls': 1, 'unified': True}
