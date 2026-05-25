"""LarkSdkCommander — 基于 lark-oapi Python SDK 的飞书 API 封装"""

from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote_plus

import lark_oapi as lark
from lark_oapi.api.authen.v1 import (
    CreateAccessTokenRequest,
    CreateAccessTokenRequestBody,
    CreateRefreshAccessTokenRequest,
    CreateRefreshAccessTokenRequestBody,
)
from lark_oapi.api.wiki.v2 import (
    ListSpaceNodeRequest,
    CreateSpaceNodeRequest,
    MoveSpaceNodeRequest,
)
from lark_oapi.api.docx.v1 import UpdateDocumentRequest
from lark_oapi.api.bitable.v1 import (
    CreateAppRequest as BaseCreateRequest,
    ListAppTableRequest,
    CreateAppTableRequest,
    ListAppTableFieldRequest,
    CreateAppTableFieldRequest,
    SearchAppTableRecordRequest,
    DeleteAppTableRecordRequest,
    BatchCreateAppTableRecordRequest,
)
from lark_oapi.api.im.v1 import CreateMessageRequest


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class LarkClient:
    """飞书 SDK 客户端单例"""

    _instance = None
    _client = None
    _config = None
    _user_access_token = None
    _refresh_token = None
    _expires_at = 0  # 过期时间戳

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._load_config()
        self._init_client()
        self._initialized = True

    def _load_config(self):
        """从 secrets.json 加载配置"""
        secrets_path = PROJECT_ROOT / 'config' / 'secrets.json'
        if not secrets_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {secrets_path}")

        with open(secrets_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        self._config = config.get('feishu', {})
        if not self._config:
            raise ValueError("配置文件缺少 'feishu' 配置项")

        if 'app_id' not in self._config or 'app_secret' not in self._config:
            raise ValueError("缺少 'app_id' 或 'app_secret'")

        self._user_access_token = self._config.get('user_access_token')
        self._refresh_token = self._config.get('refresh_token')
        self._expires_at = self._config.get('expires_at', 0)

    def _init_client(self):
        """初始化飞书 SDK 客户端"""
        self._client = lark.Client.builder()\
            .app_id(self._config['app_id'])\
            .app_secret(self._config['app_secret'])\
            .build()

    @property
    def client(self):
        """获取 SDK 客户端实例"""
        return self._client

    def get_user_access_token(self) -> Optional[str]:
        """获取并根据需要刷新 user_access_token"""
        self.check_and_refresh_token()
        return self._user_access_token

    def check_and_refresh_token(self, force=False):
        """检查并刷新 token"""
        if not self._refresh_token:
            return

        # 如果未强制刷新，且 token 还有效（预留 5 分钟），则跳过
        if not force and self._expires_at > time.time() + 300:
            return

        print(f"正在刷新 user_access_token...")
        
        request = CreateRefreshAccessTokenRequest.builder() \
            .request_body(CreateRefreshAccessTokenRequestBody.builder() \
                .grant_type("refresh_token") \
                .refresh_token(self._refresh_token) \
                .build()) \
            .build()

        response = self._client.authen.v1.refresh_access_token.create(request)

        if not response.success():
            print(f"刷新失败: {response.code} - {response.msg}")
            # 如果是 refresh_token 过期，清空它以便触发重新授权
            if response.code == 20037 or "refresh_token" in response.msg:
                print("⚠️ refresh_token 已过期或失效，请重新执行初始化授权。")
                self._refresh_token = None
            return

        # 更新内存状态
        data = response.data
        self._user_access_token = data.access_token
        self._refresh_token = data.refresh_token
        self._expires_at = int(time.time()) + data.expires_in

        # 持久化到文件
        self._save_token_to_config()
        print(f"Token 刷新成功，新过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self._expires_at))}")

    def get_auth_url(self, redirect_uri: str = None) -> str:
        """生成飞书授权 URL
        
        Args:
            redirect_uri: 重定向 URI，如果为 None 则从配置中读取端口号
        """
        app_id = self._config['app_id']
        
        # 如果没有提供 redirect_uri，则从配置中读取端口号
        if redirect_uri is None:
            redirect_port = self._config.get('redirect_port', 8080)
            redirect_uri = f"http://127.0.0.1:{redirect_port}"
        
        # scope 必须包含 offline_access 才能获得 refresh_token
        scope = "bitable:app wiki:space docx:document:read docx:document:update im:message:send_as_bot offline_access"
        # 对参数进行 URL 编码，特别是处理空格
        encoded_redirect_uri = quote_plus(redirect_uri)
        encoded_scope = quote_plus(scope)
        url = f"https://open.feishu.cn/open-apis/authen/v1/index?redirect_uri={encoded_redirect_uri}&app_id={app_id}&scope={encoded_scope}"
        return url
    
    def get_redirect_port(self) -> int:
        """获取配置的重定向端口号"""
        return self._config.get('redirect_port', 8080)

    def init_with_code(self, code: str, redirect_uri: str = "http://127.0.0.1:8080"):
        """通过 code 初始化 Token"""
        print(f"正在通过 code 换取 Token...")
        
        request = CreateAccessTokenRequest.builder() \
            .request_body(CreateAccessTokenRequestBody.builder() \
                .grant_type("authorization_code") \
                .code(code) \
                .build()) \
            .build()

        response = self._client.authen.v1.access_token.create(request)

        if not response.success():
            print(f"初始化失败: {response.code} - {response.msg}")
            return False

        # 更新内存状态
        data = response.data
        self._user_access_token = data.access_token
        self._refresh_token = data.refresh_token
        self._expires_at = int(time.time()) + data.expires_in

        # 持久化到文件
        self._save_token_to_config()
        print(f"✓ 初始化成功！Token 已保存。")
        return True

    def _save_token_to_config(self):
        """保存 token 信息到 secrets.json"""
        secrets_path = PROJECT_ROOT / 'config' / 'secrets.json'
        with open(secrets_path, 'r', encoding='utf-8') as f:
            full_config = json.load(f)
        
        feishu = full_config.get('feishu', {})
        feishu['user_access_token'] = self._user_access_token
        feishu['refresh_token'] = self._refresh_token
        feishu['expires_at'] = self._expires_at
        
        full_config['feishu'] = feishu
        
        with open(secrets_path, 'w', encoding='utf-8') as f:
            json.dump(full_config, f, indent=2, ensure_ascii=False)

    @property
    def user_access_token(self) -> Optional[str]:
        """兼容旧接口：获取 user_access_token"""
        return self.get_user_access_token()

    def update_user_access_token(self, token: str):
        """兼容旧接口：更新 user_access_token"""
        self._user_access_token = token
        self._save_token_to_config()


class LarkSdkCommand:
    """Python SDK 命令实例"""

    def __init__(
        self,
        api_type: str,
        method: str,
        use_lark_cli: bool = False,
        use_user_access_token: bool = False,
        logger=None
    ):
        self._api_type = api_type
        self._method = method
        self._kwargs: dict = {}
        self._input_text: Optional[str] = None
        self._use_lark_cli = use_lark_cli
        self._use_user_access_token = use_user_access_token
        self._logger = logger

    def args(self, **kwargs) -> 'LarkSdkCommand':
        """设置参数，返回新实例（不可变性）"""
        new_cmd = LarkSdkCommand(
            self._api_type,
            self._method,
            use_lark_cli=self._use_lark_cli,
            use_user_access_token=self._use_user_access_token,
            logger=self._logger
        )
        new_cmd._kwargs = {**self._kwargs, **kwargs}
        new_cmd._input_text = self._input_text
        return new_cmd

    def input(self, text: str) -> 'LarkSdkCommand':
        """设置输入内容，返回新实例"""
        new_cmd = self.args()
        new_cmd._input_text = text
        return new_cmd

    def with_lark_cli(self) -> 'LarkSdkCommand':
        """切换到 lark-cli 模式（回退）"""
        new_cmd = self.args()
        new_cmd._use_lark_cli = True
        return new_cmd

    def with_user_access_token(self) -> 'LarkSdkCommand':
        """使用 user_access_token 模式"""
        new_cmd = self.args()
        new_cmd._use_user_access_token = True
        return new_cmd

    def run(self, logger=None) -> Optional[str]:
        """执行命令"""
        if logger:
            self._logger = logger

        if self._use_lark_cli:
            return self._run_lark_cli()
        return self._run_sdk()

    def _run_sdk(self) -> Optional[str]:
        """使用 Python SDK 执行"""
        client = LarkClient().client
        handler = self._get_handler()
        return handler(client)

    def _run_lark_cli(self) -> Optional[str]:
        """回退到 lark-cli 执行"""
        from .lark_commander import _LarkCommand

        template_map = {
            ('wiki', 'node_list'): ['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--page-all', '-q', '{query}'],
            ('wiki', 'node_list_by_parent'): ['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--parent-node-token', '{parent_token}', '--page-all', '-q', '{query}'],
            ('wiki', 'node_create'): ['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--obj-type', 'docx', '--title', '{title}', '-q', '.data.node_token'],
            ('wiki', 'node_create_with_parent'): ['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--title', '{title}', '--parent-node-token', '{parent_token}', '-q', '.data.node_token'],
            ('wiki', 'node_move'): ['wiki', '+move', '--as', 'user', '--node-token', '{node_token}', '--target-parent-token', '{target_token}'],
            ('docs', 'doc_update'): ['docs', '+update', '--api-version', 'v1', '--as', 'user', '--doc', '{doc_token}', '--new-title', '{title}', '--mode', 'overwrite', '--markdown', '-'],
            ('base', 'base_create'): ['base', '+base-create', '--name', '{name}', '--time-zone', '{timezone}', '--format', 'json', '-q', '.data.base.base_token'],
            ('base', 'table_list'): ['base', '+table-list', '--base-token', '{base_token}', '-q', '.data.tables'],
            ('base', 'table_create'): ['base', '+table-create', '--base-token', '{base_token}', '--json', '{table_json}', '--format', 'json', '-q', '.data.table.id'],
            ('base', 'field_list'): ['base', '+field-list', '--base-token', '{base_token}', '--table-id', '{table_id}', '-q', '[.data.fields[] | {field_id: .id, name: .name, type: .type}]'],
            ('base', 'field_create'): ['base', '+field-create', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{field_json}', '-q', '.data.field.id'],
            ('base', 'record_search'): ['base', '+record-search', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{search_json}', '--format', 'json'],
            ('base', 'record_delete'): ['base', '+record-delete', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{delete_json}', '--yes', '-q', '.data.deleted_record_id_list'],
            ('base', 'record_batch_create'): ['base', '+record-batch-create', '--base-token', '{base_token}', '--table-id', '{table_id}', '--json', '{data_json}', '-q', '.data.record_id_list'],
            ('im', 'message_send'): ['im', '+messages-send', '--chat-id', '{chat_id}', '--msg-type', 'interactive', '--content', '{content}'],
        }

        key = (self._api_type, self._method)
        template = template_map.get(key)
        if not template:
            if self._logger:
                self._logger.error(f"未知的 API 类型: {key}")
            return None

        cmd = _LarkCommand(template)
        cmd._kwargs = self._kwargs
        cmd._input_text = self._input_text

        result = subprocess.run(
            ['lark-cli'] + [arg.format(**self._kwargs) for arg in template],
            capture_output=True,
            text=True,
            encoding='utf-8',
            input=self._input_text
        )

        if result.returncode != 0:
            msg = f"命令执行失败: {' '.join([arg.format(**self._kwargs) for arg in template])}"
            if result.stderr:
                msg += f" - {result.stderr.strip()}"
            if self._logger:
                self._logger.error(msg)
            return None

        output = result.stdout.strip()
        return output if output and output != 'null' else None

    def _get_handler(self):
        """获取 API 处理函数"""
        handlers = {
            ('wiki', 'node_list'): self._handle_wiki_node_list,
            ('wiki', 'node_list_by_parent'): self._handle_wiki_node_list,
            ('wiki', 'node_create'): self._handle_wiki_node_create,
            ('wiki', 'node_create_with_parent'): self._handle_wiki_node_create,
            ('wiki', 'node_move'): self._handle_wiki_node_move,
            ('docs', 'doc_update'): self._handle_doc_update,
            ('base', 'base_create'): self._handle_base_create,
            ('base', 'table_list'): self._handle_base_table_list,
            ('base', 'table_create'): self._handle_base_table_create,
            ('base', 'field_list'): self._handle_base_field_list,
            ('base', 'field_create'): self._handle_base_field_create,
            ('base', 'record_search'): self._handle_base_record_search,
            ('base', 'record_delete'): self._handle_base_record_delete,
            ('base', 'record_batch_create'): self._handle_base_record_batch_create,
            ('im', 'message_send'): self._handle_im_message_send,
        }
        return handlers.get((self._api_type, self._method))

    def _get_user_access_token(self) -> Optional[str]:
        """获取 user_access_token"""
        if self._use_user_access_token or self._api_type == 'wiki':
            return LarkClient().get_user_access_token()
        return None

    def _handle_wiki_node_list(self, client) -> Optional[str]:
        """处理 wiki 节点列表"""
        space_id = self._kwargs.get('space_id')
        parent_token = self._kwargs.get('parent_token')
        query = self._kwargs.get('query', '')

        all_items = []
        page_token = None

        while True:
            request = ListSpaceNodeRequest.builder()\
                .space_id(space_id)\
                .page_size(500)\
                .build()

            if parent_token:
                request.parent_node_token = parent_token
            if page_token:
                request.page_token = page_token

            user_token = self._get_user_access_token()
            if user_token:
                request.header_user_access_token = user_token

            response = client.wiki.v2.space_node.list(request)

            if not response.success():
                if self._logger:
                    self._logger.error(f"Wiki API 调用失败: {response.msg}")
                return None

            items = []
            response_items = response.data.items if hasattr(response.data, 'items') else []
            for item in response_items:
                if hasattr(item, 'node_token'):
                    items.append({
                        'node_token': item.node_token,
                        'title': getattr(item, 'title', ''),
                        'obj_type': getattr(item, 'obj_type', ''),
                        'obj_token': getattr(item, 'obj_token', None),
                        'parent_node_token': getattr(item, 'parent_node_token', None),
                    })
                elif isinstance(item, dict):
                    items.append(item)

            all_items.extend(items)

            page_token = getattr(response.data, 'page_token', None)
            if not page_token:
                break

        result = self._apply_query({'data': {'nodes': all_items}}, query)
        return json.dumps(result, ensure_ascii=False) if result is not None else None

    def _handle_wiki_node_create(self, client) -> Optional[str]:
        """处理 wiki 节点创建"""
        space_id = self._kwargs.get('space_id')
        title = self._kwargs.get('title')
        parent_token = self._kwargs.get('parent_token')

        request = CreateSpaceNodeRequest.builder()\
            .build()

        request.body = {
            "obj_type": "docx",
            "space_id": space_id,
            "title": title,
        }
        if parent_token:
            request.body["parent_node_token"] = parent_token

        user_token = self._get_user_access_token()
        if user_token:
            request.header_user_access_token = user_token

        response = client.wiki.v2.space_node.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Wiki 创建节点失败: {response.msg}")
            return None

        node_token = getattr(response.data, 'node', None)
        if node_token:
            return node_token.node_token
        return None

    def _handle_wiki_node_move(self, client) -> Optional[str]:
        """处理 wiki 节点移动"""
        node_token = self._kwargs.get('node_token')
        target_parent_token = self._kwargs.get('target_token')

        request = MoveSpaceNodeRequest.builder()\
            .build()

        request.body = {
            "node_token": node_token,
            "target_parent_token": target_parent_token,
        }

        user_token = self._get_user_access_token()
        if user_token:
            request.header_user_access_token = user_token

        response = client.wiki.v2.space_node.move(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Wiki 移动节点失败: {response.msg}")
            return None

        return "success"

    def _handle_doc_update(self, client) -> Optional[str]:
        """处理文档更新（使用底层 PATCH 接口支持 Markdown 覆盖）"""
        doc_token = self._kwargs.get('doc_token')
        title = self._kwargs.get('title')
        
        # 1. 准备批量更新指令 (Match 飞书 API 规范: https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1RDN/docx-v1/document/patch)
        docx_requests = []
        
        # 更新标题
        if title:
            docx_requests.append({
                "update_document_display_setting_request": {
                    "display_setting": {"title": title}
                }
            })
            
        # 覆盖全文内容 (Markdown)
        if self._input_text:
            docx_requests.append({
                "update_all_content_request": {
                    "content": self._input_text,
                    "content_type": 1  # 1 代表 Markdown
                }
            })
            
        if not docx_requests:
            return "success"

        # 2. 构造原始请求 (因为当前 SDK 1.6.5 缺少此接口的封装)
        from lark_oapi.core.model import BaseRequest
        from lark_oapi.core.enum import HttpMethod, AccessTokenType
        from lark_oapi.core.http import Transport
        from lark_oapi.core.model import RequestOption
        from lark_oapi.core.const import UTF_8, CONTENT_TYPE, APPLICATION_JSON

        request = BaseRequest()
        request.http_method = HttpMethod.PATCH
        request.uri = "/open-apis/docx/v1/documents/:document_id"
        request.paths = {"document_id": doc_token}
        request.body = {"requests": docx_requests}
        request.token_types = {AccessTokenType.USER, AccessTokenType.TENANT}

        option = RequestOption()
        user_token = self._get_user_access_token()
        if user_token:
            option.headers["Authorization"] = f"Bearer {user_token}"
        
        option.headers[CONTENT_TYPE] = f"{APPLICATION_JSON}; charset=utf-8"

        # 3. 执行请求
        response = Transport.execute(client.config, request, option)
        
        if response.status_code != 200:
            if self._logger:
                self._logger.error(f"文档更新失败 (HTTP {response.status_code}): {response.content}")
            return None
            
        result_json = json.loads(str(response.content, UTF_8))
        if result_json.get("code") != 0:
            if self._logger:
                self._logger.error(f"文档更新失败: {result_json.get('msg')} (code: {result_json.get('code')})")
            return None
            
        return "success"

    def _handle_base_create(self, client) -> Optional[str]:
        """处理 Base 创建"""
        name = self._kwargs.get('name')
        timezone = self._kwargs.get('timezone', 'Asia/Shanghai')

        request = BaseCreateRequest.builder()\
            .build()

        request.body = {
            "name": name,
            "time_zone": timezone,
        }

        response = client.bitable.v1.app.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 创建失败: {response.msg}")
            return None

        app = getattr(response.data, 'app', None)
        if app:
            return getattr(app, 'app_token', None)
        return None

    def _handle_base_table_list(self, client) -> Optional[str]:
        """处理 Base 表格列表"""
        base_token = self._kwargs.get('base_token')

        request = ListAppTableRequest.builder()\
            .app_token(base_token)\
            .build()

        response = client.bitable.v1.app_table.list(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 表格列表获取失败: {response.msg}")
            return None

        tables = []
        if hasattr(response.data, 'items') and response.data.items:
            for table in response.data.items:
                tables.append({
                    'table_id': table.table_id,
                    'name': table.name,
                })

        return json.dumps(tables, ensure_ascii=False)

    def _handle_base_table_create(self, client) -> Optional[str]:
        """处理 Base 表格创建"""
        base_token = self._kwargs.get('base_token')
        table_json_str = self._kwargs.get('table_json', '{}')

        try:
            table_json = json.loads(table_json_str)
        except json.JSONDecodeError:
            table_json = {}

        request = CreateAppTableRequest.builder()\
            .app_token(base_token) \
            .build()

        request.body = {"table": table_json}

        response = client.bitable.v1.app_table.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 表格创建失败: {response.msg}")
            return None

        return getattr(response.data, 'table_id', None)

    def _handle_base_field_list(self, client) -> Optional[str]:
        """处理 Base 字段列表"""
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')

        request = ListAppTableFieldRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .build()

        response = client.bitable.v1.app_table_field.list(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 字段列表获取失败: {response.msg}")
            return None

        fields = []
        if hasattr(response.data, 'items') and response.data.items:
            for field in response.data.items:
                fields.append({
                    'field_id': getattr(field, 'field_id', getattr(field, 'id', '')),
                    'name': getattr(field, 'name', getattr(field, 'field_name', '')),
                    'type': getattr(field, 'type', getattr(field, 'field_type', '')),
                })

        return json.dumps(fields, ensure_ascii=False)

    def _handle_base_field_create(self, client) -> Optional[str]:
        """处理 Base 字段创建"""
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')
        field_json_str = self._kwargs.get('field_json', '{}')

        try:
            field_json = json.loads(field_json_str)
        except json.JSONDecodeError:
            field_json = {}

        request = CreateAppTableFieldRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .build()

        request.body = field_json

        response = client.bitable.v1.app_table_field.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 字段创建失败: {response.msg}")
            return None

        field = getattr(response.data, 'field', None)
        if field:
            return getattr(field, 'field_id', None)
        return None

    def _handle_base_record_search(self, client) -> Optional[str]:
        """处理 Base 记录搜索"""
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')
        search_json_str = self._kwargs.get('search_json', '{}')

        try:
            search_json = json.loads(search_json_str)
        except json.JSONDecodeError:
            search_json = {}

        request = SearchAppTableRecordRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .build()

        request.body = search_json

        response = client.bitable.v1.app_table_record.search(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 记录搜索失败: {response.msg}")
            return None

        records = []
        if hasattr(response.data, 'items') and response.data.items:
            for record in response.data.items:
                records.append({
                    'record_id': record.record_id,
                    'fields': getattr(record, 'fields', {}),
                })

        return json.dumps(records, ensure_ascii=False)

    def _handle_base_record_delete(self, client) -> Optional[str]:
        """处理 Base 记录删除"""
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')
        delete_json_str = self._kwargs.get('delete_json', '{}')

        try:
            delete_json = json.loads(delete_json_str)
        except json.JSONDecodeError:
            delete_json = {}

        request = DeleteAppTableRecordRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .build()

        request.body = delete_json

        response = client.bitable.v1.app_table_record.delete(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 记录删除失败: {response.msg}")
            return None

        deleted_ids = []
        if hasattr(response.data, 'records') and response.data.records:
            for record in response.data.records:
                deleted_ids.append(record.record_id)

        return json.dumps(deleted_ids, ensure_ascii=False)

    def _handle_base_record_batch_create(self, client) -> Optional[str]:
        """处理 Base 记录批量创建"""
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')
        data_json_str = self._kwargs.get('data_json', '[]')

        try:
            data_json = json.loads(data_json_str)
        except json.JSONDecodeError:
            data_json = []

        request = BatchCreateAppTableRecordRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .build()

        request.body = {"records": data_json}

        response = client.bitable.v1.app_table_record.batch_create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 记录批量创建失败: {response.msg}")
            return None

        record_ids = []
        if hasattr(response.data, 'records') and response.data.records:
            for record in response.data.records:
                record_ids.append(record.record_id)

        return json.dumps(record_ids, ensure_ascii=False)

    def _handle_im_message_send(self, client) -> Optional[str]:
        """处理 IM 消息发送"""
        chat_id = self._kwargs.get('chat_id')
        content = self._kwargs.get('content')

        try:
            content_obj = json.loads(content) if isinstance(content, str) else content
        except json.JSONDecodeError:
            content_obj = {"text": content}

        msg_type = "text"
        
        if isinstance(content_obj, dict):
            if "type" in content_obj:
                msg_type = content_obj.get("msg_type", "text")
                if msg_type == "interactive":
                    msg_type = "interactive"
                else:
                    msg_type = "text"
                    content_obj = {"text": str(content_obj)}
            else:
                msg_type = "text"

        request = CreateMessageRequest.builder()\
            .build()

        request.body = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": json.dumps(content_obj, ensure_ascii=False),
        }
        request.receive_id_type = "chat_id"

        user_token = self._get_user_access_token()
        if user_token:
            request.header_user_access_token = user_token

        response = client.im.v1.message.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"消息发送失败: {response.msg}")
            return None

        return getattr(response.data, 'message_id', None)

    def _apply_query(self, data: dict, query: str) -> Optional[Any]:
        """应用查询表达式（简化版 jq）"""
        if not query or query == '{query}' or query == '.data':
            return data.get('data', {})

        if query == '.data.nodes':
            return data.get('data', {}).get('nodes', [])

        nodes = data.get('data', {}).get('nodes', [])

        if 'select(' in query:
            match = re.search(r'select\((.+?)\)', query)
            if match:
                condition = match.group(1)
                filtered = self._filter_nodes(nodes, condition)
                return filtered

        return nodes

    def _filter_nodes(self, nodes: list, condition: str) -> list:
        """根据条件过滤节点"""
        result = []

        for node in nodes:
            if self._match_condition(node, condition):
                result.append(node)

        return result

    def _match_condition(self, node: dict, condition: str) -> bool:
        """匹配单个节点的条件"""
        condition = condition.strip()

        if ' and ' in condition:
            parts = condition.split(' and ')
            for part in parts:
                if not self._match_single_condition(node, part.strip()):
                    return False
            return True

        return self._match_single_condition(node, condition)

    def _match_single_condition(self, node: dict, condition: str) -> bool:
        """匹配单个条件（无 and）"""
        condition = condition.strip()

        if '==' in condition:
            parts = condition.split('==')
            field = self._extract_field(node, parts[0].strip())
            value = parts[1].strip().strip('"\'')
            return str(field) == value

        if 'contains(' in condition:
            field_match = re.search(r'\.(\w+)\s*\|\s*contains\("(.+?)"\)', condition)
            if field_match:
                field_name = field_match.group(1)
                value = field_match.group(2)
                field = node.get(field_name, '')
                return value in str(field)

        obj_type_match = re.search(r'\.obj_type\s*==\s*"(\w+)"', condition)
        if obj_type_match:
            obj_type = obj_type_match.group(1)
            return node.get('obj_type') == obj_type

        return False

    def _extract_field(self, node: dict, field_path: str) -> Any:
        """提取字段值"""
        field_path = field_path.strip().lstrip('.')
        return node.get(field_path)


class LarkCmd:
    """飞书 SDK 命令模板（静态工厂）"""

    WIKI_NODE_LIST = LarkSdkCommand('wiki', 'node_list')
    WIKI_NODE_LIST_BY_PARENT = LarkSdkCommand('wiki', 'node_list_by_parent')
    WIKI_NODE_SEARCH_BITABLE = LarkSdkCommand('wiki', 'node_list')
    WIKI_NODE_CREATE = LarkSdkCommand('wiki', 'node_create')
    WIKI_NODE_CREATE_WITH_PARENT = LarkSdkCommand('wiki', 'node_create_with_parent')
    WIKI_NODE_MOVE = LarkSdkCommand('wiki', 'node_move')

    DOC_UPDATE = LarkSdkCommand('docs', 'doc_update')

    BASE_CREATE = LarkSdkCommand('base', 'base_create')
    BASE_TABLE_LIST = LarkSdkCommand('base', 'table_list')
    BASE_TABLE_CREATE = LarkSdkCommand('base', 'table_create')
    BASE_FIELD_LIST = LarkSdkCommand('base', 'field_list')
    BASE_FIELD_CREATE = LarkSdkCommand('base', 'field_create')
    BASE_RECORD_SEARCH = LarkSdkCommand('base', 'record_search')
    BASE_RECORD_DELETE = LarkSdkCommand('base', 'record_delete')
    BASE_RECORD_BATCH_CREATE = LarkSdkCommand('base', 'record_batch_create')

    IM_MESSAGE_SEND = LarkSdkCommand('im', 'message_send')