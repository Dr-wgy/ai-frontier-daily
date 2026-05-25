# 飞书 Token 自动刷新实现方案 (Implementation Plan)

日期: 2026-05-24
状态: 待实现

## 1. 变更范围概览
本次变更将涉及 `LarkClient` 类（负责 SDK 初始化和 Token 管理）的逻辑升级，以及对配置文件 `secrets.json` 读写方式的调整。

## 2. 详细变更点

### 2.1 授权初始化流程 (Plan B: Initial Authorization)
新增“授权助手”逻辑，用于获取“第一桶金”：
1. **生成 URL**: `LarkClient().get_auth_url()` 生成飞书授权页面的链接。
   - 权限集（Scope）必须包含 `offline_access` 以获取 `refresh_token`。
2. **换取 Token**: `LarkClient().init_with_code(code)` 将用户粘贴的 `code` 换取为完整的 Token 对并持久化。

### 2.2 配置文件变更 (`config/secrets.json`)
由代码自动维护，新增两个字段：
- `refresh_token`: 刷新令牌（有效期通常为 30 天）。
- `expires_at`: Token 过期的绝对时间戳（秒），用于主动判断是否需要刷新。

### 2.3 代码变更 (`project-space/utils/lark_sdk_commander.py`)

#### A. 增加导入
```python
import time
from lark_oapi.api.authen.v1 import (
    CreateAccessTokenRequest,
    CreateAccessTokenRequestBody,
    RefreshAccessTokenRequest,
    RefreshAccessTokenRequestBody,
)
```

#### B. LarkClient 类成员变量扩展
- `_refresh_token`: 存储当前有效的刷新令牌。
- `_expires_at`: 存储过期时间戳。

#### C. LarkClient 逻辑方法升级
1.  **`_load_config()`**: 初始化时增加对 `refresh_token` 和 `expires_at` 的读取。
2.  **`get_user_access_token()` (新方法)**: 
    - 替代直接访问属性。
    - **逻辑**: 如果 `当前时间 + 5分钟 > expires_at` 且存在 `refresh_token`，自动调用刷新逻辑。
3.  **`check_and_refresh_token()` (新内部方法)**:
    - 调用 `client.authen.v1.refresh_access_token.create`。
    - 刷新成功后，同时更新内存中的 `_user_access_token`、`_refresh_token` 和 `_expires_at`。
4.  **`_save_token_to_config()` (重构)**:
    - 将上述三个 Token 状态完整回写到磁盘，确保 `refresh_token` 始终是最新的。
5. **`get_auth_url()` (新方法)**: 生成跳转链接。
6. **`init_with_code(code)` (新方法)**: 首次使用 code 激活。

#### D. `LarkSdkCommand` 逻辑调整
- 修改 `_get_user_access_token()` 方法，使其调用 `LarkClient().get_user_access_token()` 而非直接取值，从而触发自动刷新检测。

## 3. 风险点与对策

| 风险点 | 对策 |
| :--- | :--- |
| **`refresh_token` 也过期了** (30天未用) | SDK 会报错，代码将捕获此错误并打印“请重新手动授权”的明确提示，不影响程序崩溃。 |
| **刷新时网络波动导致失败** | 打印错误日志，本次调用可能失败，但保留旧 Token 状态，下次运行会再次尝试刷新。 |
| **并发刷新** | 目前主要是 CLI 单进程使用，风险较小。后续如有需要可考虑加文件锁。 |
| **代码逻辑 Bug 导致 secrets.json 损坏** | 读写 `secrets.json` 时采用先读后写的安全模式，并在写入前进行 JSON 校验。 |

## 4. 验证计划
1.  **手动修改时间戳**: 将 `secrets.json` 中的 `expires_at` 改为一个过去的数值，运行集成测试，观察是否触发“正在刷新...”的日志。
2.  **检查文件回写**: 验证刷新后，`secrets.json` 中的 `refresh_token` 和 `user_access_token` 是否已变成新值。
