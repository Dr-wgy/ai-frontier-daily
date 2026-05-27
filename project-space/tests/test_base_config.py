#!/usr/bin/env python3
"""base_config.py 补充单元测试 - ConfigDict 和 PathConfig"""

import pytest
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.base_config import (
    AppConfig,
    ConfigDict,
    ModuleLayerConfig,
    LinkLayerConfig,
    ProtocolLayerConfig,
    PathConfig,
    FN_RAW_FETCHED,
    FN_INGESTED,
    FN_FILTERED_RANKED,
    FN_SUMMARY,
    FN_BRIEFING,
)


class TestConfigDict:
    """ConfigDict 类测试"""

    def test_config_dict_empty_init(self):
        cd = ConfigDict()
        assert cd.__dict__ == {}

    def test_config_dict_nested_dict(self):
        data = {
            'level1': {
                'level2': 'value'
            }
        }
        cd = ConfigDict(data)
        assert hasattr(cd, 'level1')
        assert isinstance(cd.level1, ConfigDict)
        assert cd.level1.level2 == 'value'

    def test_config_dict_list_of_dicts(self):
        data = {
            'items': [
                {'name': 'item1'},
                {'name': 'item2'},
            ]
        }
        cd = ConfigDict(data)
        assert isinstance(cd.items[0], ConfigDict)
        assert cd.items[0].name == 'item1'
        assert isinstance(cd.items[1], ConfigDict)
        assert cd.items[1].name == 'item2'

    def test_config_dict_list_of_non_dicts(self):
        data = {
            'tags': ['AI', 'ML', 'DL']
        }
        cd = ConfigDict(data)
        assert cd.tags == ['AI', 'ML', 'DL']

    def test_config_dict_mixed_types(self):
        data = {
            'string': 'text',
            'number': 42,
            'float': 3.14,
            'boolean': True,
            'null': None,
            'list': [1, 2, 3],
        }
        cd = ConfigDict(data)
        assert cd.string == 'text'
        assert cd.number == 42
        assert cd.float == 3.14
        assert cd.boolean is True
        assert cd.null is None
        assert cd.list == [1, 2, 3]

    def test_config_dict_repr(self):
        cd = ConfigDict({'key': 'value'})
        repr_str = repr(cd)
        assert 'ConfigDict' in repr_str
        assert 'key' in repr_str


class TestPathConfig:
    """PathConfig 类测试"""

    def test_path_config_init(self):
        pc = PathConfig('2026-05-23')
        assert pc.date_str == '2026-05-23'

    def test_output_dir(self):
        pc = PathConfig('2026-05-23')
        output_dir = pc.output_dir()
        assert output_dir.name == '2026-05-23'
        assert 'output' in str(output_dir)

    def test_day_paths(self):
        pc = PathConfig('2026-05-23')
        paths = pc.day_paths()
        assert 'dir' in paths
        assert 'ingested' in paths
        assert 'filtered' in paths
        assert 'summary' in paths
        assert 'briefing' in paths
        assert paths['ingested'].name == FN_INGESTED
        assert paths['filtered'].name == FN_FILTERED_RANKED
        assert paths['summary'].name == FN_SUMMARY
        assert paths['briefing'].name == FN_BRIEFING

    def test_get_templates_path(self):
        pc = PathConfig('2026-05-23')
        templates_path = pc.get_templates_path()
        assert templates_path.exists()
        assert (templates_path / 'briefing-template.md.j2').exists()

    def test_get_prompts_path(self):
        pc = PathConfig('2026-05-23')
        prompts_path = pc.get_prompts_path()
        assert prompts_path.exists()
        assert 'prompts' in str(prompts_path)

    def test_get_recent_output_dirs_no_dirs(self, tmp_path, monkeypatch):
        pc = PathConfig('2026-05-23')
        import utils.base_config
        original_root = utils.base_config.PROJECT_ROOT
        monkeypatch.setattr(utils.base_config, 'PROJECT_ROOT', tmp_path)
        recent = pc.get_recent_output_dirs(3)
        assert recent == []
        monkeypatch.setattr(utils.base_config, 'PROJECT_ROOT', original_root)


class TestModuleLayerConfig:
    """ModuleLayerConfig 类测试"""

    def test_module_layer_config_empty(self):
        mlc = ModuleLayerConfig({})
        assert hasattr(mlc, 'public_feeds')
        assert hasattr(mlc, 'dedup')
        assert hasattr(mlc, 'filter_rank')
        assert hasattr(mlc, 'keyword_dedup')
        assert hasattr(mlc, 'assembly')

    def test_public_feeds_feeds_list(self):
        data = {
            'public_feeds': {
                'settings': {'timeout_seconds': 30},
                'feeds': [
                    {'url': 'https://example.com/feed1', 'name': 'Feed1'},
                    {'url': 'https://example.com/feed2', 'name': 'Feed2'},
                ]
            }
        }
        mlc = ModuleLayerConfig(data)
        assert len(mlc.public_feeds.feeds) == 2
        assert mlc.public_feeds.timeout_seconds == 30


class TestLinkLayerConfig:
    """LinkLayerConfig 类测试"""

    def test_link_layer_config_empty(self):
        llc = LinkLayerConfig({})
        assert hasattr(llc, 'llm')

    def test_link_layer_config_with_llm(self):
        data = {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
            }
        }
        llc = LinkLayerConfig(data)
        assert llc.llm.provider == 'openai'
        assert llc.llm.model == 'gpt-4'


class TestProtocolLayerConfig:
    """ProtocolLayerConfig 类测试"""

    def test_protocol_layer_config_empty(self):
        plc = ProtocolLayerConfig({})
        assert hasattr(plc, 'protocol')
        assert hasattr(plc, 'classification')
        assert plc.vertical_tags_whitelist == []
        assert plc.general_tags_whitelist == []

    def test_protocol_layer_config_with_tags(self):
        data = {
            'classification': {
                'tags': {
                    'vertical_tags_whitelist': ['AI', 'ML'],
                    'general_tags_whitelist': ['Tech', 'News'],
                }
            }
        }
        plc = ProtocolLayerConfig(data)
        assert plc.vertical_tags_whitelist == ['AI', 'ML']
        assert plc.general_tags_whitelist == ['Tech', 'News']


class TestFileNameConstants:
    """文件名常量测试"""

    def test_file_name_constants(self):
        assert FN_RAW_FETCHED == 'raw_fetched.jsonl'
        assert FN_INGESTED == 'ingested.jsonl'
        assert FN_FILTERED_RANKED == 'filtered_ranked.json'
        assert FN_SUMMARY == 'summary.json'
        assert FN_BRIEFING == 'briefing.md'
