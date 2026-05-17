"""
Nekro User Panel - 配置文件
支持多 NA 实例，每个用户绑定一个实例。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel


# ============ 实例配置模型 ============


class InstanceConfig(BaseModel):
    """单个 NA 实例的配置"""
    id: str                  # 用户登录名（唯一标识）
    panel_password: str      # 用户面板登录密码
    na_port: int             # NA 实例端口
    na_admin_user: str = "admin"  # NA 管理员用户名
    na_admin_pass: str       # NA 管理员密码
    na_host: str = "127.0.0.1"   # NA 实例主机（默认本机）
    allowed_model_groups: List[str] = []  # 允许管理的模型组
    comment: str = ""        # 备注

    @property
    def na_backend_url(self) -> str:
        return f"http://{self.na_host}:{self.na_port}"


# ============ 加载实例配置 ============

INSTANCES_FILE = os.getenv("INSTANCES_FILE", str(Path(__file__).parent / "instances.json"))


def load_instances() -> Dict[str, InstanceConfig]:
    """从 JSON 文件加载所有实例配置"""
    path = Path(INSTANCES_FILE)
    if not path.exists():
        raise FileNotFoundError(f"实例配置文件不存在: {INSTANCES_FILE}")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    instances = {}
    for item in raw:
        inst = InstanceConfig(**item)
        instances[inst.id] = inst
    return instances


# 全局实例注册表（启动时加载，可热重载）
INSTANCES: Dict[str, InstanceConfig] = load_instances()


def reload_instances():
    """热重载实例配置，同时使代理 HTTP 客户端缓存失效"""
    global INSTANCES
    new_instances = load_instances()
    INSTANCES.clear()
    INSTANCES.update(new_instances)
    # 通知代理层清除缓存的 HTTP 客户端（端口可能已变更）
    _notify_proxy_reload()


def _notify_proxy_reload():
    """通知代理层清除 HTTP 客户端缓存"""
    try:
        from proxy import invalidate_http_clients
        invalidate_http_clients()
    except ImportError:
        pass


def get_instance(user_id: str) -> Optional[InstanceConfig]:
    """根据用户 ID 获取对应的实例配置"""
    return INSTANCES.get(user_id)


# ============ 面板认证配置 ============
PANEL_JWT_SECRET = os.getenv("PANEL_JWT_SECRET", "nekro-user-panel-secret-change-me")
PANEL_JWT_ALGORITHM = "HS256"
PANEL_JWT_EXPIRE_HOURS = int(os.getenv("PANEL_JWT_EXPIRE_HOURS", "24"))

# ============ 管理员账号 ============
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Wdx030014")

# ============ 频道管理 - 覆盖配置黑名单 ============
CHANNEL_OVERRIDE_BLOCKED = True

# ============ 服务配置 ============
PANEL_HOST = os.getenv("PANEL_HOST", "0.0.0.0")
PANEL_PORT = int(os.getenv("PANEL_PORT", "9054"))

# ============ 前端静态文件 ============
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "./frontend_static")

