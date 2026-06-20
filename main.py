"""
Nekro User Panel - 主应用入口（多实例版）
一个轻量级反向代理网关，为多个 Nekro Agent 实例提供受限的用户端管理面板。
每个用户绑定一个 NA 实例，登录后所有请求自动路由到对应实例。
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from auth import (
    LoginRequest,
    PanelToken,
    PanelUser,
    authenticate_panel_user,
    create_panel_token,
    get_current_panel_user,
    get_na_backend_token,
    get_optional_panel_user,
    get_optional_panel_user_lenient,
    is_admin,
)
from config import (
    PANEL_HOST,
    PANEL_PORT,
    PANEL_JWT_EXPIRE_HOURS,
    INSTANCES,
    INSTANCES_FILE,
    NODES,
    NODES_FILE,
    InstanceConfig,
    NodeConfig,
    get_instance,
    get_node,
    reload_instances,
    reload_nodes,
)
from filters import filter_navigation_config
from frontend_inject import get_full_inject_html
from proxy import close_http_client, proxy_request
from route_whitelist import is_route_allowed


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    yield
    await close_http_client()


app = FastAPI(
    title="Nekro User Panel",
    description="Nekro Agent 多实例用户端管理面板",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 面板自有接口 ============


@app.post("/panel/login", response_model=PanelToken, tags=["Panel Auth"])
async def panel_login(req: LoginRequest):
    """用户端面板登录"""
    user = authenticate_panel_user(req.username, req.password)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "用户名或密码错误"},
        )
    token = create_panel_token(user.username, user.instance_id)
    role = "admin" if is_admin(user) else "user"
    response = JSONResponse(content={
        "access_token": token,
        "token_type": "bearer",
        "role": role,
        "redirect": "/panel/admin" if role == "admin" else None,
    })
    response.set_cookie(
        key="panel_token",
        value=token,
        path="/",
        httponly=True,
        samesite="lax",
        max_age=PANEL_JWT_EXPIRE_HOURS * 3600,
    )
    return response


@app.post("/panel/logout", tags=["Panel Auth"])
async def panel_logout():
    """Clear panel authentication cookies."""
    response = JSONResponse(content={"status": "ok", "message": "已退出登录"})
    for key in ("panel_token", "admin_instance"):
        response.delete_cookie(key=key, path="/")
        # Explicit expired cookie for older browser/proxy combinations.
        response.set_cookie(key=key, value="", path="/", max_age=0, expires=0, samesite="lax")
    return response


@app.get("/panel/nav-config", tags=["Panel Config"])
async def get_nav_config(_user: PanelUser = Depends(get_current_panel_user)):
    """获取用户端面板的导航配置"""
    return filter_navigation_config()


@app.get("/panel/user-info", tags=["Panel Auth"])
async def get_panel_user_info(user: PanelUser = Depends(get_current_panel_user)):
    """获取当前面板用户信息"""
    inst = user.instance
    return {
        "username": user.username,
        "instance_id": user.instance_id,
        "role": "admin" if is_admin(user) else "user",
        "cluster_id": inst.cluster_id if inst else None,
        "cluster_name": inst.cluster_name if inst else None,
        "node_id": inst.node_id if inst else None,
        "node_name": inst.node_name if inst else None,
    }


@app.post("/panel/reload-instances", tags=["Panel Admin"])
async def reload_instances_endpoint(user: PanelUser = Depends(get_current_panel_user)):
    """热重载实例配置（管理员专用）"""
    if user is None or not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    try:
        reload_instances()
        return {"status": "ok", "message": "实例配置已重载"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


# ============ 管理员 API ============


@app.get("/panel/admin/nodes", tags=["Panel Admin"])
async def list_nodes(user: PanelUser = Depends(get_current_panel_user)):
    """获取所有节点列表（管理员专用）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    return [_node_summary(node) for node in NODES.values()]


@app.get("/panel/admin/nodes/{node_id}", tags=["Panel Admin"])
async def get_node_detail(node_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """获取单个节点详情"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    node = get_node(node_id)
    if not node:
        return JSONResponse(status_code=404, content={"detail": "节点不存在"})
    data = _node_summary(node)
    data["manager_api_key"] = ""
    data["manager_api_key_set"] = bool(node.manager_api_key)
    return data


@app.post("/panel/admin/nodes", tags=["Panel Admin"])
async def create_node(data: dict, user: PanelUser = Depends(get_current_panel_user)):
    """创建新节点"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    return _save_node(data, create=True)


@app.put("/panel/admin/nodes/{node_id}", tags=["Panel Admin"])
async def update_node(node_id: str, data: dict, user: PanelUser = Depends(get_current_panel_user)):
    """更新节点配置，支持修改节点 ID"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    new_id = data.get("id", node_id)
    data["_old_id"] = node_id
    data["id"] = new_id
    return _save_node(data, create=False)


@app.delete("/panel/admin/nodes/{node_id}", tags=["Panel Admin"])
async def delete_node(node_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """删除节点。仍被实例引用的节点不可删除。"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    if any(inst.node_id == node_id for inst in INSTANCES.values()):
        return JSONResponse(status_code=409, content={"detail": f"节点 {node_id} 仍有实例引用，不能删除"})

    import json
    from pathlib import Path

    path = Path(NODES_FILE)
    nodes_list = _read_nodes_list(path)
    nodes_list = [n for n in nodes_list if n.get("id") != node_id]
    _write_json_list(path, nodes_list)
    reload_nodes()
    return {"status": "ok", "message": f"节点 {node_id} 已删除"}


@app.post("/panel/admin/nodes/{node_id}/probe", tags=["Panel Admin"])
async def probe_node(node_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """Probe the HTTP-facing entry points for a node."""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    node = get_node(node_id)
    if not node:
        return JSONResponse(status_code=404, content={"detail": "节点不存在"})
    return await _probe_node(node)


def _node_summary(node: NodeConfig) -> dict:
    """Return the safe admin-list shape for a node."""
    owned_instances = [inst.id for inst in INSTANCES.values() if inst.node_id == node.id]
    return {
        "id": node.id,
        "name": node.name,
        "display_name": node.display_name,
        "cluster_id": node.cluster_id,
        "cluster_name": node.cluster_name,
        "role": node.role,
        "panel_base_url": node.panel_base_url,
        "manager_base_url": node.manager_base_url,
        "manager_api_key_set": bool(node.manager_api_key),
        "status": node.status,
        "comment": node.comment,
        "route_label": node.route_label,
        "instance_count": len(owned_instances),
        "instances": owned_instances,
    }


async def _probe_node(node: NodeConfig) -> dict:
    """Check HTTP reachability without exposing node secrets to the browser."""
    candidates: list[tuple[str, str]] = []
    if node.manager_base_url:
        candidates.append(("manager", node.manager_base_url.rstrip("/")))
    if node.panel_base_url:
        candidates.append(("panel", node.panel_base_url.rstrip("/")))

    if not candidates:
        return {
            "status": "unconfigured",
            "message": "节点还没有配置可由总部访问的 HTTP 入口。",
            "checks": [],
        }

    checks = []
    headers = {}
    if node.manager_api_key:
        headers["X-API-Key"] = node.manager_api_key
        headers["Authorization"] = f"Bearer {node.manager_api_key}"

    async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
        for kind, base_url in candidates:
            paths = ["/api/cluster/status", "/api/health", "/panel/admin/nodes", "/webui", "/"]
            if kind == "panel":
                paths = ["/webui", "/panel/admin/nodes", "/"]
            for path in paths:
                url = f"{base_url}{path}"
                try:
                    resp = await client.get(url, headers=headers if kind == "manager" else None)
                    reachable = resp.status_code < 500
                    checks.append({
                        "kind": kind,
                        "url": url,
                        "status_code": resp.status_code,
                        "reachable": reachable,
                    })
                    if reachable:
                        return {
                            "status": "online" if resp.status_code < 400 else "reachable",
                            "message": f"{kind} HTTP 入口可达: HTTP {resp.status_code}",
                            "checks": checks,
                        }
                except Exception as exc:
                    checks.append({
                        "kind": kind,
                        "url": url,
                        "status_code": None,
                        "reachable": False,
                        "error": str(exc),
                    })

    return {
        "status": "offline",
        "message": "总部无法访问该节点配置的 HTTP 入口。",
        "checks": checks,
    }


def _read_nodes_list(path: Path) -> list:
    """Read nodes.json, creating the file from current in-memory nodes if missing."""
    import json

    if not path.exists():
        return [node.model_dump() for node in NODES.values()]
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_list(path: Path, data: list) -> None:
    """Persist a JSON list with stable formatting."""
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _save_node(data: dict, create: bool):
    """保存节点到 JSON 文件"""
    from pathlib import Path

    old_id = data.pop("_old_id", None)
    if not data.get("id"):
        return JSONResponse(status_code=400, content={"detail": "缺少必填字段: id"})

    data["id"] = str(data["id"]).strip()
    data["name"] = str(data.get("name") or data["id"]).strip()
    data["cluster_id"] = str(data.get("cluster_id") or "default").strip()
    data["cluster_name"] = str(data.get("cluster_name") or "").strip()
    data["role"] = str(data.get("role") or "node").strip()
    data["panel_base_url"] = str(data.get("panel_base_url") or "").strip().rstrip("/") or None
    data["manager_base_url"] = str(
        data.get("manager_base_url") or data.get("ncqq_base_url") or data.get("address") or ""
    ).strip().rstrip("/") or None
    incoming_api_key = str(data.get("manager_api_key") or data.get("api_key") or "").strip()
    data["status"] = str(data.get("status") or "unknown").strip()
    data["comment"] = str(data.get("comment") or "").strip()

    path = Path(NODES_FILE)
    nodes_list = _read_nodes_list(path)
    existing_node = next((n for n in nodes_list if n.get("id") == (old_id or data["id"])), None)
    data["manager_api_key"] = incoming_api_key
    if not create and not incoming_api_key and existing_node:
        data["manager_api_key"] = (
            existing_node.get("manager_api_key")
            or existing_node.get("api_key")
            or ""
        )
    for deprecated in ("ncqq_base_url", "ssh_host", "ssh_user", "ssh_port", "address", "api_key"):
        data.pop(deprecated, None)

    if create:
        if any(n.get("id") == data["id"] for n in nodes_list):
            return JSONResponse(status_code=409, content={"detail": f"节点 {data['id']} 已存在"})
        nodes_list.append(data)
    else:
        lookup_id = old_id or data["id"]
        found = False
        for i, node in enumerate(nodes_list):
            if node.get("id") == lookup_id:
                if old_id and data["id"] != old_id:
                    if any(n.get("id") == data["id"] for n in nodes_list if n.get("id") != old_id):
                        return JSONResponse(status_code=409, content={"detail": f"节点 {data['id']} 已存在"})
                nodes_list[i] = data
                found = True
                break
        if not found:
            return JSONResponse(status_code=404, content={"detail": f"节点 {lookup_id} 不存在"})

    _write_json_list(path, nodes_list)
    reload_nodes()
    return {"status": "ok", "message": f"节点 {data['id']} 已{'创建' if create else '更新'}"}


@app.get("/panel/admin/instances", tags=["Panel Admin"])
async def list_instances(user: PanelUser = Depends(get_current_panel_user)):
    """获取所有实例列表（管理员专用）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    return [_instance_summary(inst) for inst in INSTANCES.values()]


@app.get("/panel/admin/instances/{instance_id}", tags=["Panel Admin"])
async def get_instance_detail(instance_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """获取单个实例详情（管理员专用，包含密码）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    inst = get_instance(instance_id)
    if not inst:
        return JSONResponse(status_code=404, content={"detail": "实例不存在"})
    return inst.model_dump()


@app.post("/panel/admin/instances/{instance_id}/probe", tags=["Panel Admin"])
async def probe_instance(instance_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """Probe a single NA instance from the headquarters panel."""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    inst = get_instance(instance_id)
    if not inst:
        return JSONResponse(status_code=404, content={"detail": "实例不存在"})
    return await _probe_instance(inst)


async def _probe_instance(inst: InstanceConfig) -> dict:
    """Check whether a configured NA backend is reachable and accepts its admin credentials."""
    import time

    started = time.perf_counter()
    checks = []
    try:
        token = await get_na_backend_token(inst)
        checks.append({"step": "token", "ok": True})
    except Exception as exc:
        return {
            "status": "offline",
            "message": "无法获取 NA 管理凭据，实例可能离线或密码已变更。",
            "latency_ms": int((time.perf_counter() - started) * 1000),
            "checks": [{"step": "token", "ok": False, "error": str(exc)}],
        }

    async with httpx.AsyncClient(base_url=inst.na_backend_url, timeout=4.0, follow_redirects=True) as client:
        for path in ("/webui/", "/api/user/me", "/"):
            try:
                headers = {"Authorization": f"Bearer {token}"}
                resp = await client.get(path, headers=headers)
                reachable = resp.status_code < 500
                checks.append({
                    "step": path,
                    "ok": reachable,
                    "status_code": resp.status_code,
                })
                if reachable:
                    return {
                        "status": "online" if resp.status_code < 400 else "reachable",
                        "message": f"{inst.id} 可访问，HTTP {resp.status_code}",
                        "latency_ms": int((time.perf_counter() - started) * 1000),
                        "checks": checks,
                    }
            except Exception as exc:
                checks.append({"step": path, "ok": False, "error": str(exc)})

    return {
        "status": "offline",
        "message": f"{inst.id} 暂时不可达。",
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "checks": checks,
    }


def _instance_summary(inst: InstanceConfig) -> dict:
    """Return the safe admin-list shape for an instance."""
    return {
        "id": inst.id,
        "na_port": inst.na_port,
        "na_host": inst.na_host,
        "na_scheme": inst.na_scheme,
        "na_base_url": inst.na_base_url,
        "na_backend_url": inst.na_backend_url,
        "na_admin_user": inst.na_admin_user,
        "cluster_id": inst.cluster_id,
        "cluster_name": inst.cluster_name,
        "node_id": inst.node_id,
        "node_name": inst.node_name,
        "login_aliases": inst.login_aliases,
        "route_label": inst.route_label,
        "comment": inst.comment,
        "allowed_model_groups": inst.allowed_model_groups,
    }


@app.post("/panel/admin/instances", tags=["Panel Admin"])
async def create_instance(data: dict, user: PanelUser = Depends(get_current_panel_user)):
    """创建新实例（管理员专用）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    return _save_instance(data, create=True)


@app.put("/panel/admin/instances/{instance_id}", tags=["Panel Admin"])
async def update_instance(instance_id: str, data: dict, user: PanelUser = Depends(get_current_panel_user)):
    """更新实例配置（管理员专用），支持修改用户ID（登录名）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    # 如果前端传了新的 id 且与 URL 中的不同，则视为重命名
    new_id = data.get("id", instance_id)
    data["_old_id"] = instance_id
    data["id"] = new_id
    return _save_instance(data, create=False)


@app.delete("/panel/admin/instances/{instance_id}", tags=["Panel Admin"])
async def delete_instance(instance_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """删除实例（管理员专用）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    import json
    from pathlib import Path

    path = Path(INSTANCES_FILE)
    with open(path, "r", encoding="utf-8") as f:
        instances_list = json.load(f)

    instances_list = [i for i in instances_list if i.get("id") != instance_id]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(instances_list, f, ensure_ascii=False, indent=2)

    reload_instances()
    return {"status": "ok", "message": f"实例 {instance_id} 已删除"}


def _save_instance(data: dict, create: bool):
    """保存实例到 JSON 文件"""
    import json
    from pathlib import Path

    # 提取内部字段
    old_id = data.pop("_old_id", None)

    # 验证必填字段
    required = ["id", "panel_password", "na_admin_pass"]
    for field in required:
        if field not in data or not data[field]:
            return JSONResponse(status_code=400, content={"detail": f"缺少必填字段: {field}"})
    if not data.get("na_base_url") and not data.get("na_port"):
        return JSONResponse(status_code=400, content={"detail": "缺少必填字段: na_port 或 na_base_url"})

    data["id"] = str(data["id"]).strip()
    data["panel_password"] = str(data["panel_password"])
    data["na_admin_user"] = str(data.get("na_admin_user") or "admin").strip()
    data["na_admin_pass"] = str(data["na_admin_pass"])
    data["na_host"] = str(data.get("na_host") or "127.0.0.1").strip()
    data["na_scheme"] = str(data.get("na_scheme") or "http").strip().lower()
    data["cluster_id"] = str(data.get("cluster_id") or "default").strip()
    data["cluster_name"] = str(data.get("cluster_name") or "").strip()
    data["node_id"] = str(data.get("node_id") or "local").strip()
    data["node_name"] = str(data.get("node_name") or "").strip()
    if data["node_id"] not in NODES:
        return JSONResponse(status_code=400, content={"detail": f"节点 {data['node_id']} 不存在，请先添加节点"})
    data["comment"] = str(data.get("comment") or "").strip()
    data["allowed_model_groups"] = data.get("allowed_model_groups") or []
    aliases = data.get("login_aliases") or []
    if isinstance(aliases, str):
        aliases = [x.strip() for x in aliases.split(",") if x.strip()]
    data["login_aliases"] = aliases
    if data.get("na_base_url"):
        data["na_base_url"] = str(data["na_base_url"]).strip().rstrip("/")
    else:
        data["na_base_url"] = None
    if data.get("na_port") not in (None, ""):
        try:
            data["na_port"] = int(data["na_port"])
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"detail": "na_port 必须是数字"})

    path = Path(INSTANCES_FILE)
    with open(path, "r", encoding="utf-8") as f:
        instances_list = json.load(f)

    if create:
        # 检查 ID 是否已存在
        if any(i.get("id") == data["id"] for i in instances_list):
            return JSONResponse(status_code=409, content={"detail": f"实例 {data['id']} 已存在"})
        instances_list.append(data)
    else:
        # 更新已有实例（支持重命名：old_id -> new id）
        lookup_id = old_id or data["id"]
        found = False
        for i, inst in enumerate(instances_list):
            if inst.get("id") == lookup_id:
                # 如果是重命名，检查新 ID 是否与其他实例冲突
                if old_id and data["id"] != old_id:
                    if any(j.get("id") == data["id"] for j in instances_list if j.get("id") != old_id):
                        return JSONResponse(status_code=409, content={"detail": f"实例 {data['id']} 已存在"})
                instances_list[i] = data
                found = True
                break
        if not found:
            return JSONResponse(status_code=404, content={"detail": f"实例 {lookup_id} 不存在"})

    with open(path, "w", encoding="utf-8") as f:
        json.dump(instances_list, f, ensure_ascii=False, indent=2)

    reload_instances()
    return {"status": "ok", "message": f"实例 {data['id']} 已{'创建' if create else '更新'}"}


@app.get("/panel/admin", tags=["Panel Admin"], include_in_schema=False)
async def admin_page(user: Optional[PanelUser] = Depends(get_optional_panel_user_lenient)):
    """管理员页面"""
    if user is None or not is_admin(user):
        return render_panel_error_page(
            title="仅管理员可操作",
            message="当前账号没有访问管理后台的权限。请切换到管理员账号，或返回自己的实例入口。",
            status_code=403,
            primary_href="/webui",
            primary_label="返回面板入口",
            secondary_href="",
            secondary_label="",
        )
    from admin_page import get_admin_html
    return HTMLResponse(content=get_admin_html())


@app.post("/panel/admin/switch-instance/{instance_id}", tags=["Panel Admin"])
async def switch_instance(instance_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """管理员切换当前管理的实例"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    inst = get_instance(instance_id)
    if not inst:
        return JSONResponse(status_code=404, content={"detail": "实例不存在"})
    response = JSONResponse(content={"status": "ok", "instance_id": instance_id, "comment": inst.comment})
    import urllib.parse
    response.set_cookie(
        key="admin_instance",
        value=urllib.parse.quote(instance_id),
        path="/",
        samesite="lax",
        max_age=86400 * 7,
    )
    return response


@app.get("/panel/admin/current-instance", tags=["Panel Admin"])
async def get_current_instance(request: Request, user: PanelUser = Depends(get_current_panel_user)):
    """获取管理员当前管理的实例"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    import urllib.parse
    instance_id = urllib.parse.unquote(request.cookies.get("admin_instance", ""))
    inst = get_instance(instance_id) if instance_id else None
    if inst:
        return {
            "instance_id": inst.id,
            "comment": inst.comment,
            "na_port": inst.na_port,
            "na_backend_url": inst.na_backend_url,
            "cluster_id": inst.cluster_id,
            "cluster_name": inst.cluster_name,
            "node_id": inst.node_id,
            "node_name": inst.node_name,
            "route_label": inst.route_label,
        }
    return {"instance_id": None, "comment": None, "na_port": None, "na_backend_url": None}


# ============ API 代理 ============


@app.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
    include_in_schema=False,
)
async def api_proxy(request: Request, _user: Optional[PanelUser] = Depends(get_optional_panel_user)):
    """
    API 代理端点。
    根据当前用户的实例配置，动态路由到对应的 NA 后端。
    """
    return await proxy_request(request, _user)


# ============ 前端静态文件代理 ============


@app.get("/webui/{path:path}", include_in_schema=False)
async def webui_proxy(request: Request, _user: Optional[PanelUser] = Depends(get_optional_panel_user_lenient)):
    """代理前端静态文件请求到 NA 后端（使用宽松认证，确保登录页静态资源可加载）"""
    return await proxy_request(request, _user)


@app.get("/", include_in_schema=False)
async def root_redirect():
    """根路径重定向到前端"""
    return RedirectResponse(url="/webui", status_code=302)


# ============ 注入前端脚本 ============



def render_panel_error_page(
    *,
    title: str,
    message: str,
    detail: str = "",
    status_code: int = 502,
    primary_href: str = "/webui",
    primary_label: str = "返回登录页",
    secondary_href: str = "/panel/admin",
    secondary_label: str = "打开管理后台",
    logout_action: bool = False,
) -> HTMLResponse:
    """Render the shared light Nekro User Panel error shell."""
    from admin_page import get_error_html

    return HTMLResponse(
        content=get_error_html(
            title=title,
            message=message,
            detail=detail,
            status_code=status_code,
            primary_href=primary_href,
            primary_label=primary_label,
            secondary_href=secondary_href,
            secondary_label=secondary_label,
            logout_action=logout_action,
        ),
        status_code=status_code,
    )

@app.get("/webui", include_in_schema=False)
async def webui_index(request: Request, _user: Optional[PanelUser] = Depends(get_optional_panel_user_lenient)):
    """
    拦截前端首页请求，注入导航裁剪脚本。
    需要确定用户绑定的实例来获取对应的前端页面。
    
    注意：使用宽松认证（不抛401），因为首页需要能加载登录页面。
    如果 token 过期，_user 为 None，会使用第一个实例加载前端（显示登录页）。
    安全性由前端注入脚本保证：过期 token 的 API 请求会收到 401 并跳转登录。
    """
    import httpx

    # 判断是否为 admin
    is_admin_user = _user and _user.instance_id == "__admin__"

    # 未登录时不再读取任何 NA 实例。
    # 旧逻辑会默认取 instances.json 的第一个实例加载登录页，
    # 如果第一个实例离线，所有用户访问 /webui 都会 500。
    # 这里返回面板自带的轻量登录页，登录成功后再按 JWT 绑定实例加载对应 NA。
    if not _user:
        from admin_page import get_login_html

        return HTMLResponse(content=get_login_html())

    # Determine the target instance.
    instance = None
    if is_admin_user:
        # admin 用户必须显式选择实例，不再默认取第一个实例。
        # 否则第一个实例离线时会把 admin /webui 打成 500。
        import urllib.parse
        admin_instance_id = urllib.parse.unquote(request.cookies.get("admin_instance", ""))
        if admin_instance_id:
            instance = get_instance(admin_instance_id)
        if not instance:
            return RedirectResponse(url="/panel/admin", status_code=302)
    elif _user:
        # 已认证用户：只能访问自己绑定的实例
        instance = _user.instance
        if not instance:
            return render_panel_error_page(
                title="账户未绑定有效实例",
                message="当前账号没有可用的实例绑定。请联系管理员检查账号配置。",
                status_code=403,
                primary_href="/webui",
                primary_label="返回登录页",
                secondary_href="",
                secondary_label="",
            )

    if not instance:
        return render_panel_error_page(
            title="无可用实例",
            message="面板暂时没有可路由的 Nekro Agent 实例。",
            status_code=503,
            primary_href="/webui",
            primary_label="返回登录页",
            secondary_href="",
            secondary_label="",
        )

    # 从对应 NA 后端获取原始 index.html。
    # 后端离线时返回可读错误，不让异常冒泡成 Internal Server Error。
    try:
        na_token = await get_na_backend_token(instance)
        async with httpx.AsyncClient(base_url=instance.na_backend_url, timeout=10.0) as client:
            resp = await client.get("/webui/", headers={"Authorization": f"Bearer {na_token}"})
            if resp.status_code != 200:
                return render_panel_error_page(
                    title="无法加载实例前端",
                    message="目标实例已响应，但未返回可用的 WebUI 页面。",
                    detail=f"实例 {instance.id} 返回 HTTP {resp.status_code}",
                    status_code=502,
                    primary_href="/webui",
                    primary_label="返回登录页",
                    secondary_href="/webui",
                    secondary_label="重新尝试",
                    logout_action=True,
                )
            html = resp.text
    except Exception as exc:
        return render_panel_error_page(
            title="实例暂时不可用",
            message="当前账号绑定的 Nekro Agent 实例暂时无法访问。",
            detail=f"实例 {instance.id} · {instance.na_backend_url}",
            status_code=502,
            primary_href="/webui",
            primary_label="返回登录页",
            secondary_href="/webui",
            secondary_label="重新尝试",
            logout_action=True,
        )

    # 注入脚本
    if is_admin_user:
        # admin: 注入登录拦截 + 管理条（不注入导航过滤和路由守卫）
        from frontend_inject import get_login_override_script, get_admin_toolbar_script
        inject_script = get_login_override_script() + get_admin_toolbar_script(instance.id, instance.comment or instance.id)
    else:
        # 普通用户: 注入完整脚本（登录拦截 + 导航过滤）
        inject_script = get_full_inject_html()
    html = html.replace("</head>", f"{inject_script}</head>")

    return HTMLResponse(content=html)


# ============ 启动入口 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=PANEL_HOST,
        port=PANEL_PORT,
        reload=False,
        log_level="info",
    )
