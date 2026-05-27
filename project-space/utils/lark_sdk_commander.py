"""LarkSdkCommander — 基于 lark-oapi Python SDK 的飞书 API 封装"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from urllib.parse import quote_plus

import jq
import lark_oapi as lark
from lark_oapi.api.authen.v1 import (
    CreateAccessTokenRequest,
    CreateAccessTokenRequestBody,
    CreateRefreshAccessTokenRequest,
    CreateRefreshAccessTokenRequestBody,
)
from lark_oapi.api.bitable.v1 import (
    CreateAppRequest as BaseCreateRequest,
    ListAppTableRequest,
    CreateAppTableRequest,
    ListAppTableFieldRequest,
    CreateAppTableFieldRequest,
    SearchAppTableRecordRequest,
    BatchDeleteAppTableRecordRequest,
    BatchDeleteAppTableRecordRequestBody,
    BatchCreateAppTableRecordRequest,
    BatchCreateAppTableRecordRequestBody,
    AppTableRecord,
)
from lark_oapi.api.im.v1 import CreateMessageRequest
from lark_oapi.api.wiki.v2 import *

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class LarkClient:
    """飞书 SDK 客户端单例"""

    _instance = None
    _client = None
    _config = None
    _user_access_token = None
    _refresh_token = None
    _expires_at = 0  # 过期时间戳
    _logger = None

    def _init_logger(self):
        """初始化日志记录器（遵循项目统一日志架构）"""
        from .logger import get_logger
        import time
        self._logger = get_logger('lark_client', time.strftime('%Y-%m-%d'))

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._init_logger()
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
            .enable_set_token(True)\
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

        if self._logger:
            self._logger.info(f"正在刷新 user_access_token...")
        
        request = CreateRefreshAccessTokenRequest.builder() \
            .request_body(CreateRefreshAccessTokenRequestBody.builder() \
                .grant_type("refresh_token") \
                .refresh_token(self._refresh_token) \
                .build()) \
            .build()

        response = self._client.authen.v1.refresh_access_token.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"刷新失败: {response.code} - {response.msg}")
            # 如果是 refresh_token 过期，清空它以便触发重新授权
            if response.code == 20037 or "refresh_token" in response.msg:
                if self._logger:
                    self._logger.warning(f"refresh_token 已过期或失效，请重新执行初始化授权。")
                self._refresh_token = None
            return

        # 更新内存状态
        data = response.data
        self._user_access_token = data.access_token
        self._refresh_token = data.refresh_token
        self._expires_at = int(time.time()) + data.expires_in

        # 持久化到文件
        self._save_token_to_config()
        if self._logger:
            self._logger.info(f"Token 刷新成功，新过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self._expires_at))}")

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
        if self._logger:
            self._logger.info(f"正在通过 code 换取 Token...")
        
        request = CreateAccessTokenRequest.builder() \
            .request_body(CreateAccessTokenRequestBody.builder() \
                .grant_type("authorization_code") \
                .code(code) \
                .build()) \
            .build()

        response = self._client.authen.v1.access_token.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"初始化失败: {response.code} - {response.msg}")
            return False

        # 更新内存状态
        data = response.data
        self._user_access_token = data.access_token
        self._refresh_token = data.refresh_token
        self._expires_at = int(time.time()) + data.expires_in

        # 持久化到文件
        self._save_token_to_config()
        if self._logger:
            self._logger.info(f"初始化成功！Token 已保存。")
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

    def _extract_field_value(self, value):
        """提取字段值，处理 SDK 返回的嵌套结构
        
        处理各种嵌套格式：
        - [[{'text': '2026-05-26', 'type': 'text'}]] -> '2026-05-26'
        - [{'text': 'value', 'type': 'text'}] -> 'value'
        - {'text': 'value'} -> 'value'
        - 其他值保持不变
        """
        if value is None:
            return None
        
        # 处理三层嵌套：[[{...}]]
        if isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], list) and len(value[0]) > 0:
                if isinstance(value[0][0], dict) and 'text' in value[0][0]:
                    return value[0][0]['text']
            # 处理两层嵌套：[{...}]
            elif isinstance(value[0], dict):
                if 'text' in value[0]:
                    return value[0]['text']
        
        # 处理单层对象：{...}
        if isinstance(value, dict):
            if 'text' in value:
                return value['text']
        
        return value

    def _convert_value_by_type(self, value, field_type):
        """根据字段类型转换值
        
        目前只处理日期类型字段的转换：
        - date 类型：将日期字符串转换为 Unix 时间戳（毫秒）
        - 其他类型：保持原值不变
        """
        if value is None:
            return None
        
        # 只对日期类型字段进行转换
        if field_type and (field_type.lower() == '5'):
            return self._convert_date_to_timestamp(value)
        
        return value

    def _convert_date_to_timestamp(self, value):
        """将日期字符串转换为 Unix 时间戳（毫秒）
        
        支持的日期格式：
        - '2026-05-26' -> 1753507200000
        - '2026-05-26 12:00:00' -> 1753546800000
        - 其他值保持不变
        """
        if value is None:
            return None
        
        if isinstance(value, int):
            # 已经是数字，假设是时间戳
            return value
        
        if isinstance(value, str):
            import re
            
            # 尝试解析日期字符串
            date_patterns = [
                r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$',  # 2026-05-26 12:00:00
                r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$',        # 2026-05-26 12:00
                r'^(\d{4})-(\d{2})-(\d{2})$',                         # 2026-05-26
            ]
            
            for pattern in date_patterns:
                match = re.match(pattern, value.strip())
                if match:
                    groups = match.groups()
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2])
                    hour = int(groups[3]) if len(groups) > 3 else 0
                    minute = int(groups[4]) if len(groups) > 4 else 0
                    second = int(groups[5]) if len(groups) > 5 else 0
                    
                    # 计算 Unix 时间戳（毫秒）
                    from datetime import datetime
                    timestamp = datetime(year, month, day, hour, minute, second).timestamp() * 1000
                    return int(timestamp)
        
        return value

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
            # 使用 Builder 链式调用，只在参数有值时添加
            builder = ListSpaceNodeRequest.builder().page_size(50)
            
            if space_id:
                builder = builder.space_id(space_id)
            if parent_token:
                builder = builder.parent_node_token(parent_token)
            if page_token:
                builder = builder.page_token(page_token)
            
            request = builder.build()

            user_token = self._get_user_access_token()
            
            if user_token:
                response = client.wiki.v2.space_node.list(request, lark.RequestOption.builder().user_access_token(user_token).build())
            else:
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

        return self._apply_query({'data': {'nodes': all_items}}, query)


    def _handle_wiki_node_create(self, client) -> Optional[str]:
        """处理 wiki 节点创建"""
        space_id = self._kwargs.get('space_id')
        title = self._kwargs.get('title')
        parent_token = self._kwargs.get('parent_token')

        request = CreateSpaceNodeRequest.builder()\
            .space_id(space_id)\
            .request_body(Node.builder()
            .obj_type("docx")
            .parent_node_token(parent_token)
            .node_type("origin")
            .title(title)
            .build()).build()

        user_token = self._get_user_access_token()
        
        if user_token:
            response = client.wiki.v2.space_node.create(request, lark.RequestOption.builder().user_access_token(user_token).build())
        else:
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
        target_parent_token = self._kwargs.get('target_parent_token')
        space_id = self._kwargs.get('space_id')

        request = MoveSpaceNodeRequest.builder()\
            .node_token(node_token)\
            .space_id(space_id)\
            .request_body(MoveSpaceNodeRequestBody.builder()
                .target_parent_token(target_parent_token)
                .target_space_id(space_id)
                .build())\
            .build()


        user_token = self._get_user_access_token()
        
        if user_token:
            response = client.wiki.v2.space_node.move(request, lark.RequestOption.builder().user_access_token(user_token).build())
        else:
            response = client.wiki.v2.space_node.move(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Wiki 移动节点失败: {response.msg}")
            return None

        return "success"

    def _handle_doc_update(self, client) -> Optional[str]:
        """处理文档更新（严格遵循 SDK 原生接口，绝不虚构）"""
        doc_token = self._kwargs.get('doc_token')
        title = self._kwargs.get('title')
        space_id = self._kwargs.get('space_id')

        document_id = None

        # 1. 如果提供了 doc_token，识别并转换 Wiki Token -> Docx Token
        if doc_token:
            from lark_oapi.api.wiki.v2 import GetNodeSpaceRequest
            get_node_req = GetNodeSpaceRequest.builder() \
                .token(doc_token) \
                .build()

            user_token = self._get_user_access_token()

            if user_token:
                get_node_resp = client.wiki.v2.space.get_node(get_node_req, lark.RequestOption.builder().user_access_token(user_token).build())
            else:
                get_node_resp = client.wiki.v2.space.get_node(get_node_req)

            if get_node_resp.success() and hasattr(get_node_resp.data, 'node'):
                node_data = get_node_resp.data.node
                document_id = node_data.obj_token
                if not space_id:
                    space_id = node_data.space_id
            else:
                if self._logger:
                    self._logger.error(f"Wiki 节点解析失败，无法进行后续操作: {get_node_resp.msg}")
                return None
        else:
            # 1.1 如果没有提供 doc_token，创建新文档
            from lark_oapi.api.docx.v1 import CreateDocumentRequest, CreateDocumentRequestBody

            create_doc_req = CreateDocumentRequest.builder() \
                .request_body(CreateDocumentRequestBody.builder()
                    .title(title or "新文档")
                    .build()) \
                .build()

            user_token = self._get_user_access_token()

            if user_token:
                create_doc_resp = client.docx.v1.document.create(create_doc_req, lark.RequestOption.builder().user_access_token(user_token).build())
            else:
                create_doc_resp = client.docx.v1.document.create(create_doc_req)

            if not create_doc_resp.success():
                if self._logger:
                    self._logger.error(f"文档创建失败: {create_doc_resp.msg}")
                return None

            document_id = create_doc_resp.data.document.document_id

        # 2. 标题更新：仅在存在对应 Wiki 接口时执行
        if title and space_id and doc_token:
            from lark_oapi.api.wiki.v2 import UpdateTitleSpaceNodeRequest, UpdateTitleSpaceNodeRequestBody
            wiki_req = UpdateTitleSpaceNodeRequest.builder() \
                .space_id(space_id) \
                .node_token(doc_token) \
                .request_body(UpdateTitleSpaceNodeRequestBody.builder()
                    .title(title)
                    .build()) \
                .build()

            user_token = self._get_user_access_token()

            if user_token:
                wiki_resp = client.wiki.v2.space_node.update_title(wiki_req, lark.RequestOption.builder().user_access_token(user_token).build())
            else:
                wiki_resp = client.wiki.v2.space_node.update_title(wiki_req)
            if not wiki_resp.success() and self._logger:
                self._logger.warning(f"Wiki 标题更新失败: {wiki_resp.msg}")

        # 3. 如果没有正文更新内容，返回 document_id
        if not self._input_text:
            return json.dumps({"document_id": document_id}, ensure_ascii=False)

        # 4. Markdown 转换 (SDK 原生支持)
        from lark_oapi.api.docx.v1 import ConvertDocumentRequest, ConvertDocumentRequestBody
        convert_req = ConvertDocumentRequest.builder() \
            .request_body(ConvertDocumentRequestBody.builder() \
                .content(self._input_text) \
                .content_type("markdown") \
                .build()) \
            .build()
        convert_resp = client.docx.v1.document.convert(convert_req)
        if not convert_resp.success():
            if self._logger:
                self._logger.error(f"Markdown 转换失败: {convert_resp.msg}")
            return None

        new_blocks = convert_resp.data.blocks if hasattr(convert_resp.data, 'blocks') else []
        first_level_block_ids = convert_resp.data.first_level_block_ids if hasattr(convert_resp.data, 'first_level_block_ids') else []
        if not new_blocks:
            return json.dumps({"document_id": document_id}, ensure_ascii=False)

        # 5. 根据 firstLevelBlockIds 重新排序 blocks
        if first_level_block_ids:
            block_map = {block.block_id: block for block in new_blocks if hasattr(block, 'block_id') and block.block_id}
            ordered_blocks = []
            for block_id in first_level_block_ids:
                if block_id in block_map:
                    ordered_blocks.append(block_map.pop(block_id))
            for block in block_map.values():
                ordered_blocks.append(block)
            new_blocks = ordered_blocks

        # 6. 清理 Blocks（移除不支持的类型和只读字段）
        UNSUPPORTED_CREATE_TYPES = {31, 32}  # 不能通过 documentBlockChildren.create API 创建的类型
        skipped_types = []
        cleaned_blocks = []
        
        for block in new_blocks:
            block_type = getattr(block, 'block_type', None)
            if block_type in UNSUPPORTED_CREATE_TYPES:
                skipped_types.append(f"type_{block_type}")
                continue
            
            if hasattr(block, 'block_id'):
                block.block_id = None
            
            if hasattr(block, 'table') and block.table:
                if hasattr(block.table, 'merge_info'):
                    block.table.merge_info = None
            
            cleaned_blocks.append(block)
        
        if skipped_types and self._logger:
            self._logger.warning(f"跳过了不支持的 block 类型: {set(skipped_types)}")
        
        new_blocks = cleaned_blocks

        # 7. 插入 Blocks 到文档（使用 /children 接口，children 最大 50 个，需分批）
        from lark_oapi.api.docx.v1 import CreateDocumentBlockChildrenRequest, CreateDocumentBlockChildrenRequestBody
        
        user_token = self._get_user_access_token()
        batch_size = 50
        total_blocks = len(new_blocks)
        
        for i in range(0, total_blocks, batch_size):
            batch = new_blocks[i:i + batch_size]
            create_req = CreateDocumentBlockChildrenRequest.builder() \
                .document_id(document_id) \
                .block_id(document_id) \
                .request_body(CreateDocumentBlockChildrenRequestBody.builder()
                    .children(batch)
                    .index(-1)
                    .build()) \
                .build()

            if user_token:
                create_resp = client.docx.v1.document_block_children.create(create_req, lark.RequestOption.builder().user_access_token(user_token).build())
            else:
                create_resp = client.docx.v1.document_block_children.create(create_req)

            if not create_resp.success():
                if self._logger:
                    self._logger.error(f"写入新内容失败（批次 {i // batch_size + 1}/{(total_blocks + batch_size - 1) // batch_size}）: {create_resp.msg}")
                return None

        return json.dumps({"document_id": document_id}, ensure_ascii=False)

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
        """处理 Base 记录搜索（兼容 lark-cli 格式）
        
        SDK 层自动处理分页，使用 page_token 循环获取所有数据，一次性返回。
        """
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')
        search_json_str = self._kwargs.get('search_json', '{}')

        try:
            search_json = json.loads(search_json_str)
        except json.JSONDecodeError:
            search_json = {}

        # 将旧格式参数转换为官方 API 格式
        # 旧格式: {keyword, search_fields, select_fields, limit, offset}
        # 新格式: {field_names, filter, sort, view_id, automatic_fields} + URL参数 page_size, page_token
        
        # 构建请求体
        body = {}
        
        # select_fields -> field_names
        select_fields = search_json.get('select_fields', [])
        if select_fields:
            body['field_names'] = select_fields
        
        # keyword + search_fields -> filter
        keyword = search_json.get('keyword')
        search_fields = search_json.get('search_fields', [])
        if keyword and search_fields:
            conditions = []
            for field in search_fields:
                conditions.append({
                    'field_name': field,
                    'operator': 'is',
                    'value': [keyword]
                })
            body['filter'] = {
                'conditions': conditions,
                'conjunction': 'or'
            }
        
        # limit -> page_size (通过 URL 参数传递)
        page_size = search_json.get('limit', 20)
        
        # 获取 offset 参数
        offset = search_json.get('offset', 0)
        
        # 获取 select_fields 参数（用于返回 fields 字段）
        select_fields = search_json.get('select_fields', [])
        
        # 如果 offset > 0，说明是第二次及以后的请求
        # 由于 SDK 层已经在第一次请求时返回了所有数据，这里直接返回空结果
        if offset > 0:
            return json.dumps({
                'data': {
                    'data': [],
                    'record_id_list': [],
                    'field_id_list': [],
                    'fields': select_fields,
                    'has_more': False
                }
            }, ensure_ascii=False)
        
        # SDK 层自动分页：使用 page_token 循环获取所有数据
        all_record_id_list = []
        all_field_id_list = []
        all_items = []
        page_token = None
        max_pages = 50  # 防止无限循环，最多请求 50 页
        
        for page_num in range(max_pages):
            request_builder = SearchAppTableRecordRequest.builder()\
                .app_token(base_token)\
                .table_id(table_id)\
                .page_size(page_size)
            
            if page_token:
                request_builder.page_token(page_token)
            
            request = request_builder.build()
            request.body = body

            response = client.bitable.v1.app_table_record.search(request)

            if not response.success():
                if self._logger:
                    self._logger.error(f"Base 记录搜索失败: {response.msg}")
                return None

            # 第一页收集字段列表
            if page_num == 0 and hasattr(response.data, 'items') and response.data.items:
                if response.data.items:
                    first_record = response.data.items[0]
                    fields = getattr(first_record, 'fields', {})
                    all_field_id_list = list(fields.keys())

            # 收集记录
            if hasattr(response.data, 'items') and response.data.items:
                for record in response.data.items:
                    all_record_id_list.append(record.record_id)
                    fields = getattr(record, 'fields', {})
                    # 提取字段值，处理嵌套结构
                    item_values = [self._extract_field_value(fields.get(fid)) for fid in all_field_id_list]
                    all_items.append(item_values)

            # 检查是否还有更多数据
            has_more = getattr(response.data, 'has_more', False)
            if not has_more:
                break
            
            # 获取下一页的 page_token
            page_token = getattr(response.data, 'page_token', None)
            if not page_token:
                break

        # 返回 lark-cli 兼容格式
        # 添加 has_more=False 防止外层循环继续请求
        # 注意：外层 data 是响应包装，内层 data 对应 lark-cli 返回的 items
        return json.dumps({
            'data': {
                'data': all_items,
                'record_id_list': all_record_id_list,
                'field_id_list': all_field_id_list,
                'fields': select_fields,
                'has_more': False
            }
        }, ensure_ascii=False)

    def _handle_base_record_delete(self, client) -> Optional[str]:
        """处理 Base 记录批量删除"""
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')
        delete_json_str = self._kwargs.get('delete_json', '{}')

        try:
            delete_json = json.loads(delete_json_str)
        except json.JSONDecodeError:
            delete_json = {}

        record_id_list = delete_json.get('record_id_list', [])
        
        if not record_id_list:
            return json.dumps([])

        request = BatchDeleteAppTableRecordRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .request_body(BatchDeleteAppTableRecordRequestBody.builder()
                .records(record_id_list)
                .build())\
            .build()

        response = client.bitable.v1.app_table_record.batch_delete(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"Base 记录批量删除失败: {response.msg}")
            return None

        deleted_ids = []
        if hasattr(response.data, 'records') and response.data.records:
            for record in response.data.records:
                deleted_ids.append(record.record_id)

        return json.dumps(deleted_ids, ensure_ascii=False)

    def _handle_base_record_batch_create(self, client) -> Optional[str]:
        """处理 Base 记录批量创建
        
        支持两种数据格式:
        1. 新格式: {"fields": ["f1", "f2"], "rows": [[v1, v2], [v3, v4], ...]}
        2. 旧格式: [{"f1": v1, "f2": v2}, {"f1": v3, "f2": v4}, ...]
        """
        base_token = self._kwargs.get('base_token')
        table_id = self._kwargs.get('table_id')
        data_json_str = self._kwargs.get('data_json', '[]')

        try:
            data_json = json.loads(data_json_str)
        except json.JSONDecodeError:
            data_json = []

        # 如果没有数据，直接返回空结果
        if not data_json:
            return json.dumps([])

        # 构建记录列表
        records = []
        
        # 判断数据格式
        if isinstance(data_json, dict) and 'fields' in data_json and 'rows' in data_json:
            # 新格式: {"fields": [...], "rows": [[...], [...]]}
            field_names = data_json['fields']
            rows = data_json['rows']
            
            # 获取字段类型信息（可选）
            field_types = data_json.get('field_types', {})
            
            for row in rows:
                fields = {}
                for i, field_name in enumerate(field_names):
                    if i < len(row):
                        # 根据字段类型处理日期转换
                        field_type = field_types.get(field_name, '')
                        fields[field_name] = self._convert_value_by_type(row[i], field_type)
                records.append(AppTableRecord.builder().fields(fields).build())
        else:
            # 旧格式: [{"field": value}, ...]
            for item in data_json:
                if isinstance(item, dict):
                    # 处理日期字段：转换为 Unix 时间戳（毫秒）
                    converted_item = {k: self._convert_date_to_timestamp(v) for k, v in item.items()}
                    records.append(AppTableRecord.builder().fields(converted_item).build())

        if not records:
            return json.dumps([])

        # 使用官方 SDK 方式构建请求
        request = BatchCreateAppTableRecordRequest.builder()\
            .app_token(base_token)\
            .table_id(table_id)\
            .request_body(BatchCreateAppTableRecordRequestBody.builder()
                .records(records)
                .build())\
            .build()

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
            response = client.im.v1.message.create(request, lark.RequestOption.builder().user_access_token(user_token).build())
        else:
            response = client.im.v1.message.create(request)

        if not response.success():
            if self._logger:
                self._logger.error(f"消息发送失败: {response.msg}")
            return None

        return getattr(response.data, 'message_id', None)

    def _apply_query(self, data: dict, query: str) -> Optional[Any]:
        """应用 jq 查询表达式"""
        if not query or query == '{query}':
            return data

        try:
            compiled = jq.compile(query)
            result = compiled.input(data).all()
            
            # 判断查询是否是数组查询（是否有方括号包裹）
            is_array_query = query.strip().startswith('[') and query.strip().endswith(']')
            
            # 如果是数组查询，保持数组格式
            if is_array_query:
                if len(result) == 1 and isinstance(result[0], list):
                    return json.dumps(result[0] , ensure_ascii=False) if result is not None else None
                return json.dumps(result[0] , ensure_ascii=False) if result is not None else None
            
            # 如果不是数组查询，单个结果返回单值
            if len(result) == 1:
                return result[0]
            
            return result
        except Exception as e:
            if self._logger:
                self._logger.error(f"jq 查询执行失败: {e}")
            return None

    def _filter_nodes(self, nodes: list, condition: str) -> list:
        """兼容旧接口：根据条件过滤节点"""
        return nodes

    def _match_condition(self, node: dict, condition: str) -> bool:
        """兼容旧接口：匹配单个节点的条件"""
        return True


class LarkCmd:
    """飞书 SDK 命令模板（静态工厂）"""

    WIKI_NODE_LIST = LarkSdkCommand('wiki', 'node_list',use_user_access_token=True)
    WIKI_NODE_LIST_BY_PARENT = LarkSdkCommand('wiki', 'node_list_by_parent',use_user_access_token=True)
    WIKI_NODE_SEARCH_BITABLE = LarkSdkCommand('wiki', 'node_list',use_user_access_token=True)
    WIKI_NODE_CREATE = LarkSdkCommand('wiki', 'node_create',use_user_access_token=True)
    WIKI_NODE_CREATE_WITH_PARENT = LarkSdkCommand('wiki', 'node_create_with_parent',use_user_access_token=True)
    WIKI_NODE_MOVE = LarkSdkCommand('wiki', 'node_move',use_user_access_token=True)

    DOC_UPDATE = LarkSdkCommand('docs', 'doc_update',use_user_access_token=True)

    BASE_CREATE = LarkSdkCommand('base', 'base_create')
    BASE_TABLE_LIST = LarkSdkCommand('base', 'table_list')
    BASE_TABLE_CREATE = LarkSdkCommand('base', 'table_create')
    BASE_FIELD_LIST = LarkSdkCommand('base', 'field_list')
    BASE_FIELD_CREATE = LarkSdkCommand('base', 'field_create')
    BASE_RECORD_SEARCH = LarkSdkCommand('base', 'record_search')
    BASE_RECORD_DELETE = LarkSdkCommand('base', 'record_delete')
    BASE_RECORD_BATCH_CREATE = LarkSdkCommand('base', 'record_batch_create')

    IM_MESSAGE_SEND = LarkSdkCommand('im', 'message_send')
