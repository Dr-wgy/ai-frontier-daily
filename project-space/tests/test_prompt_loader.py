#!/usr/bin/env python3
"""prompt_loader.py 单元测试"""

from pathlib import Path
import sys

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.prompt_loader import TemplateRenderer, PromptLoader


class TestTemplateRenderer:
    """TemplateRenderer 类测试"""

    def test_load_file_exists(self, temp_template_file):
        content = TemplateRenderer.load_file(temp_template_file)
        assert content is not None
        assert 'name' in content
        assert 'value' in content

    def test_load_file_not_exists(self):
        content = TemplateRenderer.load_file(Path('/non/existent/file.txt'))
        assert content is None

    def test_render_simple_basic(self):
        template = "Hello {{ name }}, you have {{ count }} messages."
        context = {'name': 'Alice', 'count': '5'}
        result = TemplateRenderer.render_simple(template, context)
        assert result == "Hello Alice, you have 5 messages."

    def test_render_simple_no_match(self):
        template = "Hello World"
        context = {'name': 'Alice'}
        result = TemplateRenderer.render_simple(template, context)
        assert result == "Hello World"

    def test_render_simple_missing_context(self):
        template = "Hello {{ name }}, today is {{ date }}"
        context = {'name': 'Alice'}
        result = TemplateRenderer.render_simple(template, context)
        assert 'Alice' in result
        assert '{{ date }}' in result

    def test_render_simple_non_string_value(self):
        template = "Count: {{ count }}"
        context = {'count': 123}
        result = TemplateRenderer.render_simple(template, context)
        assert result == "Count: {{ count }}"

    def test_render_with_jinja2(self, temp_template_file):
        renderer = TemplateRenderer()
        context = {'name': 'TestName', 'value': 'TestValue'}
        result = renderer.render(temp_template_file, context)
        assert result is not None
        assert 'TestName' in result
        assert 'TestValue' in result

    def test_render_file_not_exists(self):
        renderer = TemplateRenderer()
        result = renderer.render(Path('/non/existent/file.txt'), {})
        assert result is None


class TestPromptLoader:
    """PromptLoader 类测试"""

    def test_parse_frontmatter_basic(self):
        content = """x: $$$$|
Hello World
x: |$$$$
"""
        parts = PromptLoader.parse_frontmatter(content)
        assert parts.get('x') == 'Hello World'

    def test_parse_frontmatter_multiple_blocks(self):
        content = """system: $$$$|
You are a helpful assistant.
system: |$$$$

user: $$$$|
Hello!
user: |$$$$
"""
        parts = PromptLoader.parse_frontmatter(content)
        assert parts.get('system') == 'You are a helpful assistant.'
        assert parts.get('user') == 'Hello!'

    def test_parse_frontmatter_multiline_content(self):
        content = """instruction: $$$$|
Line 1
Line 2
  indented line
Line 3
instruction: |$$$$
"""
        parts = PromptLoader.parse_frontmatter(content)
        assert 'Line 1' in parts.get('instruction', '')
        assert 'Line 2' in parts.get('instruction', '')
        assert 'Line 3' in parts.get('instruction', '')

    def test_parse_frontmatter_no_match(self):
        content = """This is not frontmatter format
just regular content
"""
        parts = PromptLoader.parse_frontmatter(content)
        assert len(parts) == 0

    def test_parse_frontmatter_mismatched_keys(self):
        content = """key1: $$$|
Content
key2: |$$$$
"""
        parts = PromptLoader.parse_frontmatter(content)
        assert len(parts) == 0

    def test_render_and_parse(self, temp_template_file):
        loader = PromptLoader()
        context = {'name': 'Alice', 'value': '100'}
        system, user = loader.render_and_parse(temp_template_file, context)
        assert system == 'You are a helpful assistant.'
        assert user == 'Hello, Alice!'

    def test_render_and_parse_file_not_exists(self):
        loader = PromptLoader()
        system, user = loader.render_and_parse(Path('/non/existent/file.txt'), {})
        assert system == ''
        assert user == ''

    def test_render_and_parse_with_empty_context(self, temp_template_file):
        loader = PromptLoader()
        context = {}
        system, user = loader.render_and_parse(temp_template_file, context)
        assert system is not None
        assert user is not None
