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

# 允许普通用户在"基本配置"里看到/修改的 system 配置项（仅"模型配置"分类）。
# 基于 NA 后端 i18n_category == "模型配置" 的实际字段列表。
ALLOWED_SYSTEM_CONFIG_KEYS = {
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
}

# 允许的 i18n_category 分类名（用于动态匹配，防止后续 NA 版本新增字段遗漏）
ALLOWED_SYSTEM_CONFIG_CATEGORIES = {
    "模型配置",
}




PRIVATE_GROUP_NAMES = {
    "default",
    "default-draw",
    "default-draw-chat",
    "text-embedding",
    "CLI",
}


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
        if key in SENSITIVE_MODEL_FIELDS or any(word in key.upper() for word in ("KEY", "SECRET", "PASSWORD", "TOKEN")):
            sanitized[key] = ""
    return sanitized


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
    return None


def apply_response_filter(filter_name: str, data: Any, allowed_model_groups: List[str] = None) -> Any:
    """应用指定的响应过滤器。"""
    if filter_name == "model_groups":
        return filter_model_groups_response(data, allowed_model_groups)
    if filter_name == "config_list":
        return filter_config_list_response(data)
    return data

