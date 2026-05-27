#!/usr/bin/env python3
"""LarkSdkCommander 调试测试脚本"""

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


def test_with_debug():
    """详细调试测试"""
    from utils.lark_sdk_commander import LarkCmd, LarkClient
    
    # 1. 创建 Base
    print("1. 创建 Base...")
    base_result = LarkCmd.BASE_CREATE.args(name='调试测试表格', timezone='Asia/Shanghai').run()
    print(f"   结果: {base_result}")
    
    if not base_result:
        print("   ✗ 创建失败，退出")
        return
    
    base_token = base_result
    
    # 2. 获取表格列表
    print("\n2. 获取表格列表...")
    table_result = LarkCmd.BASE_TABLE_LIST.args(base_token=base_token).run()
    print(f"   结果: {table_result}")
    
    if table_result:
        tables = json.loads(table_result)
        table_id = tables[0]['table_id']
        print(f"   table_id: {table_id}")
    else:
        print("   ✗ 获取失败，退出")
        return
    
    # 3. 获取字段列表
    print("\n3. 获取字段列表...")
    field_result = LarkCmd.BASE_FIELD_LIST.args(base_token=base_token, table_id=table_id).run()
    print(f"   结果: {field_result}")
    
    # 4. 批量创建记录（带调试信息）
    print("\n4. 批量创建记录...")
    records = [{"fields": {"文本": "测试1"}}]
    data_json = json.dumps(records)
    
    # 直接调用 SDK 来获取详细错误
    client = LarkClient()
    import lark_oapi as lark
    
    request = lark.api.bitable.v1.BatchCreateAppTableRecordRequest.builder()\
        .app_token(base_token)\
        .table_id(table_id)\
        .build()
    request.body = {"records": records}
    
    response = client.client.bitable.v1.app_table_record.batch_create(request)
    
    print(f"   success: {response.success()}")
    print(f"   code: {response.code}")
    print(f"   msg: {response.msg}")
    
    if response.success():
        print(f"   data: {response.data}")
        record_ids = []
        if hasattr(response.data, 'records') and response.data.records:
            for record in response.data.records:
                record_ids.append(getattr(record, 'record_id', None))
        print(f"   record_ids: {record_ids}")
    else:
        print("   ✗ 创建失败")


if __name__ == '__main__':
    test_with_debug()
