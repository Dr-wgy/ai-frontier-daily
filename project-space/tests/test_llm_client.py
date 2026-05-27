#!/usr/bin/env python3
"""llm_client.py 测试"""

import json
import re
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.llm_client import LLMClient


class TestLLMClient:
    """LLMClient 测试"""

    def test_init(self):
        """测试初始化"""
        cfg = {'api_key': 'test_key', 'base_url': 'http://test.com', 'model_name': 'gpt-4'}
        client = LLMClient(cfg, '2026-05-23')
        assert client._cfg == cfg
        assert client._client is None

    def test_get_client_invalid_config(self):
        """测试配置不完整的情况"""
        cfg = {'api_key': '', 'base_url': '', 'model_name': ''}
        client = LLMClient(cfg, '2026-05-23')
        result = client._get_client()
        assert result is None

    def test_get_client_missing_fields(self):
        """测试缺少必要配置字段"""
        cfg = {'api_key': 'test_key'}
        client = LLMClient(cfg, '2026-05-23')
        result = client._get_client()
        assert result is None

    def test_call_json_extraction(self):
        """测试 JSON 提取逻辑（不需要调用 OpenAI）"""
        cfg = {'api_key': 'test_key', 'base_url': 'http://test.com', 'model_name': 'gpt-4'}
        client = LLMClient(cfg, '2026-05-23')
        
        # 让我们创建一个 mock 来测试 call_json 的解析部分
        with patch.object(client, 'call') as mock_call:
            # 测试带代码块的情况
            mock_call.return_value = '```json\n{"test": "value"}\n```'
            result = client.call_json('system prompt', 'user prompt')
            assert result == {'test': 'value'}
            
            # 测试不带代码块的情况
            mock_call.return_value = '{"test": "value"}'
            result = client.call_json('system prompt', 'user prompt')
            assert result == {'test': 'value'}
            
            # 测试解析失败的情况
            mock_call.return_value = 'not a json'
            with pytest.raises(RuntimeError):
                client.call_json('system prompt', 'user prompt')
    
    def test_call_json_with_other_json_patterns(self):
        """测试其他 JSON 模式的提取"""
        cfg = {'api_key': 'test_key', 'base_url': 'http://test.com', 'model_name': 'gpt-4'}
        client = LLMClient(cfg, '2026-05-23')
        
        with patch.object(client, 'call') as mock_call:
            # 测试其他 JSON 格式
            mock_call.return_value = 'Here is the data: {"key": "val"}'
            result = client.call_json('system prompt', 'user prompt')
            assert result == {'key': 'val'}
