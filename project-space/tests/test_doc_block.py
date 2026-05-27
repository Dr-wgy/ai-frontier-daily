#!/usr/bin/env python3
"""测试文档根 Block ID"""

import sys
sys.path.insert(0, '/Users/guanyu.wu/IdeaProjects/ai-frontier-daily/project-space')

import json
from utils.lark_sdk_commander import LarkClient
from lark_oapi.api.docx.v1 import *

def main():
    # 初始化客户端
    client = LarkClient()
    lark_client = client.client

    print("=== 第 1 步：创建文档 ===")
    # 创建文档
    create_req = CreateDocumentRequest.builder() \
        .request_body(CreateDocumentRequestBody.builder()
            .title("SDK 测试文档")
            .build()) \
        .build()
    create_resp = lark_client.docx.v1.document.create(create_req)

    if create_resp.success():
        document_id = create_resp.data.document.document_id
        print(f"文档创建成功: {document_id}")

        # 第 2 步：获取 Blocks
        print("\n=== 第 2 步：获取文档 Blocks ===")
        list_req = ListDocumentBlockRequest.builder() \
            .document_id(document_id) \
            .build()
        list_resp = lark_client.docx.v1.document_block.list(list_req)

        if list_resp.success():
            print(f"Blocks 数量: {len(list_resp.data.items)}")
            for block in list_resp.data.items[:3]:
                print(f"  - block_id: {block.block_id}")
                print(f"    block_type: {block.block_type}")
                print(f"    parent_id: {getattr(block, 'parent_id', 'N/A')}")
                print()

            # 检查根 block
            if list_resp.data.items:
                root_block = list_resp.data.items[0]
                print(f"=== 根节点验证 ===")
                print(f"block_id == document_id? {root_block.block_id == document_id}")
                print(f"block_id: {root_block.block_id}")
                print(f"document_id: {document_id}")
                print(f"block_type == 1 (Page)? {root_block.block_type == 1}")
        else:
            print(f"获取 Blocks 失败: {list_resp.msg}")
    else:
        print(f"创建文档失败: {create_resp.msg}")

if __name__ == "__main__":
    main()
