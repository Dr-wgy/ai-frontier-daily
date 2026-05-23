"""LarkCommander — 封装 lark-cli 命令为链式调用对象"""

from __future__ import annotations

import subprocess
from typing import Optional


class _LarkCommand:
    """lark-cli 命令实例（由 LarkCmd.args() 创建）"""

    def __init__(self, template: list[str]):
        self._template = template
        self._kwargs: dict = {}
        self._input_text: Optional[str] = None

    def args(self, **kwargs) -> '_LarkCommand':
        """设置命令模板中的占位符参数"""
        self._kwargs.update(kwargs)
        return self

    def input(self, text: str) -> '_LarkCommand':
        """设置 stdin 输入内容（如文档正文）"""
        self._input_text = text
        return self

    def run(self, logger=None) -> Optional[str]:
        """执行 lark-cli 命令

        Args:
            logger: 可选 logger 实例，用于记录错误日志

        Returns:
            命令执行成功返回 stdout（去除空白和 'null'），失败返回 None
        """
        cmd_args = [arg.format(**self._kwargs) for arg in self._template]

        result = subprocess.run(
            ['lark-cli'] + cmd_args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            input=self._input_text
        )

        if result.returncode != 0:
            msg = f"命令执行失败: {' '.join(cmd_args)}"
            if result.stderr:
                msg += f" - {result.stderr.strip()}"
            if logger:
                logger.error(msg)
            return None

        output = result.stdout.strip()
        return output if output and output != 'null' else None


class LarkCmd:
    """lark-cli 命令模板（静态工厂）"""

    # === Wiki 命令 ===
    WIKI_NODE_LIST = _LarkCommand(['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--page-all', '-q', '{query}'])
    WIKI_NODE_LIST_BY_PARENT = _LarkCommand(['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--parent-node-token', '{parent_token}', '--page-all', '-q', '{query}'])
    WIKI_NODE_SEARCH_BITABLE = _LarkCommand(['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--page-all', '-q', '.data.nodes[] | select(.obj_type == "bitable" and (.title | contains("{keyword}"))) | {node_token: .node_token, obj_token: .obj_token, title: .title}'])
    WIKI_NODE_CREATE = _LarkCommand(['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--obj-type', 'docx', '--title', '{title}', '-q', '.data.node_token'])
    WIKI_NODE_CREATE_WITH_PARENT = _LarkCommand(['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--title', '{title}', '--parent-node-token', '{parent_token}', '-q', '.data.node_token'])
    WIKI_NODE_MOVE = _LarkCommand(['wiki', '+move', '--as', 'user', '--node-token', '{node_token}', '--target-parent-token', '{target_token}'])

    # === Docs 命令 ===
    DOC_UPDATE = _LarkCommand(['docs', '+update', '--api-version', 'v1', '--as', 'user', '--doc', '{doc_token}', '--new-title', '{title}', '--mode', 'overwrite', '--markdown', '-'])

    # === Base 命令 ===
    BASE_CREATE = _LarkCommand(['base', '+base-create', '--name', '{name}', '--time-zone', '{timezone}', '--format', 'json', '-q', '.data.base.base_token'])
    BASE_TABLE_LIST = _LarkCommand(['base', '+table-list', '--base-token', '{base_token}', '--format', 'json', '-q', '.data.tables'])
    BASE_TABLE_CREATE = _LarkCommand(['base', '+table-create', '--base-token', '{base_token}', '--json', '{table_json}', '--format', 'json', '-q', '.data.table.id'])
    BASE_FIELD_LIST = _LarkCommand(['base', '+field-list', '--base-token', '{base_token}', '--table-id', '{table_id}', '-q', '[.data.fields[] | {field_id: .id, name: .name, type: .type}]'])
    BASE_FIELD_CREATE = _LarkCommand(['base', '+field-create', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{field_json}', '-q', '.data.field.id'])
    BASE_RECORD_SEARCH = _LarkCommand(['base', '+record-search', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{search_json}', '--format', 'json'])
    BASE_RECORD_DELETE = _LarkCommand(['base', '+record-delete', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{delete_json}', '--yes', '-q', '.data.deleted_record_id_list'])
    BASE_RECORD_BATCH_CREATE = _LarkCommand(['base', '+record-batch-create', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{data_json}', '-q', '.data.record_id_list'])

    # === IM 命令 ===
    IM_MESSAGE_SEND = _LarkCommand(['im', '+messages-send', '--chat-id', '{chat_id}', '--msg-type', 'interactive', '--content', '{content}'])
