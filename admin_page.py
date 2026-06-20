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
.sidebar{position:sticky;top:0;height:100dvh;border-right:1px solid var(--line);background:rgba(13,17,25,.86);backdrop-filter:blur(18px);padding:24px;display:flex;flex-direction:column;gap:24px}
.brand{display:flex;align-items:center;gap:12px}.logo{width:36px;height:36px;border-radius:10px;display:grid;place-items:center;background:var(--accent);color:var(--accent-text);font-weight:800;letter-spacing:-.04em}.brand b{display:block;font-size:14px}.brand span{display:block;color:var(--faint);font-size:12px;margin-top:2px}
.nav-note{border:1px solid var(--line);background:rgba(255,255,255,.025);padding:14px;border-radius:12px;color:var(--muted);font-size:12px;line-height:1.55}
.nav-actions{margin-top:auto;display:grid;gap:10px}.side-btn{width:100%;min-height:40px;border-radius:10px;border:1px solid var(--line-strong);background:var(--surface-3);color:var(--text);font-weight:650;cursor:pointer;text-align:left;padding:0 12px;transition:.18s ease}.side-btn:hover{border-color:var(--accent);color:#fff}.side-btn.danger{color:var(--danger)}
.main{padding:30px;max-width:1380px;width:100%;margin:0 auto}.topbar{position:sticky;top:0;z-index:10;margin:-30px -30px 22px;padding:28px 30px 18px;background:linear-gradient(180deg,rgba(11,13,18,.96) 0%,rgba(11,13,18,.86) 70%,rgba(11,13,18,0) 100%);backdrop-filter:blur(14px)}.topbar-row{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}h1{margin:0;font-size:30px;letter-spacing:-.03em;line-height:1.12}.sub{margin:9px 0 0;color:var(--muted);font-size:14px;line-height:1.6;max-width:68ch}.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.btn{min-height:38px;padding:0 14px;border:0;border-radius:10px;cursor:pointer;font-size:13px;font-weight:750;transition:background .18s ease,transform .18s ease,border-color .18s ease;color:var(--text);background:var(--surface-3);border:1px solid var(--line-strong);white-space:nowrap}.btn:hover{border-color:var(--accent)}.btn:active{transform:translateY(1px)}.btn-primary{background:var(--accent);color:var(--accent-text);border-color:transparent}.btn-primary:hover{background:var(--accent-hover)}.btn-danger{color:var(--danger)}.btn-success{color:var(--success)}.btn-sm{min-height:32px;padding:0 10px;font-size:12px}
.summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:18px}.metric{border:1px solid var(--line);background:rgba(17,21,29,.78);padding:15px;border-radius:14px}.metric span{display:block;color:var(--faint);font-size:12px}.metric b{display:block;margin-top:6px;font-size:22px;font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.controls{display:grid;grid-template-columns:minmax(220px,1fr) auto auto;gap:10px;align-items:center;margin:0 0 16px}.search-wrap{position:relative}.search-wrap input{width:100%;min-height:40px;border-radius:11px;border:1px solid var(--line-strong);background:rgba(12,16,23,.9);color:var(--text);padding:0 42px 0 12px;outline:none}.search-wrap input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(143,184,255,.14)}.search-icon{position:absolute;right:12px;top:50%;transform:translateY(-50%);color:var(--faint);font-size:13px}.result-count{color:var(--faint);font-size:12px;white-space:nowrap}
.section-block{margin-top:18px}.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin:0 0 12px}.section-head h2{margin:0;font-size:18px;letter-spacing:-.02em}.section-head p{margin:5px 0 0;color:var(--muted);font-size:13px;line-height:1.5}.list{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:12px;align-items:start}.nodes-list{grid-template-columns:repeat(auto-fill,minmax(420px,1fr))}.card{border:1px solid var(--line);background:rgba(17,21,29,.82);border-radius:14px;padding:15px;display:grid;gap:14px;min-height:148px}.card:hover{border-color:#3c465a}.card-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}.card h3{margin:0;font-size:15px;letter-spacing:-.01em;line-height:1.25}.comment{margin-top:5px;color:var(--muted);font-size:12px;line-height:1.45}.status-pill{border:1px solid rgba(133,225,180,.34);background:rgba(133,225,180,.06);color:var(--success);font-size:11px;border-radius:999px;padding:4px 7px;white-space:nowrap}.status-pill.partial{border-color:rgba(255,208,138,.42);background:rgba(255,208,138,.07);color:var(--warning)}.status-pill.offline{border-color:rgba(255,141,155,.48);background:rgba(255,141,155,.08);color:var(--danger)}.fields{display:flex;flex-wrap:wrap;gap:7px}.field{border:1px solid var(--line);background:rgba(255,255,255,.022);color:#c9d2df;border-radius:9px;padding:6px 8px;font-size:12px;font-variant-numeric:tabular-nums}.actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;margin-top:auto}.empty{grid-column:1/-1;border:1px dashed var(--line-strong);border-radius:14px;padding:34px;text-align:center;color:var(--muted);background:rgba(17,21,29,.42)}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.66);z-index:20;align-items:center;justify-content:center;padding:18px}.modal-overlay.active{display:flex}.modal{width:min(560px,100%);max-height:calc(100dvh - 36px);overflow:auto;background:var(--surface);border:1px solid var(--line-strong);border-radius:16px;padding:22px;box-shadow:0 24px 70px rgba(0,0,0,.45)}.modal h2{margin:0 0 16px;font-size:20px;letter-spacing:-.02em}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.form-group.full{grid-column:1/-1}.form-group label{display:block;margin-bottom:7px;color:#dbe3ef;font-size:12px;font-weight:650}.form-group input{width:100%;min-height:40px;border-radius:10px;border:1px solid var(--line-strong);background:var(--surface-3);color:var(--text);padding:9px 10px;outline:none}.form-group input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(143,184,255,.14)}.form-actions{display:flex;gap:10px;justify-content:flex-end;margin-top:18px}
.toast{position:fixed;top:18px;right:18px;z-index:30;max-width:380px;padding:12px 14px;border-radius:11px;background:var(--surface);border:1px solid var(--line-strong);color:var(--text);box-shadow:0 14px 40px rgba(0,0,0,.34);font-size:13px}.toast.success{border-color:rgba(133,225,180,.45)}.toast.error{border-color:rgba(255,141,155,.55)}
@media(max-width:980px){.app{grid-template-columns:1fr}.sidebar{position:sticky;top:0;height:auto;z-index:15;border-right:0;border-bottom:1px solid var(--line);padding:14px 18px;display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center}.nav-note{display:none}.nav-actions{margin-top:0;display:flex;gap:8px}.side-btn{width:auto;min-height:36px}.main{padding:22px}.topbar{top:65px;margin:-22px -22px 18px;padding:20px 22px 14px}.topbar-row{display:grid}.summary{grid-template-columns:1fr 1fr}.controls{grid-template-columns:1fr auto}.result-count{grid-column:1/-1}.list,.nodes-list{grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}}
@media(max-width:560px){.sidebar{grid-template-columns:1fr}.nav-actions{width:100%;display:grid;grid-template-columns:1fr 1fr}.topbar{top:122px}.summary{grid-template-columns:1fr}.controls{grid-template-columns:1fr}.toolbar{width:100%;display:grid;grid-template-columns:1fr 1fr}.btn{justify-content:center}.actions{justify-content:flex-start}.card-head{display:grid}.status-pill{width:max-content}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition-duration:.01ms!important;animation-duration:.01ms!important}}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand"><div class="logo">N</div><div><b>Nekro User Panel</b><span>Admin console</span></div></div>
    <div class="nav-note">Denia 是总部面板。先登记节点，再把实例挂到对应节点，避免跨服务器路由混乱。</div>
    <div class="nav-actions">
      <button class="side-btn" onclick="location.href='/webui'">打开当前 WebUI</button>
      <button class="side-btn danger" onclick="logout()">退出登录</button>
    </div>
  </aside>
  <main class="main">
    <div class="topbar">
      <div class="topbar-row">
        <div><h1>总部路由管理</h1><p class="sub">维护服务器节点与 Nekro Agent 实例映射。节点代表服务器，实例代表用户登录后进入的 NA 后端。</p></div>
        <div class="toolbar"><button class="btn" onclick="loadAll()">刷新</button><button class="btn" onclick="showCreateNodeModal()">添加节点</button><button class="btn btn-primary" onclick="showCreateInstanceModal()">添加实例</button></div>
      </div>
    </div>
    <section class="summary" aria-label="概览">
      <div class="metric"><span>节点数量</span><b id="metric-node-count">0</b></div>
      <div class="metric"><span>实例数量</span><b id="metric-count">0</b></div>
      <div class="metric"><span>当前选择</span><b id="metric-current">未选择</b></div>
      <div class="metric"><span>路由策略</span><b>集群 / 节点</b></div>
    </section>
    <section class="section-block" aria-label="节点">
      <div class="section-head">
        <div><h2>节点</h2><p>服务器级入口。总部、苏州、后续机器都在这里维护。</p></div>
        <button class="btn" onclick="showCreateNodeModal()">添加节点</button>
      </div>
      <div id="nodes-list" class="list nodes-list"></div>
    </section>
    <section class="section-block" aria-label="实例">
      <div class="section-head">
        <div><h2>实例</h2><p>用户账号到 NA 后端的最终路由。实例可以挂到任意节点。</p></div>
        <button class="btn btn-primary" onclick="showCreateInstanceModal()">添加实例</button>
      </div>
      <section class="controls" aria-label="筛选实例">
        <div class="search-wrap"><input id="search" type="search" placeholder="搜索实例 ID、集群、节点、备注、端口或主机" autocomplete="off" oninput="renderInstances()"><span class="search-icon">Search</span></div>
        <button class="btn" onclick="clearSearch()">清空搜索</button>
        <div class="result-count" id="result-count">0 个结果</div>
      </section>
      <div id="instances-list" class="list"></div>
    </section>
  </main>
</div>

<div class="modal-overlay" id="node-modal">
  <div class="modal">
    <h2 id="node-modal-title">添加节点</h2>
    <div class="form-grid">
      <div class="form-group"><label>节点 ID</label><input id="n-id" placeholder="例如 suzhou"></div>
      <div class="form-group"><label>节点名称</label><input id="n-name" placeholder="例如 Suzhou"></div>
      <div class="form-group"><label>集群 ID</label><input id="n-cluster-id" value="default"></div>
      <div class="form-group"><label>集群名称</label><input id="n-cluster-name" placeholder="例如 Suzhou"></div>
      <div class="form-group"><label>角色</label><input id="n-role" value="node" placeholder="headquarters 或 node"></div>
      <div class="form-group"><label>状态</label><input id="n-status" value="unknown" placeholder="online / partial / offline"></div>
      <div class="form-group full"><label>Nekro User Panel 地址</label><input id="n-panel-url" placeholder="可选，例如 http://host:9054"></div>
      <div class="form-group full"><label>ncqq-manager 地址</label><input id="n-ncqq-url" placeholder="可选，例如 http://host:8000"></div>
      <div class="form-group"><label>SSH Host</label><input id="n-ssh-host" placeholder="one.akiyo.fun"></div>
      <div class="form-group"><label>SSH Port</label><input id="n-ssh-port" type="number" placeholder="24022"></div>
      <div class="form-group full"><label>SSH User</label><input id="n-ssh-user" placeholder="f1ycar"></div>
      <div class="form-group full"><label>备注</label><input id="n-comment" placeholder="节点说明或当前阻塞"></div>
    </div>
    <div class="form-actions"><button class="btn" onclick="closeNodeModal()">取消</button><button class="btn btn-primary" onclick="submitNodeForm()">保存节点</button></div>
  </div>
</div>

<div class="modal-overlay" id="modal">
  <div class="modal">
    <h2 id="modal-title">添加实例</h2>
    <div class="form-grid">
      <div class="form-group"><label>用户 ID</label><input id="f-id" placeholder="例如 GBNA1"></div>
      <div class="form-group"><label>面板登录密码</label><input id="f-password" type="text" placeholder="面板密码"></div>
      <div class="form-group"><label>NA 端口</label><input id="f-port" type="number" placeholder="8021"></div>
      <div class="form-group"><label>NA 主机</label><input id="f-host" value="127.0.0.1"></div>
      <div class="form-group"><label>集群 ID</label><input id="f-cluster-id" value="default" placeholder="default"></div>
      <div class="form-group"><label>集群名称</label><input id="f-cluster-name" placeholder="例如 Denia"></div>
      <div class="form-group"><label>节点 ID</label><input id="f-node-id" value="local" placeholder="local"></div>
      <div class="form-group"><label>节点名称</label><input id="f-node-name" placeholder="例如 Denia Mac mini"></div>
      <div class="form-group full"><label>NA 完整地址</label><input id="f-base-url" placeholder="可选，例如 http://10.0.0.12:8021；填写后优先使用"></div>
      <div class="form-group full"><label>登录别名</label><input id="f-aliases" placeholder="可选，多个用英文逗号分隔"></div>
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
let editingNodeId = null;
let instancesCache = [];
let nodesCache = [];

function escapeHtml(v){return String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function searchableText(i){return [i.id,i.comment,i.na_host,i.na_port,i.na_admin_user,i.cluster_id,i.cluster_name,i.node_id,i.node_name,i.na_base_url,i.na_backend_url,(i.login_aliases||[]).join(',')].map(v=>String(v ?? '').toLowerCase()).join(' ');}

function clearAuthStorage(){
  ['nekro_user_panel_token','nekro_user_panel_username','nekro_user_panel_userinfo','panel_token','token','auth-storage'].forEach(k => localStorage.removeItem(k));
  ['panel_token','admin_instance'].forEach(k => { document.cookie = k + '=; path=/; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax'; });
}
function syncWebuiAuthStorage(){
  if(!TOKEN) return;
  localStorage.setItem('nekro_user_panel_token', TOKEN);
  localStorage.setItem('panel_token', TOKEN);
  localStorage.setItem('token', TOKEN);
  localStorage.setItem('nekro_user_panel_username', 'admin');
  localStorage.setItem('auth-storage', JSON.stringify({
    state: { token: TOKEN, userInfo: { username: 'admin', userId: 1, perm_level: 2, perm_role: 'Admin' } },
    version: 0,
  }));
  document.cookie = 'panel_token=' + encodeURIComponent(TOKEN) + '; path=/; max-age=86400; SameSite=Lax';
}
async function logout(){try { await fetch('/panel/logout', {method:'POST', headers}); } catch(e) {} clearAuthStorage(); location.href = '/webui';}

async function loadCurrent(){
  try{const resp = await fetch('/panel/admin/current-instance', {headers}); if(resp.ok){const data = await resp.json(); document.getElementById('metric-current').textContent = data.instance_id ? `${data.instance_id} · ${data.route_label || data.na_backend_url || ''}` : '未选择';}}catch(e){}
}
async function loadNodes(){
  const resp = await fetch('/panel/admin/nodes', {headers});
  if(resp.status === 401 || resp.status === 403){ clearAuthStorage(); location.href='/webui'; return; }
  const data = await resp.json();
  nodesCache = data.sort((a,b)=>String(a.id).localeCompare(String(b.id), 'zh-Hans-u-kn-true'));
  document.getElementById('metric-node-count').textContent = data.length;
  renderNodes();
}
async function loadInstances(){
  const resp = await fetch('/panel/admin/instances', {headers});
  if(resp.status === 401 || resp.status === 403){ clearAuthStorage(); location.href='/webui'; return; }
  const data = await resp.json();
  instancesCache = data.sort((a,b)=>String(a.id).localeCompare(String(b.id), 'zh-Hans-u-kn-true'));
  document.getElementById('metric-count').textContent = data.length;
  await loadCurrent();
  renderInstances();
}
async function loadAll(){ await loadNodes(); await loadInstances(); }
function statusClass(status){return String(status || 'unknown').toLowerCase().replace(/[^a-z0-9_-]/g,'');}
function renderNodes(){
  const el = document.getElementById('nodes-list');
  if(!nodesCache.length){ el.innerHTML='<div class="empty">暂无节点。先添加 Denia 总部或远程服务器节点。</div>'; return; }
  el.innerHTML = nodesCache.map(n => `
    <article class="card">
      <div class="card-head">
        <div><h3>${escapeHtml(n.display_name || n.name || n.id)}</h3><div class="comment">ID: ${escapeHtml(n.id)} · ${escapeHtml(n.route_label || n.cluster_id || 'default')}</div></div>
        <span class="status-pill ${statusClass(n.status)}">${escapeHtml(n.status || 'unknown')}</span>
      </div>
      <div class="fields">
        <span class="field">${escapeHtml(n.role || 'node')}</span>
        <span class="field">实例 ${escapeHtml(n.instance_count || 0)}</span>
        ${n.panel_base_url ? `<span class="field">${escapeHtml(n.panel_base_url)}</span>` : ''}
        ${n.ncqq_base_url ? `<span class="field">ncqq ${escapeHtml(n.ncqq_base_url)}</span>` : ''}
        ${n.ssh_host ? `<span class="field">ssh ${escapeHtml(n.ssh_user || '')}@${escapeHtml(n.ssh_host)}${n.ssh_port ? ':' + escapeHtml(n.ssh_port) : ''}</span>` : ''}
      </div>
      ${n.comment ? `<div class="comment">${escapeHtml(n.comment)}</div>` : ''}
      <div class="actions">
        ${n.panel_base_url ? `<button class="btn btn-success btn-sm" onclick="location.href='${escapeHtml(n.panel_base_url)}'">打开面板</button>` : ''}
        <button class="btn btn-sm" onclick="editNode('${escapeHtml(n.id)}')">编辑节点</button>
        <button class="btn btn-danger btn-sm" onclick="deleteNode('${escapeHtml(n.id)}')">删除节点</button>
      </div>
    </article>`).join('');
}
function renderInstances(){
  const q = document.getElementById('search').value.trim().toLowerCase();
  const data = q ? instancesCache.filter(i => searchableText(i).includes(q)) : instancesCache;
  document.getElementById('result-count').textContent = `${data.length} / ${instancesCache.length} 个结果`;
  const el = document.getElementById('instances-list');
  if(!instancesCache.length){ el.innerHTML='<div class="empty">暂无实例。添加一个实例后才能路由到 WebUI。</div>'; return; }
  if(!data.length){ el.innerHTML='<div class="empty">没有匹配的实例。换个关键词试试。</div>'; return; }
  el.innerHTML = data.map(i => `
    <article class="card">
      <div class="card-head">
        <div><h3>${escapeHtml(i.comment || i.id)}</h3><div class="comment">ID: ${escapeHtml(i.id)}</div></div>
        <span class="status-pill">configured</span>
      </div>
      <div class="fields">
        <span class="field">${escapeHtml(i.route_label || `${i.cluster_id || 'default'}/${i.node_id || 'local'}`)}</span>
        <span class="field">${escapeHtml(i.na_backend_url || i.na_base_url || `${i.na_host}:${i.na_port}`)}</span>
        <span class="field">管理员 ${escapeHtml(i.na_admin_user)}</span>
        ${(i.login_aliases || []).length ? `<span class="field">别名 ${escapeHtml(i.login_aliases.join(', '))}</span>` : ''}
      </div>
      <div class="actions">
        <button class="btn btn-success btn-sm" onclick="enterInstance('${escapeHtml(i.id)}')">进入管理</button>
        <button class="btn btn-sm" onclick="editInstance('${escapeHtml(i.id)}')">编辑</button>
        <button class="btn btn-danger btn-sm" onclick="deleteInstance('${escapeHtml(i.id)}')">删除</button>
      </div>
    </article>`).join('');
}
function clearSearch(){document.getElementById('search').value=''; renderInstances(); document.getElementById('search').focus();}
function showCreateInstanceModal(){editingId=null; document.getElementById('modal-title').textContent='添加实例'; ['f-id','f-password','f-port','f-comment','f-cluster-name','f-node-name','f-base-url','f-aliases'].forEach(id=>document.getElementById(id).value=''); document.getElementById('f-id').disabled=false; document.getElementById('f-admin-user').value='admin'; document.getElementById('f-admin-pass').value=''; document.getElementById('f-host').value='127.0.0.1'; const firstNode=nodesCache[0] || {}; document.getElementById('f-cluster-id').value=firstNode.cluster_id || 'default'; document.getElementById('f-cluster-name').value=firstNode.cluster_name || ''; document.getElementById('f-node-id').value=firstNode.id || 'local'; document.getElementById('f-node-name').value=firstNode.display_name || firstNode.name || ''; document.getElementById('modal').classList.add('active');}
async function editInstance(id){const resp = await fetch(`/panel/admin/instances/${encodeURIComponent(id)}`, {headers}); const data = await resp.json(); editingId=id; document.getElementById('modal-title').textContent='编辑实例: '+id; document.getElementById('f-id').value=data.id; document.getElementById('f-id').disabled=false; document.getElementById('f-password').value=data.panel_password; document.getElementById('f-port').value=data.na_port || ''; document.getElementById('f-admin-user').value=data.na_admin_user; document.getElementById('f-admin-pass').value=data.na_admin_pass; document.getElementById('f-host').value=data.na_host || '127.0.0.1'; document.getElementById('f-cluster-id').value=data.cluster_id || 'default'; document.getElementById('f-cluster-name').value=data.cluster_name || ''; document.getElementById('f-node-id').value=data.node_id || 'local'; document.getElementById('f-node-name').value=data.node_name || ''; document.getElementById('f-base-url').value=data.na_base_url || ''; document.getElementById('f-aliases').value=(data.login_aliases || []).join(', '); document.getElementById('f-comment').value=data.comment || ''; document.getElementById('modal').classList.add('active');}
function closeModal(){document.getElementById('modal').classList.remove('active');}
async function submitForm(){const portValue=document.getElementById('f-port').value.trim(); const baseUrl=document.getElementById('f-base-url').value.trim(); const body={id:document.getElementById('f-id').value.trim(),panel_password:document.getElementById('f-password').value,na_port:portValue ? parseInt(portValue,10) : null,na_admin_user:document.getElementById('f-admin-user').value.trim(),na_admin_pass:document.getElementById('f-admin-pass').value,na_host:document.getElementById('f-host').value.trim(),na_base_url:baseUrl || null,cluster_id:document.getElementById('f-cluster-id').value.trim() || 'default',cluster_name:document.getElementById('f-cluster-name').value.trim(),node_id:document.getElementById('f-node-id').value.trim() || 'local',node_name:document.getElementById('f-node-name').value.trim(),login_aliases:document.getElementById('f-aliases').value.split(',').map(v=>v.trim()).filter(Boolean),comment:document.getElementById('f-comment').value.trim()}; if(!body.id || !body.panel_password || (!body.na_port && !body.na_base_url) || !body.na_admin_pass){toast('请填写用户 ID、面板密码、NA 地址/端口、NA 管理员密码','error');return;} const url = editingId ? `/panel/admin/instances/${encodeURIComponent(editingId)}` : '/panel/admin/instances'; const method = editingId ? 'PUT' : 'POST'; const resp = await fetch(url,{method,headers,body:JSON.stringify(body)}); const result = await resp.json().catch(()=>({})); if(resp.ok){toast(result.message || '已保存','success'); closeModal(); loadAll();} else {toast(result.detail || '操作失败','error');}}
async function deleteInstance(id){if(!confirm(`确定删除实例 "${id}" 吗？`)) return; const resp = await fetch(`/panel/admin/instances/${encodeURIComponent(id)}`,{method:'DELETE',headers}); const result = await resp.json().catch(()=>({})); if(resp.ok){toast(result.message || '已删除','success'); loadAll();} else {toast(result.detail || '删除失败','error');}}
async function enterInstance(id){const resp = await fetch(`/panel/admin/switch-instance/${encodeURIComponent(id)}`,{method:'POST',headers}); if(resp.ok){syncWebuiAuthStorage(); toast('已切换到实例: '+id,'success'); await loadCurrent(); setTimeout(()=>{location.href='/webui#/dashboard';},350);} else {const err=await resp.json().catch(()=>({})); toast(err.detail || '切换失败','error');}}
function showCreateNodeModal(){editingNodeId=null; document.getElementById('node-modal-title').textContent='添加节点'; ['n-id','n-name','n-cluster-name','n-panel-url','n-ncqq-url','n-ssh-host','n-ssh-port','n-ssh-user','n-comment'].forEach(id=>document.getElementById(id).value=''); document.getElementById('n-cluster-id').value='default'; document.getElementById('n-role').value='node'; document.getElementById('n-status').value='unknown'; document.getElementById('node-modal').classList.add('active');}
async function editNode(id){const resp = await fetch(`/panel/admin/nodes/${encodeURIComponent(id)}`, {headers}); const data = await resp.json(); editingNodeId=id; document.getElementById('node-modal-title').textContent='编辑节点: '+id; document.getElementById('n-id').value=data.id; document.getElementById('n-name').value=data.name || ''; document.getElementById('n-cluster-id').value=data.cluster_id || 'default'; document.getElementById('n-cluster-name').value=data.cluster_name || ''; document.getElementById('n-role').value=data.role || 'node'; document.getElementById('n-status').value=data.status || 'unknown'; document.getElementById('n-panel-url').value=data.panel_base_url || ''; document.getElementById('n-ncqq-url').value=data.ncqq_base_url || ''; document.getElementById('n-ssh-host').value=data.ssh_host || ''; document.getElementById('n-ssh-port').value=data.ssh_port || ''; document.getElementById('n-ssh-user').value=data.ssh_user || ''; document.getElementById('n-comment').value=data.comment || ''; document.getElementById('node-modal').classList.add('active');}
function closeNodeModal(){document.getElementById('node-modal').classList.remove('active');}
async function submitNodeForm(){const portValue=document.getElementById('n-ssh-port').value.trim(); const body={id:document.getElementById('n-id').value.trim(),name:document.getElementById('n-name').value.trim(),cluster_id:document.getElementById('n-cluster-id').value.trim() || 'default',cluster_name:document.getElementById('n-cluster-name').value.trim(),role:document.getElementById('n-role').value.trim() || 'node',status:document.getElementById('n-status').value.trim() || 'unknown',panel_base_url:document.getElementById('n-panel-url').value.trim() || null,ncqq_base_url:document.getElementById('n-ncqq-url').value.trim() || null,ssh_host:document.getElementById('n-ssh-host').value.trim(),ssh_port:portValue ? parseInt(portValue,10) : null,ssh_user:document.getElementById('n-ssh-user').value.trim(),comment:document.getElementById('n-comment').value.trim()}; if(!body.id){toast('请填写节点 ID','error');return;} const url = editingNodeId ? `/panel/admin/nodes/${encodeURIComponent(editingNodeId)}` : '/panel/admin/nodes'; const method = editingNodeId ? 'PUT' : 'POST'; const resp = await fetch(url,{method,headers,body:JSON.stringify(body)}); const result = await resp.json().catch(()=>({})); if(resp.ok){toast(result.message || '已保存','success'); closeNodeModal(); loadNodes();} else {toast(result.detail || '操作失败','error');}}
async function deleteNode(id){if(!confirm(`确定删除节点 "${id}" 吗？仍有实例引用的节点会被拒绝删除。`)) return; const resp = await fetch(`/panel/admin/nodes/${encodeURIComponent(id)}`,{method:'DELETE',headers}); const result = await resp.json().catch(()=>({})); if(resp.ok){toast(result.message || '已删除','success'); loadAll();} else {toast(result.detail || '删除失败','error');}}
function toast(msg,type){const el=document.createElement('div');el.className='toast '+type;el.textContent=msg;document.body.appendChild(el);setTimeout(()=>el.remove(),3200);}
loadAll();
</script>
</body>
</html>"""
