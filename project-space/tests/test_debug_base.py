#!/usr/bin/env python3
"""调试 BASE_TABLE_CREATE 和 BASE_RECORD_DELETE"""

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

from utils.lark_sdk_commander import LarkCmd, LarkClient


def test_base_table_create():
    """调试表格创建"""
    print("=== 调试 BASE_TABLE_CREATE ===")
    
    # 创建一个新的 base
    base_token = LarkCmd.BASE_CREATE.args(name='DebugBase', timezone='Asia/Shanghai').run()
    print(f"创建的 base_token: {base_token}")
    
    if not base_token:
        print("创建 base 失败")
        return
    
    # 获取表格列表
    tables = LarkCmd.BASE_TABLE_LIST.args(base_token=base_token).run()
    print(f"表格列表: {tables}")
    
    # 直接调用 SDK 创建表格
    client = LarkClient()
    import lark_oapi as lark
    
    request = lark.api.bitable.v1.CreateAppTableRequest.builder()\
        .app_token(base_token)\
        .build()
    request.body = {"name": "新表格"}
    
    response = client.client.bitable.v1.app_table.create(request)
    
    print(f"\nSDK 调用结果:")
    print(f"  success: {response.success()}")
    print(f"  code: {response.code}")
    print(f"  msg: {response.msg}")
    
    if response.success():
        print(f"  table_id: {getattr(response.data.table, 'table_id', '未知')}")


def test_base_record_delete():
    """调试记录删除"""
    print("\n=== 调试 BASE_RECORD_DELETE ===")
    
    # 创建 base 和记录
    base_token = LarkCmd.BASE_CREATE.args(name='DebugBase_Delete', timezone='Asia/Shanghai').run()
    print(f"创建的 base_token: {base_token}")
    
    if not base_token:
        print("创建 base 失败")
        return
    
    # 获取表格 ID
    tables = LarkCmd.BASE_TABLE_LIST.args(base_token=base_token).run()
    if not tables:
        print("获取表格失败")
        return
    
    table_id = json.loads(tables)[0]['table_id']
    print(f"table_id: {table_id}")
    
    # 创建记录
    records = [{"fields": {"文本": "测试删除"}}]
    create_result = LarkCmd.BASE_RECORD_BATCH_CREATE.args(
        base_token=base_token, 
        table_id=table_id, 
        data_json=json.dumps(records)
    ).run()
    print(f"创建记录结果: {create_result}")
    
    if create_result:
        record_ids = json.loads(create_result)
        print(f"创建的 record_ids: {record_ids}")
        
        # 尝试删除
        delete_json = json.dumps({"record_ids": record_ids})
        delete_result = LarkCmd.BASE_RECORD_DELETE.args(
            base_token=base_token, 
            table_id=table_id, 
            delete_json=delete_json
        ).run()
        print(f"删除结果: {delete_result}")
        
        # 直接调用 SDK 删除
        client = LarkClient()
        import lark_oapi as lark
        
        request = lark.api.bitable.v1.DeleteAppTableRecordRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .build()
        request.body = {"record_ids": record_ids}
        
        response = client.client.bitable.v1.app_table_record.delete(request)
        
        print(f"\nSDK 调用结果:")
        print(f"  success: {response.success()}")
        print(f"  code: {response.code}")
        print(f"  msg: {response.msg}")


if __name__ == '__main__':
    test_base_table_create()
    test_base_record_delete()
