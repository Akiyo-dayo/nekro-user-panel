"""
Nekro User Panel - 响应过滤器
对 NA 后端返回的数据进行过滤，隐藏敏感信息。
"""

import copy
from typing import Any, Dict, List, Optional


SENSITIVE_MODEL_FIELDS = {
    "API_KEY",
    "api_key",
    "SECRET",
    "secret",
    "PASSWORD",
    "password",
    "TOKEN",
    "token",
}

SENSITIVE_KEYWORDS = (
    "KEY",
    "SECRET",
    "PASSWORD",
    "TOKEN",
    "API_KEY",
    "ACCESS_KEY",
    "PRIVATE",
    "CREDENTIAL",
)

# 允许普通用户在"基本配置"里看到/修改的 system 配置项（模型配置 + 聊天配置）。
# 基于 NA 后端 i18n_category 的实际字段列表。
ALLOWED_SYSTEM_CONFIG_KEYS = {
    # 模型配置
    "USE_MODEL_GROUP",
    "DEBUG_MIGRATION_MODEL_GROUP",
    "FALLBACK_MODEL_GROUP",
    "AI_SCRIPT_MAX_RETRY_TIMES",
    "AI_CHAT_LLM_API_MAX_RETRIES",
    "AI_GENERATE_TIMEOUT",
    "AI_REQUEST_STREAM_MODE",
    "AI_STREAM_FIRST_TOKEN_TIMEOUT",
    "PLUGIN_GENERATE_MODEL_GROUP",
    "PLUGIN_APPLY_MODEL_GROUP",
    "SYSTEM_LANG",
    # 聊天配置
    "AI_CHAT_DEFAULT_PRESET_ID",
    "AI_CHAT_PRESET_NAME",
    "AI_CHAT_PRESET_SETTING",
    "AI_CHAT_CONTEXT_EXPIRE_SECONDS",
    "AI_CHAT_CONTEXT_MAX_LENGTH",
    "AI_DEBOUNCE_WAIT_SECONDS",
    "AI_IGNORED_PREFIXES",
    "AI_COMMAND_OUTPUT_PREFIX",
    "AI_CHAT_RANDOM_REPLY_PROBABILITY",
    "AI_CHAT_TRIGGER_REGEX",
    "AI_CHAT_IGNORE_REGEX",
    "AI_RESPONSE_PRE_DROP_REGEX",
    "AI_CONTEXT_LENGTH_PER_MESSAGE",
    "AI_CONTEXT_LENGTH_PER_SESSION",
    "AI_VISION_IMAGE_LIMIT",
    "AI_VISION_IMAGE_SIZE_LIMIT_KB",
    "AI_SYSTEM_NOTIFY_WINDOW_SIZE",
    "AI_SYSTEM_NOTIFY_LIMIT",
    "AI_ALWAYS_INCLUDE_MSG_ID",
    "AI_INCLUDE_TOME_INDICATOR",
    "AI_SHOW_REMOTE_URL",
    "SESSION_GROUP_ACTIVE_DEFAULT",
    "SESSION_PRIVATE_ACTIVE_DEFAULT",
    "SESSION_ENABLE_FAILED_LLM_FEEDBACK",
}

# 允许的 i18n_category 分类名（用于动态匹配，防止后续 NA 版本新增字段遗漏）
ALLOWED_SYSTEM_CONFIG_CATEGORIES = {
    "模型配置",
    "聊天配置",
}




PRIVATE_GROUP_NAMES = {
    "default",
    "default-draw",
    "default-draw-chat",
    "text-embedding",
    "CLI",
}


def is_sensitive_plugin_config_key(key: str) -> bool:
    """判断插件配置项是否属于敏感项。"""
    if not key:
        return False
    key_text = str(key).upper()
    return any(word in key_text for word in SENSITIVE_KEYWORDS) or key_text in SENSITIVE_MODEL_FIELDS


def infer_allowed_model_groups(data: Any) -> List[str]:
    """
    在实例未显式配置 allowed_model_groups 时，自动推断可交给用户管理的分组。
    默认隐藏系统/管理员分组，只暴露非内置分组，避免泄露站长自己的 API Key。
    """
    if not isinstance(data, dict):
        return []
    return [name for name in data.keys() if name not in PRIVATE_GROUP_NAMES]


def sanitize_model_group(group: Any) -> Any:
    """隐藏模型组中的密钥类字段。"""
    if not isinstance(group, dict):
        return group
    sanitized = copy.deepcopy(group)
    for key in list(sanitized.keys()):
        if key in SENSITIVE_MODEL_FIELDS or any(word in key.upper() for word in SENSITIVE_KEYWORDS):
            sanitized[key] = ""
    return sanitized


def _sanitize_sensitive_values(data: Any) -> Any:
    """递归遮蔽响应中的密钥类字段，防止插件接口泄露 API Key/Token。"""
    if isinstance(data, list):
        return [_sanitize_sensitive_values(item) for item in data]
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_text = str(key).upper()
            if key in SENSITIVE_MODEL_FIELDS or any(word in key_text for word in SENSITIVE_KEYWORDS):
                sanitized[key] = ""
            else:
                sanitized[key] = _sanitize_sensitive_values(value)
        return sanitized
    return data


def sanitize_plugin_management_response(data: Any) -> Any:
    """
    过滤插件管理响应。
    普通用户可看到插件列表/详情、数据管理和插件配置页，但敏感字段仍需隐藏。
    """
    return _sanitize_sensitive_values(copy.deepcopy(data))


def sanitize_plugin_config_response(data: Any) -> Any:
    """
    过滤插件配置响应。
    - 配置列表中隐藏敏感配置项，保留其它配置项供用户查看/修改。
    - 字典/嵌套结构中递归遮蔽敏感值，避免 API Key 等泄露。
    """
    if isinstance(data, list):
        filtered = []
        for item in data:
            if not isinstance(item, dict):
                filtered.append(item)
                continue
            key = item.get("key", "")
            if is_sensitive_plugin_config_key(str(key)) or item.get("is_secret"):
                continue
            filtered.append(item)
        return filtered
    return _sanitize_sensitive_values(copy.deepcopy(data))


def filter_model_groups_response(data: Any, allowed: List[str] = None) -> Any:
    """
    过滤模型组列表响应。
    只保留用户被授权管理的模型组，并隐藏密钥类字段。
    allowed 为 None/空时采用安全默认值：隐藏内置管理员分组，只展示非内置用户分组。
    """
    if not isinstance(data, dict):
        return data

    effective_allowed = allowed or infer_allowed_model_groups(data)
    return {
        k: sanitize_model_group(v)
        for k, v in data.items()
        if k in effective_allowed
    }


def filter_model_group_update(group_name: str, allowed: List[str] = None) -> bool:
    """检查用户是否有权限更新指定的模型组。"""
    if allowed is None:
        return group_name not in PRIVATE_GROUP_NAMES
    return group_name in allowed


def filter_model_group_delete(group_name: str, allowed: List[str] = None) -> bool:
    """检查用户是否有权限删除指定的模型组。"""
    if allowed is None:
        return group_name not in PRIVATE_GROUP_NAMES
    return group_name in allowed


def filter_model_group_test_request(data: dict, allowed: List[str] = None) -> dict:
    """过滤模型组测试请求，只允许测试用户被授权的分组。"""
    if not isinstance(data, dict):
        return data
    if "group_names" in data and isinstance(data["group_names"], list):
        if allowed is None:
            data["group_names"] = [g for g in data["group_names"] if g not in PRIVATE_GROUP_NAMES]
        else:
            data["group_names"] = [g for g in data["group_names"] if g in allowed]
    elif "group_name" in data:
        group = data.get("group_name")
        if (allowed is None and group in PRIVATE_GROUP_NAMES) or (allowed is not None and group not in allowed):
            data["group_name"] = ""
    return data


def is_allowed_system_config_key(key: str) -> bool:
    """判断普通用户是否可以访问指定的 system 配置项（白名单模式，仅模型配置）。"""
    if not key:
        return False
    return key in ALLOWED_SYSTEM_CONFIG_KEYS


def filter_config_list_response(data: Any) -> Any:
    """
    过滤基本配置列表响应。
    白名单模式：仅展示"模型配置"分类的配置项，并遮蔽 secret 值。
    同时支持按 key 白名单和按 i18n_category 分类动态匹配。
    """
    if not isinstance(data, list):
        return data

    filtered = []
    for item in data:
        if not isinstance(item, dict):
            continue
        key = item.get("key", "")
        # 按 key 白名单匹配
        allowed_by_key = key in ALLOWED_SYSTEM_CONFIG_KEYS
        # 按 i18n_category 分类动态匹配
        i18n_cat = item.get("i18n_category", "")
        if isinstance(i18n_cat, dict):
            cat_name = i18n_cat.get("zh", "") or i18n_cat.get("zh-CN", "") or i18n_cat.get("en", "")
        else:
            cat_name = i18n_cat or ""
        allowed_by_category = cat_name in ALLOWED_SYSTEM_CONFIG_CATEGORIES

        if allowed_by_key or allowed_by_category:
            safe_item = dict(item)
            if safe_item.get("is_secret"):
                safe_item["value"] = ""
            filtered.append(safe_item)

    return filtered


def filter_navigation_config() -> Dict[str, Any]:
    """返回用户端面板的导航配置。"""
    return {
        "pages": [
            {"key": "dashboard", "title": "仪表盘", "icon": "Dashboard", "path": "/dashboard"},
            {"key": "chat-channel", "title": "频道管理", "icon": "Chat", "path": "/chat-channel", "children": [{"key": "chat-channel-management", "title": "频道列表", "path": "/chat-channel/management"}]},
            {"key": "user-manager", "title": "用户管理", "icon": "Group", "path": "/user-manager"},
            {"key": "presets", "title": "人设管理", "icon": "Face", "path": "/presets"},
            {"key": "plugins-market", "title": "插件市场", "icon": "Extension", "path": "/cloud/plugins-market"},
            {"key": "logs", "title": "系统日志", "icon": "Terminal", "path": "/logs"},
            {"key": "sandbox-logs", "title": "沙盒日志", "icon": "Code", "path": "/sandbox-logs"},
            {"key": "settings", "title": "系统配置", "icon": "Settings", "path": "/settings", "children": [
                {"key": "settings-models", "title": "模型管理", "path": "/settings/models"},
                {"key": "settings-system", "title": "基本配置", "path": "/settings/system"},
            ]},
        ]
    }


def should_filter_response(method: str, path: str) -> Optional[str]:
    """判断是否需要对响应进行过滤。"""
    if method == "GET" and path == "/api/config/model-groups":
        return "model_groups"
    if method == "GET" and path in ("/api/config/list/system", "/api/config/list/basic_config"):
        return "config_list"
    if method == "GET" and (path == "/api/plugins/list" or path.startswith("/api/plugins/detail/")):
        return "plugin_management"
    if method == "GET" and (path.startswith("/api/config/list/plugin_") or path.startswith("/api/config/get/plugin_")):
        return "plugin_config"
    return None


def apply_response_filter(filter_name: str, data: Any, allowed_model_groups: List[str] = None) -> Any:
    """应用指定的响应过滤器。"""
    if filter_name == "model_groups":
        return filter_model_groups_response(data, allowed_model_groups)
    if filter_name == "config_list":
        return filter_config_list_response(data)
    if filter_name == "plugin_management":
        return sanitize_plugin_management_response(data)
    if filter_name == "plugin_config":
        return sanitize_plugin_config_response(data)
    return data

