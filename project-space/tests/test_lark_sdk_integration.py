#!/usr/bin/env python3
"""LarkSdkCommander 集成测试

测试 lark_sdk_commander 模块的导入和基本功能。
注意：完整的 API 测试需要实际的飞书 API 访问权限。
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def test_import():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from utils.lark_sdk_commander import LarkClient, LarkSdkCommand, LarkCmd
        print("✓ 导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_command_creation():
    """测试命令创建"""
    print("\n测试命令创建...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        commands = [
            LarkCmd.WIKI_NODE_LIST,
            LarkCmd.WIKI_NODE_LIST_BY_PARENT,
            LarkCmd.WIKI_NODE_CREATE,
            LarkCmd.WIKI_NODE_MOVE,
            LarkCmd.DOC_UPDATE,
            LarkCmd.BASE_CREATE,
            LarkCmd.BASE_TABLE_LIST,
            LarkCmd.BASE_TABLE_CREATE,
            LarkCmd.BASE_FIELD_LIST,
            LarkCmd.BASE_FIELD_CREATE,
            LarkCmd.BASE_RECORD_SEARCH,
            LarkCmd.BASE_RECORD_DELETE,
            LarkCmd.BASE_RECORD_BATCH_CREATE,
            LarkCmd.IM_MESSAGE_SEND,
        ]

        for cmd in commands:
            assert cmd is not None, f"命令 {cmd} 为 None"

        print(f"✓ 创建了 {len(commands)} 个命令")
        return True
    except Exception as e:
        print(f"✗ 命令创建失败: {e}")
        return False


def test_chain_calls():
    """测试链式调用"""
    print("\n测试链式调用...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        cmd = LarkCmd.WIKI_NODE_LIST
        assert cmd._kwargs == {}

        cmd = cmd.args(space_id='test_space')
        assert cmd._kwargs == {'space_id': 'test_space'}

        cmd = cmd.args(query='.data.nodes')
        assert cmd._kwargs == {'space_id': 'test_space', 'query': '.data.nodes'}

        cmd_with_input = LarkCmd.DOC_UPDATE.input('test content')
        assert cmd_with_input._input_text == 'test content'

        cmd_cli = cmd.with_lark_cli()
        assert cmd_cli._use_lark_cli is True

        cmd_user = cmd.with_user_access_token()
        assert cmd_user._use_user_access_token is True

        print("✓ 链式调用正常")
        return True
    except Exception as e:
        print(f"✗ 链式调用失败: {e}")
        return False


def test_query_filter():
    """测试查询过滤"""
    print("\n测试查询过滤...")
    try:
        from utils.lark_sdk_commander import LarkSdkCommand

        cmd = LarkSdkCommand('wiki', 'node_list')

        nodes = [
            {'node_token': 't1', 'title': 'AI新闻', 'obj_type': 'bitable'},
            {'node_token': 't2', 'title': '科技动态', 'obj_type': 'docx'},
            {'node_token': 't3', 'title': 'AI技术', 'obj_type': 'bitable'},
        ]

        result = cmd._filter_nodes(nodes, '.obj_type == "bitable"')
        assert len(result) == 2

        result = cmd._filter_nodes(nodes, '.obj_type == "bitable" and .title | contains("AI")')
        assert len(result) == 2

        print("✓ 查询过滤正常")
        return True
    except Exception as e:
        print(f"✗ 查询过滤失败: {e}")
        return False


def main():
    print("=" * 60)
    print("LarkSdkCommander 集成测试")
    print("=" * 60)

    results = []
    results.append(test_import())
    results.append(test_command_creation())
    results.append(test_chain_calls())
    results.append(test_query_filter())

    print("\n" + "=" * 60)
    if all(results):
        print("所有测试通过！")
        print("=" * 60)
        return 0
    else:
        print("部分测试失败！")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
