"""
Nekro User Panel - 反向代理核心（多实例版）
根据当前用户绑定的实例，动态路由请求到对应的 NA 后端。
"""

import re
from typing import Dict, Optional

import httpx
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from starlette import status

from auth import PanelUser, get_na_backend_token
from config import INSTANCES, InstanceConfig, get_instance
from filters import (
    apply_response_filter,
    filter_model_group_delete,
    filter_model_group_test_request,
    filter_model_group_update,
    is_allowed_system_config_key,
    should_filter_response,
)
from route_whitelist import is_route_allowed

# 按实例缓存 httpx 客户端
_http_clients: Dict[str, httpx.AsyncClient] = {}


async def get_http_client(instance: InstanceConfig) -> httpx.AsyncClient:
    """获取指定实例的 HTTP 客户端"""
    global _http_clients
    key = instance.id
    if key not in _http_clients or _http_clients[key].is_closed:
        _http_clients[key] = httpx.AsyncClient(
            base_url=instance.na_backend_url,
            timeout=httpx.Timeout(60.0, connect=10.0),
            follow_redirects=False,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_clients[key]


async def close_http_client():
    """关闭所有 HTTP 客户端"""
    global _http_clients
    for key, client in _http_clients.items():
        if not client.is_closed:
            await client.aclose()
    _http_clients = {}


def _is_streaming_request(path: str) -> bool:
    """判断是否是 SSE 流式请求"""
    streaming_patterns = [
        r"/stream$",
        r"/logs/stream$",
        r"/list/stream$",
    ]
    return any(re.search(p, path) for p in streaming_patterns)


async def _check_model_group_permission(method: str, path: str, body: Optional[bytes] = None, allowed_groups: list = None) -> None:
    """
    检查模型组相关操作的权限。
    """
    # POST /api/config/model-groups/{group_name} - 更新模型组
    match = re.match(r"^/api/config/model-groups/([^/]+)$", path)
    if match and method in ("POST", "DELETE"):
        group_name = match.group(1)
        if group_name == "actions":
            return

        if method == "POST" and not filter_model_group_update(group_name, allowed_groups):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权操作模型组: {group_name}",
            )
        if method == "DELETE" and not filter_model_group_delete(group_name, allowed_groups):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权删除模型组: {group_name}",
            )

    # POST /api/config/model-groups/actions/test - 测试模型组
    if path == "/api/config/model-groups/actions/test" and method == "POST" and body:
        import json
        try:
            data = json.loads(body)
            filtered = filter_model_group_test_request(data, allowed_groups)
            if not filtered.get("group_names"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权测试指定的模型组",
                )
        except (json.JSONDecodeError, KeyError):
            pass


async def _check_system_config_permission(method: str, path: str, body: Optional[bytes] = None) -> None:
    """限制普通用户只能读取/修改模型相关的 system 配置项。"""
    match = re.match(r"^/api/config/(?:get|set)/(?:system|basic_config)/([^/]+)$", path)
    if match:
        key = match.group(1)
        if not is_allowed_system_config_key(key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权访问配置项: {key}",
            )

    if path in ("/api/config/batch/system", "/api/config/save/system", "/api/config/batch/basic_config", "/api/config/save/basic_config") and method == "POST" and body:
        import json
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return

        keys = []
        if isinstance(data, dict):
            if "key" in data:
                keys.append(data.get("key"))
            if "data" in data and isinstance(data["data"], dict):
                keys.extend(data["data"].keys())
            if "items" in data and isinstance(data["items"], list):
                for item in data["items"]:
                    if isinstance(item, dict):
                        keys.append(item.get("key"))
            # 兼容直接以 {KEY: value} 形式提交的批量保存。
            keys.extend(k for k in data.keys() if k not in ("data", "items", "key", "value"))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    keys.append(item.get("key"))

        for key in keys:
            if key and not is_allowed_system_config_key(str(key)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权修改配置项: {key}",
                )


async def proxy_request(request: Request, user: Optional[PanelUser] = None) -> Response:
    """
    核心代理逻辑（多实例版）：
    1. 确定目标实例
    2. 检查路由白名单（admin 跳过）
    3. 检查模型组权限
    4. 转发请求到对应 NA 后端
    5. 过滤响应数据
    6. 返回给客户端
    """
    method = request.method.upper()
    path = request.url.path
    query_string = str(request.url.query) if request.url.query else ""

    # 判断是否为 admin 用户
    is_admin_user = user and user.instance_id == "__admin__"

    # 0. 确定目标实例
    instance = None
    if is_admin_user:
        # admin 用户：从 cookie 中读取选择的实例
        admin_instance_id = request.cookies.get("admin_instance")
        if admin_instance_id:
            instance = get_instance(admin_instance_id)
        # 如果没有选择实例或实例无效，使用第一个
        if not instance and INSTANCES:
            instance = next(iter(INSTANCES.values()))
    elif user and user.instance:
        instance = user.instance
    else:
        # 未认证时使用第一个可用实例（用于加载前端静态资源等）
        if INSTANCES:
            instance = next(iter(INSTANCES.values()))

    if not instance:
        raise HTTPException(status_code=503, detail="无可用实例")

    # 1. 路由白名单检查（admin 跳过，拥有完整权限）
    if not is_admin_user and not is_route_allowed(method, path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该操作未被授权",
        )

    # 2. 读取请求体
    body = await request.body() if method in ("POST", "PUT", "PATCH", "DELETE") else None

    # 3. 模型组权限检查（admin 跳过）
    if not is_admin_user:
        allowed_groups = instance.allowed_model_groups or None
        await _check_model_group_permission(method, path, body, allowed_groups)
        await _check_system_config_permission(method, path, body)

    # 4. 获取 NA 后端 token
    na_token = await get_na_backend_token(instance)

    # 5. 构建代理请求头
    proxy_headers = {
        "Authorization": f"Bearer {na_token}",
        "Content-Type": request.headers.get("Content-Type", "application/json"),
        "Accept": request.headers.get("Accept", "*/*"),
    }

    # 传递 User-Agent
    if "User-Agent" in request.headers:
        proxy_headers["User-Agent"] = request.headers["User-Agent"]

    # 6. 构建目标 URL
    # 兼容旧前端/旧白名单中的 basic_config 命名：NA 2.3.x 实际配置键为 system。
    backend_path = path.replace("/basic_config", "/system")
    target_url = backend_path
    if query_string:
        target_url = f"{backend_path}?{query_string}"

    # 7. 发送代理请求
    client = await get_http_client(instance)

    try:
        # SSE 流式请求特殊处理
        if _is_streaming_request(path) and method == "GET":
            return await _proxy_streaming(client, method, target_url, proxy_headers)

        # 普通请求
        response = await client.request(
            method=method,
            url=target_url,
            headers=proxy_headers,
            content=body,
        )

        # 8. 过滤响应（admin 拥有完整权限，不能隐藏任何模型组/配置项）
        filter_name = None if is_admin_user else should_filter_response(method, path)

        if filter_name and response.status_code == 200:
            try:
                data = response.json()
                allowed_groups = instance.allowed_model_groups or None
                filtered_data = apply_response_filter(filter_name, data, allowed_groups)
                return JSONResponse(
                    content=filtered_data,
                    status_code=response.status_code,
                )
            except Exception:
                pass  # 如果 JSON 解析失败，直接返回原始响应

        # 9. 构建响应
        response_headers = {}
        for key, value in response.headers.items():
            # 跳过 hop-by-hop 头
            if key.lower() not in (
                "transfer-encoding", "connection", "keep-alive",
                "proxy-authenticate", "proxy-authorization", "te",
                "trailers", "upgrade",
            ):
                response_headers[key] = value

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
        )

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="无法连接到 NA 后端服务",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="NA 后端服务响应超时",
        )


async def _proxy_streaming(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict,
) -> StreamingResponse:
    """代理 SSE 流式响应"""

    async def stream_generator():
        async with client.stream(method, url, headers=headers) as response:
            async for chunk in response.aiter_bytes():
                yield chunk

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
