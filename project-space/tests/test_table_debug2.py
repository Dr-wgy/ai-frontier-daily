#!/usr/bin/env python3
"""调试 BASE_TABLE_CREATE"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.lark_sdk_commander import LarkClient, LarkCmd

client = LarkClient()
import lark_oapi as lark

base_token = LarkCmd.BASE_CREATE.args(name='DebugBase', timezone='Asia/Shanghai').run()
print(f"创建的 base_token: {base_token}")

test_cases = [
    {"name": "新表格"},
    {"default_view_name": "表格视图"},
    {"name": "新表格", "default_view_name": "表格视图"},
]

for i, table_data in enumerate(test_cases):
    print(f"\n测试用例 {i+1}: {json.dumps(table_data)}")
    
    request = lark.api.bitable.v1.CreateAppTableRequest.builder()\
        .app_token(base_token)\
        .build()
    request.body = {"table": table_data}
    
    response = client.client.bitable.v1.app_table.create(request)
    
    print(f"  success: {response.success()}")
    print(f"  code: {response.code}")
    print(f"  msg: {response.msg}")
    
    if response.success():
        print(f"  response.data: {response.data}")
        print(f"  response.data attrs: {[attr for attr in dir(response.data) if not attr.startswith('_')]}")
