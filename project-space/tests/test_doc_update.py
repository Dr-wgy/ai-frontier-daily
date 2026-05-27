#!/usr/bin/env python3
"""测试 DOC_UPDATE 功能 - Markdown 转 Blocks 插入"""

import sys
sys.path.insert(0, '/Users/guanyu.wu/IdeaProjects/ai-frontier-daily/project-space')

from utils.lark_sdk_commander import LarkCmd

def main():
    print("=== 测试 DOC_UPDATE ===\n")

    # 测试 Markdown 内容
    markdown_content = """# 测试标题

这是一个测试文档。

## 子标题

- 列表项 1
- 列表项 2
- 列表项 3

### 代码示例

```python
def hello():
    print("Hello, World!")
```

这是正文内容。
"""

    # 创建文档并插入内容
    print("1. 创建新文档...")
    create_result = LarkCmd.DOC_UPDATE.args(
        title="SDK Markdown 测试文档"
    ).input(markdown_content).run()

    print(f"   结果: {create_result}")
    print()

    # 解析返回的 document_id
    import json
    try:
        result_json = json.loads(create_result) if create_result else {}
        document_id = result_json.get('document_id')
        print(f"2. 文档创建成功: {document_id}")
        print(f"   文档链接: https://ucni7p523jc2.feishu.cn/docx/{document_id}")
    except Exception as e:
        print(f"   解析失败: {e}")

if __name__ == "__main__":
    main()
