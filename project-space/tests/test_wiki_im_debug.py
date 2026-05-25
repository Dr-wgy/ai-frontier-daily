#!/usr/bin/env python3
"""调试 Wiki 和 IM API"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 加载配置
secrets_path = project_root.parent / 'config' / 'secrets.json'
with open(secrets_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('feishu', {})


def test_wiki():
    """测试 Wiki API"""
    print("=== 测试 Wiki API ===")
    from utils.lark_sdk_commander import LarkCmd, LarkClient
    
    space_id = feishu_config.get('space_id')
    user_token = feishu_config.get('user_access_token')
    
    print(f"space_id: {space_id}")
    print(f"user_access_token: {'已配置' if user_token else '未配置'}")
    print(f"token长度: {len(user_token) if user_token else 0}")
    
    # 直接调用 SDK
    client = LarkClient()
    
    import lark_oapi as lark
    request = lark.api.wiki.v2.ListSpaceNodeRequest.builder()\
        .space_id(space_id)\
        .page_size(10)\
        .build()
    
    if user_token:
        request.header_user_access_token = user_token
    
    response = client.client.wiki.v2.space_node.list(request)
    
    print(f"\nWiki API 调用结果:")
    print(f"  success: {response.success()}")
    print(f"  code: {response.code}")
    print(f"  msg: {response.msg}")
    
    if response.success() and hasattr(response.data, 'items'):
        print(f"  items count: {len(response.data.items)}")
        for item in response.data.items[:3]:
            print(f"    - {getattr(item, 'title', '未知')}")


def test_im():
    """测试 IM API"""
    print("\n=== 测试 IM API ===")
    from utils.lark_sdk_commander import LarkCmd, LarkClient
    
    chat_id = feishu_config.get('chat_id')
    webhook = feishu_config.get('bot_webhook')
    print(f"chat_id: {chat_id}")
    print(f"bot_webhook: {'已配置' if webhook else '未配置'}")
    
    # 测试使用 bot_webhook 发送消息
    if webhook:
        print("\n尝试使用 bot_webhook...")
        import requests
        
        data = {
            "msg_type": "text",
            "content": {
                "text": "测试消息"
            }
        }
        
        try:
            response = requests.post(webhook, json=data)
            print(f"  status_code: {response.status_code}")
            print(f"  response: {response.text}")
        except Exception as e:
            print(f"  错误: {e}")
    
    # 测试使用 SDK
    print("\n尝试使用 SDK...")
    client = LarkClient()
    
    import lark_oapi as lark
    
    # 使用简单的文本消息格式
    content = "{\"text\": \"测试消息\"}"
    
    request = lark.api.im.v1.CreateMessageRequest.builder()\
        .build()
    
    request.body = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": content,
    }
    request.receive_id_type = "chat_id"
    
    response = client.client.im.v1.message.create(request)
    
    print(f"IM API 调用结果:")
    print(f"  success: {response.success()}")
    print(f"  code: {response.code}")
    print(f"  msg: {response.msg}")
    
    if response.success():
        print(f"  message_id: {getattr(response.data, 'message_id', '未知')}")


if __name__ == '__main__':
    test_wiki()
    test_im()
