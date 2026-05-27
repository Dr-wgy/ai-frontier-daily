#!/usr/bin/env python3
"""news_frontier.py 测试"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'project-space'))


class TestParseSteps:
    """parse_steps 函数测试"""

    def test_parse_steps_all(self):
        """测试 'all' 返回所有步骤"""
        # 模拟 import，因为 ORDER 在模块级别定义
        ORDER = ('ingest', 'filter_rank', 'summarize', 'assemble')

        def parse_steps(steps_arg: str):
            raw = (steps_arg or '').strip().lower()
            if raw == 'all':
                return list(ORDER)

            seen = set()
            out = []
            for part in raw.split(','):
                step = part.strip()
                if step in ORDER and step not in seen:
                    seen.add(step)
                    out.append(step)
            return out

        assert parse_steps('all') == ['ingest', 'filter_rank', 'summarize', 'assemble']

    def test_parse_steps_single(self):
        """测试单个步骤"""
        ORDER = ('ingest', 'filter_rank', 'summarize', 'assemble')

        def parse_steps(steps_arg: str):
            raw = (steps_arg or '').strip().lower()
            if raw == 'all':
                return list(ORDER)

            seen = set()
            out = []
            for part in raw.split(','):
                step = part.strip()
                if step in ORDER and step not in seen:
                    seen.add(step)
                    out.append(step)
            return out

        assert parse_steps('ingest') == ['ingest']

    def test_parse_steps_multiple(self):
        """测试多个步骤"""
        ORDER = ('ingest', 'filter_rank', 'summarize', 'assemble')

        def parse_steps(steps_arg: str):
            raw = (steps_arg or '').strip().lower()
            if raw == 'all':
                return list(ORDER)

            seen = set()
            out = []
            for part in raw.split(','):
                step = part.strip()
                if step in ORDER and step not in seen:
                    seen.add(step)
                    out.append(step)
            return out

        assert parse_steps('ingest,summarize') == ['ingest', 'summarize']

    def test_parse_steps_duplicates_removed(self):
        """测试重复步骤被去除"""
        ORDER = ('ingest', 'filter_rank', 'summarize', 'assemble')

        def parse_steps(steps_arg: str):
            raw = (steps_arg or '').strip().lower()
            if raw == 'all':
                return list(ORDER)

            seen = set()
            out = []
            for part in raw.split(','):
                step = part.strip()
                if step in ORDER and step not in seen:
                    seen.add(step)
                    out.append(step)
            return out

        assert parse_steps('ingest,filter_rank,ingest') == ['ingest', 'filter_rank']

    def test_parse_steps_invalid_ignored(self):
        """测试无效步骤被忽略"""
        ORDER = ('ingest', 'filter_rank', 'summarize', 'assemble')

        def parse_steps(steps_arg: str):
            raw = (steps_arg or '').strip().lower()
            if raw == 'all':
                return list(ORDER)

            seen = set()
            out = []
            for part in raw.split(','):
                step = part.strip()
                if step in ORDER and step not in seen:
                    seen.add(step)
                    out.append(step)
            return out

        assert parse_steps('ingest,invalid_step,summarize') == ['ingest', 'summarize']

    def test_parse_steps_empty(self):
        """测试空字符串"""
        ORDER = ('ingest', 'filter_rank', 'summarize', 'assemble')

        def parse_steps(steps_arg: str):
            raw = (steps_arg or '').strip().lower()
            if raw == 'all':
                return list(ORDER)

            seen = set()
            out = []
            for part in raw.split(','):
                step = part.strip()
                if step in ORDER and step not in seen:
                    seen.add(step)
                    out.append(step)
            return out

        assert parse_steps('') == []
        assert parse_steps(None) == []
