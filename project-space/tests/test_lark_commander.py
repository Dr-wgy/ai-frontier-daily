#!/usr/bin/env python3
"""LarkCommander 单元测试

测试覆盖:
- LarkClient 单例初始化
- 配置加载和验证
- Wiki API 方法（创建、查询、移动）
- Docs API 方法（文档更新）
- Base API 方法（表格、字段、记录操作）
- IM API 方法（消息发送）
- 错误处理和异常情况
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, PropertyMock

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class TestLarkClientSingleton:
    """LarkClient 单例模式测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def test_singleton_returns_same_instance(self):
        """测试单例模式返回同一实例"""
        from utils.lark_commander import LarkClient

        with patch.object(LarkClient, '_load_config'):
            with patch.object(LarkClient, '_init_client'):
                instance1 = LarkClient()
                instance2 = LarkClient()
                assert instance1 is instance2

    def test_singleton_multiple_calls_do_not_reinit(self):
        """测试多次调用不会重复初始化"""
        from utils.lark_commander import LarkClient

        # 第一次调用会初始化
        with patch.object(LarkClient, '_load_config') as mock_load:
            with patch.object(LarkClient, '_init_client') as mock_init:
                LarkClient()
                # 此时 _client 已被设置为非 None（因为 _init_client 被 mock）
                # 我们手动设置 _client 为一个非 None 值来模拟已初始化状态
                LarkClient._client = MagicMock()
        
        # 重置 mock 计数
        mock_load.reset_mock()
        mock_init.reset_mock()
        
        # 第二次调用不会重新初始化（因为 _client 已经不是 None）
        with patch.object(LarkClient, '_load_config') as mock_load:
            with patch.object(LarkClient, '_init_client') as mock_init:
                LarkClient()
                assert mock_load.call_count == 0
                assert mock_init.call_count == 0


class TestLarkClientConfig:
    """LarkClient 配置加载测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def test_config_file_not_found(self):
        """测试配置文件不存在时抛出异常"""
        from utils.lark_commander import LarkClient

        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                LarkClient()
            assert "配置文件不存在" in str(exc_info.value)

    def test_config_missing_feishu_key(self):
        """测试配置文件缺少 feishu 配置项"""
        from utils.lark_commander import LarkClient

        mock_config = {'other_key': 'value'}

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True):
                with patch('json.load', return_value=mock_config):
                    with pytest.raises(ValueError) as exc_info:
                        LarkClient()
                    assert "缺少 'feishu' 配置项" in str(exc_info.value)

    def test_config_missing_app_id(self):
        """测试配置文件缺少 app_id"""
        from utils.lark_commander import LarkClient

        mock_config = {'feishu': {'app_secret': 'secret123'}}

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True):
                with patch('json.load', return_value=mock_config):
                    with pytest.raises(ValueError) as exc_info:
                        LarkClient()
                    assert "缺少 'app_id' 或 'app_secret'" in str(exc_info.value)

    def test_config_missing_app_secret(self):
        """测试配置文件缺少 app_secret"""
        from utils.lark_commander import LarkClient

        mock_config = {'feishu': {'app_id': 'app123'}}

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True):
                with patch('json.load', return_value=mock_config):
                    with pytest.raises(ValueError) as exc_info:
                        LarkClient()
                    assert "缺少 'app_id' 或 'app_secret'" in str(exc_info.value)

    def test_config_valid(self):
        """测试有效配置加载"""
        from utils.lark_commander import LarkClient

        mock_config = {
            'feishu': {
                'app_id': 'test_app_id',
                'app_secret': 'test_app_secret'
            }
        }

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True):
                with patch('json.load', return_value=mock_config):
                    with patch.object(LarkClient, '_init_client'):
                        client = LarkClient()
                        assert client._config == mock_config['feishu']

    def test_client_property_raises_when_not_initialized(self):
        """测试未初始化时访问 client 属性抛出异常"""
        from utils.lark_commander import LarkClient

        instance = LarkClient.__new__(LarkClient)
        instance._client = None

        with pytest.raises(RuntimeError) as exc_info:
            _ = instance.client
        assert "飞书客户端未初始化" in str(exc_info.value)

    def test_config_property_raises_when_not_loaded(self):
        """测试未加载配置时访问 config 属性抛出异常"""
        from utils.lark_commander import LarkClient

        instance = LarkClient.__new__(LarkClient)
        instance._config = None

        with pytest.raises(RuntimeError) as exc_info:
            _ = instance.config
        assert "飞书配置未加载" in str(exc_info.value)


class TestLarkCommand:
    """_LarkCommand 测试"""

    def test_args_returns_new_instance(self):
        """测试 args() 返回新实例"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('wiki', 'node_list')
        cmd2 = cmd1.args(space_id='test_space')

        assert cmd1 is not cmd2
        assert cmd1._kwargs == {}
        assert cmd2._kwargs == {'space_id': 'test_space'}

    def test_input_returns_new_instance(self):
        """测试 input() 返回新实例"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('docs', 'doc_update')
        cmd2 = cmd1.input('test content')

        assert cmd1 is not cmd2
        assert cmd1._input_text is None
        assert cmd2._input_text == 'test content'

    def test_args_merges_kwargs(self):
        """测试 args() 合并参数"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('wiki', 'node_list', {'space_id': 'space1'})
        cmd2 = cmd1.args(title='test_title')
        cmd3 = cmd2.args(parent_token='parent1')

        assert cmd1._kwargs == {'space_id': 'space1'}
        assert cmd2._kwargs == {'space_id': 'space1', 'title': 'test_title'}
        assert cmd3._kwargs == {'space_id': 'space1', 'title': 'test_title', 'parent_token': 'parent1'}

    def test_run_unknown_api_type(self):
        """测试未知 API 类型"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('unknown', 'unknown_method')
        result = cmd.run()

        assert result is None

    def test_use_lark_cli_parameter(self):
        """测试 use_lark_cli 参数"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('wiki', 'node_list', use_lark_cli=True)
        assert cmd1._use_lark_cli is True

        cmd2 = _LarkCommand('wiki', 'node_list', use_lark_cli=False)
        assert cmd2._use_lark_cli is False

        cmd3 = _LarkCommand('wiki', 'node_list')
        assert cmd3._use_lark_cli is False  # 默认值

    def test_args_preserves_use_lark_cli(self):
        """测试 args() 保留 use_lark_cli 设置"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('wiki', 'node_list', use_lark_cli=True)
        cmd2 = cmd1.args(space_id='test_space')

        assert cmd2._use_lark_cli is True

    def test_input_preserves_use_lark_cli(self):
        """测试 input() 保留 use_lark_cli 设置"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('docs', 'doc_update', use_lark_cli=True)
        cmd2 = cmd1.input('test content')

        assert cmd2._use_lark_cli is True

    def test_logger_parameter(self):
        """测试 logger 参数"""
        import logging
        from utils.lark_commander import _LarkCommand

        test_logger = logging.getLogger('test_logger')
        cmd = _LarkCommand('wiki', 'node_list', logger=test_logger)

        assert cmd._logger is test_logger

    def test_args_preserves_logger(self):
        """测试 args() 保留 logger 设置"""
        import logging
        from utils.lark_commander import _LarkCommand

        test_logger = logging.getLogger('test_logger')
        cmd1 = _LarkCommand('wiki', 'node_list', logger=test_logger)
        cmd2 = cmd1.args(space_id='test_space')

        assert cmd2._logger is test_logger


class TestWikiApi:
    """Wiki API 测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def _create_mock_client(self):
        """创建模拟的飞书客户端"""
        mock_client = MagicMock()
        return mock_client

    def test_wiki_node_list_success(self):
        """测试获取知识库节点列表成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        # 创建模拟响应
        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.items = [
            MagicMock(node_token='token1', title='标题1', obj_type='docx', parent_node_token='parent1'),
            MagicMock(node_token='token2', title='标题2', obj_type='bitable', parent_node_token='parent1'),
        ]
        mock_response.data.page_token = None

        mock_client = self._create_mock_client()
        mock_client.wiki.v2.space_node.list.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_list', {'space_id': 'test_space'})
            result = cmd.run()

            assert result is not None
            assert len(result) == 2
            assert result[0]['node_token'] == 'token1'
            assert result[1]['title'] == '标题2'

    def test_wiki_node_list_with_pagination(self):
        """测试分页获取知识库节点列表"""
        from utils.lark_commander import _LarkCommand, LarkClient

        # 第一页响应
        mock_response1 = MagicMock()
        mock_response1.success.return_value = True
        mock_response1.data.items = [
            MagicMock(node_token='token1', title='标题1', obj_type='docx', parent_node_token='parent1'),
        ]
        mock_response1.data.page_token = 'page_token_2'

        # 第二页响应
        mock_response2 = MagicMock()
        mock_response2.success.return_value = True
        mock_response2.data.items = [
            MagicMock(node_token='token2', title='标题2', obj_type='docx', parent_node_token='parent1'),
        ]
        mock_response2.data.page_token = None

        mock_client = self._create_mock_client()
        mock_client.wiki.v2.space_node.list.side_effect = [mock_response1, mock_response2]

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_list', {'space_id': 'test_space'})
            result = cmd.run()

            assert result is not None
            assert len(result) == 2
            assert mock_client.wiki.v2.space_node.list.call_count == 2

    def test_wiki_node_list_failure(self):
        """测试获取知识库节点列表失败"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = 'Bad Request'

        mock_client = self._create_mock_client()
        mock_client.wiki.v2.space_node.list.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_list', {'space_id': 'test_space'})
            result = cmd.run()

            assert result is None

    def test_wiki_node_list_by_parent_success(self):
        """测试根据父节点获取子节点列表成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.items = [
            MagicMock(node_token='child1', title='子节点1', obj_type='docx', parent_node_token='parent1'),
        ]
        mock_response.data.page_token = None

        mock_client = self._create_mock_client()
        mock_client.wiki.v2.space_node.list.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_list_by_parent', {
                'space_id': 'test_space',
                'parent_token': 'parent1'
            })
            result = cmd.run()

            assert result is not None
            assert len(result) == 1
            assert result[0]['node_token'] == 'child1'

    def test_wiki_node_create_success(self):
        """测试创建知识库节点成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.node.node_token = 'new_node_token'

        mock_client = self._create_mock_client()
        mock_client.wiki.v2.space_node.create.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_create', {
                'space_id': 'test_space',
                'title': '新文档'
            })
            result = cmd.run()

            assert result == 'new_node_token'

    def test_wiki_node_create_with_parent_success(self):
        """测试在指定父节点下创建知识库节点成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.node.node_token = 'new_child_token'

        mock_client = self._create_mock_client()
        mock_client.wiki.v2.space_node.create.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_create_with_parent', {
                'space_id': 'test_space',
                'title': '子文档',
                'parent_token': 'parent_token'
            })
            result = cmd.run()

            assert result == 'new_child_token'

    def test_wiki_node_move_success(self):
        """测试移动知识库节点成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True

        mock_client = self._create_mock_client()
        mock_client.wiki.v2.space_node.move.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_move', {
                'node_token': 'node1',
                'target_token': 'target_parent'
            })
            result = cmd.run()

            assert result is True

    def test_wiki_unknown_method(self):
        """测试未知的 Wiki API 方法"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = self._create_mock_client()

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'unknown_method')
            result = cmd.run()

            assert result is None


class TestJqQuery:
    """jq 查询测试"""

    def test_jq_query_select_equals(self):
        """测试 jq 查询 - select 精确匹配"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('wiki', 'node_list')
        data = {
            'data': {
                'nodes': [
                    {'node_token': 'token1', 'title': '目标标题'},
                    {'node_token': 'token2', 'title': '其他标题'},
                ]
            }
        }

        result = cmd._apply_jq_query(data, '.data.nodes[] | select(.title == "目标标题") | .node_token')
        assert result == 'token1'

    def test_jq_query_select_contains(self):
        """测试 jq 查询 - select contains 匹配"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('wiki', 'node_list')
        data = {
            'data': {
                'nodes': [
                    {'node_token': 'token1', 'title': 'AI新闻'},
                    {'node_token': 'token2', 'title': '科技动态'},
                    {'node_token': 'token3', 'title': 'AI技术'},
                ]
            }
        }

        result = cmd._apply_jq_query(data, '[.data.nodes[] | select(.title | contains("AI")) | .node_token]')
        assert result == json.dumps(['token1', 'token3'])

    def test_jq_query_no_match(self):
        """测试 jq 查询 - 无匹配结果"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('wiki', 'node_list')
        data = {
            'data': {
                'nodes': [
                    {'node_token': 'token1', 'title': '标题1'},
                ]
            }
        }

        result = cmd._apply_jq_query(data, '.data.nodes[] | select(.title == "不存在的标题") | .node_token')
        assert result is None

    def test_jq_query_unsupported_format(self):
        """测试 jq 查询 - 不支持的格式"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('wiki', 'node_list')
        data = {'data': {'nodes': []}}

        result = cmd._apply_jq_query(data, '.unsupported.query.format')
        assert result is None


class TestDocsApi:
    """Docs API 测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def _create_mock_client(self):
        """创建模拟的飞书客户端"""
        return MagicMock()

    def test_docs_update_title_only(self):
        """测试更新文档标题"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True

        mock_client = self._create_mock_client()
        mock_client.docx.v1.document.update.return_value = mock_response

        # Mock 导入的 UpdateDocumentRequest 类
        with patch('utils.lark_commander.UpdateDocumentRequest') as mock_request:
            with patch('utils.lark_commander.lark') as mock_lark:
                # 配置 mock 返回链式调用
                mock_builder = MagicMock()
                mock_request.builder.return_value = mock_builder
                mock_builder.document_id.return_value = mock_builder
                mock_builder.request_body.return_value = mock_builder
                mock_builder.build.return_value = MagicMock()
                
                # Mock UpdateDocumentRequestBody.builder()
                mock_body_builder = MagicMock()
                mock_lark.docx.v1.UpdateDocumentRequestBody.builder.return_value = mock_body_builder
                mock_body_builder.title.return_value = mock_body_builder
                mock_body_builder.build.return_value = MagicMock()

                with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                    mock_prop.return_value = mock_client

                    cmd = _LarkCommand('docs', 'doc_update', {
                        'doc_token': 'doc_token_123',
                        'title': '新标题'
                    })
                    result = cmd.run()

                    assert result is True
                    mock_client.docx.v1.document.update.assert_called_once()

    def test_docs_update_title_failure(self):
        """测试更新文档标题失败"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = 'Bad Request'

        mock_client = self._create_mock_client()
        mock_client.docx.v1.document.update.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('docs', 'doc_update', {
                'doc_token': 'doc_token_123',
                'title': '新标题'
            })
            result = cmd.run()

            assert result is None

    def test_docs_unknown_method(self):
        """测试未知的 Docs API 方法"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = self._create_mock_client()

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('docs', 'unknown_method')
            result = cmd.run()

            assert result is None


class TestMarkdownToBlocks:
    """Markdown 转换测试
    
    注意：这些测试需要 mock lark SDK 的内部 API。
    由于 lark SDK 的 API 可能与代码中使用的不匹配，这些测试主要用于验证逻辑流程。
    """

    def test_markdown_heading(self):
        """测试标题转换"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('docs', 'doc_update')
        
        # Mock 整个 lark 模块
        with patch('utils.lark_commander.lark') as mock_lark:
            # 配置 mock 返回链式调用
            mock_builder = MagicMock()
            mock_lark.docx.v1.Block.builder.return_value = mock_builder
            mock_builder.block_type.return_value = mock_builder
            mock_builder.heading.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            # Mock Heading.builder()
            mock_heading_builder = MagicMock()
            mock_lark.docx.v1.Heading.builder.return_value = mock_heading_builder
            mock_heading_builder.style.return_value = mock_heading_builder
            mock_heading_builder.elements.return_value = mock_heading_builder
            mock_heading_builder.build.return_value = MagicMock()
            
            # Mock HeadingStyle.builder()
            mock_style_builder = MagicMock()
            mock_lark.docx.v1.HeadingStyle.builder.return_value = mock_style_builder
            mock_style_builder.heading_level.return_value = mock_style_builder
            mock_style_builder.build.return_value = MagicMock()
            
            # Mock TextRun.builder()
            mock_text_run_builder = MagicMock()
            mock_lark.docx.v1.TextRun.builder.return_value = mock_text_run_builder
            mock_text_run_builder.content.return_value = mock_text_run_builder
            mock_text_run_builder.build.return_value = MagicMock()
            
            # Mock BlockElement.builder()
            mock_element_builder = MagicMock()
            mock_lark.docx.v1.BlockElement.builder.return_value = mock_element_builder
            mock_element_builder.text_run.return_value = mock_element_builder
            mock_element_builder.build.return_value = MagicMock()

            blocks = cmd._markdown_to_blocks('# 一级标题\n## 二级标题\n### 三级标题')
            assert len(blocks) == 3

    def test_markdown_paragraph(self):
        """测试段落转换"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('docs', 'doc_update')
        
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.docx.v1.Block.builder.return_value = mock_builder
            mock_builder.block_type.return_value = mock_builder
            mock_builder.text.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_text_builder = MagicMock()
            mock_lark.docx.v1.Text.builder.return_value = mock_text_builder
            mock_text_builder.elements.return_value = mock_text_builder
            mock_text_builder.build.return_value = MagicMock()
            
            mock_element_builder = MagicMock()
            mock_lark.docx.v1.BlockElement.builder.return_value = mock_element_builder
            mock_element_builder.text_run.return_value = mock_element_builder
            mock_element_builder.build.return_value = MagicMock()
            
            mock_text_run_builder = MagicMock()
            mock_lark.docx.v1.TextRun.builder.return_value = mock_text_run_builder
            mock_text_run_builder.content.return_value = mock_text_run_builder
            mock_text_run_builder.build.return_value = MagicMock()
            
            blocks = cmd._markdown_to_blocks('这是普通段落')
            assert len(blocks) == 1

    def test_markdown_bullet_list(self):
        """测试无序列表转换"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('docs', 'doc_update')
        
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.docx.v1.Block.builder.return_value = mock_builder
            mock_builder.block_type.return_value = mock_builder
            mock_builder.bullet.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_bullet_builder = MagicMock()
            mock_lark.docx.v1.Bullet.builder.return_value = mock_bullet_builder
            mock_bullet_builder.elements.return_value = mock_bullet_builder
            mock_bullet_builder.build.return_value = MagicMock()
            
            mock_element_builder = MagicMock()
            mock_lark.docx.v1.BlockElement.builder.return_value = mock_element_builder
            mock_element_builder.text_run.return_value = mock_element_builder
            mock_element_builder.build.return_value = MagicMock()
            
            mock_text_run_builder = MagicMock()
            mock_lark.docx.v1.TextRun.builder.return_value = mock_text_run_builder
            mock_text_run_builder.content.return_value = mock_text_run_builder
            mock_text_run_builder.build.return_value = MagicMock()
            
            blocks = cmd._markdown_to_blocks('- 项目1\n- 项目2\n* 项目3')
            assert len(blocks) == 3

    def test_markdown_ordered_list(self):
        """测试有序列表转换"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('docs', 'doc_update')
        
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.docx.v1.Block.builder.return_value = mock_builder
            mock_builder.block_type.return_value = mock_builder
            mock_builder.ordered.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_ordered_builder = MagicMock()
            mock_lark.docx.v1.Ordered.builder.return_value = mock_ordered_builder
            mock_ordered_builder.elements.return_value = mock_ordered_builder
            mock_ordered_builder.build.return_value = MagicMock()
            
            mock_element_builder = MagicMock()
            mock_lark.docx.v1.BlockElement.builder.return_value = mock_element_builder
            mock_element_builder.text_run.return_value = mock_element_builder
            mock_element_builder.build.return_value = MagicMock()
            
            mock_text_run_builder = MagicMock()
            mock_lark.docx.v1.TextRun.builder.return_value = mock_text_run_builder
            mock_text_run_builder.content.return_value = mock_text_run_builder
            mock_text_run_builder.build.return_value = MagicMock()
            
            blocks = cmd._markdown_to_blocks('1. 第一项\n2. 第二项\n3. 第三项')
            assert len(blocks) == 3

    def test_markdown_code_block(self):
        """测试代码块转换"""
        from utils.lark_commander import _LarkCommand

        cmd = _LarkCommand('docs', 'doc_update')
        
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.docx.v1.Block.builder.return_value = mock_builder
            mock_builder.block_type.return_value = mock_builder
            mock_builder.code.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_code_builder = MagicMock()
            mock_lark.docx.v1.Code.builder.return_value = mock_code_builder
            mock_code_builder.style.return_value = mock_code_builder
            mock_code_builder.elements.return_value = mock_code_builder
            mock_code_builder.build.return_value = MagicMock()
            
            mock_style_builder = MagicMock()
            mock_lark.docx.v1.CodeStyle.builder.return_value = mock_style_builder
            mock_style_builder.language.return_value = mock_style_builder
            mock_style_builder.build.return_value = MagicMock()
            
            mock_element_builder = MagicMock()
            mock_lark.docx.v1.BlockElement.builder.return_value = mock_element_builder
            mock_element_builder.text_run.return_value = mock_element_builder
            mock_element_builder.build.return_value = MagicMock()
            
            mock_text_run_builder = MagicMock()
            mock_lark.docx.v1.TextRun.builder.return_value = mock_text_run_builder
            mock_text_run_builder.content.return_value = mock_text_run_builder
            mock_text_run_builder.build.return_value = MagicMock()
            
            blocks = cmd._markdown_to_blocks('```python\nprint("hello")\n```')
            assert len(blocks) == 1

    def test_markdown_mixed_content(self):
        """测试混合内容转换"""
        from utils.lark_commander import _LarkCommand

        markdown = """# 标题

这是段落

- 列表项1
- 列表项2

```python
code
```
"""
        cmd = _LarkCommand('docs', 'doc_update')
        
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.docx.v1.Block.builder.return_value = mock_builder
            mock_builder.block_type.return_value = mock_builder
            # 配置所有可能的链式调用
            mock_builder.heading.return_value = mock_builder
            mock_builder.text.return_value = mock_builder
            mock_builder.bullet.return_value = mock_builder
            mock_builder.code.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            # Mock 所有需要的构建器
            mock_lark.docx.v1.Heading.builder.return_value = MagicMock()
            mock_lark.docx.v1.Text.builder.return_value = MagicMock()
            mock_lark.docx.v1.Bullet.builder.return_value = MagicMock()
            mock_lark.docx.v1.Code.builder.return_value = MagicMock()
            mock_lark.docx.v1.BlockElement.builder.return_value = MagicMock()
            mock_lark.docx.v1.TextRun.builder.return_value = MagicMock()
            mock_lark.docx.v1.HeadingStyle.builder.return_value = MagicMock()
            mock_lark.docx.v1.CodeStyle.builder.return_value = MagicMock()
            
            blocks = cmd._markdown_to_blocks(markdown)
            assert len(blocks) >= 4  # 至少包含标题、段落、列表项、代码块


class TestBaseApi:
    """Base API 测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def _create_mock_client(self):
        """创建模拟的飞书客户端"""
        return MagicMock()

    def test_base_create_success(self):
        """测试创建多维表格成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.app.base_token = 'new_base_token'

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app.create.return_value = mock_response

        # Mock 整个 lark 模块
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.bitable.v1.CreateAppRequest.builder.return_value = mock_builder
            mock_builder.request_body.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_body_builder = MagicMock()
            mock_lark.bitable.v1.CreateAppRequestBody.builder.return_value = mock_body_builder
            mock_body_builder.name.return_value = mock_body_builder
            mock_body_builder.time_zone.return_value = mock_body_builder
            mock_body_builder.build.return_value = MagicMock()

            with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                mock_prop.return_value = mock_client

                cmd = _LarkCommand('base', 'base_create', {'name': '测试表格'})
                result = cmd.run()

                assert result == 'new_base_token'

    def test_base_create_failure(self):
        """测试创建多维表格失败"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = 'Bad Request'

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app.create.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('base', 'base_create', {'name': '测试表格'})
            result = cmd.run()

            assert result is None

    def test_base_table_list_success(self):
        """测试获取数据表列表成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        # 创建模拟的表格对象，使用真实的字符串属性
        mock_table1 = MagicMock()
        mock_table1.table_id = 'table1'
        mock_table1.name = '表1'
        
        mock_table2 = MagicMock()
        mock_table2.table_id = 'table2'
        mock_table2.name = '表2'

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.items = [mock_table1, mock_table2]

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app_table.list.return_value = mock_response

        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.bitable.v1.ListAppTableRequest.builder.return_value = mock_builder
            mock_builder.app_token.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()

            with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                mock_prop.return_value = mock_client

                cmd = _LarkCommand('base', 'table_list', {'base_token': 'base_token_123'})
                result = cmd.run()

                assert result is not None
                parsed = json.loads(result)
                assert len(parsed) == 2
                assert parsed[0]['id'] == 'table1'

    def test_base_table_create_success(self):
        """测试创建数据表成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.table.table_id = 'new_table_id'

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app_table.create.return_value = mock_response

        # Mock 整个 lark 模块
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.bitable.v1.CreateAppTableRequest.builder.return_value = mock_builder
            mock_builder.app_token.return_value = mock_builder
            mock_builder.request_body.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_body_builder = MagicMock()
            mock_lark.bitable.v1.CreateAppTableRequestBody.builder.return_value = mock_body_builder
            mock_body_builder.table.return_value = mock_body_builder
            mock_body_builder.build.return_value = MagicMock()
            
            mock_table_builder = MagicMock()
            mock_lark.bitable.v1.Table.builder.return_value = mock_table_builder
            mock_table_builder.name.return_value = mock_table_builder
            mock_table_builder.build.return_value = MagicMock()

            with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                mock_prop.return_value = mock_client

                cmd = _LarkCommand('base', 'table_create', {
                    'base_token': 'base_token_123',
                    'table_json': json.dumps({'name': '新数据表'})
                })
                result = cmd.run()

                assert result == 'new_table_id'

    def test_base_field_list_success(self):
        """测试获取字段列表成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.items = [
            MagicMock(field_id='field1', field_name='字段1', type=1),
            MagicMock(field_id='field2', field_name='字段2', type=2),
        ]

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app_table_field.list.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('base', 'field_list', {
                'base_token': 'base_token_123',
                'table_id': 'table_id_123'
            })
            result = cmd.run()

            assert result is not None
            parsed = json.loads(result)
            assert len(parsed) == 2
            assert parsed[0]['field_id'] == 'field1'

    def test_base_field_create_success(self):
        """测试创建字段成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.field.field_id = 'new_field_id'

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app_table_field.create.return_value = mock_response

        # Mock 整个 lark 模块
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.bitable.v1.CreateAppTableFieldRequest.builder.return_value = mock_builder
            mock_builder.app_token.return_value = mock_builder
            mock_builder.table_id.return_value = mock_builder
            mock_builder.request_body.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_body_builder = MagicMock()
            mock_lark.bitable.v1.CreateAppTableFieldRequestBody.builder.return_value = mock_body_builder
            mock_body_builder.field.return_value = mock_body_builder
            mock_body_builder.build.return_value = MagicMock()
            
            mock_field_builder = MagicMock()
            mock_lark.bitable.v1.Field.builder.return_value = mock_field_builder
            mock_field_builder.field_name.return_value = mock_field_builder
            mock_field_builder.type.return_value = mock_field_builder
            mock_field_builder.build.return_value = MagicMock()

            with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                mock_prop.return_value = mock_client

                cmd = _LarkCommand('base', 'field_create', {
                    'base_token': 'base_token_123',
                    'table_id': 'table_id_123',
                    'field_json': json.dumps({'name': '新字段', 'type': 1})
                })
                result = cmd.run()

                assert result == 'new_field_id'

    def test_base_record_search_success(self):
        """测试搜索记录成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_record = MagicMock()
        mock_record.record_id = 'record1'
        mock_record.fields = {'field1': 'value1', 'field2': 'value2'}

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.items = [mock_record]

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app_table_record.search.return_value = mock_response

        # Mock 整个 lark 模块
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.bitable.v1.SearchAppTableRecordRequest.builder.return_value = mock_builder
            mock_builder.app_token.return_value = mock_builder
            mock_builder.table_id.return_value = mock_builder
            mock_builder.request_body.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_body_builder = MagicMock()
            mock_lark.bitable.v1.SearchAppTableRecordRequestBody.builder.return_value = mock_body_builder
            mock_body_builder.build.return_value = MagicMock()

            with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                mock_prop.return_value = mock_client

                cmd = _LarkCommand('base', 'record_search', {
                    'base_token': 'base_token_123',
                    'table_id': 'table_id_123',
                    'search_json': json.dumps({
                        'keyword': 'test',
                        'select_fields': ['field1', 'field2']
                    })
                })
                result = cmd.run()

                assert result is not None
                parsed = json.loads(result)
                assert 'data' in parsed
                assert 'record_id_list' in parsed['data']

    def test_base_record_delete_success(self):
        """测试批量删除记录成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        # 创建模拟的记录对象
        mock_record1 = MagicMock()
        mock_record1.record_id = 'record1'
        mock_record2 = MagicMock()
        mock_record2.record_id = 'record2'

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.records = [mock_record1, mock_record2]

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app_table_record.batch_delete.return_value = mock_response

        # Mock 整个 lark 模块
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.bitable.v1.BatchDeleteAppTableRecordRequest.builder.return_value = mock_builder
            mock_builder.app_token.return_value = mock_builder
            mock_builder.table_id.return_value = mock_builder
            mock_builder.request_body.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_body_builder = MagicMock()
            mock_lark.bitable.v1.BatchDeleteAppTableRecordRequestBody.builder.return_value = mock_body_builder
            mock_body_builder.records.return_value = mock_body_builder
            mock_body_builder.build.return_value = MagicMock()
            
            mock_lark.bitable.v1.Record.builder.return_value = MagicMock()

            with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                mock_prop.return_value = mock_client

                cmd = _LarkCommand('base', 'record_delete', {
                    'base_token': 'base_token_123',
                    'table_id': 'table_id_123',
                    'delete_json': json.dumps({'record_id_list': ['record1', 'record2']})
                })
                result = cmd.run()

                assert result is not None
                parsed = json.loads(result)
                assert 'record1' in parsed

    def test_base_record_batch_create_success(self):
        """测试批量创建记录成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        # 创建模拟的记录对象
        mock_record1 = MagicMock()
        mock_record1.record_id = 'new_record1'
        mock_record2 = MagicMock()
        mock_record2.record_id = 'new_record2'

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.records = [mock_record1, mock_record2]

        mock_client = self._create_mock_client()
        mock_client.bitable.v1.app_table_record.batch_create.return_value = mock_response

        # Mock 整个 lark 模块
        with patch('utils.lark_commander.lark') as mock_lark:
            mock_builder = MagicMock()
            mock_lark.bitable.v1.BatchCreateAppTableRecordRequest.builder.return_value = mock_builder
            mock_builder.app_token.return_value = mock_builder
            mock_builder.table_id.return_value = mock_builder
            mock_builder.request_body.return_value = mock_builder
            mock_builder.build.return_value = MagicMock()
            
            mock_body_builder = MagicMock()
            mock_lark.bitable.v1.BatchCreateAppTableRecordRequestBody.builder.return_value = mock_body_builder
            mock_body_builder.records.return_value = mock_body_builder
            mock_body_builder.build.return_value = MagicMock()
            
            mock_lark.bitable.v1.Record.builder.return_value = MagicMock()

            with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
                mock_prop.return_value = mock_client

                cmd = _LarkCommand('base', 'record_batch_create', {
                    'base_token': 'base_token_123',
                    'table_id': 'table_id_123',
                    'data_json': json.dumps({
                        'fields': ['field1', 'field2'],
                        'rows': [['value1', 'value2'], ['value3', 'value4']]
                    })
                })
                result = cmd.run()

                assert result is not None
                parsed = json.loads(result)
                assert 'new_record1' in parsed

    def test_base_unknown_method(self):
        """测试未知的 Base API 方法"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = self._create_mock_client()

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('base', 'unknown_method')
            result = cmd.run()

            assert result is None


class TestImApi:
    """IM API 测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def _create_mock_client(self):
        """创建模拟的飞书客户端"""
        return MagicMock()

    def test_im_message_send_success(self):
        """测试发送消息成功"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.message_id = 'msg_id_123'

        mock_client = self._create_mock_client()
        mock_client.im.v1.message.create.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('im', 'message_send', {
                'chat_id': 'chat_id_123',
                'content': json.dumps({'text': '测试消息'})
            })
            result = cmd.run()

            assert result == 'msg_id_123'

    def test_im_message_send_failure(self):
        """测试发送消息失败"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = False
        mock_response.code = 400
        mock_response.msg = 'Bad Request'

        mock_client = self._create_mock_client()
        mock_client.im.v1.message.create.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('im', 'message_send', {
                'chat_id': 'chat_id_123',
                'content': json.dumps({'text': '测试消息'})
            })
            result = cmd.run()

            assert result is None

    def test_im_unknown_method(self):
        """测试未知的 IM API 方法"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = self._create_mock_client()

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('im', 'unknown_method')
            result = cmd.run()

            assert result is None


class TestLarkCmd:
    """LarkCmd 工厂类测试"""

    def test_wiki_commands_exist(self):
        """测试 Wiki 命令常量存在"""
        from utils.lark_commander import LarkCmd

        assert hasattr(LarkCmd, 'WIKI_NODE_LIST')
        assert hasattr(LarkCmd, 'WIKI_NODE_LIST_BY_PARENT')
        assert hasattr(LarkCmd, 'WIKI_NODE_SEARCH_BITABLE')
        assert hasattr(LarkCmd, 'WIKI_NODE_CREATE')
        assert hasattr(LarkCmd, 'WIKI_NODE_CREATE_WITH_PARENT')
        assert hasattr(LarkCmd, 'WIKI_NODE_MOVE')

    def test_docs_commands_exist(self):
        """测试 Docs 命令常量存在"""
        from utils.lark_commander import LarkCmd

        assert hasattr(LarkCmd, 'DOC_UPDATE')

    def test_base_commands_exist(self):
        """测试 Base 命令常量存在"""
        from utils.lark_commander import LarkCmd

        assert hasattr(LarkCmd, 'BASE_CREATE')
        assert hasattr(LarkCmd, 'BASE_TABLE_LIST')
        assert hasattr(LarkCmd, 'BASE_TABLE_CREATE')
        assert hasattr(LarkCmd, 'BASE_FIELD_LIST')
        assert hasattr(LarkCmd, 'BASE_FIELD_CREATE')
        assert hasattr(LarkCmd, 'BASE_RECORD_SEARCH')
        assert hasattr(LarkCmd, 'BASE_RECORD_DELETE')
        assert hasattr(LarkCmd, 'BASE_RECORD_BATCH_CREATE')

    def test_im_commands_exist(self):
        """测试 IM 命令常量存在"""
        from utils.lark_commander import LarkCmd

        assert hasattr(LarkCmd, 'IM_MESSAGE_SEND')

    def test_command_chain_usage(self):
        """测试命令链式调用"""
        from utils.lark_commander import LarkCmd, LarkClient

        # 模拟客户端
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.node.node_token = 'test_token'
        mock_client.wiki.v2.space_node.create.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            # 链式调用
            result = LarkCmd.WIKI_NODE_CREATE.args(
                space_id='test_space',
                title='测试标题'
            ).run()

            assert result == 'test_token'


class TestErrorHandling:
    """错误处理测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def test_api_call_exception_handling(self):
        """测试 API 调用异常处理"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = MagicMock()
        mock_client.wiki.v2.space_node.list.side_effect = Exception('Network error')

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('wiki', 'node_list', {'space_id': 'test_space'})
            result = cmd.run()

            assert result is None

    def test_json_parse_error_in_record_search(self):
        """测试记录搜索 JSON 解析错误"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = MagicMock()

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('base', 'record_search', {
                'base_token': 'base_token_123',
                'table_id': 'table_id_123',
                'search_json': 'invalid json'
            })
            result = cmd.run()

            assert result is None

    def test_empty_record_list_delete(self):
        """测试空记录列表删除"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = MagicMock()

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('base', 'record_delete', {
                'base_token': 'base_token_123',
                'table_id': 'table_id_123',
                'delete_json': json.dumps({'record_id_list': []})
            })
            result = cmd.run()

            assert result == '[]'
            # 不应该调用删除 API
            mock_client.bitable.v1.app_table_record.batch_delete.assert_not_called()

    def test_empty_row_list_batch_create(self):
        """测试空行列表批量创建"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_client = MagicMock()

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client

            cmd = _LarkCommand('base', 'record_batch_create', {
                'base_token': 'base_token_123',
                'table_id': 'table_id_123',
                'data_json': json.dumps({'fields': [], 'rows': []})
            })
            result = cmd.run()

            assert result == '[]'
            # 不应该调用创建 API
            mock_client.bitable.v1.app_table_record.batch_create.assert_not_called()


class TestConvenienceFunctions:
    """便捷函数测试"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def test_get_lark_client(self):
        """测试获取飞书客户端单例"""
        from utils.lark_commander import get_lark_client, LarkClient

        with patch.object(LarkClient, '_load_config'):
            with patch.object(LarkClient, '_init_client'):
                client = get_lark_client()
                assert isinstance(client, LarkClient)

    def test_get_lark_config(self):
        """测试获取飞书配置"""
        from utils.lark_commander import get_lark_config, LarkClient

        mock_config = {
            'app_id': 'test_app_id',
            'app_secret': 'test_app_secret'
        }

        with patch.object(LarkClient, '_load_config'):
            with patch.object(LarkClient, '_init_client'):
                LarkClient._config = mock_config
                config = get_lark_config()
                assert config == mock_config


class TestUseUserAccessToken:
    """测试使用 user_access_token 功能"""

    def setup_method(self):
        """每个测试前重置单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def teardown_method(self):
        """每个测试后清理单例状态"""
        from utils.lark_commander import LarkClient
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

    def test_with_user_access_token_method(self):
        """测试 with_user_access_token 方法"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('wiki', 'node_list')
        cmd2 = cmd1.with_user_access_token()

        assert cmd1 is not cmd2
        assert cmd1._use_user_access_token is False
        assert cmd2._use_user_access_token is True

    def test_args_preserves_use_user_access_token(self):
        """测试 args 方法保留 use_user_access_token 标志"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('wiki', 'node_list', use_user_access_token=True)
        cmd2 = cmd1.args(space_id='test_space')

        assert cmd2._use_user_access_token is True

    def test_input_preserves_use_user_access_token(self):
        """测试 input 方法保留 use_user_access_token 标志"""
        from utils.lark_commander import _LarkCommand

        cmd1 = _LarkCommand('docs', 'doc_update', use_user_access_token=True)
        cmd2 = cmd1.input('test content')

        assert cmd2._use_user_access_token is True

    def test_api_call_with_user_access_token_flag(self):
        """测试使用 user_access_token 标志的 API 调用"""
        from utils.lark_commander import _LarkCommand, LarkClient

        mock_response = MagicMock()
        mock_response.success.return_value = True
        mock_response.data.items = []
        mock_response.data.page_token = None

        mock_client = MagicMock()
        mock_client.wiki.v2.space_node.list.return_value = mock_response

        with patch.object(LarkClient, 'client', new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_client
            with patch.object(LarkClient, 'user_access_token', new_callable=PropertyMock) as mock_token:
                mock_token.return_value = 'test_user_token'

                cmd = _LarkCommand('wiki', 'node_list', {
                    'space_id': 'test_space'
                }, use_user_access_token=True)
                cmd.run()

                # 验证 API 被调用时传递了 option
                call_args = mock_client.wiki.v2.space_node.list.call_args
                assert len(call_args[0]) == 2  # request 和 option


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
