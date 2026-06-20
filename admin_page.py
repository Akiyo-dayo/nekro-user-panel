"""Inline UI shells for Nekro User Panel."""

import html


BRAND_STYLE = """
:root{
  --bg:#fff0f3;--bg-soft:#ffe8ee;--surface:#fff8fb;--surface-2:#fff1f6;--surface-3:#fffafd;
  --line:#f2cfd9;--line-strong:#eab8c6;--ink:#261b25;--muted:#755d6a;--faint:#9a7f8c;
  --brand:#ea5252;--brand-2:#ff9bb3;--brand-3:#9c6ade;--sun:#ffd34d;
  --brand-soft:rgba(234,82,82,.12);--accent-soft:rgba(255,155,179,.18);
  --success:#2fa66a;--warning:#f59e0b;--danger:#e5484d;--info:#2f80ed;
  --shadow:0 18px 42px rgba(166,70,92,.13);--shadow-soft:0 10px 26px rgba(234,82,82,.13);
  --radius:8px;--ease:cubic-bezier(.16,1,.3,1);
  font-family:Inter,"Open Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
}
*{box-sizing:border-box}html,body{min-height:100%}
body{
  margin:0;color:var(--ink);background:
    radial-gradient(circle at 12% 8%,rgba(234,82,82,.16),transparent 30rem),
    radial-gradient(circle at 84% 14%,rgba(255,155,179,.18),transparent 32rem),
    linear-gradient(135deg,var(--bg),#fff8fb 48%,#fff3f7);
  font-size:14px;
}
body:before{
  content:"";position:fixed;inset:0;pointer-events:none;opacity:.55;
  background-image:
    linear-gradient(rgba(234,82,82,.045) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,155,179,.045) 1px,transparent 1px);
  background-size:44px 44px;
  mask-image:linear-gradient(to bottom,black,transparent 78%);
}
button,input,select{font:inherit}button{letter-spacing:0}
a{color:inherit}
.brand-word{font-weight:850;letter-spacing:0}
.brand-word .hot{color:var(--brand)}.brand-word .cool{color:var(--brand-2)}
.brand-mark{
  width:38px;height:38px;border-radius:8px;display:grid;place-items:center;position:relative;isolation:isolate;
  background:linear-gradient(135deg,#fff,var(--surface-3));border:1px solid rgba(234,82,82,.20);box-shadow:var(--shadow-soft);
  color:var(--brand);font-weight:900;font-size:13px;
}
.brand-mark:after{content:"";position:absolute;right:6px;bottom:6px;width:8px;height:8px;border-radius:50%;background:var(--brand-3);box-shadow:0 0 0 3px rgba(32,207,227,.15)}
.btn{
  min-height:36px;padding:0 13px;border-radius:var(--radius);border:1px solid var(--line-strong);
  background:var(--surface);color:var(--ink);font-size:13px;font-weight:760;cursor:pointer;white-space:nowrap;
  display:inline-flex;align-items:center;justify-content:center;gap:7px;text-decoration:none;
  transition:background .18s var(--ease),border-color .18s var(--ease),box-shadow .18s var(--ease),transform .18s var(--ease),color .18s var(--ease);
}
.btn:hover{border-color:rgba(234,82,82,.38);box-shadow:0 8px 18px rgba(55,64,88,.10);transform:translateY(-1px)}
.btn:active{transform:translateY(0) scale(.99)}
.btn:disabled{opacity:.68;cursor:wait;transform:none;box-shadow:none}
.btn:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid rgba(234,82,82,.18);outline-offset:2px}
.btn-primary{position:relative;overflow:hidden;background:linear-gradient(135deg,var(--brand),#f06f78);border-color:transparent;color:#fff;box-shadow:0 10px 24px rgba(234,82,82,.22)}
.btn-primary:before{content:"";position:absolute;inset:-80% auto -80% -45%;width:38%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.42),transparent);transform:rotate(16deg);transition:left .55s var(--ease)}
.btn-primary:hover:before{left:115%}.btn-primary:hover{border-color:transparent;color:#fff}
.btn-secondary{background:rgba(156,106,222,.10);border-color:rgba(156,106,222,.20);color:#5b3a92}
.btn-good{color:var(--success);border-color:rgba(47,166,106,.25);background:rgba(47,166,106,.08)}
.btn-danger{color:var(--danger);border-color:rgba(229,72,77,.24);background:rgba(229,72,77,.06)}
.btn-sm{min-height:30px;padding:0 9px;font-size:12px}
.badge{
  display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:4px 8px;font-size:11px;font-weight:820;white-space:nowrap;
  border:1px solid rgba(47,166,106,.24);background:rgba(47,166,106,.08);color:var(--success);
}
.badge:before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor;box-shadow:0 0 0 4px color-mix(in srgb,currentColor 12%,transparent)}
.badge.online:before,.badge.reachable:before{animation:pulse 1.6s var(--ease) infinite}
.badge.offline,.badge.unconfigured{border-color:rgba(229,72,77,.25);background:rgba(229,72,77,.07);color:var(--danger)}
.badge.partial,.badge.unknown{border-color:rgba(245,158,11,.28);background:rgba(245,158,11,.09);color:#9a6400}
@keyframes pulse{0%,100%{box-shadow:0 0 0 3px color-mix(in srgb,currentColor 10%,transparent)}50%{box-shadow:0 0 0 7px color-mix(in srgb,currentColor 0%,transparent)}}
@keyframes riseIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes toastIn{from{opacity:0;transform:translateY(-8px) scale(.98)}to{opacity:1;transform:translateY(0) scale(1)}}
@keyframes tinyWave{0%,100%{transform:translateY(0)}50%{transform:translateY(-2px)}}
@media(prefers-reduced-motion:reduce){
  *,*:before,*:after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}
}
"""


def get_login_html() -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light" />
  <title>Nekro User Panel</title>
  <style>
    {BRAND_STYLE}
    body{{min-height:100dvh;display:grid;place-items:center;padding:28px}}
    .login-shell{{position:relative;z-index:1;width:min(1060px,100%);min-height:620px;display:grid;grid-template-columns:440px minmax(0,1fr);border:1px solid var(--line);background:rgba(255,255,255,.82);box-shadow:var(--shadow);border-radius:var(--radius);overflow:hidden;animation:riseIn .45s var(--ease) both}}
    .panel{{padding:46px 42px;display:flex;flex-direction:column;justify-content:center;background:rgba(255,255,255,.94);border-right:1px solid var(--line)}}
    .brand-line{{display:flex;align-items:center;gap:12px;margin-bottom:42px}}
    .brand-line:hover .brand-mark{{animation:tinyWave .42s var(--ease) both}}
    h1{{margin:0;font-size:28px;line-height:1.2;letter-spacing:0;text-wrap:balance}}
    .lead{{margin:10px 0 26px;color:var(--muted);line-height:1.65;font-size:14px;max-width:42ch;text-wrap:pretty}}
    label{{display:block;margin:17px 0 8px;color:var(--ink);font-size:13px;font-weight:760}}
    input{{width:100%;min-height:46px;border-radius:var(--radius);border:1px solid var(--line-strong);background:#fff;color:var(--ink);padding:11px 12px;font-size:15px;outline:none;transition:border-color .18s var(--ease),box-shadow .18s var(--ease),background .18s var(--ease)}}
    input::placeholder{{color:#7f8796;opacity:1}}input:hover{{border-color:#c4ccdb}}input:focus{{border-color:var(--brand);box-shadow:0 0 0 4px rgba(234,82,82,.12);background:#fff}}
    .submit{{width:100%;min-height:46px;margin-top:22px}}
    .err{{min-height:21px;margin-top:13px;color:var(--danger);font-size:13px;line-height:1.5}}
    .err.shake{{animation:shake .24s var(--ease)}}@keyframes shake{{0%,100%{{transform:translateX(0)}}30%{{transform:translateX(-4px)}}70%{{transform:translateX(4px)}}}}
    .note{{margin-top:24px;padding-top:18px;border-top:1px solid var(--line);color:var(--faint);font-size:12px;line-height:1.65}}
    .showcase{{position:relative;padding:46px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;background:
      linear-gradient(135deg,rgba(255,246,250,.95),rgba(247,251,255,.92)),
      radial-gradient(circle at 78% 18%,rgba(156,106,222,.18),transparent 20rem)}}
    .showcase:before{{content:">NA_";position:absolute;right:-18px;top:72px;font-size:126px;line-height:1;font-weight:900;color:rgba(234,82,82,.08);letter-spacing:-.04em;transform:rotate(-6deg)}}
    .showcase:after{{content:"";position:absolute;inset:auto 36px 42px auto;width:150px;height:150px;border:1px solid rgba(156,106,222,.12);background:linear-gradient(135deg,rgba(234,82,82,.10),rgba(32,207,227,.10));border-radius:28px;transform:rotate(10deg);opacity:.9}}
    .hero-copy{{position:relative;max-width:58ch}}.hero-copy h2{{margin:0;font-size:34px;line-height:1.12;letter-spacing:0;text-wrap:balance}}.hero-copy p{{margin:15px 0 0;color:var(--muted);line-height:1.72;font-size:15px;text-wrap:pretty}}
    .service-card{{position:relative;width:min(360px,100%);border:1px solid rgba(234,82,82,.13);background:rgba(255,255,255,.82);box-shadow:var(--shadow-soft);border-radius:var(--radius);padding:16px;display:grid;gap:12px;backdrop-filter:blur(12px)}}
    .service-row{{display:flex;justify-content:space-between;gap:14px;color:var(--muted);font-size:13px}}.service-row b{{color:var(--ink);font-weight:820}}.service-row .ok{{color:var(--success)}}
    .chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:24px}}.chip{{border:1px solid rgba(156,106,222,.18);background:rgba(156,106,222,.08);color:#5b3a92;border-radius:999px;padding:6px 9px;font-size:12px;font-weight:760}}
    @media(max-width:880px){{body{{padding:18px;place-items:start center}}.login-shell{{grid-template-columns:1fr;min-height:auto}}.panel{{padding:32px;border-right:0}}.showcase{{order:-1;padding:28px;min-height:230px;border-bottom:1px solid var(--line)}}.hero-copy h2{{font-size:26px}}.showcase:before{{font-size:74px;top:26px}}}}
  </style>
</head>
<body>
  <main class="login-shell">
    <form class="panel" id="loginForm" autocomplete="on">
      <div class="brand-line">
        <div class="brand-mark" aria-hidden="true">&gt;NA</div>
        <div class="brand-word"><span class="hot">N</span>ekro <span class="cool">User Panel</span></div>
      </div>
      <h1>登录 Nekro User Panel</h1>
      <p class="lead">进入实例管理、权限配置和运行状态查看。登录后会自动路由到账号对应的 NA 实例。</p>
      <label for="username">用户名</label>
      <input id="username" name="username" autocomplete="username" placeholder="例如 GBNA1" required autofocus />
      <label for="password">密码</label>
      <input id="password" name="password" type="password" autocomplete="current-password" placeholder="输入面板密码" required />
      <button class="btn btn-primary submit" type="submit"><span id="btnText">登录面板</span></button>
      <div class="err" id="err" role="status" aria-live="polite"></div>
      <div class="note">如果登录后提示实例不可用，说明绑定的 NA 后端暂时离线。其他账号和实例不受影响。</div>
    </form>
    <section class="showcase" aria-label="服务状态">
      <div class="hero-copy">
        <h2>Denia 总部入口</h2>
        <p>面板认证独立于任何单个 NA 实例，节点离线不会阻塞登录页。管理员可在后台切换、维护和探测全部实例。</p>
        <div class="chips"><span class="chip">HTTP 节点接入</span><span class="chip">多集群路由</span><span class="chip">实例隔离</span></div>
      </div>
      <div class="service-card">
        <div class="service-row"><span>面板服务</span><b class="ok">在线</b></div>
        <div class="service-row"><span>登录 API</span><b class="ok">可用</b></div>
        <div class="service-row"><span>最近检查</span><b id="clock">--:--</b></div>
      </div>
    </section>
  </main>
  <script>
    const form = document.getElementById('loginForm');
    const clock = document.getElementById('clock');
    clock.textContent = new Date().toLocaleTimeString('zh-CN', {{hour12:false,hour:'2-digit',minute:'2-digit'}});
    form.addEventListener('submit', async (ev) => {{
      ev.preventDefault();
      const btn = form.querySelector('button');
      const btnText = document.getElementById('btnText');
      const err = document.getElementById('err');
      btn.disabled = true;
      btnText.textContent = '正在验证';
      err.textContent = '';
      err.classList.remove('shake');
      const body = {{ username: form.username.value.trim(), password: form.password.value }};
      try {{
        const res = await fetch('/panel/login', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify(body) }});
        const data = await res.json().catch(() => ({{}}));
        if (!res.ok) throw new Error(data.detail || '用户名或密码不正确，请重新输入。');
        if (data.access_token) {{
          localStorage.setItem('panel_token', data.access_token);
          localStorage.setItem('nekro_user_panel_token', data.access_token);
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('nekro_user_panel_username', body.username);
          localStorage.setItem('auth-storage', JSON.stringify({{ state: {{ token: data.access_token, userInfo: {{ username: body.username, userId: 1, perm_level: 2, perm_role: data.role === 'admin' ? 'Admin' : 'User' }} }}, version: 0 }}));
        }}
        document.querySelector('.login-shell').style.animation = 'riseIn .18s reverse var(--ease) both';
        setTimeout(() => {{ location.href = data.redirect || '/webui'; }}, 140);
      }} catch (e) {{
        err.textContent = e.message || '无法连接面板服务，请检查反向代理或后端容器。';
        err.classList.add('shake');
      }} finally {{
        btn.disabled = false;
        btnText.textContent = '登录面板';
      }}
    }});
  </script>
</body>
</html>"""


def get_error_html(
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
) -> str:
    safe_title = html.escape(title)
    safe_message = html.escape(message)
    safe_detail = html.escape(detail)
    safe_primary_href = html.escape(primary_href, quote=True)
    safe_primary_label = html.escape(primary_label)
    safe_secondary_href = html.escape(secondary_href, quote=True) if secondary_href else ""
    safe_secondary_label = html.escape(secondary_label) if secondary_label else ""
    primary_action = (
        f'<button class="btn btn-primary" type="button" onclick="returnToLogin()">{safe_primary_label}</button>'
        if logout_action
        else f'<a class="btn btn-primary" href="{safe_primary_href}">{safe_primary_label}</a>'
    )
    secondary_action = (
        f'<a class="btn" href="{safe_secondary_href}">{safe_secondary_label}</a>'
        if safe_secondary_href and safe_secondary_label
        else ""
    )
    detail_block = f'<details class="detail"><summary>查看诊断信息</summary><code>{safe_detail}</code></details>' if safe_detail else ""
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="light" />
  <title>{safe_title} | Nekro User Panel</title>
  <style>
    {BRAND_STYLE}
    body{{min-height:100dvh;display:grid;place-items:center;padding:28px}}
    .shell{{position:relative;z-index:1;width:min(880px,100%);display:grid;grid-template-columns:230px minmax(0,1fr);border:1px solid var(--line);background:rgba(255,255,255,.90);box-shadow:var(--shadow);border-radius:var(--radius);overflow:hidden;animation:riseIn .35s var(--ease) both}}
    .status{{padding:32px;border-right:1px solid var(--line);background:linear-gradient(180deg,rgba(234,82,82,.08),rgba(156,106,222,.05));display:flex;flex-direction:column;justify-content:space-between;gap:52px}}
    .brand{{display:flex;align-items:center;gap:11px;color:var(--muted);font-size:13px}}
    .code{{font-size:58px;line-height:1;font-weight:900;color:var(--brand);font-variant-numeric:tabular-nums}}
    .mini{{margin-top:10px;color:var(--muted);font-size:13px;line-height:1.55}}
    .content{{padding:42px;display:flex;flex-direction:column;justify-content:center}}
    h1{{margin:0;font-size:30px;line-height:1.16;letter-spacing:0;text-wrap:balance}}
    .msg{{margin:14px 0 0;color:var(--muted);line-height:1.75;font-size:15px;max-width:62ch;text-wrap:pretty}}
    .detail{{margin-top:22px;border:1px solid var(--line);background:var(--surface-2);border-radius:var(--radius);padding:12px 14px;color:var(--muted);font-size:13px;line-height:1.6;word-break:break-all}}
    .detail summary{{cursor:pointer;color:var(--ink);font-weight:760;margin-bottom:8px}}code{{white-space:normal;color:#394154}}
    .actions{{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}}
    .hint{{margin-top:24px;padding-top:18px;border-top:1px solid var(--line);color:var(--faint);font-size:12px;line-height:1.65}}
    @media(max-width:720px){{body{{padding:18px;place-items:start center}}.shell{{grid-template-columns:1fr}}.status{{border-right:0;border-bottom:1px solid var(--line);padding:24px}}.content{{padding:28px}}.code{{font-size:42px}}h1{{font-size:25px}}}}
  </style>
</head>
<body>
  <main class="shell">
    <aside class="status">
      <div class="brand"><div class="brand-mark" aria-hidden="true">&gt;NA</div><span>Nekro User Panel</span></div>
      <div><div class="code">{status_code}</div><div class="mini">当前请求没有完成</div></div>
    </aside>
    <section class="content">
      <h1>{safe_title}</h1>
      <p class="msg">{safe_message}</p>
      {detail_block}
      <div class="actions">{primary_action}{secondary_action}</div>
      <div class="hint">如果问题持续存在，请在总部后台检查实例状态、节点入口或后端端口。</div>
    </section>
  </main>
  <script>
    async function returnToLogin() {{
      try {{ await fetch('/panel/logout', {{ method: 'POST' }}); }} catch(e) {{}}
      try {{
        ['nekro_user_panel_token','nekro_user_panel_username','nekro_user_panel_userinfo','panel_token','token','auth-storage'].forEach(k => localStorage.removeItem(k));
        ['panel_token','admin_instance'].forEach(k => {{ document.cookie = k + '=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax'; }});
      }} catch(e) {{}}
      window.location.href = '/webui';
    }}
  </script>
</body>
</html>"""


def get_admin_html() -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="color-scheme" content="light" />
<title>Nekro User Panel Admin</title>
<style>
{BRAND_STYLE}
.app{{position:relative;z-index:1;min-height:100dvh;display:grid;grid-template-columns:252px minmax(0,1fr)}}
.sidebar{{position:sticky;top:0;height:100dvh;border-right:1px solid var(--line);background:rgba(255,248,251,.92);backdrop-filter:blur(16px);padding:22px;display:flex;flex-direction:column;gap:20px}}
.brand{{display:flex;align-items:center;gap:11px}}.brand:hover .brand-mark{{animation:tinyWave .42s var(--ease) both}}.brand b{{display:block;font-size:14px}}.brand .brand-sub{{display:block;color:var(--faint);font-size:12px;margin-top:2px}}
.nav{{display:grid;gap:8px}}.nav-item{{border:1px solid transparent;background:transparent;color:var(--muted);justify-content:flex-start;width:100%;box-shadow:none}}.nav-item.active{{background:var(--brand-soft);border-color:rgba(234,82,82,.14);color:var(--brand)}}.nav-item:hover{{background:rgba(234,82,82,.06);box-shadow:none}}
.nav-note{{border:1px solid var(--line);background:var(--surface-2);border-radius:var(--radius);padding:13px;color:var(--muted);font-size:12px;line-height:1.55}}
.nav-actions{{margin-top:auto;display:grid;gap:9px}}.side-btn{{width:100%;justify-content:flex-start}}
.main{{padding:28px;max-width:1480px;width:100%;margin:0 auto}}
.topbar{{position:sticky;top:0;z-index:10;margin:-28px -28px 18px;padding:22px 28px 16px;background:linear-gradient(180deg,rgba(255,240,243,.96),rgba(255,240,243,.82) 74%,rgba(255,240,243,0));backdrop-filter:blur(14px)}}
.topbar-row{{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}}.crumb{{margin:0 0 8px;color:var(--brand);font-size:12px;font-weight:820}}.title{{margin:0;font-size:27px;line-height:1.15;letter-spacing:0;text-wrap:balance}}.sub{{margin:8px 0 0;color:var(--muted);line-height:1.55;max-width:76ch;text-wrap:pretty}}.toolbar{{display:flex;gap:9px;align-items:center;flex-wrap:wrap;justify-content:flex-end}}
.ops-strip{{display:grid;grid-template-columns:minmax(260px,1.45fr) repeat(3,minmax(140px,1fr));gap:10px;margin-bottom:18px}}
.stat{{border:1px solid rgba(234,82,82,.14);background:rgba(255,248,251,.86);border-radius:var(--radius);padding:13px 14px;min-width:0;box-shadow:0 8px 22px rgba(166,70,92,.07);animation:riseIn .32s var(--ease) both}}.stat:nth-child(2){{animation-delay:.03s}}.stat:nth-child(3){{animation-delay:.06s}}.stat:nth-child(4){{animation-delay:.09s}}
.stat span{{display:block;color:var(--faint);font-size:12px}}.stat b{{display:block;margin-top:6px;font-size:18px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.stat.current{{background:linear-gradient(135deg,#fff,rgba(234,82,82,.07));border-color:rgba(234,82,82,.18)}}.stat.current b{{color:var(--brand)}}
.section{{margin-top:20px}}.section-head{{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:10px}}.section-head h2{{margin:0;font-size:17px;letter-spacing:0}}.section-head p{{margin:5px 0 0;color:var(--muted);font-size:13px;line-height:1.45}}
.node-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:12px}}.instance-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}}
.card{{border:1px solid rgba(234,82,82,.13);background:linear-gradient(145deg,rgba(255,250,252,.96),rgba(255,243,247,.90));border-radius:var(--radius);padding:15px;display:grid;gap:12px;min-width:0;box-shadow:0 10px 28px rgba(166,70,92,.08);transition:border-color .18s var(--ease),box-shadow .18s var(--ease),transform .18s var(--ease);animation:riseIn .28s var(--ease) both}}
.card:hover{{border-color:rgba(234,82,82,.24);box-shadow:0 14px 30px rgba(166,70,92,.13);transform:translateY(-1px)}}.card-head{{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}}.card h3{{margin:0;font-size:15px;line-height:1.3;letter-spacing:0}}.caption{{margin-top:4px;color:var(--muted);font-size:12px;line-height:1.45}}
.fields{{display:grid;gap:7px}}.field{{display:flex;justify-content:space-between;gap:12px;border:1px solid rgba(242,207,217,.70);background:rgba(255,255,255,.48);border-radius:var(--radius);padding:7px 9px;min-width:0}}.field span:first-child{{color:var(--faint);font-size:12px;white-space:nowrap}}.field span:last-child{{color:#59404d;font-size:12px;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}}
.chips{{display:flex;gap:6px;flex-wrap:wrap}}.chip{{border:1px solid rgba(156,106,222,.18);background:rgba(156,106,222,.08);color:#6845a0;border-radius:999px;padding:4px 7px;font-size:11px;font-weight:720}}.actions{{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;margin-top:2px}}
.instance-card{{position:relative;overflow:hidden;gap:13px}}.instance-card:before{{content:"";position:absolute;inset:0 auto 0 0;width:4px;background:linear-gradient(180deg,var(--brand-2),var(--brand));opacity:.68}}.instance-card .card-head,.instance-card .instance-meta,.instance-card .chips,.instance-card .actions,.instance-card details{{position:relative}}.instance-meta{{display:flex;gap:7px;flex-wrap:wrap}}.meta-pill{{border:1px solid rgba(234,82,82,.12);background:rgba(255,255,255,.58);border-radius:999px;padding:5px 8px;color:var(--muted);font-size:12px}}.meta-pill strong{{color:var(--ink);font-weight:760}}.status-note{{color:var(--faint);font-size:12px;line-height:1.45;min-height:18px}}.tech-details{{border-top:1px solid rgba(234,82,82,.10);padding-top:8px;color:var(--muted);font-size:12px}}.tech-details summary{{cursor:pointer;color:var(--faint);font-weight:720}}.tech-details code{{display:block;margin-top:7px;color:#6b5360;word-break:break-all;white-space:normal}}
.empty{{grid-column:1/-1;border:1px dashed var(--line-strong);border-radius:var(--radius);padding:28px;text-align:center;color:var(--muted);background:rgba(255,255,255,.76)}}.empty b{{display:block;color:var(--ink);margin-bottom:6px}}
.controls{{display:grid;grid-template-columns:minmax(220px,1fr) 190px auto auto;gap:9px;align-items:center;margin:0 0 12px}}.search input,.controls select{{width:100%;min-height:38px;border-radius:var(--radius);border:1px solid var(--line-strong);background:#fff;color:var(--ink);padding:0 11px;outline:none}}.search input:focus,.controls select:focus{{border-color:var(--brand);box-shadow:0 0 0 4px rgba(234,82,82,.10)}}.result-count{{color:var(--faint);font-size:12px;white-space:nowrap}}
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(24,32,51,.32);z-index:30;align-items:center;justify-content:center;padding:18px;backdrop-filter:blur(8px)}}.modal-overlay.active{{display:flex}}.modal{{width:min(700px,100%);max-height:calc(100dvh - 36px);overflow:auto;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 24px 80px rgba(55,64,88,.24);padding:20px;animation:riseIn .22s var(--ease) both}}.modal h2{{margin:0 0 14px;font-size:20px}}.form-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.form-group.full{{grid-column:1/-1}}.form-group label{{display:block;margin-bottom:6px;color:var(--ink);font-size:12px;font-weight:760}}.form-group input,.form-group select{{width:100%;min-height:39px;border-radius:var(--radius);border:1px solid var(--line-strong);background:#fff;color:var(--ink);padding:8px 10px;outline:none}}.form-group input[readonly]{{color:var(--muted);background:var(--surface-2)}}.form-section{{grid-column:1/-1;margin-top:2px;padding-top:12px;border-top:1px solid var(--line);color:var(--brand);font-size:12px;font-weight:850}}.hint{{margin-top:6px;color:var(--faint);font-size:12px;line-height:1.4}}.form-actions{{display:flex;justify-content:flex-end;gap:9px;margin-top:18px}}
.toast{{position:fixed;right:18px;top:18px;z-index:40;max-width:420px;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:var(--radius);padding:11px 13px;box-shadow:var(--shadow);font-size:13px;animation:toastIn .22s var(--ease) both}}.toast.success{{border-color:rgba(47,166,106,.34)}}.toast.error{{border-color:rgba(229,72,77,.34)}}
@media(max-width:1040px){{.app{{grid-template-columns:1fr}}.sidebar{{height:auto;position:sticky;z-index:20;border-right:0;border-bottom:1px solid var(--line);padding:14px 18px;display:grid;grid-template-columns:1fr auto;align-items:center}}.nav,.nav-note{{display:none}}.nav-actions{{margin:0;display:flex}}.main{{padding:22px}}.topbar{{top:67px;margin:-22px -22px 16px;padding:20px 22px 14px}}.topbar-row{{display:grid}}.ops-strip{{grid-template-columns:1fr 1fr}}.controls{{grid-template-columns:1fr 160px auto}}.result-count{{grid-column:1/-1}}.form-grid{{grid-template-columns:1fr}}}}
@media(max-width:620px){{.sidebar{{grid-template-columns:1fr}}.nav-actions{{display:grid;grid-template-columns:1fr 1fr}}.topbar{{top:120px}}.toolbar{{display:grid;grid-template-columns:1fr 1fr;width:100%}}.toolbar .btn:first-child{{grid-column:1/-1}}.ops-strip,.controls,.node-grid,.instance-grid{{grid-template-columns:1fr}}.card-head{{display:grid}}.actions{{justify-content:flex-start}}.field{{display:grid}}.field span:last-child{{text-align:left}}.modal{{padding:16px}}}}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand"><div class="brand-mark">&gt;NA</div><div><b class="brand-word"><span class="hot">N</span>ekro <span class="cool">User Panel</span></b><span class="brand-sub">Denia headquarters</span></div></div>
    <nav class="nav" aria-label="后台导航">
      <button class="btn nav-item active" type="button">总览</button>
      <button class="btn nav-item" type="button" onclick="document.getElementById('nodes-section').scrollIntoView({{behavior:'smooth'}})">节点</button>
      <button class="btn nav-item" type="button" onclick="document.getElementById('instances-section').scrollIntoView({{behavior:'smooth'}})">实例</button>
    </nav>
    <div class="nav-note">节点只保存总部可访问的 HTTP 入口。实例保存用户登录名、路由归属和对应 NA 后端，不需要也不应该填写 SSH 信息。</div>
    <div class="nav-actions">
      <button class="btn side-btn" onclick="location.href='/webui'">打开当前 WebUI</button>
      <button class="btn side-btn btn-danger" onclick="logout()">退出登录</button>
    </div>
  </aside>
  <main class="main">
    <div class="topbar">
      <div class="topbar-row">
        <div>
          <p class="crumb">总部控制台 / 路由管理</p>
          <h1 class="title">多节点实例路由</h1>
          <p class="sub">Denia 作为总部维护节点、入口状态和用户实例映射。远端节点通过 HTTP 面板或管理 API 接入，登录后自动进入账号绑定的 NA 实例。</p>
        </div>
        <div class="toolbar">
          <button class="btn" onclick="loadAll()">刷新状态</button>
          <button class="btn btn-secondary" onclick="showCreateNodeModal()">添加节点</button>
          <button class="btn btn-primary" onclick="showCreateInstanceModal()">添加实例</button>
        </div>
      </div>
    </div>

    <section class="ops-strip" aria-label="运行状态">
      <div class="stat current"><span>当前管理目标</span><b id="metric-current">未选择</b></div>
      <div class="stat"><span>节点</span><b id="metric-node-count">0</b></div>
      <div class="stat"><span>实例</span><b id="metric-count">0</b></div>
      <div class="stat"><span>最近刷新</span><b id="metric-updated">未刷新</b></div>
    </section>

    <section class="section" id="nodes-section" aria-label="节点">
      <div class="section-head">
        <div><h2>节点拓扑</h2><p>总部、苏州和后续服务器按节点维护，状态由 HTTP 探测确认。</p></div>
        <button class="btn btn-secondary" onclick="showCreateNodeModal()">添加节点</button>
      </div>
      <div id="nodes-list" class="node-grid"></div>
    </section>

    <section class="section" id="instances-section" aria-label="实例">
      <div class="section-head">
        <div><h2>实例清单</h2><p>每个用户登录名会路由到一个具体 NA 后端。</p></div>
        <button class="btn btn-primary" onclick="showCreateInstanceModal()">添加实例</button>
      </div>
      <div class="controls" aria-label="筛选实例">
        <div class="search"><input id="search" type="search" placeholder="搜索账号、备注、节点或别名" autocomplete="off" oninput="renderInstances(); probeVisibleInstances();"></div>
        <select id="node-filter" onchange="renderInstances()"><option value="">全部节点</option></select>
        <button class="btn" onclick="clearSearch()">清空筛选</button>
        <div class="result-count" id="result-count">0 个结果</div>
      </div>
      <div id="instances-list" class="instance-grid"></div>
    </section>
  </main>
</div>

<div class="modal-overlay" id="node-modal">
  <div class="modal">
    <h2 id="node-modal-title">添加节点</h2>
    <div class="form-grid">
      <div class="form-section">节点身份</div>
      <div class="form-group"><label>节点 ID</label><input id="n-id" placeholder="suzhou"></div>
      <div class="form-group"><label>节点名称</label><input id="n-name" placeholder="Suzhou"></div>
      <div class="form-group"><label>集群 ID</label><input id="n-cluster-id" value="default"></div>
      <div class="form-group"><label>集群名称</label><input id="n-cluster-name" placeholder="Suzhou"></div>
      <div class="form-group"><label>角色</label><select id="n-role"><option value="node">普通节点</option><option value="headquarters">总部</option></select></div>
      <div class="form-group"><label>状态标记</label><select id="n-status"><option value="unknown">unknown</option><option value="online">online</option><option value="partial">partial</option><option value="offline">offline</option></select></div>
      <div class="form-section">HTTP 入口</div>
      <div class="form-group full"><label>Nekro User Panel 地址</label><input id="n-panel-url" placeholder="可选，例如 https://node.example.com"></div>
      <div class="form-group full"><label>节点管理 API 地址</label><input id="n-manager-url" placeholder="可选，例如 https://node.example.com/api"></div>
      <div class="form-group full"><label>API Key</label><input id="n-manager-key" type="password" placeholder="编辑时留空表示保持原密钥"></div>
      <div class="form-group full"><label>维护说明</label><input id="n-comment" placeholder="入口、隧道或当前阻塞原因"></div>
    </div>
    <div class="form-actions"><button class="btn" onclick="closeNodeModal()">取消</button><button class="btn btn-primary" onclick="submitNodeForm()">保存节点</button></div>
  </div>
</div>

<div class="modal-overlay" id="modal">
  <div class="modal">
    <h2 id="modal-title">添加实例</h2>
    <div class="form-grid">
      <div class="form-section">登录身份</div>
      <div class="form-group"><label>用户 ID</label><input id="f-id" placeholder="GBNA1"></div>
      <div class="form-group"><label>面板登录密码</label><input id="f-password" type="text" placeholder="面板密码"></div>
      <div class="form-group full"><label>登录别名</label><input id="f-aliases" placeholder="多个别名用英文逗号分隔"></div>
      <div class="form-section">挂载节点</div>
      <div class="form-group full"><label>节点</label><select id="f-node-select" onchange="syncNodeSelection()"></select></div>
      <div class="form-group"><label>集群 ID</label><input id="f-cluster-id" readonly></div>
      <div class="form-group"><label>节点 ID</label><input id="f-node-id" readonly></div>
      <input id="f-cluster-name" type="hidden"><input id="f-node-name" type="hidden">
      <div class="form-section">NA 后端</div>
      <div class="form-group full"><label>NA 完整地址</label><input id="f-base-url" placeholder="优先使用，例如 http://127.0.0.1:8061"></div>
      <div class="form-group"><label>NA Host</label><input id="f-host" value="127.0.0.1"></div>
      <div class="form-group"><label>NA 端口</label><input id="f-port" type="number" placeholder="8061"></div>
      <div class="form-section">NA 管理凭据</div>
      <div class="form-group"><label>管理员用户名</label><input id="f-admin-user" value="admin"></div>
      <div class="form-group"><label>管理员密码</label><input id="f-admin-pass" type="text" placeholder="NA admin 密码"></div>
      <div class="form-group full"><label>备注</label><input id="f-comment" placeholder="用途或维护说明"></div>
    </div>
    <div class="form-actions"><button class="btn" onclick="closeModal()">取消</button><button class="btn btn-primary" id="modal-submit" onclick="submitForm()">保存实例</button></div>
  </div>
</div>

<script>
const TOKEN = decodeURIComponent(document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('panel_token='))?.split('=')[1] || '')
  || localStorage.getItem('nekro_user_panel_token') || localStorage.getItem('panel_token') || localStorage.getItem('token');
const headers = {{'Content-Type':'application/json'}};
if (TOKEN) headers['Authorization'] = 'Bearer ' + TOKEN;
let editingId = null;
let editingNodeId = null;
let instancesCache = [];
let nodesCache = [];
let instanceStatusCache = {{}};

function escapeHtml(v){{return String(v ?? '').replace(/[&<>'"]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}}[c]));}}
function escapeAttr(v){{return escapeHtml(v).replace(/`/g,'&#96;');}}
function nodeById(id){{return nodesCache.find(n => n.id === id) || null;}}
function statusClass(status){{return String(status || 'unknown').toLowerCase().replace(/[^a-z0-9_-]/g,'') || 'unknown';}}
function statusLabel(status){{
  const map = {{online:'在线', reachable:'可达', offline:'离线', checking:'探测中', unknown:'待探测', partial:'部分可达', unconfigured:'未配置'}};
  return map[String(status || 'unknown').toLowerCase()] || status || '待探测';
}}
function searchableText(i){{return [i.id,i.comment,i.na_host,i.na_port,i.na_admin_user,i.cluster_id,i.cluster_name,i.node_id,i.node_name,i.na_base_url,i.na_backend_url,(i.login_aliases||[]).join(',')].map(v=>String(v ?? '').toLowerCase()).join(' ');}}
function nowLabel(){{return new Date().toLocaleTimeString('zh-CN',{{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'}});}}

function clearAuthStorage(){{
  ['nekro_user_panel_token','nekro_user_panel_username','nekro_user_panel_userinfo','panel_token','token','auth-storage'].forEach(k => localStorage.removeItem(k));
  ['panel_token','admin_instance'].forEach(k => {{ document.cookie = k + '=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax'; }});
}}
function syncWebuiAuthStorage(){{
  if(!TOKEN) return;
  localStorage.setItem('nekro_user_panel_token', TOKEN);
  localStorage.setItem('panel_token', TOKEN);
  localStorage.setItem('token', TOKEN);
  localStorage.setItem('nekro_user_panel_username', 'admin');
  localStorage.setItem('auth-storage', JSON.stringify({{
    state: {{ token: TOKEN, userInfo: {{ username: 'admin', userId: 1, perm_level: 2, perm_role: 'Admin' }} }},
    version: 0,
  }}));
  document.cookie = 'panel_token=' + encodeURIComponent(TOKEN) + '; path=/; max-age=86400; SameSite=Lax';
}}
async function logout(){{try{{await fetch('/panel/logout',{{method:'POST',headers}});}}catch(e){{}} clearAuthStorage(); location.href='/webui';}}

async function loadCurrent(){{
  try{{
    const resp = await fetch('/panel/admin/current-instance',{{headers}});
    if(resp.ok){{
      const data = await resp.json();
      document.getElementById('metric-current').textContent = data.instance_id ? `${{data.instance_id}} · ${{data.route_label || data.na_backend_url || ''}}` : '未选择';
    }}
  }}catch(e){{}}
}}
async function loadNodes(){{
  const resp = await fetch('/panel/admin/nodes',{{headers}});
  if(resp.status === 401 || resp.status === 403){{ clearAuthStorage(); location.href='/webui'; return; }}
  const data = await resp.json();
  nodesCache = data.sort((a,b)=>String(a.id).localeCompare(String(b.id),'zh-Hans-u-kn-true'));
  document.getElementById('metric-node-count').textContent = data.length;
  renderNodeOptions();
  renderNodes();
}}
async function loadInstances(){{
  const resp = await fetch('/panel/admin/instances',{{headers}});
  if(resp.status === 401 || resp.status === 403){{ clearAuthStorage(); location.href='/webui'; return; }}
  const data = await resp.json();
  instancesCache = data.sort((a,b)=>String(a.id).localeCompare(String(b.id),'zh-Hans-u-kn-true'));
  document.getElementById('metric-count').textContent = data.length;
  await loadCurrent();
  renderInstances();
  probeVisibleInstances();
}}
async function loadAll(){{await loadNodes(); await loadInstances(); document.getElementById('metric-updated').textContent = nowLabel(); toast('状态已更新','success');}}

function renderNodeOptions(){{
  const filter = document.getElementById('node-filter');
  const oldFilter = filter.value;
  filter.innerHTML = '<option value="">全部节点</option>' + nodesCache.map(n => `<option value="${{escapeAttr(n.id)}}">${{escapeHtml(n.display_name || n.id)}}</option>`).join('');
  filter.value = oldFilter;
  const select = document.getElementById('f-node-select');
  if(select) select.innerHTML = nodesCache.map(n => `<option value="${{escapeAttr(n.id)}}">${{escapeHtml(n.display_name || n.id)}} · ${{escapeHtml(n.route_label || n.cluster_id)}}</option>`).join('');
}}
function renderNodes(){{
  const el = document.getElementById('nodes-list');
  if(!nodesCache.length){{el.innerHTML='<div class="empty"><b>还没有节点</b>添加 Denia 总部或远端 HTTP 节点后会显示在这里。</div>';return;}}
  el.innerHTML = nodesCache.map(n => {{
    const endpoint = n.manager_base_url || n.panel_base_url || '未配置入口';
    const canOpen = !!n.panel_base_url;
    const nodeCopy = n.role === 'headquarters'
      ? `总部节点，承载 ${{n.instance_count || 0}} 个实例。`
      : `远端节点，当前承载 ${{n.instance_count || 0}} 个实例。`;
    return `<article class="card node-card">
      <div class="card-head">
        <div><h3>${{escapeHtml(n.display_name || n.name || n.id)}}</h3><div class="caption">${{escapeHtml(n.route_label || n.cluster_id || 'default')}}</div></div>
        <span class="badge ${{statusClass(n.status)}}">${{escapeHtml(statusLabel(n.status))}}</span>
      </div>
      <div class="instance-meta">
        <span class="meta-pill">角色 <strong>${{escapeHtml(n.role || 'node')}}</strong></span>
        <span class="meta-pill">实例 <strong>${{escapeHtml(n.instance_count || 0)}}</strong></span>
      </div>
      <div class="status-note">${{escapeHtml(nodeCopy)}}</div>
      <details class="tech-details">
        <summary>节点入口</summary>
        <code>${{escapeHtml(endpoint)}}</code>
      </details>
      <div class="actions">
        ${{canOpen ? `<button class="btn btn-sm btn-good" onclick="openPanel('${{escapeAttr(n.panel_base_url)}}')">打开</button>` : ''}}
        <button class="btn btn-sm" onclick="probeNode('${{escapeAttr(n.id)}}')">探测</button>
        <button class="btn btn-sm" onclick="editNode('${{escapeAttr(n.id)}}')">编辑</button>
        <button class="btn btn-sm btn-danger" onclick="deleteNode('${{escapeAttr(n.id)}}')">删除</button>
      </div>
    </article>`;
  }}).join('');
}}
function renderInstances(){{
  const q = document.getElementById('search').value.trim().toLowerCase();
  const nodeFilter = document.getElementById('node-filter').value;
  let data = instancesCache;
  if(nodeFilter) data = data.filter(i => i.node_id === nodeFilter);
  if(q) data = data.filter(i => searchableText(i).includes(q));
  document.getElementById('result-count').textContent = `${{data.length}} / ${{instancesCache.length}} 个实例`;
  const el = document.getElementById('instances-list');
  if(!instancesCache.length){{el.innerHTML='<div class="empty"><b>还没有可管理的实例</b>添加实例后，这里会显示账号入口和运行状态。</div>';return;}}
  if(!data.length){{el.innerHTML='<div class="empty"><b>没有符合条件的实例</b>清空筛选或换一个关键词试试。</div>';return;}}
  el.innerHTML = data.map(i => {{
    const node = nodeById(i.node_id);
    const nodeName = node ? (node.display_name || node.id) : (i.node_name || i.node_id || '未登记节点');
    const backend = i.na_backend_url || i.na_base_url || `${{i.na_host}}:${{i.na_port}}`;
    const route = i.route_label || `${{i.cluster_id || 'default'}}/${{i.node_id || 'local'}}`;
    const state = instanceStatusCache[i.id] || {{status:'unknown', message:'等待总部探测'}};
    const aliases = (i.login_aliases || []).slice(0, 3);
    return `<article class="card instance-card" data-instance-id="${{escapeAttr(i.id)}}">
      <div class="card-head">
        <div><h3>${{escapeHtml(i.id)}}</h3><div class="caption">${{escapeHtml(i.comment || 'Nekro Agent 实例')}}</div></div>
        <span class="badge ${{statusClass(state.status)}}">${{escapeHtml(statusLabel(state.status))}}</span>
      </div>
      <div class="instance-meta">
        <span class="meta-pill">节点 <strong>${{escapeHtml(nodeName)}}</strong></span>
        <span class="meta-pill">路由 <strong>${{escapeHtml(route)}}</strong></span>
      </div>
      ${{aliases.length ? `<div class="chips">${{aliases.map(a => `<span class="chip">${{escapeHtml(a)}}</span>`).join('')}}</div>` : ''}}
      <div class="status-note">${{escapeHtml(state.message || '等待总部探测')}}</div>
      <details class="tech-details">
        <summary>技术详情</summary>
        <code>${{escapeHtml(backend)}}</code>
      </details>
      <div class="actions">
        <button class="btn btn-sm btn-good" onclick="enterInstance('${{escapeAttr(i.id)}}')">进入</button>
        <button class="btn btn-sm" onclick="probeInstance('${{escapeAttr(i.id)}}')">探测</button>
        <button class="btn btn-sm" onclick="editInstance('${{escapeAttr(i.id)}}')">编辑</button>
        <button class="btn btn-sm btn-danger" onclick="deleteInstance('${{escapeAttr(i.id)}}')">删除</button>
      </div>
    </article>`;
  }}).join('');
}}
function updateInstanceCard(id, result){{
  instanceStatusCache[id] = result;
  const card = document.querySelector(`[data-instance-id="${{CSS.escape(id)}}"]`);
  if(!card) return;
  const badge = card.querySelector('.badge');
  const note = card.querySelector('.status-note');
  if(badge){{
    badge.className = 'badge ' + statusClass(result.status);
    badge.textContent = statusLabel(result.status);
  }}
  if(note) note.textContent = result.message || statusLabel(result.status);
}}
async function probeInstance(id, quiet=false){{
  updateInstanceCard(id, {{status:'checking', message:'总部正在探测'}});
  const resp = await fetch(`/panel/admin/instances/${{encodeURIComponent(id)}}/probe`, {{method:'POST', headers}});
  const result = await resp.json().catch(()=>({{}}));
  if(resp.ok){{
    updateInstanceCard(id, result);
    if(!quiet) toast(result.message || '实例状态已更新', (result.status === 'online' || result.status === 'reachable') ? 'success' : 'error');
  }} else {{
    const failed = {{status:'offline', message: result.detail || '探测失败'}};
    updateInstanceCard(id, failed);
    if(!quiet) toast(failed.message, 'error');
  }}
}}
async function probeVisibleInstances(){{
  const cards = Array.from(document.querySelectorAll('[data-instance-id]')).slice(0, 60);
  const queue = cards.map(card => card.getAttribute('data-instance-id')).filter(Boolean);
  const workers = Array.from({{length: Math.min(5, queue.length)}}, async () => {{
    while(queue.length){{
      const id = queue.shift();
      if(id) await probeInstance(id, true).catch(() => updateInstanceCard(id, {{status:'offline', message:'探测失败'}}));
    }}
  }});
  await Promise.all(workers);
}}
function clearSearch(){{document.getElementById('search').value=''; document.getElementById('node-filter').value=''; renderInstances(); probeVisibleInstances(); document.getElementById('search').focus();}}
function openPanel(url){{ if(url.includes('127.0.0.1:9054') || url.includes('localhost:9054')) location.href='/panel/admin'; else window.open(url, '_blank', 'noopener'); }}
async function copyText(text){{if(!text){{toast('没有可复制的后端地址','error');return;}} await navigator.clipboard.writeText(text); toast('已复制后端地址','success');}}

function showCreateInstanceModal(){{
  editingId=null; document.getElementById('modal-title').textContent='添加实例';
  ['f-id','f-password','f-port','f-comment','f-base-url','f-aliases','f-admin-pass'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('f-id').disabled=false; document.getElementById('f-admin-user').value='admin'; document.getElementById('f-host').value='127.0.0.1';
  renderNodeOptions(); document.getElementById('f-node-select').value=(nodesCache[0]||{{}}).id || ''; syncNodeSelection(); document.getElementById('modal').classList.add('active');
}}
function syncNodeSelection(){{
  const node = nodeById(document.getElementById('f-node-select').value) || nodesCache[0] || {{}};
  document.getElementById('f-cluster-id').value=node.cluster_id || 'default';
  document.getElementById('f-cluster-name').value=node.cluster_name || '';
  document.getElementById('f-node-id').value=node.id || 'local';
  document.getElementById('f-node-name').value=node.display_name || node.name || '';
}}
async function editInstance(id){{
  const resp = await fetch(`/panel/admin/instances/${{encodeURIComponent(id)}}`,{{headers}}); const data = await resp.json();
  editingId=id; document.getElementById('modal-title').textContent='编辑实例: '+id;
  document.getElementById('f-id').value=data.id; document.getElementById('f-id').disabled=false; document.getElementById('f-password').value=data.panel_password;
  document.getElementById('f-port').value=data.na_port || ''; document.getElementById('f-admin-user').value=data.na_admin_user || 'admin'; document.getElementById('f-admin-pass').value=data.na_admin_pass || '';
  document.getElementById('f-host').value=data.na_host || '127.0.0.1'; document.getElementById('f-base-url').value=data.na_base_url || ''; document.getElementById('f-aliases').value=(data.login_aliases || []).join(', ');
  document.getElementById('f-comment').value=data.comment || ''; renderNodeOptions(); document.getElementById('f-node-select').value=data.node_id || 'local';
  syncNodeSelection(); document.getElementById('f-cluster-id').value=data.cluster_id || document.getElementById('f-cluster-id').value; document.getElementById('f-cluster-name').value=data.cluster_name || document.getElementById('f-cluster-name').value;
  document.getElementById('f-node-id').value=data.node_id || document.getElementById('f-node-id').value; document.getElementById('f-node-name').value=data.node_name || document.getElementById('f-node-name').value; document.getElementById('modal').classList.add('active');
}}
function closeModal(){{document.getElementById('modal').classList.remove('active');}}
async function submitForm(){{
  const portValue=document.getElementById('f-port').value.trim(); const baseUrl=document.getElementById('f-base-url').value.trim();
  const body={{id:document.getElementById('f-id').value.trim(),panel_password:document.getElementById('f-password').value,na_port:portValue?parseInt(portValue,10):null,na_admin_user:document.getElementById('f-admin-user').value.trim(),na_admin_pass:document.getElementById('f-admin-pass').value,na_host:document.getElementById('f-host').value.trim(),na_base_url:baseUrl || null,cluster_id:document.getElementById('f-cluster-id').value.trim() || 'default',cluster_name:document.getElementById('f-cluster-name').value.trim(),node_id:document.getElementById('f-node-id').value.trim() || 'local',node_name:document.getElementById('f-node-name').value.trim(),login_aliases:document.getElementById('f-aliases').value.split(',').map(v=>v.trim()).filter(Boolean),comment:document.getElementById('f-comment').value.trim()}};
  if(!body.id || !body.panel_password || (!body.na_port && !body.na_base_url) || !body.na_admin_pass){{toast('请填写用户 ID、面板密码、NA 地址或端口，以及 NA 管理员密码','error');return;}}
  const url = editingId ? `/panel/admin/instances/${{encodeURIComponent(editingId)}}` : '/panel/admin/instances'; const method = editingId ? 'PUT' : 'POST';
  const resp = await fetch(url,{{method,headers,body:JSON.stringify(body)}}); const result = await resp.json().catch(()=>({{}}));
  if(resp.ok){{toast(result.message || '配置已保存','success'); closeModal(); loadAll();}} else {{toast(result.detail || '操作失败','error');}}
}}
async function deleteInstance(id){{if(!confirm(`删除实例 "${{id}}"？此操作会移除该登录路由。`)) return; const resp = await fetch(`/panel/admin/instances/${{encodeURIComponent(id)}}`,{{method:'DELETE',headers}}); const result = await resp.json().catch(()=>({{}})); if(resp.ok){{toast(result.message || '已删除','success'); loadAll();}} else {{toast(result.detail || '删除失败','error');}}}}
async function enterInstance(id){{const resp = await fetch(`/panel/admin/switch-instance/${{encodeURIComponent(id)}}`,{{method:'POST',headers}}); if(resp.ok){{syncWebuiAuthStorage(); toast('已切换到实例: '+id,'success'); await loadCurrent(); setTimeout(()=>{{location.href='/webui#/dashboard';}},350);}} else {{const err=await resp.json().catch(()=>({{}})); toast(err.detail || '切换失败','error');}}}}

function showCreateNodeModal(){{
  editingNodeId=null; document.getElementById('node-modal-title').textContent='添加节点';
  ['n-id','n-name','n-cluster-name','n-panel-url','n-manager-url','n-manager-key','n-comment'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('n-cluster-id').value='default'; document.getElementById('n-role').value='node'; document.getElementById('n-status').value='unknown'; document.getElementById('node-modal').classList.add('active');
}}
async function editNode(id){{
  const resp = await fetch(`/panel/admin/nodes/${{encodeURIComponent(id)}}`,{{headers}}); const data = await resp.json();
  editingNodeId=id; document.getElementById('node-modal-title').textContent='编辑节点: '+id;
  document.getElementById('n-id').value=data.id; document.getElementById('n-name').value=data.name || ''; document.getElementById('n-cluster-id').value=data.cluster_id || 'default'; document.getElementById('n-cluster-name').value=data.cluster_name || '';
  document.getElementById('n-role').value=data.role || 'node'; document.getElementById('n-status').value=data.status || 'unknown'; document.getElementById('n-panel-url').value=data.panel_base_url || ''; document.getElementById('n-manager-url').value=data.manager_base_url || '';
  document.getElementById('n-manager-key').value=''; document.getElementById('n-manager-key').placeholder=data.manager_api_key_set ? '已设置，留空保持原密钥' : '可选'; document.getElementById('n-comment').value=data.comment || ''; document.getElementById('node-modal').classList.add('active');
}}
function closeNodeModal(){{document.getElementById('node-modal').classList.remove('active');}}
async function submitNodeForm(){{
  const body={{id:document.getElementById('n-id').value.trim(),name:document.getElementById('n-name').value.trim(),cluster_id:document.getElementById('n-cluster-id').value.trim() || 'default',cluster_name:document.getElementById('n-cluster-name').value.trim(),role:document.getElementById('n-role').value,status:document.getElementById('n-status').value,panel_base_url:document.getElementById('n-panel-url').value.trim() || null,manager_base_url:document.getElementById('n-manager-url').value.trim() || null,manager_api_key:document.getElementById('n-manager-key').value.trim(),comment:document.getElementById('n-comment').value.trim()}};
  if(!body.id){{toast('请填写节点 ID','error');return;}}
  const url = editingNodeId ? `/panel/admin/nodes/${{encodeURIComponent(editingNodeId)}}` : '/panel/admin/nodes'; const method = editingNodeId ? 'PUT' : 'POST';
  const resp = await fetch(url,{{method,headers,body:JSON.stringify(body)}}); const result = await resp.json().catch(()=>({{}}));
  if(resp.ok){{toast(result.message || '配置已保存','success'); closeNodeModal(); loadAll();}} else {{toast(result.detail || '操作失败','error');}}
}}
async function deleteNode(id){{if(!confirm(`删除节点 "${{id}}"？仍有实例引用的节点会被拒绝删除。`)) return; const resp = await fetch(`/panel/admin/nodes/${{encodeURIComponent(id)}}`,{{method:'DELETE',headers}}); const result = await resp.json().catch(()=>({{}})); if(resp.ok){{toast(result.message || '已删除','success'); loadAll();}} else {{toast(result.detail || '删除失败','error');}}}}
async function probeNode(id){{
  toast('正在测试节点连接','success');
  const resp = await fetch(`/panel/admin/nodes/${{encodeURIComponent(id)}}/probe`,{{method:'POST',headers}}); const result = await resp.json().catch(()=>({{}}));
  if(resp.ok){{toast(result.message || `状态: ${{result.status}}`,(result.status === 'online' || result.status === 'reachable') ? 'success' : 'error'); loadAll();}} else {{toast(result.detail || '测试失败','error');}}
}}
function toast(msg,type='success'){{const el=document.createElement('div'); el.className='toast '+type; el.textContent=msg; document.body.appendChild(el); setTimeout(()=>el.remove(),3200);}}
document.addEventListener('keydown', (ev)=>{{ if(ev.key === 'Escape'){{ closeModal(); closeNodeModal(); }} }});
loadAll();
</script>
</body>
</html>"""
