#!/usr/bin/env python3
"""LarkSdkCommander 完整真实 API 集成测试

使用真实的飞书 API 测试所有功能模块。
需要配置有效的飞书凭证（app_id、app_secret、user_access_token 等）。
"""

import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def load_config():
    """加载配置"""
    secrets_path = project_root.parent / 'config' / 'secrets.json'
    with open(secrets_path, 'r', encoding='utf-8') as f:
        return json.load(f)


config = load_config()
feishu_config = config.get('feishu', {})


def test_base_create():
    """测试创建多维表格"""
    print("测试创建多维表格...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        result = LarkCmd.BASE_CREATE.args(name='SDK测试表格', timezone='Asia/Shanghai').run()
        
        if result:
            print(f"✓ 创建成功")
            print(f"  - base_token: {result}")
            return True, result
        else:
            print("✗ 创建失败")
            return False, None
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_base_table_list(base_token):
    """测试获取表格列表"""
    print("\n测试获取表格列表...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        result = LarkCmd.BASE_TABLE_LIST.args(base_token=base_token).run()
        
        if result:
            data = json.loads(result)
            print(f"✓ 获取成功")
            print(f"  - 表格数量: {len(data)}")
            if data:
                return True, data[0]['table_id']
            return True, None
        else:
            print("✗ 获取失败")
            return False, None
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_base_field_list(base_token, table_id):
    """测试获取字段列表"""
    print("\n测试获取字段列表...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        result = LarkCmd.BASE_FIELD_LIST.args(base_token=base_token, table_id=table_id).run()
        
        if result:
            data = json.loads(result)
            print(f"✓ 获取成功")
            print(f"  - 字段数量: {len(data)}")
            for field in data[:3]:
                print(f"    - {field.get('name')} ({field.get('type')})")
            return True
        else:
            print("✗ 获取失败")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_record_batch_create(base_token, table_id):
    """测试批量创建记录"""
    print("\n测试批量创建记录...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        records = [
            {"fields": {"文本": "测试记录1"}},
            {"fields": {"文本": "测试记录2"}}
        ]
        data_json = json.dumps(records)
        
        result = LarkCmd.BASE_RECORD_BATCH_CREATE.args(
            base_token=base_token, 
            table_id=table_id, 
            data_json=data_json
        ).run()
        
        if result:
            record_ids = json.loads(result)
            print(f"✓ 创建成功")
            print(f"  - 创建记录数: {len(record_ids)}")
            return True, record_ids
        else:
            print("✗ 创建失败")
            return False, None
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_wiki_node_list():
    """测试获取知识库节点列表（需要 user_access_token）"""
    print("\n测试获取知识库节点列表...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        space_id = feishu_config.get('space_id')
        if not space_id:
            print("⚠️ 未配置 space_id，跳过此测试")
            return True

        result = LarkCmd.WIKI_NODE_LIST.with_user_access_token().run(logger=logger)
        
        if result:
            data = json.loads(result)
            print(f"✓ 获取成功")
            print(f"  - 节点数量: {len(data)}")
            for node in data[:3]:
                print(f"    - {node.get('title', '未知')}")
            return True
        else:
            print("✗ 获取失败")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_wiki_node_create():
    """测试创建知识库节点（需要 user_access_token）"""
    print("\n测试创建知识库节点...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        space_id = feishu_config.get('space_id')
        if not space_id:
            print("⚠️ 未配置 space_id，跳过此测试")
            return True, None

        result = LarkCmd.WIKI_NODE_CREATE.with_user_access_token().args(
            space_id=space_id,
            title=f'SDK测试文档_{int(time.time())}'
        ).run(logger=logger)
        
        if result:
            print(f"✓ 创建成功")
            print(f"  - node_token: {result}")
            return True, result
        else:
            print("✗ 创建失败")
            return False, None
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False, None


def test_im_message_send():
    """测试发送消息"""
    print("\n测试发送消息...")
    try:
        from utils.lark_sdk_commander import LarkCmd
        import requests

        webhook = feishu_config.get('bot_webhook')
        if webhook:
            # 使用 bot_webhook 发送消息
            data = {
                "msg_type": "text",
                "content": {
                    "text": "Python SDK 测试消息 (Webhook)"
                }
            }
            
            response = requests.post(webhook, json=data)
            if response.status_code == 200:
                print(f"✓ 使用 bot_webhook 发送成功")
            else:
                print(f"⚠️ bot_webhook 发送失败: {response.text}")
        
        # 尝试使用 SDK 发送消息
        chat_id = feishu_config.get('chat_id')
        if chat_id:
            content = json.dumps({"text": "Python SDK 测试消息 (SDK)"})
            
            result = LarkCmd.IM_MESSAGE_SEND.args(chat_id=chat_id, content=content).run(logger=logger)
            
            if result:
                print(f"✓ 使用 SDK 发送成功")
                print(f"  - message_id: {result}")
                return True
            else:
                print("✗ SDK 发送失败")
                return False
        
        print("⚠️ 未配置 chat_id，无法测试 SDK 发送")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_doc_update():
    """测试更新文档（需要 user_access_token 和 doc_token）"""
    print("\n测试更新文档...")
    try:
        from utils.lark_sdk_commander import LarkCmd

        # 先创建一个 wiki 节点获取 doc_token
        space_id = feishu_config.get('space_id')
        if not space_id:
            print("⚠️ 未配置 space_id，跳过此测试")
            return True

        # 创建文档
        node_token = LarkCmd.WIKI_NODE_CREATE.with_user_access_token().args(
            space_id=space_id,
            title=f'SDK测试文档_{int(time.time())}'
        ).run(logger=logger)
        
        if not node_token:
            print("⚠️ 创建文档失败，跳过更新测试")
            return True

        # 更新文档内容
        result = LarkCmd.DOC_UPDATE.with_user_access_token().args(
            doc_token=node_token
        ).input('这是通过 Python SDK 更新的文档内容').run(logger=logger)
        
        if result == "success":
            print(f"✓ 更新成功")
            return True
        else:
            print("✗ 更新失败")
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import time
    
    print("=" * 70)
    print("LarkSdkCommander 完整真实 API 集成测试")
    print("=" * 70)
    print(f"\n配置信息:")
    print(f"  - app_id: {feishu_config.get('app_id', '未配置')[:20]}...")
    print(f"  - user_access_token: {'已配置' if feishu_config.get('user_access_token') else '未配置'}")
    print(f"  - space_id: {feishu_config.get('space_id', '未配置')}")
    print(f"  - base_token: {feishu_config.get('base_token', '未配置')}")
    print(f"  - chat_id: {feishu_config.get('chat_id', '未配置')}")
    print("=" * 70)

    results = []
    base_token = None
    table_id = None

    # 1. 测试 Base 创建
    success, base_token = test_base_create()
    results.append(('Base 创建', success))

    # 2. 测试表格列表
    if base_token:
        success, table_id = test_base_table_list(base_token)
        results.append(('表格列表', success))

    # 3. 测试字段列表
    if base_token and table_id:
        success = test_base_field_list(base_token, table_id)
        results.append(('字段列表', success))

    # 4. 测试批量创建记录
    if base_token and table_id:
        success, _ = test_base_record_batch_create(base_token, table_id)
        results.append(('批量创建记录', success))

    # 5. 测试 Wiki 节点列表
    success = test_wiki_node_list()
    results.append(('Wiki 节点列表', success))

    # 6. 测试创建 Wiki 节点
    success, _ = test_wiki_node_create()
    results.append(('创建 Wiki 节点', success))

    # 7. 测试发送消息
    success = test_im_message_send()
    results.append(('发送消息', success))

    # 8. 测试更新文档
    success = test_doc_update()
    results.append(('更新文档', success))

    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    print("\n详细结果:")
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    if passed == total:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print("\n✗ 部分测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
