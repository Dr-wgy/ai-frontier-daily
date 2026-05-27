#!/usr/bin/env python3
"""pytest 全局共享 fixtures"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_news_item_dict():
    """样例 NewsItem 字典数据"""
    return {
        'title': 'GPT-5 发布：OpenAI 推出新一代大模型',
        'url': 'https://example.com/gpt5-release',
        'source': 'TechCrunch',
        'summary': 'OpenAI 宣布推出 GPT-5，带来革命性突破',
        'pub_time': '2026-05-23T10:00:00Z',
        '_feed_url': 'https://example.com/feed',
    }


@pytest.fixture
def sample_filtered_item_dict():
    """样例 FilteredItem 字典数据"""
    return {
        'title': 'Claude 4 发布：Anthropic 推出新一代大模型',
        'url': 'https://example.com/claude4-release',
        'source': 'The Verge',
        'summary': 'Anthropic 宣布推出 Claude 4，带来革命性突破',
        'pub_time': '2026-05-23T10:00:00Z',
        '_feed_url': 'https://example.com/feed',
        'main_section': 'core_tech',
        'sub_section': 'large_language_model',
        'keywords': ['AI', '大模型', 'Anthropic'],
        'relevance': 0.95,
        'hot_level': 0.88,
        'rank': 1,
    }


@pytest.fixture
def sample_summary_item_dict():
    """样例 SummaryItem 字典数据"""
    return {
        'title': 'Claude 4 发布：Anthropic 推出新一代大模型',
        'url': 'https://example.com/claude4-release',
        'source': 'The Verge',
        'summary': 'Anthropic 宣布推出 Claude 4，带来革命性突破',
        'pub_time': '2026-05-23T10:00:00Z',
        '_feed_url': 'https://example.com/feed',
        'main_section': 'core_tech',
        'sub_section': 'large_language_model',
        'keywords': ['AI', '大模型', 'Anthropic'],
        'relevance': 0.95,
        'hot_level': 0.88,
        'rank': 1,
        'headline': 'Claude 4 发布：Anthropic 推出新一代大模型',
        'plain_explain': 'Anthropic推出新一代AI助手',
        'impacts': ['AI助手能力提升', '安全性改善'],
        'digest_for_outline': 'Claude 4是最新一代模型',
        'vertical_tags': ['AI', 'Anthropic'],
        'general_tags': ['科技', '人工智能'],
        'hot': 'hot',
    }


@pytest.fixture
def temp_jsonl_file(tmp_path, sample_news_item_dict):
    """创建临时 JSONL 文件"""
    import json
    file_path = tmp_path / "test.jsonl"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(sample_news_item_dict, ensure_ascii=False) + '\n')
        f.write(json.dumps({**sample_news_item_dict, 'title': '第二篇新闻'}, ensure_ascii=False) + '\n')
    return file_path


@pytest.fixture
def temp_json_file(tmp_path, sample_news_item_dict):
    """创建临时 JSON 文件"""
    import json
    file_path = tmp_path / "test.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({'items': [sample_news_item_dict]}, f, ensure_ascii=False, indent=2)
    return file_path


@pytest.fixture
def temp_template_file(tmp_path):
    """创建临时模板文件"""
    template_content = """x: $$$$|
{{ name }}
{{ value }}
x: |$$$$

system: $$$$|
You are a helpful assistant.
system: |$$$$

user: $$$$|
Hello, {{ name }}!
user: |$$$$
"""
    file_path = tmp_path / "test_template.md"
    file_path.write_text(template_content, encoding='utf-8')
    return file_path
