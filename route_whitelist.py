"""
Nekro User Panel - 路由白名单
定义用户端面板允许代理的 API 路径。
不在白名单中的请求一律返回 403。
"""

import re
from typing import List, Tuple

from config import CHANNEL_OVERRIDE_BLOCKED

# ============ 白名单规则 ============
# 格式: (HTTP方法, 路径正则)
# 方法可以是 "*" 表示匹配所有方法

ALLOWED_ROUTES: List[Tuple[str, str]] = [
    # ============ 健康检查 ============
    ("GET", r"^/api/health$"),

    # ============ 认证（NA 原生 token 接口，用于网关内部） ============
    ("POST", r"^/api/token$"),
    ("POST", r"^/api/user/login$"),
    ("GET", r"^/api/user/me$"),
    ("GET", r"^/api/user/info$"),

    # ============ 频道管理 ============
    ("GET", r"^/api/chat-channel/list$"),
    ("GET", r"^/api/chat-channel/list/stream$"),
    ("GET", r"^/api/chat-channel/directory$"),
    ("GET", r"^/api/chat-channel/detail/[^/]+$"),
    ("POST", r"^/api/chat-channel/[^/]+/active$"),
    ("POST", r"^/api/chat-channel/[^/]+/status$"),
    ("POST", r"^/api/chat-channel/[^/]+/reset$"),
    ("GET", r"^/api/chat-channel/[^/]+/messages$"),
    ("POST", r"^/api/chat-channel/[^/]+/preset$"),
    ("GET", r"^/api/chat-channel/[^/]+/users$"),
    ("POST", r"^/api/chat-channel/[^/]+/poke$"),
    ("POST", r"^/api/chat-channel/[^/]+/send$"),
    ("GET", r"^/api/chat-channel/[^/]+/stream$"),
    ("GET", r"^/api/chat-channel/[^/]+/plugin-data$"),
    ("PUT", r"^/api/chat-channel/[^/]+/plugin-data/\d+$"),
    ("DELETE", r"^/api/chat-channel/[^/]+/plugin-data/\d+$"),
    ("POST", r"^/api/chat-channel/announcement/send$"),
    ("GET", r"^/api/chat-channel/[^/]+/delete-preview$"),
    ("DELETE", r"^/api/chat-channel/[^/]+$"),

    # ============ 用户管理（完整） ============
    ("GET", r"^/api/user-manager/list$"),
    ("GET", r"^/api/user-manager/\d+$"),
    ("POST", r"^/api/user-manager/create$"),
    ("PUT", r"^/api/user-manager/\d+$"),
    ("POST", r"^/api/user-manager/\d+/ban$"),
    ("POST", r"^/api/user-manager/\d+/prevent-trigger$"),
    ("POST", r"^/api/user-manager/\d+/reset-password$"),
    ("DELETE", r"^/api/user-manager/\d+$"),

    # ============ 人设管理（完整） ============
    ("GET", r"^/api/presets/tags$"),
    ("GET", r"^/api/presets/list$"),
    ("GET", r"^/api/presets/\d+$"),
    ("GET", r"^/api/presets/by-remote/[^/]+$"),
    ("POST", r"^/api/presets$"),
    ("PUT", r"^/api/presets/\d+$"),
    ("DELETE", r"^/api/presets/\d+$"),
    ("POST", r"^/api/presets/\d+/sync$"),
    ("POST", r"^/api/presets/upload-avatar$"),
    ("POST", r"^/api/presets/\d+/share$"),
    ("POST", r"^/api/presets/\d+/unshare$"),
    ("POST", r"^/api/presets/\d+/sync-to-cloud$"),
    ("POST", r"^/api/presets/refresh-shared-status$"),

    # ============ 系统日志 ============
    ("GET", r"^/api/logs$"),
    ("GET", r"^/api/logs/sources$"),
    ("GET", r"^/api/logs/stream$"),
    ("GET", r"^/api/logs/download$"),

    # ============ 沙盒日志 ============
    ("GET", r"^/api/sandbox/logs$"),
    ("GET", r"^/api/sandbox/log-content$"),
    ("GET", r"^/api/sandbox/models$"),
    ("GET", r"^/api/sandbox/stats$"),

    # ============ 系统配置 - 基本配置（模型配置界面） ============
    ("GET", r"^/api/config/keys$"),
    ("GET", r"^/api/config/info/[^/]+$"),
    ("GET", r"^/api/config/list/system$"),
    ("GET", r"^/api/config/get/system/[^/]+$"),
    ("POST", r"^/api/config/set/system/[^/]+$"),
    ("POST", r"^/api/config/batch/system$"),
    ("POST", r"^/api/config/save/system$"),
    ("GET", r"^/api/config/list/basic_config$"),
    ("GET", r"^/api/config/get/basic_config/[^/]+$"),
    ("POST", r"^/api/config/set/basic_config/[^/]+$"),
    ("POST", r"^/api/config/batch/basic_config$"),
    ("POST", r"^/api/config/save/basic_config$"),

    # ============ 模型管理（分组过滤在 filters.py 中处理） ============
    ("GET", r"^/api/config/model-groups$"),
    ("POST", r"^/api/config/model-groups/[^/]+$"),
    ("DELETE", r"^/api/config/model-groups/[^/]+$"),
    ("GET", r"^/api/config/model-types$"),
    ("POST", r"^/api/config/model-groups/actions/fetch-models$"),
    ("POST", r"^/api/config/model-groups/actions/test$"),
    ("POST", r"^/api/config/model-groups/actions/test-inline$"),

    # ============ 插件管理（开放数据管理与非敏感配置项） ============
    ("GET", r"^/api/plugins/list$"),
    ("GET", r"^/api/plugins/detail/[^/]+$"),
    ("GET", r"^/api/plugins/docs/[^/]+$"),
    ("POST", r"^/api/plugins/toggle/[^/]+$"),
    ("POST", r"^/api/plugins/activation-strategy/[^/]+$"),
    ("POST", r"^/api/plugins/reload$"),
    ("GET", r"^/api/plugins/data/[^/]+$"),
    ("DELETE", r"^/api/plugins/data/[^/]+$"),
    ("DELETE", r"^/api/plugins/data/[^/]+/[^/]+$"),
    ("DELETE", r"^/api/plugins/package/[^/]+$"),
    ("POST", r"^/api/plugins/package/update/[^/]+$"),
    ("GET", r"^/api/config/list/plugin_[^/]+$"),
    ("GET", r"^/api/config/get/plugin_[^/]+/[^/]+$"),
    ("POST", r"^/api/config/set/plugin_[^/]+/[^/]+$"),
    ("POST", r"^/api/config/batch/plugin_[^/]+$"),
    ("POST", r"^/api/config/save/plugin_[^/]+$"),

    # ============ 版本信息 ============
    ("GET", r"^/api/config/version$"),

    # ============ 空间回收（只读缓存状态） ============
    ("GET", r"^/api/space-cleanup/scan/load-cache$"),

    # ============ 事件流 ============
    ("GET", r"^/api/events/stream$"),

    # ============ 云端（只读） ============
    ("GET", r"^/api/cloud/.*"),

    # ============ 通用资源（头像等） ============
    ("GET", r"^/api/resources/.*"),

    # ============ 仪表盘 ============
    ("GET", r"^/api/dashboard/.*"),

    # ============ 前端静态文件 ============
    ("GET", r"^/webui(/.*)?$"),
]

# ============ 黑名单规则（优先级高于白名单） ============
# 即使白名单匹配了，如果命中黑名单也会被拒绝

BLOCKED_ROUTES: List[Tuple[str, str]] = []

# 插件编辑器允许直接读取/修改插件源码，普通用户端绝不开放。
# 插件配置接口已在 proxy.py/filters.py 中按配置键过滤，仅开放非敏感项。
BLOCKED_ROUTES.extend([
    ("*", r"^/api/plugin-editor(/.*)?$"),
])

if CHANNEL_OVERRIDE_BLOCKED:
    BLOCKED_ROUTES.extend([
        # 频道覆盖配置相关（通过适配器的 override config 实现）
        ("*", r"^/api/chat-channel/[^/]+/override"),
    ])


# ============ 编译正则（性能优化） ============

_compiled_allowed: List[Tuple[str, re.Pattern]] = [
    (method, re.compile(pattern)) for method, pattern in ALLOWED_ROUTES
]

_compiled_blocked: List[Tuple[str, re.Pattern]] = [
    (method, re.compile(pattern)) for method, pattern in BLOCKED_ROUTES
]


def is_route_allowed(method: str, path: str) -> bool:
    """
    检查请求是否被允许通过。
    先检查黑名单（命中则拒绝），再检查白名单（命中则放行）。
    """
    method = method.upper()

    # 先检查黑名单
    for blocked_method, pattern in _compiled_blocked:
        if (blocked_method == "*" or blocked_method == method) and pattern.match(path):
            return False

    # 再检查白名单
    for allowed_method, pattern in _compiled_allowed:
        if (allowed_method == "*" or allowed_method == method) and pattern.match(path):
            return True

    return False

