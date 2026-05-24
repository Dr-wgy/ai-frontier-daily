#!/usr/bin/env python3
"""work_module.py 单元测试"""

from pathlib import Path
import sys

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.work_module import WorkModule


class TestWorkModuleStaticMethods:
    """WorkModule 静态方法测试"""

    def test_load_jsonl_success(self, temp_jsonl_file):
        items = WorkModule.load_jsonl(str(temp_jsonl_file))
        assert len(items) == 2
        assert items[0]['title'] == 'GPT-5 发布：OpenAI 推出新一代大模型'
        assert items[1]['title'] == '第二篇新闻'

    def test_load_jsonl_file_not_exists(self):
        items = WorkModule.load_jsonl('/non/existent/path/file.jsonl')
        assert items == []

    def test_load_jsonl_empty_file(self, tmp_path):
        empty_file = tmp_path / 'empty.jsonl'
        empty_file.write_text('', encoding='utf-8')
        items = WorkModule.load_jsonl(str(empty_file))
        assert items == []

    def test_load_jsonl_with_blank_lines(self, tmp_path):
        file_with_blanks = tmp_path / 'blanks.jsonl'
        file_with_blanks.write_text('{"a": 1}\n\n{"b": 2}\n  \n{"c": 3}\n', encoding='utf-8')
        items = WorkModule.load_jsonl(str(file_with_blanks))
        assert len(items) == 3

    def test_load_jsonl_invalid_json(self, tmp_path):
        invalid_file = tmp_path / 'invalid.jsonl'
        invalid_file.write_text('{"valid": true}\ninvalid json\n{"also": "valid"}\n', encoding='utf-8')
        items = WorkModule.load_jsonl(str(invalid_file))
        assert len(items) == 2
        assert items[0]['valid'] is True
        assert items[1]['also'] == 'valid'

    def test_save_jsonl_success(self, tmp_path):
        output_file = tmp_path / 'output.jsonl'
        items = [{'a': 1}, {'b': 2}]
        WorkModule.save_jsonl(str(output_file), items)
        content = output_file.read_text(encoding='utf-8')
        assert '{"a": 1}' in content
        assert '{"b": 2}' in content

    def test_save_jsonl_creates_directory(self, tmp_path):
        output_file = tmp_path / 'subdir' / 'output.jsonl'
        items = [{'test': True}]
        WorkModule.save_jsonl(str(output_file), items)
        assert output_file.exists()

    def test_save_jsonl_empty_list(self, tmp_path):
        output_file = tmp_path / 'empty.jsonl'
        WorkModule.save_jsonl(str(output_file), [])
        content = output_file.read_text(encoding='utf-8')
        assert content == ''

    def test_load_json_success(self, temp_json_file):
        data = WorkModule.load_json(str(temp_json_file))
        assert data is not None
        assert 'items' in data
        assert len(data['items']) == 1

    def test_load_json_file_not_exists(self):
        data = WorkModule.load_json('/non/existent/path/file.json')
        assert data is None

    def test_save_json_success(self, tmp_path):
        output_file = tmp_path / 'output.json'
        data = {'items': [{'title': 'Test'}]}
        WorkModule.save_json(str(output_file), data)
        content = output_file.read_text(encoding='utf-8')
        assert 'Test' in content

    def test_save_json_creates_directory(self, tmp_path):
        output_file = tmp_path / 'subdir' / 'output.json'
        data = {'test': True}
        WorkModule.save_json(str(output_file), data)
        assert output_file.exists()

    def test_save_json_nested_data(self, tmp_path):
        output_file = tmp_path / 'nested.json'
        data = {
            'level1': {
                'level2': {
                    'level3': 'deep'
                }
            },
            'list': [1, 2, 3]
        }
        WorkModule.save_json(str(output_file), data)
        loaded = WorkModule.load_json(str(output_file))
        assert loaded['level1']['level2']['level3'] == 'deep'
        assert loaded['list'] == [1, 2, 3]

    def test_clip_text_normal(self):
        text = "Short text"
        result = WorkModule.clip_text(text, 50)
        assert result == text

    def test_clip_text_exceeds_max(self):
        text = "This is a very long text that should be truncated"
        result = WorkModule.clip_text(text, 20)
        assert len(result) < len(text)
        assert result.endswith('…')

    def test_clip_text_exactly_max(self):
        text = "Short text"
        result = WorkModule.clip_text(text, 5)
        assert result != text
        assert result.endswith('…')

    def test_clip_text_empty(self):
        result = WorkModule.clip_text("", 10)
        assert result == ""

    def test_clip_text_none(self):
        result = WorkModule.clip_text(None, 10)
        assert result == ""

    def test_clip_text_with_whitespace(self):
        text = "This   has    multiple   spaces"
        result = WorkModule.clip_text(text, 30)
        assert '  ' not in result

    def test_clip_text_custom_suffix(self):
        text = "This is a very long text that should be truncated"
        result = WorkModule.clip_text(text, 20, suffix='...')
        assert result.endswith('...')
        assert len(result) < len(text)


class TestWorkModuleAbstract:
    """WorkModule 抽象类测试"""

    def test_work_module_is_abstract(self):
        with pytest.raises(TypeError):
            WorkModule('test_module', '2026-05-23')

    def test_work_module_concrete_implementation(self):
        class ConcreteModule(WorkModule):
            def run(self, *args, **kwargs):
                return {'status': 'ok'}

        module = ConcreteModule('test', '2026-05-23')
        assert module.name == 'test'
        assert module.date == '2026-05-23'
        assert module._config_loaded is False

    def test_work_module_run_method(self):
        class ConcreteModule(WorkModule):
            def run(self, *args, **kwargs):
                return {'result': args[0] if args else None}

        module = ConcreteModule('test', '2026-05-23')
        result = module.run('test_arg')
        assert result['result'] == 'test_arg'

    def test_work_module_ensure_config(self):
        class ConcreteModule(WorkModule):
            def run(self, *args, **kwargs):
                return {'status': 'ok'}

        module = ConcreteModule('test', '2026-05-23')
        module._ensure_config()
        assert module._config_loaded is False
