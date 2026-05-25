#!/usr/bin/env python3
"""LarkSdkCommander 真实 API 集成测试

注意：此测试需要配置有效的飞书凭证（app_id、app_secret）才能正常运行。
如果没有配置，测试会失败并显示错误信息。
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def test_client_initialization():
    """测试客户端初始化（真实配置加载）"""
    print("测试客户端初始化...")
    try:
        from utils.lark_sdk_commander import LarkClient

        # 重置单例状态
        LarkClient._instance = None
        LarkClient._client = None
        LarkClient._config = None

        client = LarkClient()
        print("✓ 客户端初始化成功")
        print(f"  - app_id: {client._config.get('app_id', '未配置')[:20] if client._config else '无配置'}")
        print(f"  - user_access_token: {'已配置' if client.user_access_token else '未配置'}")
        return True
    except FileNotFoundError as e:
        print(f"✗ 配置文件未找到: {e}")
        return False
    except ValueError as e:
        print(f"✗ 配置错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_access_token():
    """测试获取 app_access_token（真实 API 调用）"""
    print("\n测试获取 app_access_token...")
    try:
        from utils.lark_sdk_commander import LarkClient

        client = LarkClient()
        
        # 直接调用 SDK 获取 token
        token_response = client.client.get_internal_token()
        if token_response.success():
            access_token = token_response.data.access_token
            print(f"✓ 获取 app_access_token 成功")
            print(f"  - token: {access_token[:20]}...")
            print(f"  - expires_in: {token_response.data.expires_in} 秒")
            return True
        else:
            print(f"✗ 获取 app_access_token 失败")
            print(f"  - 错误码: {token_response.code}")
            print(f"  - 错误信息: {token_response.msg}")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_list():
    """测试获取多维表格列表（真实 API 调用）"""
    print("\n测试获取多维表格列表...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        result = LarkCmd.BASE_TABLE_LIST.args(base_token='your_base_token').run()
        if result:
            data = json.loads(result)
            print(f"✓ 获取表格列表成功")
            print(f"  - 表格数量: {len(data)}")
            for table in data[:3]:
                print(f"    - {table.get('name', '未知')} (id: {table.get('table_id', '未知')})")
            return True
        else:
            print("✗ 获取表格列表失败")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wiki_node_list():
    """测试获取知识库节点列表（真实 API 调用）"""
    print("\n测试获取知识库节点列表...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        result = LarkCmd.WIKI_NODE_LIST.args(space_id='your_space_id', query='.data.nodes').run()
        if result:
            data = json.loads(result)
            print(f"✓ 获取节点列表成功")
            print(f"  - 节点数量: {len(data)}")
            for node in data[:3]:
                print(f"    - {node.get('title', '未知')} (token: {node.get('node_token', '未知')[:10]}...)")
            return True
        else:
            print("✗ 获取节点列表失败")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_im_send_message():
    """测试发送消息（真实 API 调用）"""
    print("\n测试发送消息...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        content = json.dumps({
            "type": "interactive",
            "data": {
                "version": "1.0",
                "config": {"wide_screen_mode": True},
                "elements": [
                    {"tag": "markdown", "content": "这是一条来自 Python SDK 的测试消息"}
                ]
            }
        })

        result = LarkCmd.IM_MESSAGE_SEND.args(chat_id='your_chat_id', content=content).run()
        if result:
            print(f"✓ 消息发送成功")
            print(f"  - message_id: {result}")
            return True
        else:
            print("✗ 消息发送失败")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 70)
    print("LarkSdkCommander 真实 API 集成测试")
    print("=" * 70)
    print("\n注意：此测试需要配置有效的飞书凭证才能正常运行。")
    print("请在 config/secrets.json 中配置 app_id、app_secret 等参数。")
    print("=" * 70)

    results = []
    
    # 测试客户端初始化
    results.append(test_client_initialization())
    
    # 测试获取 app_access_token（需要有效凭证）
    results.append(test_app_access_token())
    
    # 以下测试需要配置具体的 ID
    # results.append(test_base_list())      # 需要 base_token
    # results.append(test_wiki_node_list())  # 需要 space_id 和 user_access_token
    # results.append(test_im_send_message()) # 需要 chat_id

    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！")
        return 0
    else:
        print("✗ 部分测试失败，请检查配置")
        return 1


if __name__ == '__main__':
    sys.exit(main())
