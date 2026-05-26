#!/usr/bin/env python3
"""测试 BASE_RECORD_SEARCH 兼容性修复"""

import sys
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, PropertyMock

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def test_response_format_compatibility():
    """测试响应格式是否与 lark-cli 兼容"""
    from utils.lark_sdk_commander import LarkCmd
    
    # 创建模拟记录
    mock_record1 = MagicMock()
    mock_record1.record_id = 'rec123'
    mock_record1.fields = {'daily_report_time': '2026-05-26', 'title': 'Test Article'}
    
    mock_record2 = MagicMock()
    mock_record2.record_id = 'rec456'
    mock_record2.fields = {'daily_report_time': '2026-05-26', 'title': 'Another Article'}
    
    mock_response = MagicMock()
    mock_response.success.return_value = True
    mock_response.data.items = [mock_record1, mock_record2]
    setattr(mock_response.data, 'has_more', False)
    
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.search.return_value = mock_response
    
    with patch('utils.lark_sdk_commander.LarkClient.client', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_client
        
        result = LarkCmd.BASE_RECORD_SEARCH.args(
            base_token='test_base_token',
            table_id='test_table_id',
            search_json=json.dumps({
                'keyword': '2026-05-26',
                'search_fields': ['daily_report_time'],
                'select_fields': ['daily_report_time', 'title'],
                'limit': 200
            })
        ).run()
        
        assert result is not None, "结果不应为 None"
        
        parsed = json.loads(result)
        assert 'data' in parsed, "响应应包含 'data' 字段"
        
        data = parsed['data']
        assert 'record_id_list' in data, "响应应包含 'record_id_list' 字段"
        assert 'field_id_list' in data, "响应应包含 'field_id_list' 字段"
        assert 'items' in data, "响应应包含 'items' 字段"
        
        # 验证 record_id_list
        assert len(data['record_id_list']) == 2
        assert data['record_id_list'][0] == 'rec123'
        assert data['record_id_list'][1] == 'rec456'
        
        # 验证 field_id_list
        assert len(data['field_id_list']) == 2
        assert 'daily_report_time' in data['field_id_list']
        assert 'title' in data['field_id_list']
        
        # 验证 items 格式（数组格式，与 lark-cli 兼容）
        assert len(data['items']) == 2
        assert isinstance(data['items'][0], list), "items 元素应为数组格式"
        assert len(data['items'][0]) == 2, "每个 items 元素应包含与 field_id_list 对应的字段值"
        
        print("✓ 响应格式与 lark-cli 兼容")
        print(f"  record_id_list: {data['record_id_list']}")
        print(f"  field_id_list: {data['field_id_list']}")
        print(f"  items: {data['items']}")


def test_request_body_conversion():
    """测试请求体参数转换"""
    from utils.lark_sdk_commander import LarkCmd
    
    mock_response = MagicMock()
    mock_response.success.return_value = True
    mock_response.data.items = []
    
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.search = Mock(side_effect=lambda request: mock_response)
    
    with patch('utils.lark_sdk_commander.LarkClient.client', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_client
        
        LarkCmd.BASE_RECORD_SEARCH.args(
            base_token='test_base_token',
            table_id='test_table_id',
            search_json=json.dumps({
                'keyword': 'test_keyword',
                'search_fields': ['field1', 'field2'],
                'select_fields': ['field1', 'field2', 'field3'],
                'limit': 100
            })
        ).run()
        
        # 验证调用参数
        call_args = mock_client.bitable.v1.app_table_record.search.call_args[0][0]
        
        # 验证 app_token 和 table_id
        assert call_args.app_token == 'test_base_token'
        assert call_args.table_id == 'test_table_id'
        
        # 验证 page_size（limit 转换）
        assert call_args.page_size == 100
        
        # 验证 body 参数
        body = call_args.body
        assert 'field_names' in body, "body 应包含 field_names"
        assert body['field_names'] == ['field1', 'field2', 'field3']
        
        assert 'filter' in body, "body 应包含 filter"
        assert 'conditions' in body['filter']
        assert len(body['filter']['conditions']) == 2
        assert body['filter']['conjunction'] == 'or'
        
        print("✓ 请求参数转换正确")
        print(f"  page_size: {call_args.page_size}")
        print(f"  field_names: {body['field_names']}")
        print(f"  filter: {json.dumps(body['filter'])}")


def test_batch_create():
    """测试批量创建功能"""
    from utils.lark_sdk_commander import LarkCmd
    
    mock_record1 = MagicMock()
    mock_record1.record_id = 'new_rec1'
    
    mock_record2 = MagicMock()
    mock_record2.record_id = 'new_rec2'
    
    mock_response = MagicMock()
    mock_response.success.return_value = True
    mock_response.data.records = [mock_record1, mock_record2]
    
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.batch_create.return_value = mock_response
    
    with patch('utils.lark_sdk_commander.LarkClient.client', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_client
        
        # 测试新格式: {"fields": [...], "rows": [[...], [...]]}
        result = LarkCmd.BASE_RECORD_BATCH_CREATE.args(
            base_token='test_base_token',
            table_id='test_table_id',
            data_json=json.dumps({
                "fields": ["title", "content"],
                "rows": [
                    ["Article 1", "Content 1"],
                    ["Article 2", "Content 2"]
                ]
            })
        ).run()
        
        assert result is not None
        created_ids = json.loads(result)
        assert len(created_ids) == 2
        assert 'new_rec1' in created_ids
        assert 'new_rec2' in created_ids
        
        print("✓ 批量创建功能正常 (新格式)")
        print(f"  创建的记录ID: {created_ids}")


def test_batch_delete():
    """测试批量删除功能"""
    from utils.lark_sdk_commander import LarkCmd
    
    mock_record1 = MagicMock()
    mock_record1.record_id = 'rec1'
    
    mock_record2 = MagicMock()
    mock_record2.record_id = 'rec2'
    
    mock_response = MagicMock()
    mock_response.success.return_value = True
    mock_response.data.records = [mock_record1, mock_record2]
    
    mock_client = MagicMock()
    mock_client.bitable.v1.app_table_record.batch_delete.return_value = mock_response
    
    with patch('utils.lark_sdk_commander.LarkClient.client', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_client
        
        result = LarkCmd.BASE_RECORD_DELETE.args(
            base_token='test_base_token',
            table_id='test_table_id',
            delete_json=json.dumps({'record_id_list': ['rec1', 'rec2']})
        ).run()
        
        assert result is not None
        deleted_ids = json.loads(result)
        assert len(deleted_ids) == 2
        assert 'rec1' in deleted_ids
        assert 'rec2' in deleted_ids
        
        # 验证调用参数
        call_args = mock_client.bitable.v1.app_table_record.batch_delete.call_args[0][0]
        assert call_args.app_token == 'test_base_token'
        assert call_args.table_id == 'test_table_id'
        
        print("✓ 批量删除功能正常")
        print(f"  删除的记录ID: {deleted_ids}")


def test_auto_pagination():
    """测试 SDK 层自动分页功能"""
    from utils.lark_sdk_commander import LarkCmd
    
    # 模拟多页数据
    mock_record1 = MagicMock()
    mock_record1.record_id = 'rec1'
    mock_record1.fields = {'title': 'Article 1'}
    
    mock_record2 = MagicMock()
    mock_record2.record_id = 'rec2'
    mock_record2.fields = {'title': 'Article 2'}
    
    # 第一页响应
    mock_response1 = MagicMock()
    mock_response1.success.return_value = True
    mock_response1.data.items = [mock_record1]
    setattr(mock_response1.data, 'has_more', True)
    setattr(mock_response1.data, 'page_token', 'page_token_2')
    
    # 第二页响应
    mock_response2 = MagicMock()
    mock_response2.success.return_value = True
    mock_response2.data.items = [mock_record2]
    setattr(mock_response2.data, 'has_more', False)
    
    mock_client = MagicMock()
    # 模拟两次请求
    mock_client.bitable.v1.app_table_record.search = Mock(side_effect=[mock_response1, mock_response2])
    
    with patch('utils.lark_sdk_commander.LarkClient.client', new_callable=PropertyMock) as mock_prop:
        mock_prop.return_value = mock_client
        
        result = LarkCmd.BASE_RECORD_SEARCH.args(
            base_token='test_base_token',
            table_id='test_table_id',
            search_json=json.dumps({
                'keyword': 'test',
                'search_fields': ['title'],
                'select_fields': ['title'],
                'limit': 10,
                'offset': 0
            })
        ).run()
        
        assert result is not None
        parsed = json.loads(result)
        data = parsed['data']
        
        # 验证 SDK 自动获取了两页数据
        assert len(data['record_id_list']) == 2
        assert 'rec1' in data['record_id_list']
        assert 'rec2' in data['record_id_list']
        assert len(data['items']) == 2
        assert data.get('has_more') is False
        
        print("✓ SDK 层自动分页功能正常")
        print(f"  总记录数: {len(data['record_id_list'])}")
        print(f"  record_id_list: {data['record_id_list']}")
        
        # 模拟第二次请求 (offset=10) - 返回空结果，防止外层循环死循环
        result2 = LarkCmd.BASE_RECORD_SEARCH.args(
            base_token='test_base_token',
            table_id='test_table_id',
            search_json=json.dumps({
                'keyword': 'test',
                'search_fields': ['title'],
                'select_fields': ['title'],
                'limit': 10,
                'offset': 10
            })
        ).run()
        
        assert result2 is not None
        parsed2 = json.loads(result2)
        data2 = parsed2['data']
        
        # 验证返回空结果
        assert len(data2['record_id_list']) == 0
        assert len(data2['items']) == 0
        assert data2.get('has_more') is False
        
        print("✓ offset > 0 时返回空结果，防止外层循环死循环")


if __name__ == '__main__':
    print("=== 测试 BASE_RECORD_SEARCH 兼容性修复 ===\n")
    
    test_response_format_compatibility()
    print()
    test_request_body_conversion()
    print()
    test_batch_create()
    print()
    test_batch_delete()
    print()
    test_auto_pagination()
    
    print("\n=== 所有测试通过 ===")
