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
    get_optional_panel_user_lenient,
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
    return {"username": user.username, "instance_id": user.instance_id, "role": "user"}


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
) -> HTMLResponse:
    """Render a polished standalone panel error page."""
    import html
    safe_title = html.escape(title)
    safe_message = html.escape(message)
    safe_detail = html.escape(detail)
    safe_primary_href = html.escape(primary_href, quote=True)
    safe_primary_label = html.escape(primary_label)
    safe_secondary_href = html.escape(secondary_href, quote=True) if secondary_href else ""
    safe_secondary_label = html.escape(secondary_label) if secondary_label else ""
    secondary_action = f'<a class="secondary" href="{safe_secondary_href}">{safe_secondary_label}</a>' if safe_secondary_href and safe_secondary_label else ""
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="dark" />
  <title>{safe_title} · Nekro User Panel</title>
  <style>
    :root {{
      --bg:#0b0d12; --surface:#11151d; --surface-2:#151a24; --field:#0c1017;
      --line:#242b38; --line-strong:#343d4f; --text:#eef3fb; --muted:#9aa6b7; --faint:#6e7a8c;
      --accent:#8fb8ff; --accent-hover:#a8c8ff; --accent-text:#07101f; --danger:#ff8d9b; --warning:#ffd08a; --success:#85e1b4;
      font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",system-ui,sans-serif;
    }}
    *{{box-sizing:border-box}} html,body{{min-height:100%}}
    body{{margin:0;min-height:100dvh;color:var(--text);background:radial-gradient(circle at 14% 12%,rgba(255,208,138,.13),transparent 28rem),radial-gradient(circle at 88% 86%,rgba(143,184,255,.10),transparent 28rem),var(--bg);display:grid;place-items:center;padding:28px}}
    body:before{{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.032) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.026) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(to bottom,black,transparent 80%)}}
    .shell{{position:relative;z-index:1;width:min(880px,100%);display:grid;grid-template-columns:280px minmax(0,1fr);border:1px solid var(--line);background:rgba(17,21,29,.9);box-shadow:0 24px 80px rgba(0,0,0,.42)}}
    .status{{border-right:1px solid var(--line);padding:34px;background:linear-gradient(180deg,rgba(255,255,255,.03),transparent);display:flex;flex-direction:column;justify-content:space-between;gap:42px}}
    .brand{{display:flex;align-items:center;gap:12px;color:var(--muted);font-size:13px}}.logo{{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;background:var(--warning);color:#1d1203;font-weight:850;letter-spacing:-.04em}}
    .code{{font-size:54px;line-height:.95;letter-spacing:-.05em;font-weight:850;color:var(--warning);font-variant-numeric:tabular-nums}}
    .mini{{margin-top:10px;color:var(--faint);font-size:13px;line-height:1.55}}
    .content{{padding:42px;display:flex;flex-direction:column;justify-content:center}}
    h1{{margin:0;font-size:32px;line-height:1.12;letter-spacing:-.03em;text-wrap:balance}}
    .msg{{margin:14px 0 0;color:var(--muted);line-height:1.75;font-size:15px;max-width:62ch;text-wrap:pretty}}
    .detail{{margin-top:22px;border:1px solid var(--line);background:var(--field);border-radius:12px;padding:13px 14px;color:#c5cfdd;font-size:13px;line-height:1.6;word-break:break-all;font-variant-numeric:tabular-nums}}
    .actions{{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}}
    a{{min-height:40px;display:inline-flex;align-items:center;justify-content:center;padding:0 14px;border-radius:10px;text-decoration:none;font-size:13px;font-weight:750;transition:background .18s ease,border-color .18s ease,transform .18s ease}}
    a:active{{transform:translateY(1px)}}.primary{{background:var(--accent);color:var(--accent-text)}}.primary:hover{{background:var(--accent-hover)}}.secondary{{border:1px solid var(--line-strong);color:var(--text);background:var(--surface-2)}}.secondary:hover{{border-color:var(--accent)}}
    .hint{{margin-top:24px;padding-top:18px;border-top:1px solid var(--line);color:var(--faint);font-size:12px;line-height:1.65}}
    @media(max-width:760px){{body{{padding:18px;place-items:start center}}.shell{{grid-template-columns:1fr}}.status{{border-right:0;border-bottom:1px solid var(--line);padding:26px}}.content{{padding:28px}}.code{{font-size:42px}}h1{{font-size:26px}}}}
    @media(prefers-reduced-motion:reduce){{*,*:before,*:after{{transition-duration:.01ms!important;animation-duration:.01ms!important}}}}
  </style>
</head>
<body>
  <main class="shell">
    <aside class="status">
      <div class="brand"><div class="logo">N</div><span>Nekro User Panel</span></div>
      <div><div class="code">{status_code}</div><div class="mini">实例路由没有完成。面板仍然在线。</div></div>
    </aside>
    <section class="content">
      <h1>{safe_title}</h1>
      <p class="msg">{safe_message}</p>
      {f'<div class="detail">{safe_detail}</div>' if safe_detail else ''}
      <div class="actions">
        <a class="primary" href="{safe_primary_href}">{safe_primary_label}</a>
        {secondary_action}
      </div>
      <div class="hint">这只影响当前绑定实例。其他用户的登录页和其他实例不会被这个错误拖下线。</div>
    </section>
  </main>
</body>
</html>"""
    return HTMLResponse(content=page, status_code=status_code)


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
        login_html = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="dark" />
  <title>Nekro User Panel</title>
  <style>
    :root {
      --bg: #0b0d12;
      --surface: #11151d;
      --surface-2: #151a24;
      --field: #0c1017;
      --line: #242b38;
      --line-strong: #333c4d;
      --text: #eef3fb;
      --muted: #9aa6b7;
      --faint: #6e7a8c;
      --accent: #8fb8ff;
      --accent-hover: #a8c8ff;
      --accent-text: #07101f;
      --danger: #ff8d9b;
      --success: #85e1b4;
      --warning: #ffd08a;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", system-ui, sans-serif;
    }
    * { box-sizing: border-box; }
    html, body { min-height: 100%; }
    body {
      margin: 0;
      min-height: 100dvh;
      color: var(--text);
      background:
        radial-gradient(circle at 14% 10%, rgba(143,184,255,.12), transparent 28rem),
        radial-gradient(circle at 86% 84%, rgba(133,225,180,.07), transparent 26rem),
        var(--bg);
      display: grid;
      place-items: center;
      padding: 28px;
    }
    body::before {
      content: "";
      position: fixed; inset: 0;
      pointer-events: none;
      background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
      background-size: 48px 48px;
      mask-image: linear-gradient(to bottom, black, transparent 78%);
    }
    .wrap {
      position: relative;
      z-index: 1;
      width: min(1020px, 100%);
      display: grid;
      grid-template-columns: minmax(0, 1fr) 420px;
      border: 1px solid var(--line);
      background: color-mix(in srgb, var(--surface) 92%, transparent);
      box-shadow: 0 22px 70px rgba(0,0,0,.38);
      min-height: 600px;
    }
    .context {
      padding: 44px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      border-right: 1px solid var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,.025), transparent);
    }
    .topline { display: flex; align-items: center; gap: 12px; color: var(--muted); font-size: 13px; }
    .logo { width: 34px; height: 34px; display:grid; place-items:center; background: var(--accent); color: var(--accent-text); font-weight: 800; border-radius: 10px; letter-spacing: -.04em; }
    h1 { margin: 0; max-width: 12ch; font-size: 52px; line-height: .98; letter-spacing: -.035em; text-wrap: balance; }
    .copy { max-width: 58ch; margin: 20px 0 0; color: var(--muted); line-height: 1.72; font-size: 15px; text-wrap: pretty; }
    .rule-list { display: grid; gap: 12px; margin-top: 34px; padding: 0; list-style: none; max-width: 620px; }
    .rule-list li {
      display: grid; grid-template-columns: 10px 1fr; gap: 12px; align-items: start;
      color: #c9d2df; font-size: 14px; line-height: 1.55;
    }
    .dot { width: 7px; height: 7px; margin-top: 7px; border-radius: 50%; background: var(--success); box-shadow: 0 0 16px rgba(133,225,180,.5); }
    .meta { display:flex; flex-wrap:wrap; gap: 8px; margin-top: 40px; }
    .meta span { color: var(--faint); border: 1px solid var(--line); padding: 7px 9px; border-radius: 9px; font-size: 12px; font-variant-numeric: tabular-nums; background: rgba(255,255,255,.018); }
    .panel { padding: 44px 38px; display:flex; flex-direction:column; justify-content:center; background: var(--surface-2); }
    .panel h2 { margin: 0; font-size: 24px; line-height: 1.18; letter-spacing: -.02em; }
    .panel p { margin: 10px 0 28px; color: var(--muted); line-height: 1.6; font-size: 14px; }
    label { display:block; margin: 18px 0 8px; color: #dbe3ef; font-size: 13px; font-weight: 650; }
    input {
      width: 100%;
      min-height: 44px;
      border-radius: 10px;
      border: 1px solid var(--line-strong);
      background: var(--field);
      color: var(--text);
      padding: 11px 12px;
      font-size: 15px;
      outline: none;
      transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
    }
    input::placeholder { color: #8792a3; opacity: 1; }
    input:hover { border-color: #455066; }
    input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(143,184,255,.16); background: #0a0e15; }
    button {
      width: 100%;
      min-height: 44px;
      margin-top: 22px;
      border: 0;
      border-radius: 10px;
      background: var(--accent);
      color: var(--accent-text);
      font-weight: 750;
      font-size: 14px;
      cursor: pointer;
      transition: background .18s ease, transform .18s ease, box-shadow .18s ease;
    }
    button:hover { background: var(--accent-hover); box-shadow: 0 10px 24px rgba(143,184,255,.18); }
    button:active { transform: translateY(1px); }
    button:disabled { opacity: .68; cursor: wait; box-shadow: none; }
    .err { min-height: 21px; margin-top: 13px; color: var(--danger); font-size: 13px; line-height: 1.5; }
    .note {
      margin-top: 24px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--faint);
      font-size: 12px;
      line-height: 1.65;
    }
    code { color: #b9c8df; background: rgba(255,255,255,.04); border: 1px solid var(--line); border-radius: 6px; padding: 1px 5px; }
    @media (max-width: 860px) {
      body { padding: 18px; place-items: start center; }
      .wrap { grid-template-columns: 1fr; min-height: auto; }
      .context { padding: 30px; border-right: 0; border-bottom: 1px solid var(--line); }
      .panel { padding: 30px; }
      h1 { font-size: 40px; max-width: 14ch; }
      .meta { margin-top: 28px; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; scroll-behavior: auto !important; }
    }
  </style>
</head>
<body>
  <main class="wrap">
    <section class="context" aria-label="面板说明">
      <div>
        <div class="topline"><div class="logo" aria-hidden="true">N</div><span>Nekro User Panel</span></div>
        <div style="margin-top:72px">
          <h1>实例登录入口</h1>
          <p class="copy">先验证面板账号，再连接账号绑定的 Nekro Agent。登录页本身不会请求默认实例，因此一个离线实例不会拖垮其他人的入口。</p>
          <ul class="rule-list">
            <li><span class="dot"></span><span>未认证访问只渲染本地登录页，不调用 <code>/api/token</code>。</span></li>
            <li><span class="dot"></span><span>普通用户只会被路由到自己的绑定实例。</span></li>
            <li><span class="dot"></span><span>管理员需要显式选择实例，不再回退到列表第一项。</span></li>
          </ul>
        </div>
      </div>
      <div class="meta"><span>route scoped</span><span>no default instance</span><span>status-aware errors</span></div>
    </section>
    <form class="panel" id="loginForm" autocomplete="on">
      <h2>登录</h2>
      <p>使用分配的面板账号。成功后会打开对应实例的控制台。</p>
      <label for="username">用户名</label>
      <input id="username" name="username" autocomplete="username" placeholder="例如 GBNA1" required autofocus />
      <label for="password">密码</label>
      <input id="password" name="password" type="password" autocomplete="current-password" placeholder="输入面板密码" required />
      <button type="submit">登录并打开实例</button>
      <div class="err" id="err" role="status" aria-live="polite"></div>
      <div class="note">如果登录后提示实例不可用，说明你绑定的 NA 后端离线。其他用户不受影响。</div>
    </form>
  </main>
  <script>
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const btn = form.querySelector('button');
      const err = document.getElementById('err');
      btn.disabled = true;
      btn.textContent = '正在验证';
      err.textContent = '';
      const body = { username: form.username.value.trim(), password: form.password.value };
      try {
        const res = await fetch('/panel/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.detail || '登录失败，请检查用户名和密码');
        if (data.access_token) localStorage.setItem('panel_token', data.access_token);
        location.href = data.redirect || '/webui';
      } catch (e) {
        err.textContent = e.message || '登录失败，请稍后再试';
      } finally {
        btn.disabled = false;
        btn.textContent = '登录并打开实例';
      }
    });
  </script>
</body>
</html>"""
        return HTMLResponse(content=login_html)

    # 确定目标实例
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
                message="当前账号已通过认证，但没有找到可用的 Nekro Agent 实例绑定。请联系管理员检查 instances.json。",
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
                    message="绑定实例已响应请求，但没有返回可用的 WebUI 页面。",
                    detail=f"实例 {instance.id} 返回 HTTP {resp.status_code}",
                    status_code=502,
                    primary_href="/webui",
                    primary_label="重新尝试",
                    secondary_href="",
                    secondary_label="",
                )
            html = resp.text
    except Exception as exc:
        return render_panel_error_page(
            title="实例暂时不可用",
            message="面板已经确认你的登录状态，但当前绑定的 Nekro Agent 后端无法连接。",
            detail=f"实例 {instance.id} · {instance.na_backend_url}",
            status_code=502,
            primary_href="/webui",
            primary_label="重新尝试",
            secondary_href="",
            secondary_label="",
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

