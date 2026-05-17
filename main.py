"""
Nekro User Panel - 主应用入口（多实例版）
一个轻量级反向代理网关，为多个 Nekro Agent 实例提供受限的用户端管理面板。
每个用户绑定一个 NA 实例，登录后所有请求自动路由到对应实例。
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

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
    is_admin,
)
from config import PANEL_HOST, PANEL_PORT, PANEL_JWT_EXPIRE_HOURS, INSTANCES, INSTANCES_FILE, get_instance, reload_instances
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


@app.get("/panel/nav-config", tags=["Panel Config"])
async def get_nav_config(_user: PanelUser = Depends(get_current_panel_user)):
    """获取用户端面板的导航配置"""
    return filter_navigation_config()


@app.get("/panel/user-info", tags=["Panel Auth"])
async def get_panel_user_info(user: PanelUser = Depends(get_current_panel_user)):
    """获取当前面板用户信息"""
    return {"username": user.username, "instance_id": user.instance_id, "role": "user"}


@app.post("/panel/reload-instances", tags=["Panel Admin"])
async def reload_instances_endpoint(user: PanelUser = Depends(get_current_panel_user)):
    """热重载实例配置（管理员专用）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    try:
        reload_instances()
        return {"status": "ok", "message": "实例配置已重载"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


# ============ 管理员 API ============


@app.get("/panel/admin/instances", tags=["Panel Admin"])
async def list_instances(user: PanelUser = Depends(get_current_panel_user)):
    """获取所有实例列表（管理员专用）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    return [
        {
            "id": inst.id,
            "na_port": inst.na_port,
            "na_host": inst.na_host,
            "na_admin_user": inst.na_admin_user,
            "comment": inst.comment,
            "allowed_model_groups": inst.allowed_model_groups,
        }
        for inst in INSTANCES.values()
    ]


@app.get("/panel/admin/instances/{instance_id}", tags=["Panel Admin"])
async def get_instance_detail(instance_id: str, user: PanelUser = Depends(get_current_panel_user)):
    """获取单个实例详情（管理员专用，包含密码）"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
    inst = get_instance(instance_id)
    if not inst:
        return JSONResponse(status_code=404, content={"detail": "实例不存在"})
    return inst.model_dump()


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
    required = ["id", "panel_password", "na_port", "na_admin_pass"]
    for field in required:
        if field not in data or not data[field]:
            return JSONResponse(status_code=400, content={"detail": f"缺少必填字段: {field}"})

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
async def admin_page(user: PanelUser = Depends(get_current_panel_user)):
    """管理员页面"""
    if not is_admin(user):
        return JSONResponse(status_code=403, content={"detail": "仅管理员可操作"})
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
    response.set_cookie(
        key="admin_instance",
        value=instance_id,
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
    instance_id = request.cookies.get("admin_instance", "")
    inst = get_instance(instance_id) if instance_id else None
    if inst:
        return {"instance_id": inst.id, "comment": inst.comment, "na_port": inst.na_port}
    return {"instance_id": None, "comment": None, "na_port": None}


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
async def webui_proxy(request: Request, _user: Optional[PanelUser] = Depends(get_optional_panel_user)):
    """代理前端静态文件请求到 NA 后端"""
    return await proxy_request(request, _user)


@app.get("/", include_in_schema=False)
async def root_redirect():
    """根路径重定向到前端"""
    return RedirectResponse(url="/webui", status_code=302)


# ============ 注入前端脚本 ============


@app.get("/webui", include_in_schema=False)
async def webui_index(request: Request, _user: Optional[PanelUser] = Depends(get_optional_panel_user)):
    """
    拦截前端首页请求，注入导航裁剪脚本。
    需要确定用户绑定的实例来获取对应的前端页面。
    """
    import httpx

    # 判断是否为 admin
    is_admin_user = _user and _user.instance_id == "__admin__"

    # 确定目标实例
    instance = None
    if is_admin_user:
        # admin 用户：从 cookie 中读取选择的实例
        admin_instance_id = request.cookies.get("admin_instance")
        if admin_instance_id:
            instance = get_instance(admin_instance_id)
        if not instance:
            from config import INSTANCES as _INSTANCES
            if _INSTANCES:
                instance = next(iter(_INSTANCES.values()))
    elif _user and _user.instance:
        instance = _user.instance
    else:
        # 未登录时，使用第一个可用实例来加载前端页面（登录页是通用的）
        from config import INSTANCES
        if INSTANCES:
            instance = next(iter(INSTANCES.values()))

    if not instance:
        return HTMLResponse(content="<h1>无可用实例</h1>", status_code=503)

    # 从对应 NA 后端获取原始 index.html
    na_token = await get_na_backend_token(instance)
    async with httpx.AsyncClient(base_url=instance.na_backend_url, timeout=10.0) as client:
        resp = await client.get("/webui/", headers={"Authorization": f"Bearer {na_token}"})
        if resp.status_code != 200:
            return HTMLResponse(content="<h1>无法加载前端页面</h1>", status_code=502)
        html = resp.text

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
