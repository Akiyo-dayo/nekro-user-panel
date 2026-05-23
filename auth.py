"""
Nekro User Panel - 独立认证系统（多实例版）
每个用户绑定一个 NA 实例，JWT 中携带实例 ID。
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

import httpx
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel

from config import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    INSTANCES,
    InstanceConfig,
    PANEL_JWT_ALGORITHM,
    PANEL_JWT_EXPIRE_HOURS,
    PANEL_JWT_SECRET,
    get_instance,
)


# ============ 数据模型 ============


class PanelUser(BaseModel):
    username: str
    instance_id: str  # 绑定的实例 ID（等于 username）

    @property
    def instance(self) -> Optional[InstanceConfig]:
        return get_instance(self.instance_id)


class PanelToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


# ============ NA 后端 Token 缓存（按实例） ============

_na_token_cache: Dict[str, Tuple[str, datetime]] = {}


def clear_na_backend_token(instance: InstanceConfig) -> None:
    """清理指定 NA 实例的管理员 token 缓存"""
    _na_token_cache.pop(instance.id, None)


async def get_na_backend_token(instance: InstanceConfig) -> str:
    """获取指定 NA 实例的管理员 token（带缓存）"""
    global _na_token_cache

    cache_key = instance.id
    if cache_key in _na_token_cache:
        token, expire = _na_token_cache[cache_key]
        if datetime.now(timezone.utc) < expire:
            return token

    # 向 NA 后端请求新 token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{instance.na_backend_url}/api/token",
            data={
                "username": instance.na_admin_user,
                "password": instance.na_admin_pass,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"无法获取 NA 后端 token (实例 {instance.id}): {response.status_code}",
            )

        data = response.json()
        token = data["access_token"]
        expire = datetime.now(timezone.utc) + timedelta(hours=23)
        _na_token_cache[cache_key] = (token, expire)
        return token


# ============ 面板认证逻辑 ============


def authenticate_panel_user(username: str, password: str) -> Optional[PanelUser]:
    """验证面板用户（从 instances.json 中查找，或管理员账号）"""
    # 管理员账号
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return PanelUser(username=username, instance_id="__admin__")

    # 普通用户
    instance = get_instance(username)
    if instance and instance.panel_password == password:
        return PanelUser(username=username, instance_id=instance.id)
    return None


def create_panel_token(username: str, instance_id: str) -> str:
    """创建面板 JWT token（包含实例 ID 和角色）"""
    expire = datetime.now(timezone.utc) + timedelta(hours=PANEL_JWT_EXPIRE_HOURS)
    role = "admin" if instance_id == "__admin__" else "user"
    payload = {
        "sub": username,
        "instance_id": instance_id,
        "role": role,
        "exp": expire,
        "iss": "nekro-user-panel",
    }
    return jwt.encode(payload, PANEL_JWT_SECRET, algorithm=PANEL_JWT_ALGORITHM)


def _try_decode_panel_token(token: str) -> Optional[PanelUser]:
    """尝试解码 panel token，成功返回 PanelUser，失败返回 None"""
    try:
        payload = jwt.decode(token, PANEL_JWT_SECRET, algorithms=[PANEL_JWT_ALGORITHM])
        username: str = payload.get("sub")
        instance_id: str = payload.get("instance_id", username)
        if username is None:
            return None
        if instance_id == "__admin__":
            return PanelUser(username=username, instance_id="__admin__")
        if get_instance(instance_id) is None:
            return None
        return PanelUser(username=username, instance_id=instance_id)
    except JWTError:
        return None


async def get_current_panel_user(request: Request) -> PanelUser:
    """从 token 中解析当前面板用户（支持 Authorization header 和 cookie）。
    先尝试 Authorization header，如果失败再尝试 cookie。"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. 尝试从 Authorization header 获取 token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        user = _try_decode_panel_token(auth_header[7:])
        if user:
            return user

    # 2. 尝试从 cookie 获取
    cookie_token = request.cookies.get("panel_token")
    if cookie_token:
        user = _try_decode_panel_token(cookie_token)
        if user:
            return user

    raise credentials_exception


async def get_optional_panel_user(request: Request) -> Optional[PanelUser]:
    """尝试解析面板用户，失败时返回 None 而不是抛出 401。
    先尝试 Authorization header，如果失败再尝试 cookie。
    
    重要安全逻辑：
    - 如果请求中没有任何认证信息 → 返回 None（允许匿名访问前端静态资源）
    - 如果请求中携带了认证信息但无效/过期 → 抛出 401（防止 fallback 到其他实例）
    """
    has_credentials = False

    # 1. 尝试从 Authorization header 获取 token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        has_credentials = True
        user = _try_decode_panel_token(auth_header[7:])
        if user:
            return user

    # 2. Authorization header 失败或不存在，尝试从 cookie 获取
    cookie_token = request.cookies.get("panel_token")
    if cookie_token:
        has_credentials = True
        user = _try_decode_panel_token(cookie_token)
        if user:
            return user

    # 3. 如果提供了认证信息但全部无效，拒绝请求（防止 fallback 到其他用户的实例）
    if has_credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. 完全没有认证信息 → 匿名访问（用于加载登录页等）
    return None


def is_admin(user: PanelUser) -> bool:
    """判断用户是否是管理员"""
    return user.instance_id == "__admin__"



async def get_optional_panel_user_lenient(request: Request) -> Optional[PanelUser]:
    """与 get_optional_panel_user 类似，但永远不抛出 401。
    用于前端静态资源（CSS/JS/图片），这些资源在登录页面也需要加载。"""
    # 1. 尝试从 Authorization header 获取 token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        user = _try_decode_panel_token(auth_header[7:])
        if user:
            return user

    # 2. 尝试从 cookie 获取
    cookie_token = request.cookies.get("panel_token")
    if cookie_token:
        user = _try_decode_panel_token(cookie_token)
        if user:
            return user

    return None

