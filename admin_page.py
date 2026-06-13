"""
Nekro User Panel - 管理员页面
产品型管理后台，用于管理 instances.json 配置。
"""


def get_admin_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="color-scheme" content="dark" />
<title>Nekro User Panel · Admin</title>
<style>
:root {
  --bg:#0b0d12; --surface:#11151d; --surface-2:#151a24; --surface-3:#0c1017;
  --line:#242b38; --line-strong:#343d4f; --text:#eef3fb; --muted:#9aa6b7; --faint:#6e7a8c;
  --accent:#8fb8ff; --accent-hover:#a8c8ff; --accent-text:#07101f; --danger:#ff8d9b; --success:#85e1b4; --warning:#ffd08a;
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",system-ui,sans-serif;
}
*{box-sizing:border-box} html,body{min-height:100%}
body{margin:0;color:var(--text);background:radial-gradient(circle at 10% 0%,rgba(143,184,255,.12),transparent 28rem),radial-gradient(circle at 90% 100%,rgba(133,225,180,.07),transparent 28rem),var(--bg);}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.024) 1px,transparent 1px);background-size:48px 48px;mask-image:linear-gradient(to bottom,black,transparent 82%)}
.app{position:relative;z-index:1;min-height:100dvh;display:grid;grid-template-columns:260px minmax(0,1fr)}
.sidebar{border-right:1px solid var(--line);background:rgba(13,17,25,.78);padding:24px;display:flex;flex-direction:column;gap:24px}
.brand{display:flex;align-items:center;gap:12px}.logo{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;background:var(--accent);color:var(--accent-text);font-weight:800;letter-spacing:-.04em}.brand b{display:block;font-size:14px}.brand span{display:block;color:var(--faint);font-size:12px;margin-top:2px}
.nav-note{border:1px solid var(--line);background:rgba(255,255,255,.025);padding:14px;border-radius:12px;color:var(--muted);font-size:12px;line-height:1.55}
.nav-actions{margin-top:auto;display:grid;gap:10px}.side-btn{width:100%;min-height:40px;border-radius:10px;border:1px solid var(--line-strong);background:var(--surface-3);color:var(--text);font-weight:650;cursor:pointer;text-align:left;padding:0 12px;transition:.18s ease}.side-btn:hover{border-color:var(--accent);color:#fff}.side-btn.danger{color:var(--danger)}
.main{padding:34px;max-width:1280px;width:100%;margin:0 auto}.topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:26px}h1{margin:0;font-size:30px;letter-spacing:-.03em;line-height:1.12}.sub{margin:9px 0 0;color:var(--muted);font-size:14px;line-height:1.6;max-width:68ch}.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.btn{min-height:38px;padding:0 14px;border:0;border-radius:10px;cursor:pointer;font-size:13px;font-weight:750;transition:background .18s ease,transform .18s ease,border-color .18s ease;color:var(--text);background:var(--surface-3);border:1px solid var(--line-strong)}.btn:hover{border-color:var(--accent)}.btn:active{transform:translateY(1px)}.btn-primary{background:var(--accent);color:var(--accent-text);border-color:transparent}.btn-primary:hover{background:var(--accent-hover)}.btn-danger{color:var(--danger)}.btn-success{color:var(--success)}.btn-sm{min-height:32px;padding:0 10px;font-size:12px}
.summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-bottom:18px}.metric{border:1px solid var(--line);background:rgba(17,21,29,.78);padding:16px;border-radius:14px}.metric span{display:block;color:var(--faint);font-size:12px}.metric b{display:block;margin-top:6px;font-size:22px;font-variant-numeric:tabular-nums}
.list{display:grid;gap:10px}.card{border:1px solid var(--line);background:rgba(17,21,29,.82);border-radius:14px;padding:16px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px;align-items:start}.card:hover{border-color:#3c465a}.card h3{margin:0;font-size:16px;letter-spacing:-.01em}.comment{margin-top:7px;color:var(--muted);font-size:13px;line-height:1.45}.fields{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.field{border:1px solid var(--line);background:rgba(255,255,255,.022);color:#c9d2df;border-radius:9px;padding:6px 8px;font-size:12px;font-variant-numeric:tabular-nums}.actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.empty{border:1px dashed var(--line-strong);border-radius:14px;padding:34px;text-align:center;color:var(--muted);background:rgba(17,21,29,.42)}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.66);z-index:20;align-items:center;justify-content:center;padding:18px}.modal-overlay.active{display:flex}.modal{width:min(560px,100%);max-height:calc(100dvh - 36px);overflow:auto;background:var(--surface);border:1px solid var(--line-strong);border-radius:16px;padding:22px;box-shadow:0 24px 70px rgba(0,0,0,.45)}.modal h2{margin:0 0 16px;font-size:20px;letter-spacing:-.02em}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.form-group.full{grid-column:1/-1}.form-group label{display:block;margin-bottom:7px;color:#dbe3ef;font-size:12px;font-weight:650}.form-group input{width:100%;min-height:40px;border-radius:10px;border:1px solid var(--line-strong);background:var(--surface-3);color:var(--text);padding:9px 10px;outline:none}.form-group input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(143,184,255,.14)}.form-actions{display:flex;gap:10px;justify-content:flex-end;margin-top:18px}
.toast{position:fixed;top:18px;right:18px;z-index:30;max-width:380px;padding:12px 14px;border-radius:11px;background:var(--surface);border:1px solid var(--line-strong);color:var(--text);box-shadow:0 14px 40px rgba(0,0,0,.34);font-size:13px}.toast.success{border-color:rgba(133,225,180,.45)}.toast.error{border-color:rgba(255,141,155,.55)}
@media(max-width:880px){.app{grid-template-columns:1fr}.sidebar{border-right:0;border-bottom:1px solid var(--line)}.main{padding:22px}.topbar{display:grid}.summary{grid-template-columns:1fr}.card{grid-template-columns:1fr}.actions{justify-content:flex-start}.form-grid{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition-duration:.01ms!important;animation-duration:.01ms!important}}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand"><div class="logo">N</div><div><b>Nekro User Panel</b><span>Admin console</span></div></div>
    <div class="nav-note">选择实例后再进入 WebUI。管理员不会自动回退到第一项，避免离线实例拖垮控制台。</div>
    <div class="nav-actions">
      <button class="side-btn" onclick="location.href='/webui'">打开当前 WebUI</button>
      <button class="side-btn danger" onclick="logout()">退出登录</button>
    </div>
  </aside>
  <main class="main">
    <div class="topbar">
      <div><h1>实例管理</h1><p class="sub">管理面板账号与 Nekro Agent 后端映射。保存后会热重载实例配置。</p></div>
      <div class="toolbar"><button class="btn" onclick="loadInstances()">刷新列表</button><button class="btn btn-primary" onclick="showCreateModal()">添加实例</button></div>
    </div>
    <section class="summary" aria-label="概览">
      <div class="metric"><span>实例数量</span><b id="metric-count">0</b></div>
      <div class="metric"><span>当前选择</span><b id="metric-current">未选择</b></div>
      <div class="metric"><span>路由策略</span><b>显式选择</b></div>
    </section>
    <div id="instances-list" class="list"></div>
  </main>
</div>

<div class="modal-overlay" id="modal">
  <div class="modal">
    <h2 id="modal-title">添加实例</h2>
    <div class="form-grid">
      <div class="form-group"><label>用户 ID</label><input id="f-id" placeholder="例如 GBNA1"></div>
      <div class="form-group"><label>面板登录密码</label><input id="f-password" type="text" placeholder="面板密码"></div>
      <div class="form-group"><label>NA 端口</label><input id="f-port" type="number" placeholder="8021"></div>
      <div class="form-group"><label>NA 主机</label><input id="f-host" value="127.0.0.1"></div>
      <div class="form-group"><label>NA 管理员用户名</label><input id="f-admin-user" value="admin"></div>
      <div class="form-group"><label>NA 管理员密码</label><input id="f-admin-pass" type="text" placeholder="NA admin 密码"></div>
      <div class="form-group full"><label>备注</label><input id="f-comment" placeholder="可选"></div>
    </div>
    <div class="form-actions"><button class="btn" onclick="closeModal()">取消</button><button class="btn btn-primary" id="modal-submit" onclick="submitForm()">保存</button></div>
  </div>
</div>

<script>
const TOKEN = decodeURIComponent(document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('panel_token='))?.split('=')[1] || '')
    || localStorage.getItem('nekro_user_panel_token') || localStorage.getItem('panel_token') || localStorage.getItem('token');
const headers = {'Content-Type':'application/json'};
if (TOKEN) headers['Authorization'] = 'Bearer ' + TOKEN;
let editingId = null;
let instancesCache = [];

function escapeHtml(v){return String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}

function clearAuthStorage(){
  ['nekro_user_panel_token','nekro_user_panel_username','nekro_user_panel_userinfo','panel_token','token','auth-storage'].forEach(k => localStorage.removeItem(k));
  ['panel_token','admin_instance'].forEach(k => { document.cookie = k + '=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax'; });
}

async function logout(){
  try { await fetch('/panel/logout', {method:'POST', headers}); } catch(e) {}
  clearAuthStorage();
  location.href = '/webui';
}

async function loadCurrent(){
  try{
    const resp = await fetch('/panel/admin/current-instance', {headers});
    if(resp.ok){
      const data = await resp.json();
      document.getElementById('metric-current').textContent = data.instance_id || '未选择';
    }
  }catch(e){}
}

async function loadInstances(){
  const resp = await fetch('/panel/admin/instances', {headers});
  if(resp.status === 401 || resp.status === 403){ clearAuthStorage(); location.href='/webui'; return; }
  const data = await resp.json();
  instancesCache = data;
  document.getElementById('metric-count').textContent = data.length;
  await loadCurrent();
  const el = document.getElementById('instances-list');
  if(!data.length){ el.innerHTML='<div class="empty">暂无实例。添加一个实例后才能路由到 WebUI。</div>'; return; }
  el.innerHTML = data.map(i => `
    <article class="card">
      <div>
        <h3>${escapeHtml(i.comment || i.id)}</h3>
        <div class="comment">ID: ${escapeHtml(i.id)}</div>
        <div class="fields">
          <span class="field">${escapeHtml(i.na_host)}:${escapeHtml(i.na_port)}</span>
          <span class="field">管理员 ${escapeHtml(i.na_admin_user)}</span>
        </div>
      </div>
      <div class="actions">
        <button class="btn btn-success btn-sm" onclick="enterInstance('${escapeHtml(i.id)}')">进入管理</button>
        <button class="btn btn-sm" onclick="editInstance('${escapeHtml(i.id)}')">编辑</button>
        <button class="btn btn-danger btn-sm" onclick="deleteInstance('${escapeHtml(i.id)}')">删除</button>
      </div>
    </article>`).join('');
}

function showCreateModal(){
  editingId=null; document.getElementById('modal-title').textContent='添加实例';
  ['f-id','f-password','f-port','f-comment'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('f-id').disabled=false; document.getElementById('f-admin-user').value='admin'; document.getElementById('f-admin-pass').value=''; document.getElementById('f-host').value='127.0.0.1';
  document.getElementById('modal').classList.add('active');
}
async function editInstance(id){
  const resp = await fetch(`/panel/admin/instances/${encodeURIComponent(id)}`, {headers});
  const data = await resp.json(); editingId=id;
  document.getElementById('modal-title').textContent='编辑实例: '+id;
  document.getElementById('f-id').value=data.id; document.getElementById('f-id').disabled=false;
  document.getElementById('f-password').value=data.panel_password; document.getElementById('f-port').value=data.na_port;
  document.getElementById('f-admin-user').value=data.na_admin_user; document.getElementById('f-admin-pass').value=data.na_admin_pass;
  document.getElementById('f-host').value=data.na_host; document.getElementById('f-comment').value=data.comment || '';
  document.getElementById('modal').classList.add('active');
}
function closeModal(){document.getElementById('modal').classList.remove('active');}
async function submitForm(){
  const body={id:document.getElementById('f-id').value.trim(),panel_password:document.getElementById('f-password').value,na_port:parseInt(document.getElementById('f-port').value),na_admin_user:document.getElementById('f-admin-user').value.trim(),na_admin_pass:document.getElementById('f-admin-pass').value,na_host:document.getElementById('f-host').value.trim(),comment:document.getElementById('f-comment').value.trim()};
  if(!body.id || !body.panel_password || !body.na_port || !body.na_admin_pass){toast('请填写所有必填字段','error');return;}
  const url = editingId ? `/panel/admin/instances/${encodeURIComponent(editingId)}` : '/panel/admin/instances';
  const method = editingId ? 'PUT' : 'POST';
  const resp = await fetch(url,{method,headers,body:JSON.stringify(body)}); const result = await resp.json().catch(()=>({}));
  if(resp.ok){toast(result.message || '已保存','success'); closeModal(); loadInstances();} else {toast(result.detail || '操作失败','error');}
}
async function deleteInstance(id){
  if(!confirm(`确定删除实例 "${id}" 吗？`)) return;
  const resp = await fetch(`/panel/admin/instances/${encodeURIComponent(id)}`,{method:'DELETE',headers}); const result = await resp.json().catch(()=>({}));
  if(resp.ok){toast(result.message || '已删除','success'); loadInstances();} else {toast(result.detail || '删除失败','error');}
}
async function enterInstance(id){
  const resp = await fetch(`/panel/admin/switch-instance/${encodeURIComponent(id)}`,{method:'POST',headers});
  if(resp.ok){toast('已切换到实例: '+id,'success'); await loadCurrent(); setTimeout(()=>{location.href='/webui#/dashboard';},350);} else {const err=await resp.json().catch(()=>({})); toast(err.detail || '切换失败','error');}
}
function toast(msg,type){const el=document.createElement('div');el.className='toast '+type;el.textContent=msg;document.body.appendChild(el);setTimeout(()=>el.remove(),3200);}
loadInstances();
</script>
</body>
</html>"""
