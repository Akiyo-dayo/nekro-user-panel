"""
Nekro User Panel - 配置文件
支持多 NA 实例，每个用户绑定一个实例。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ============ 实例配置模型 ============


class InstanceConfig(BaseModel):
    """单个 NA 实例的配置"""
    id: str                  # 用户登录名（唯一标识）
    panel_password: str      # 用户面板登录密码
    na_port: Optional[int] = None  # NA 实例端口；na_base_url 存在时可省略
    na_admin_user: str = "admin"  # NA 管理员用户名
    na_admin_pass: str       # NA 管理员密码
    na_host: str = "127.0.0.1"   # NA 实例主机（默认本机）
    na_scheme: str = "http"  # NA 实例协议
    na_base_url: Optional[str] = None  # 显式后端地址，优先级高于 na_host/na_port
    cluster_id: str = "default"  # 集群 ID，用于多集群归类
    cluster_name: str = ""    # 集群展示名称
    node_id: str = "local"    # 节点 ID
    node_name: str = ""       # 节点展示名称
    login_aliases: List[str] = Field(default_factory=list)  # 可选登录别名
    allowed_model_groups: List[str] = Field(default_factory=list)  # 允许管理的模型组
    comment: str = ""        # 备注

    @property
    def na_backend_url(self) -> str:
        if self.na_base_url:
            return self.na_base_url.rstrip("/")
        if self.na_port is None:
            raise ValueError(f"实例 {self.id} 缺少 na_port 或 na_base_url")
        return f"{self.na_scheme}://{self.na_host}:{self.na_port}"

    @property
    def route_label(self) -> str:
        node = self.node_name or self.node_id
        cluster = self.cluster_name or self.cluster_id
        return f"{cluster}/{node}"

    @property
    def login_names(self) -> List[str]:
        names = [
            self.id,
            f"{self.cluster_id}/{self.id}",
            f"{self.node_id}/{self.id}",
        ]
        if self.cluster_id and self.node_id:
            names.append(f"{self.cluster_id}/{self.node_id}/{self.id}")
        names.extend(self.login_aliases or [])
        return list(dict.fromkeys(str(name) for name in names if name))


class NodeConfig(BaseModel):
    """A server node that can own one or more NA instances."""

    id: str
    name: str = ""
    cluster_id: str = "default"
    cluster_name: str = ""
    role: str = "node"
    panel_base_url: Optional[str] = None
    ncqq_base_url: Optional[str] = None
    ssh_host: str = ""
    ssh_port: Optional[int] = None
    ssh_user: str = ""
    status: str = "unknown"
    comment: str = ""

    @property
    def display_name(self) -> str:
        return self.name or self.id

    @property
    def route_label(self) -> str:
        cluster = self.cluster_name or self.cluster_id
        return f"{cluster}/{self.display_name}"


# ============ 加载实例配置 ============

INSTANCES_FILE = os.getenv("INSTANCES_FILE", str(Path(__file__).parent / "instances.json"))
NODES_FILE = os.getenv("NODES_FILE", str(Path(__file__).parent / "nodes.json"))


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


# ============ 加载节点配置 ============


def _default_nodes() -> List[dict]:
    return [
        {
            "id": "denia",
            "name": "Denia headquarters",
            "cluster_id": "denia",
            "cluster_name": "Denia",
            "role": "headquarters",
            "panel_base_url": "http://127.0.0.1:9054",
            "ssh_host": "xa.akiyo.fun",
            "ssh_port": 24022,
            "ssh_user": "F1yCar",
            "status": "online",
            "comment": "Headquarters panel on Denia.",
        }
    ]


def load_nodes() -> Dict[str, NodeConfig]:
    """从 JSON 文件加载节点配置；文件缺失时返回 Denia 总部节点。"""
    path = Path(NODES_FILE)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    else:
        raw = _default_nodes()

    nodes = {}
    for item in raw:
        node = NodeConfig(**item)
        nodes[node.id] = node
    return nodes


# 全局实例注册表（启动时加载，可热重载）
INSTANCES: Dict[str, InstanceConfig] = load_instances()
NODES: Dict[str, NodeConfig] = load_nodes()


def reload_instances():
    """热重载实例配置，同时使代理 HTTP 客户端缓存失效"""
    global INSTANCES
    new_instances = load_instances()
    INSTANCES.clear()
    INSTANCES.update(new_instances)
    # 通知代理层清除缓存的 HTTP 客户端（端口可能已变更）
    _notify_proxy_reload()


def reload_nodes():
    """热重载节点配置。"""
    global NODES
    new_nodes = load_nodes()
    NODES.clear()
    NODES.update(new_nodes)


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


def get_node(node_id: str) -> Optional[NodeConfig]:
    """根据节点 ID 获取节点配置"""
    return NODES.get(node_id)


def find_instance_by_login(username: str) -> Optional[InstanceConfig]:
    """根据登录名或别名查找唯一实例。

    精确匹配实例 id 优先；别名匹配必须唯一，避免跨集群同名账号误路由。
    """
    username = (username or "").strip()
    if not username:
        return None
    if username in INSTANCES:
        return INSTANCES[username]
    matches = [inst for inst in INSTANCES.values() if username in inst.login_names]
    if len(matches) == 1:
        return matches[0]
    return None


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
