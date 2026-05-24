#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble.py — 拼版渲染模块

输入格式：{'clusters': [...], 'blocks': {...}}
"""

from __future__ import annotations
import os
from typing import Sequence, List

from utils import AppConfig, TEMPLATE_BRIEFING, TEMPLATE_BRIEFING_HTML, TemplateRenderer, WorkModule
from utils.domain import SummaryCluster

_CN_NUM = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


class AssembleModule(WorkModule):
    """拼版渲染"""

    def __init__(self, config: AppConfig):
        super().__init__('assemble', config.date_str)
        self._app_config = config
        self.assembly_cfg = config.modules.assembly
        self.modules = config.protocols.classification.main_sections
        self.section_name_to_id = {m.name: m.id for m in self.modules}

    def _load_clusters(self, input_file: str) -> tuple:
        """加载 clusters 数据
        
        Returns:
            (clusters: List[SummaryCluster], blocks: dict)
        """
        data = self.load_json(input_file)
        blocks = data.get('blocks', {})
        
        clusters = [SummaryCluster.from_dict(c) for c in data.get('clusters', [])]
        return clusters, blocks

    def _news_row(self, number: str, sc: SummaryCluster, cap: int) -> dict:
        """生成新闻行数据"""
        summary = (sc.digest_for_outline or sc.summary)[:cap]
        vertical_tags = sc.vertical_tags if isinstance(sc.vertical_tags, list) else []
        general_tags = sc.general_tags if isinstance(sc.general_tags, list) else []

        return {
            'number': number,
            'headline': (sc.headline or sc.title)[:100],
            'tag': '其他',
            'link_label': f"{sc.source}：{sc.title}" if sc.title else '（无标题）',
            'url': sc.url or '#',
            'summary': summary,
            'plain_explain': sc.plain_explain,
            'impacts': sc.impacts if isinstance(sc.impacts, list) else [],
            'hot': sc.hot,
            'vertical_tags': vertical_tags,
            'general_tags': general_tags,
        }

    def _group_clusters(self, clusters: Sequence[SummaryCluster]) -> dict:
        """按 main_section 分组"""
        groups = {m.id: [] for m in self.modules}
        for sc in clusters:
            main_section = sc.main_section
            if main_section:
                section_id = self.section_name_to_id.get(main_section)
                if section_id and section_id in groups:
                    groups[section_id].append(sc)

        return groups

    def _build_context(self, clusters: List[SummaryCluster], blocks: dict) -> dict:
        """构建渲染上下文"""
        groups = self._group_clusters(clusters)
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
            for sc in mod_items:
                has_plain = bool(sc.plain_explain)
                has_impacts = bool(sc.impacts)
                if has_plain or has_impacts:
                    summary_items.append(sc)
                else:
                    self.logger.debug(f"[过滤] [{m.name}] 标题: {sc.title[:50]}... 原因: plain_explain={has_plain}, impacts={has_impacts}")
            entries = [self._news_row(f"{i}.{j+1}", sc, cap) for j, sc in enumerate(summary_items)]
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
        clusters, blocks = self._load_clusters(input_file)

        if not clusters:
            self.save_json(output_file, {'clusters': [], 'blocks': {}})
            return {'path': output_file, 'count': 0}

        ctx = self._build_context(clusters, blocks)
        renderer = TemplateRenderer()
        md = renderer.render(TEMPLATE_BRIEFING, ctx)
        html = renderer.render(TEMPLATE_BRIEFING_HTML, ctx)

        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)

        html_file = output_file.replace('.md', '.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)

        return {'path': output_file, 'html_path': html_file, 'count': len(clusters)}
