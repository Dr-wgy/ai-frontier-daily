# 项目技术规范文档

> **文档版本**: 1.0  
> **创建日期**: 2026-05-26  
> **适用项目**: ai-frontier-daily

---

## 一、文档目的

本文档基于 Lark SDK 替换 lark-cli 的实际开发经验，总结技术规范和最佳实践，作为团队后续开发的参考标准。

---

## 二、核心经验总结

### 经验 1：入参和出参兼容性核对

#### 2.1 重要性

Lark SDK 和 lark-cli 在数据格式上存在差异，必须确保调用方（lark-cli）传入的参数能正确转换为 SDK 要求的格式，同时 SDK 返回的结果要转换回调用方期望的格式。

#### 2.2 常见差异类型

**请求参数差异**：

| 差异类型 | lark-cli | Python SDK | 处理方式 |
|---------|----------|------------|----------|
| 日期格式 | 字符串 `'2026-05-26'` | Unix 时间戳（毫秒） | 转换函数 |
| 布尔值 | `'true'` / `'false'` | `True` / `False` | 类型转换 |
| 数组格式 | JSON 字符串 | Python List | JSON 解析 |
| 字段类型 | 字段名 | 字段 ID | 映射转换 |

**响应格式差异**：

| 差异类型 | lark-cli 返回 | SDK 返回 | 处理方式 |
|---------|--------------|----------|----------|
| 记录数据 | `[['val1', 'val2']]` | `[{record_id, fields}]` | 结构转换 |
| 嵌套结构 | `[[{'text': 'val'}]]` | 多层嵌套 | 扁平化处理 |
| 分页方式 | `offset` / `limit` | `page_token` | SDK 层自动处理 |

#### 2.3 兼容性检查清单

```
□ 列出所有 API 调用
□ 对比 lark-cli 和 SDK 的请求参数格式
□ 对比 lark-cli 和 SDK 的响应数据格式
□ 设计参数转换函数
□ 设计响应转换函数
□ 编写单元测试验证转换逻辑
□ 编写集成测试验证端到端流程
```

---

### 经验 2：严格遵循官方文档

#### 2.1 禁止自由发挥

本次开发中存在过度"自由发挥"的情况，导致后期频繁返工。

**反面案例**：

```python
# ❌ 错误：自行设计 filter 格式
filter = {
    "keyword": "2026-05-26",
    "search_fields": ["date_field"],
    "operator": "contains"
}

# ✅ 正确：严格遵循飞书 API 文档
filter = {
    "conditions": [
        {
            "field_name": "date_field",
            "operator": "is",
            "value": ["2026-05-26"]
        }
    ],
    "conjunction": "or"
}
```

#### 2.2 正确做法

**步骤 1：阅读 API 文档**
- 飞书开放平台 API 文档：`https://open.feishu.cn/document/`
- 关注请求参数、响应格式、错误码

**步骤 2：阅读 SDK 文档**
- SDK 使用说明：`https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/`
- 关注 SDK 的请求构建方式和数据模型

**步骤 3：参考官方示例**
- SDK Demo 代码
- API 调试台的示例

**步骤 4：实现并验证**
- 严格按照文档实现
- 用测试用例验证

#### 2.3 文档对照表

| 文档类型 | 用途 | 示例 |
|---------|------|------|
| API 文档 | 了解接口功能、参数、返回值 | `SearchAppTableRecord` |
| SDK 文档 | 了解 SDK 的使用方式 | `BatchCreateAppTableRecordRequest` |
| 类型定义 | 了解数据结构 | `AppTableRecord`, `AppTableRecordRequestBody` |

---

### 经验 3：自动化测试

#### 3.1 测试分层

```
┌─────────────────────────────────────────────┐
│           集成测试 (Integration Test)         │
│  - 端到端测试真实 API                        │
│  - 验证完整业务流程                           │
├─────────────────────────────────────────────┤
│           单元测试 (Unit Test)               │
│  - Mock SDK 调用                             │
│  - 测试参数转换逻辑                          │
│  - 测试响应转换逻辑                          │
│  - 测试边界条件                              │
└─────────────────────────────────────────────┘
```

#### 3.2 单元测试规范

**测试文件命名**：
```
test_<模块名>_<功能名>.py
```

**示例**：
```
test_base_record_search_fix.py    # Base 记录搜索修复
test_lark_sdk_commander.py        # SDK 命令器
```

**测试用例结构**：
```python
def test_xxx():
    """测试描述"""
    # Arrange: 准备测试数据和 Mock
    mock_response = create_mock_response()
    
    # Act: 执行被测方法
    result = method_under_test()
    
    # Assert: 验证结果
    assert result == expected_value
```

**必须测试的场景**：
- [ ] 正常流程
- [ ] 边界条件（空值、最大值）
- [ ] 错误处理
- [ ] 类型转换
- [ ] 数据格式转换

#### 3.3 集成测试规范

**测试环境要求**：
- 使用测试应用/测试环境
- 不要在生产环境测试
- 准备测试数据（测试前创建，测试后清理）

**集成测试示例**：
```python
def test_real_api_call():
    """集成测试：调用真实 API"""
    # 跳过标记（避免 CI 失败时阻塞）
    if not os.getenv('RUN_INTEGRATION_TEST'):
        pytest.skip("Integration test skipped")
    
    # 真实 API 调用
    result = real_api_call()
    
    # 验证
    assert result is not None
```

#### 3.4 测试覆盖率要求

| 模块类型 | 最低覆盖率 |
|---------|-----------|
| 核心业务逻辑 | 90% |
| 数据转换逻辑 | 100% |
| API 调用封装 | 80% |

---

## 三、开发流程规范

### 流程 1：API 替换开发

```
1. 需求分析
   ├─ 列出需要替换的 API
   ├─ 对比 lark-cli 和 SDK 的差异
   └─ 设计转换方案

2. 文档准备
   ├─ 阅读飞书 API 文档
   ├─ 阅读 SDK 文档
   └─ 整理参数映射表

3. 编码实现
   ├─ 实现请求参数转换
   ├─ 实现响应数据转换
   └─ 保持接口兼容性

4. 测试验证
   ├─ 编写单元测试
   ├─ 验证参数转换
   ├─ 验证响应转换
   └─ 编写集成测试

5. 代码审查
   ├─ 检查是否符合文档
   ├─ 检查测试覆盖
   └─ 检查错误处理
```

### 流程 2：测试驱动开发（推荐）

```
1. 编写测试用例
   ├─ 定义期望的输入
   └─ 定义期望的输出

2. 实现功能
   ├─ 按照文档实现
   └─ 通过测试用例

3. 重构优化
   ├─ 优化代码结构
   └─ 确保测试通过
```

---

## 四、数据格式转换规范

### 4.1 请求参数转换

**原则**：
- 将调用方格式转换为 SDK 格式
- 在 SDK 封装层完成转换
- 调用方代码无需修改

**示例**：

```python
class LarkSdkCommander:
    def _convert_request_params(self, params, api_type):
        """将 lark-cli 格式转换为 SDK 格式"""
        if api_type == 'BASE_RECORD_SEARCH':
            return self._convert_search_params(params)
        elif api_type == 'BASE_RECORD_BATCH_CREATE':
            return self._convert_create_params(params)
        # ... 其他 API
    
    def _convert_search_params(self, params):
        """搜索参数转换"""
        return {
            'field_names': params.get('select_fields', []),
            'filter': self._build_filter(params),
            'page_size': params.get('limit', 100),
            'page_token': params.get('page_token')
        }
    
    def _build_filter(self, params):
        """构建 filter 条件（严格遵循 API 文档）"""
        conditions = []
        for field_name in params.get('search_fields', []):
            conditions.append({
                'field_name': field_name,
                'operator': 'is',  # 必须使用文档中的操作符
                'value': [params.get('keyword', '')]
            })
        
        return {
            'conditions': conditions,
            'conjunction': params.get('conjunction', 'or')
        }
```

### 4.2 响应数据转换

**原则**：
- 将 SDK 格式转换为调用方格式
- 在 SDK 封装层完成转换
- 返回与 lark-cli 一致的数据结构

**示例**：

```python
def _convert_response(self, response, api_type):
    """将 SDK 响应转换为 lark-cli 格式"""
    if api_type == 'BASE_RECORD_SEARCH':
        return self._convert_search_response(response)
    # ... 其他 API

def _convert_search_response(self, response):
    """搜索响应转换"""
    if not hasattr(response.data, 'items'):
        return json.dumps({'data': []})
    
    items = []
    record_ids = []
    
    for record in response.data.items:
        record_ids.append(record.record_id)
        # 处理嵌套结构
        fields = self._flatten_fields(record.fields)
        items.append(list(fields.values()))
    
    return json.dumps({
        'data': {
            'record_id_list': record_ids,
            'field_id_list': list(record.fields.keys()) if record.fields else [],
            'data': items
        }
    })

def _flatten_fields(self, fields):
    """扁平化嵌套的字段值"""
    result = {}
    for field_id, value in fields.items():
        result[field_id] = self._extract_simple_value(value)
    return result

def _extract_simple_value(self, value):
    """提取简单值，处理嵌套结构"""
    if value is None:
        return None
    
    # 处理 [[{...}]] 格式
    if isinstance(value, list) and len(value) > 0:
        if isinstance(value[0], list) and len(value[0]) > 0:
            if isinstance(value[0][0], dict) and 'text' in value[0][0]:
                return value[0][0]['text']
        # 处理 [{...}] 格式
        elif isinstance(value[0], dict) and 'text' in value[0]:
            return value[0]['text']
    
    return value
```

---

## 五、字段类型处理规范

### 5.1 日期字段

**问题**：飞书 API 要求日期字段为 Unix 时间戳（毫秒），但调用方通常传入字符串格式。

**处理方式**：

```python
def _convert_value_by_type(self, value, field_type):
    """根据字段类型转换值"""
    if value is None:
        return None
    
    # 日期类型转换
    if field_type and field_type.lower() in ('date', 'datetime'):
        return self._convert_date_to_timestamp(value)
    
    return value

def _convert_date_to_timestamp(self, value):
    """日期字符串转换为 Unix 时间戳（毫秒）"""
    if isinstance(value, int):
        return value  # 已是时间戳
    
    if isinstance(value, str):
        # 解析日期字符串
        patterns = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d'
        ]
        for pattern in patterns:
            try:
                dt = datetime.strptime(value, pattern)
                return int(dt.timestamp() * 1000)
            except ValueError:
                continue
    
    return value
```

### 5.2 其他类型转换

| 字段类型 | 输入格式 | 输出格式 | 说明 |
|---------|---------|---------|------|
| 日期 | `'2026-05-26'` | `1779724800000` | 转换为时间戳 |
| 数字 | `'123'` | `123` | 类型转换 |
| 布尔 | `'true'` | `True` | 字符串转布尔 |
| 数组 | `'["a", "b"]'` | `['a', 'b']` | JSON 解析 |

---

## 六、错误处理规范

### 6.1 错误分类

| 错误类型 | 处理方式 | 示例 |
|---------|---------|------|
| SDK 调用失败 | 记录日志，返回 None | 网络超时 |
| 参数校验失败 | 抛出异常 | 缺少必需参数 |
| API 返回错误 | 转换错误信息 | 权限不足 |
| Token 过期 | 自动刷新 | 401 Unauthorized |

### 6.2 错误处理示例

```python
def _handle_sdk_error(self, response, operation):
    """处理 SDK 错误"""
    if not response.success():
        error_msg = f"{operation} 失败: {response.code} - {response.msg}"
        
        if self._logger:
            self._logger.error(error_msg)
        
        # Token 过期处理
        if response.code == 401:
            self._handle_token_expired()
        
        return None
    
    return response.data

def _handle_token_expired(self):
    """处理 Token 过期"""
    if self._refresh_token:
        self._refresh_user_token()
    else:
        raise AuthError("Token 已过期，请重新授权")
```

---

## 七、日志规范

### 7.1 日志级别使用

| 级别 | 使用场景 |
|------|---------|
| DEBUG | 详细的调试信息（参数、返回值） |
| INFO | 正常的业务流程信息 |
| WARNING | 警告信息（可恢复的错误） |
| ERROR | 错误信息（需要处理） |

### 7.2 日志格式

```python
# 结构化日志
self._logger.info(f"Base 记录搜索成功，返回 {len(items)} 条记录")

# 带参数的日志
self._logger.debug(f"请求参数: {params}")

# 带上下文的日志
self._logger.error(f"API 调用失败", extra={'api': 'search', 'code': response.code})
```

---

## 八、文档编写规范

### 8.1 必须包含的内容

**API 文档**：
- 接口功能描述
- 请求参数说明
- 响应数据格式
- 错误码说明
- 使用示例

**代码注释**：
- 函数功能说明
- 参数和返回值类型
- 注意事项
- 示例代码

### 8.2 文档更新要求

| 变更类型 | 更新范围 |
|---------|---------|
| 新增 API | 文档 + 测试用例 |
| 参数变更 | 文档 + 调用方代码 |
| 返回格式变更 | 文档 + 测试用例 |
| Bug 修复 | 测试用例 + CHANGELOG |

---

## 九、CI/CD 集成

### 9.1 测试自动化

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run unit tests
        run: pytest project-space/tests/ -v --cov=project-space/utils
      
      - name: Run integration tests
        run: pytest project-space/tests/ -v -k integration --cov-report=xml
        env:
          RUN_INTEGRATION_TEST: true
```

### 9.2 测试环境配置

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest -m "not integration"

# 运行集成测试
pytest -m integration -v

# 生成覆盖率报告
pytest --cov=project-space/utils --cov-report=html
```

---

## 十、常见问题自查清单

### 开发前检查

```
□ 是否阅读了飞书 API 文档？
□ 是否阅读了 SDK 文档？
□ 是否对比了 lark-cli 和 SDK 的参数差异？
□ 是否设计了参数转换方案？
□ 是否设计了响应转换方案？
□ 是否准备了测试用例？
```

### 开发中检查

```
□ 是否严格按照文档实现？
□ 是否有"自由发挥"的地方？
□ 是否处理了所有字段类型？
□ 是否有硬编码？
□ 是否有 TODO 或 FIXME？
□ 测试用例是否通过？
```

### 开发后检查

```
□ 代码是否符合规范？
□ 单元测试覆盖率是否达标？
□ 集成测试是否通过？
□ 文档是否更新？
□ 是否有性能问题？
□ 错误处理是否完善？
```

---

## 十一、相关文档

| 文档 | 说明 |
|------|------|
| [飞书开放平台 API 文档](https://open.feishu.cn/document/) | 官方 API 文档 |
| [飞书 SDK 文档](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/) | Python SDK 文档 |
| [OAuth 配置指南](file:///Users/guanyu.wu/IdeaProjects/ai-frontier-daily/project-space/docs/oauth-setup-guide.md) | OAuth 授权配置 |
| [Lark SDK 迁移指南](file:///Users/guanyu.wu/IdeaProjects/ai-frontier-daily/docs/migration-guide-lark-sdk.md) | SDK 迁移经验 |

---

**维护人**: 开发团队  
**下次审查时间**: 每季度审查一次  
**版本历史**:  
- v1.0 (2026-05-26): 初始版本
