#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble.py — 拼版渲染模块

支持两种输入格式：
1. 新格式（阶段一改造后）：{'clusters': [...], 'blocks': {...}}
2. 旧格式（兼容）：{'items': [...], 'blocks': {...}}
"""

from __future__ import annotations
import os
from typing import Sequence, List

from utils import AppConfig, TEMPLATE_BRIEFING, TemplateRenderer, WorkModule
from utils.domain import BriefingMeta, SummaryItem, NewsCluster

_CN_NUM = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


class AssembleModule(WorkModule):
    """拼版渲染"""

    def __init__(self, config: AppConfig):
        super().__init__('assemble', config.date_str)
        self._app_config = config
        self.assembly_cfg = config.modules.assembly
        self.modules = config.protocols.classification.main_sections
        self.section_name_to_id = {m.name: m.id for m in self.modules}

    def _load_items(self, input_file: str) -> BriefingMeta:
        """加载 items 或 clusters，兼容新旧格式
        
        新格式：{'clusters': [...], 'blocks': {...}}
        旧格式：{'items': [...], 'blocks': {...}}
        """
        data = self.load_json(input_file)
        blocks = data.get('blocks', {})
        header = blocks.get('header', {})
        
        # 优先从 clusters 加载（新格式）
        if 'clusters' in data:
            clusters = [NewsCluster.from_dict(c) for c in data.get('clusters', [])]
            # 将集群转换为 SummaryItem
            items = [self._cluster_to_summary_item(c) for c in clusters]
            return BriefingMeta(
                items=items,
                tags_full=header.get('tags_full', '#AI早报'),
                data_sources=header.get('data_sources', '多家媒体'),
                footer=blocks.get('footer', {})
            )
        
        # 兼容旧格式
        items = [SummaryItem.from_dict(it) for it in data.get('items', [])]
        return BriefingMeta(
            items=items,
            tags_full=header.get('tags_full', '#AI早报'),
            data_sources=header.get('data_sources', '多家媒体'),
            footer=blocks.get('footer', {})
        )

    def _cluster_to_summary_item(self, cluster: NewsCluster) -> SummaryItem:
        """将新闻集群转换为 SummaryItem 格式
        
        集群包含多条新闻，转换为单条摘要时：
        - title: 取集群标题（最相关新闻的标题）
        - url: 取集群内第一个新闻的 URL
        - source: 取集群内第一个新闻的 source
        - 其他摘要字段从 cluster 本身获取（已在 summarize.py 生成）
        """
        # 取第一个新闻作为基础
        first_item = cluster.items[0] if cluster.items else None
        
        # 从 cluster 获取 LLM 生成的内容（如果有的话）
        # 注意：BriefingMeta.items 需要 SummaryItem，这里需要从 clusters 数据中提取
        # 由于 clusters 数据来自 summarize.py 的 SummaryCluster.to_dict()，包含了这些字段
        cluster_dict = cluster.__dict__.copy()
        
        # 构建 SummaryItem 需要的字段
        return SummaryItem(
            title=cluster.title,
            url=first_item.url if first_item else '',
            source=first_item.source if first_item else '',
            summary=cluster.merged_summary,
            pub_time=first_item.pub_time if first_item else '',
            _feed_url=first_item._feed_url if first_item else '',
            main_section=cluster.main_section,
            sub_section=cluster.sub_section,
            relevance=cluster.merged_relevance,
            hot_level=cluster.merged_hot_level,
            rank=cluster.rank,
            keywords=cluster.keywords,
            # 下面这些字段在集群转换时需要特殊处理
            # 因为 SummaryItem.from_dict 需要 headline, plain_explain 等
            # 但 cluster 对象可能没有这些字段（需要从 to_dict 结果中提取）
            headline='',
            plain_explain='',
            impacts=[],
            digest_for_outline='',
            vertical_tags=[],
            general_tags=[],
            hot='',
        )

    def _load_clusters_as_items(self, input_file: str) -> tuple:
        """加载数据并返回 items（支持 clusters 和 items 两种格式）
        
        Returns:
            (items: List[SummaryItem], blocks: dict)
        """
        data = self.load_json(input_file)
        blocks = data.get('blocks', {})
        header = blocks.get('header', {})
        
        # 优先从 clusters 加载（新格式）
        if 'clusters' in data:
            clusters = [NewsCluster.from_dict(c) for c in data.get('clusters', [])]
            # 直接使用 clusters 字典数据中的字段（summarize.py 已生成完整字段）
            items = []
            for cluster_data in data.get('clusters', []):
                # 取第一个新闻作为基础字段来源
                first_item = cluster_data.get('items', [{}])[0] if cluster_data.get('items') else {}
                items.append(SummaryItem(
                    title=cluster_data.get('title', cluster_data.get('headline', '')),
                    url=first_item.get('url', ''),
                    source=first_item.get('source', ''),
                    summary=cluster_data.get('merged_summary', first_item.get('summary', '')),
                    pub_time=first_item.get('pub_time', ''),
                    _feed_url=first_item.get('_feed_url', ''),
                    main_section=cluster_data.get('main_section', ''),
                    sub_section=cluster_data.get('sub_section', ''),
                    relevance=cluster_data.get('merged_relevance', 0),
                    hot_level=cluster_data.get('merged_hot_level', 0),
                    rank=cluster_data.get('rank', 0),
                    keywords=cluster_data.get('keywords', []),
                    headline=cluster_data.get('headline', ''),
                    plain_explain=cluster_data.get('plain_explain', ''),
                    impacts=cluster_data.get('impacts', []) if isinstance(cluster_data.get('impacts'), list) else [],
                    digest_for_outline=cluster_data.get('digest_for_outline', ''),
                    vertical_tags=cluster_data.get('vertical_tags', []) if isinstance(cluster_data.get('vertical_tags'), list) else [],
                    general_tags=cluster_data.get('general_tags', []) if isinstance(cluster_data.get('general_tags'), list) else [],
                    hot=cluster_data.get('hot', ''),
                ))
            return items, blocks
        
        # 兼容旧格式
        items = [SummaryItem.from_dict(it) for it in data.get('items', [])]
        return items, blocks

    def _news_row(self, number: str, it: SummaryItem, cap: int) -> dict:
        """生成新闻行数据"""
        summary = (it.digest_for_outline or it.summary)[:cap]
        vertical_tags = it.vertical_tags if isinstance(it.vertical_tags, list) else []
        general_tags = it.general_tags if isinstance(it.general_tags, list) else []

        return {
            'number': number,
            'headline': (it.headline or it.title)[:100],
            'tag': '其他',
            'link_label': f"{it.source}：{it.title}" if it.title else '（无标题）',
            'url': it.url or '#',
            'summary': summary,
            'plain_explain': it.plain_explain,
            'impacts': it.impacts if isinstance(it.impacts, list) else [],
            'hot': it.hot,
            'vertical_tags': vertical_tags,
            'general_tags': general_tags,
        }

    def _group_items(self, items: Sequence[SummaryItem]) -> dict:
        """按 main_section 分组"""
        groups = {m.id: [] for m in self.modules}
        for it in items:
            main_section = it.main_section
            if main_section:
                section_id = self.section_name_to_id.get(main_section)
                if section_id and section_id in groups:
                    groups[section_id].append(it)

        return groups

    def _build_context(self, items: List[SummaryItem], blocks: dict) -> dict:
        """构建渲染上下文"""
        groups = self._group_items(items)
        cap = max(200, int(self.assembly_cfg.summary_max_chars))

        rules = self._app_config.protocols.classification.main_sections
        header_data = blocks.get('header', {})
        header = {
            'date_str': self._app_config.date_str,
            'coverage_line': ' · '.join(getattr(m, 'name', '') for m in rules),
            'sources_str': header_data.get('data_sources', '多家媒体'),
            'header_tag': header_data.get('tags_full', '#AI早报'),
        }

        sections = []
        for i, m in enumerate(self.modules, 1):
            cn = _CN_NUM[i - 1] if i <= len(_CN_NUM) else str(i)
            mod_items = groups.get(m.id, [])[:self.assembly_cfg.max_news_per_module]
            summary_items = []
            for it in mod_items:
                has_plain = bool(it.plain_explain)
                has_impacts = bool(it.impacts)
                if has_plain or has_impacts:
                    summary_items.append(it)
                else:
                    self.logger.debug(f"[过滤] [{m.name}] 标题: {it.title[:50]}... 原因: plain_explain={has_plain}, impacts={has_impacts}")
            entries = [self._news_row(f"{i}.{j+1}", it, cap) for j, it in enumerate(summary_items)]
            sections.append({'heading': f"## {cn}、{m.name}\n", 'empty': not summary_items, 'entries': entries})

        footer_data = blocks.get('footer', {})
        footer_rows = []
        for m in self.modules:
            raw = footer_data.get(m.id, '')
            lines = [ln.strip() for ln in str(raw).splitlines() if ln.strip()][:self.assembly_cfg.footer_max_lines_per_module]
            footer_rows.append({'abbrev': m.name, 'lines': lines or ['今日暂无相关报道']})

        return {
            'header': header,
            'sections': sections,
            'footer': {'mode': 'blocks', 'rows': footer_rows}
        }

    def run(self, input_file: str, output_file: str) -> dict:
        """执行完整流程"""
        items, blocks = self._load_clusters_as_items(input_file)

        if not items:
            self.save_json(output_file, {'items': [], 'blocks': {}})
            return {'path': output_file, 'count': 0}

        ctx = self._build_context(items, blocks)
        renderer = TemplateRenderer()
        md = renderer.render(TEMPLATE_BRIEFING, ctx)

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        return {'path': output_file, 'count': len(items)}
