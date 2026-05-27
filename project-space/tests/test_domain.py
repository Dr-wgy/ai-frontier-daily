#!/usr/bin/env python3
"""domain.py 单元测试 - 数据模型层"""

import pytest
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.domain import NewsItem, FilteredItem, SummaryItem, NewsCluster


class TestNewsItem:
    """NewsItem 数据模型测试"""

    def test_create_news_item(self, sample_news_item_dict):
        item = NewsItem.from_dict(sample_news_item_dict)
        assert item.title == 'GPT-5 发布：OpenAI 推出新一代大模型'
        assert item.url == 'https://example.com/gpt5-release'
        assert item.source == 'TechCrunch'
        assert item.summary == 'OpenAI 宣布推出 GPT-5，带来革命性突破'
        assert item.pub_time == '2026-05-23T10:00:00Z'
        assert item._feed_url == 'https://example.com/feed'

    def test_news_item_missing_fields(self):
        item = NewsItem.from_dict({})
        assert item.title == ''
        assert item.url == ''
        assert item.source == ''
        assert item.summary == ''
        assert item.pub_time == ''
        assert item._feed_url == ''

    def test_news_item_partial_fields(self):
        partial_dict = {'title': 'Test Title', 'source': 'Test Source'}
        item = NewsItem.from_dict(partial_dict)
        assert item.title == 'Test Title'
        assert item.source == 'Test Source'
        assert item.url == ''

    def test_news_item_is_frozen(self, sample_news_item_dict):
        item = NewsItem.from_dict(sample_news_item_dict)
        with pytest.raises(AttributeError):
            item.title = 'New Title'


class TestFilteredItem:
    """FilteredItem 数据模型测试"""

    def test_create_filtered_item(self, sample_filtered_item_dict):
        item = FilteredItem.from_dict(sample_filtered_item_dict)
        assert item.title == 'Claude 4 发布：Anthropic 推出新一代大模型'
        assert item.main_section == 'core_tech'
        assert item.sub_section == 'large_language_model'
        assert item.keywords == ['AI', '大模型', 'Anthropic']
        assert item.relevance == 0.95
        assert item.hot_level == 0.88
        assert item.rank == 1

    def test_filtered_item_keywords_string_conversion(self):
        item_dict = {
            'title': 'Test',
            'url': 'https://test.com',
            'source': 'Test',
            'summary': 'Test',
            'pub_time': '2026-05-23',
            '_feed_url': '',
            'keywords': 'single_keyword',
        }
        item = FilteredItem.from_dict(item_dict)
        assert item.keywords == ['single_keyword']

    def test_filtered_item_keywords_empty_string(self):
        item_dict = {
            'title': 'Test',
            'url': 'https://test.com',
            'source': 'Test',
            'summary': 'Test',
            'pub_time': '2026-05-23',
            '_feed_url': '',
            'keywords': '',
        }
        item = FilteredItem.from_dict(item_dict)
        assert item.keywords == []

    def test_filtered_item_keywords_none(self):
        item_dict = {
            'title': 'Test',
            'url': 'https://test.com',
            'source': 'Test',
            'summary': 'Test',
            'pub_time': '2026-05-23',
            '_feed_url': '',
            'keywords': None,
        }
        item = FilteredItem.from_dict(item_dict)
        assert item.keywords is None

    def test_filtered_item_from_llm_response(self):
        llm_response = {
            'items': [
                {
                    'source_index': '0',
                    'main_section': 'core_tech',
                    'sub_section': 'llm',
                    'keywords': ['AI', 'GPT'],
                    'relevance': '0.9',
                    'hot_level': '0.8',
                },
                {
                    'source_index': '1',
                    'main_section': 'application',
                    'sub_section': 'robotics',
                    'keywords': ['robot'],
                    'relevance': 0.7,
                    'hot_level': 0.6,
                },
            ]
        }
        items = FilteredItem.from_llm_response(llm_response)
        assert len(items) == 2
        assert items[0]['source_index'] == 0
        assert items[0]['main_section'] == 'core_tech'
        assert items[1]['source_index'] == 1

    def test_filtered_item_from_llm_response_invalid_index(self):
        llm_response = {
            'items': [
                {'source_index': 'invalid', 'main_section': 'test'},
                {'source_index': None, 'main_section': 'test2'},
                {},
            ]
        }
        items = FilteredItem.from_llm_response(llm_response)
        assert len(items) == 0

    def test_filtered_item_from_llm_response_not_dict(self):
        assert FilteredItem.from_llm_response("not a dict") == []
        assert FilteredItem.from_llm_response(None) == []

    def test_filtered_item_from_news_and_llm(self, sample_news_item_dict):
        news_item = NewsItem.from_dict(sample_news_item_dict)
        llm_result = {
            'main_section': 'core_tech',
            'sub_section': 'llm',
            'keywords': ['AI', '大模型'],
            'relevance': 0.95,
            'hot_level': 0.88,
        }
        filtered = FilteredItem.from_news_and_llm(news_item, llm_result, rank=1)
        assert filtered.title == news_item.title
        assert filtered.main_section == 'core_tech'
        assert filtered.rank == 1
        assert filtered.keywords == ['AI', '大模型']

    def test_filtered_item_inherits_from_news_item(self, sample_filtered_item_dict):
        item = FilteredItem.from_dict(sample_filtered_item_dict)
        assert isinstance(item, NewsItem)
        assert hasattr(item, 'title')
        assert hasattr(item, 'url')
        assert hasattr(item, 'source')


class TestSummaryItem:
    """SummaryItem 数据模型测试"""

    def test_create_summary_item(self, sample_summary_item_dict):
        item = SummaryItem.from_dict(sample_summary_item_dict)
        assert item.title == 'Claude 4 发布：Anthropic 推出新一代大模型'
        assert item.headline == 'Claude 4 发布：Anthropic 推出新一代大模型'
        assert item.plain_explain == 'Anthropic推出新一代AI助手'
        assert item.impacts == ['AI助手能力提升', '安全性改善']
        assert item.digest_for_outline == 'Claude 4是最新一代模型'
        assert item.vertical_tags == ['AI', 'Anthropic']
        assert item.general_tags == ['科技', '人工智能']
        assert item.hot == 'hot'

    def test_summary_item_from_filtered_and_llm(self, sample_filtered_item_dict):
        filtered = FilteredItem.from_dict(sample_filtered_item_dict)
        llm_data = {
            'headline': 'Claude 4 重磅发布',
            'plain_explain': 'Anthropic 推出新一代 AI 助手',
            'impacts': ['AI 助手能力提升', '安全性改善'],
            'digest_for_outline': 'Claude 4 是最新一代模型',
            'vertical_tags': ['AI', 'Anthropic'],
            'general_tags': ['科技', '人工智能'],
            'hot': 'hot',
        }
        summary = SummaryItem.from_filtered_and_llm(filtered, llm_data)
        assert summary.title == filtered.title
        assert summary.headline == 'Claude 4 重磅发布'
        assert summary.plain_explain == 'Anthropic 推出新一代 AI 助手'
        assert summary.impacts == ['AI 助手能力提升', '安全性改善']
        assert summary.vertical_tags == ['AI', 'Anthropic']
        assert summary.general_tags == ['科技', '人工智能']
        assert summary.hot == 'hot'

    def test_summary_item_vertical_tags_string_conversion(self):
        item_dict = {
            'title': 'Test',
            'url': 'https://test.com',
            'source': 'Test',
            'summary': 'Test',
            'pub_time': '2026-05-23',
            '_feed_url': '',
            'vertical_tags': 'single_tag',
        }
        item = SummaryItem.from_dict(item_dict)
        assert item.vertical_tags == ['single_tag']

    def test_summary_item_general_tags_string_conversion(self):
        item_dict = {
            'title': 'Test',
            'url': 'https://test.com',
            'source': 'Test',
            'summary': 'Test',
            'pub_time': '2026-05-23',
            '_feed_url': '',
            'general_tags': 'single_tag',
        }
        item = SummaryItem.from_dict(item_dict)
        assert item.general_tags == ['single_tag']

    def test_summary_item_impacts_non_list(self):
        item_dict = {
            'title': 'Test',
            'url': 'https://test.com',
            'source': 'Test',
            'summary': 'Test',
            'pub_time': '2026-05-23',
            '_feed_url': '',
            'impacts': 'not a list',
        }
        item = SummaryItem.from_dict(item_dict)
        assert item.impacts == []

    def test_summary_item_extract_articles(self):
        llm_response = {
            'articles': [
                {'source_index': 0, 'title': 'Article 1'},
                {'source_index': 1, 'title': 'Article 2'},
                {'source_index': 2, 'title': 'Article 3'},
            ],
            'deduplication': {
                'drop_indices': [1, '3']
            }
        }
        articles, drop_indices = SummaryItem.extract_articles(llm_response)
        assert len(articles) == 3
        assert 0 in articles
        assert 1 in articles
        assert 2 in articles
        assert drop_indices == {1, 3}

    def test_summary_item_extract_articles_invalid(self):
        llm_response = {
            'articles': [
                {'source_index': 'invalid'},
                {'source_index': None},
                {},
            ],
            'deduplication': {
                'drop_indices': ['invalid', None]
            }
        }
        articles, drop_indices = SummaryItem.extract_articles(llm_response)
        assert len(articles) == 0
        assert drop_indices == set()

    def test_summary_item_extract_articles_not_dict(self):
        articles, drop_indices = SummaryItem.extract_articles("not a dict")
        assert articles == {}
        assert drop_indices == set()
        articles, drop_indices = SummaryItem.extract_articles(None)
        assert articles == {}
        assert drop_indices == set()

    def test_summary_item_inherits_from_filtered_item(self, sample_summary_item_dict):
        item = SummaryItem.from_dict(sample_summary_item_dict)
        assert isinstance(item, FilteredItem)
        assert isinstance(item, NewsItem)


class TestNewsCluster:
    """NewsCluster 数据模型测试"""

    def test_create_news_cluster(self, sample_filtered_item_dict):
        filtered = FilteredItem.from_dict(sample_filtered_item_dict)
        cluster = NewsCluster(
            cluster_id='cluster_1',
            keywords=['AI', '大模型'],
            items=[filtered],
            merged_relevance=0.95,
            merged_hot_level=0.88,
            main_section='core_tech',
            sub_section='llm',
            rank=1,
        )
        assert cluster.cluster_id == 'cluster_1'
        assert cluster.keywords == ['AI', '大模型']
        assert len(cluster.items) == 1
        assert cluster.merged_relevance == 0.95
        assert cluster.main_section == 'core_tech'

    def test_news_cluster_title_property(self, sample_filtered_item_dict):
        filtered = FilteredItem.from_dict(sample_filtered_item_dict)
        filtered2 = FilteredItem.from_dict({**sample_filtered_item_dict, 'title': 'Lower Relevance', 'relevance': 0.5})
        cluster = NewsCluster(
            cluster_id='cluster_1',
            keywords=['AI'],
            items=[filtered2, filtered],
            merged_relevance=0.95,
            merged_hot_level=0.88,
            main_section='core_tech',
            sub_section='llm',
            rank=1,
        )
        assert cluster.title == filtered.title

    def test_news_cluster_title_empty_items(self):
        cluster = NewsCluster(
            cluster_id='cluster_1',
            keywords=['AI'],
            items=[],
            merged_relevance=0,
            merged_hot_level=0,
            main_section='core_tech',
            sub_section='llm',
            rank=1,
        )
        assert cluster.title == ''

    def test_news_cluster_urls(self, sample_filtered_item_dict):
        filtered = FilteredItem.from_dict(sample_filtered_item_dict)
        filtered2 = FilteredItem.from_dict({**sample_filtered_item_dict, 'url': 'https://test2.com'})
        cluster = NewsCluster(
            cluster_id='cluster_1',
            keywords=['AI'],
            items=[filtered, filtered2],
            merged_relevance=0.95,
            merged_hot_level=0.88,
            main_section='core_tech',
            sub_section='llm',
            rank=1,
        )
        assert len(cluster.urls) == 2
        assert 'https://example.com/claude4-release' in cluster.urls
        assert 'https://test2.com' in cluster.urls
