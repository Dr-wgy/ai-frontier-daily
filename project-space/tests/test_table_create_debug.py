#!/usr/bin/env python3
"""详细调试 BASE_TABLE_CREATE"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.lark_sdk_commander import LarkClient

client = LarkClient()
import lark_oapi as lark

# 创建一个 base
create_response = client.client.bitable.v1.app.create(
    lark.api.bitable.v1.CreateAppRequest.builder().build()
)

if not create_response.success():
    print(f"创建 base 失败: {create_response.msg}")
    sys.exit(1)

base_token = create_response.data.app_token
print(f"创建的 base_token: {base_token}")

# 尝试各种表格创建格式
test_cases = [
    {"name": "新表格"},
    {"default_view_name": "表格视图"},
    {"name": "新表格", "default_view_name": "表格视图"},
    {"default_view_name": "表格视图", "fields": [{"field_name": "名称", "type": 1}]},
    {"name": "新表格", "default_view_name": "表格视图", "fields": [{"field_name": "名称", "type": 1}]},
]

for i, body in enumerate(test_cases):
    print(f"\n测试用例 {i+1}: {json.dumps(body)}")
    
    request = lark.api.bitable.v1.CreateAppTableRequest.builder()\
        .app_token(base_token)\
        .build()
    request.body = body
    
    response = client.client.bitable.v1.app_table.create(request)
    
    print(f"  success: {response.success()}")
    print(f"  code: {response.code}")
    print(f"  msg: {response.msg}")
    
    if response.success():
        print(f"  table_id: {getattr(response.data.table, 'table_id', '未知')}")
