"""Admin console HTML for Nekro User Panel."""


def get_admin_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="color-scheme" content="dark" />
<title>Nekro User Panel Admin</title>
<style>
:root{
  --bg:#090c11;--panel:#101722;--panel-2:#151e2b;--panel-3:#0d131c;
  --line:#283244;--line-strong:#3a465c;--text:#f2f7ff;--muted:#a4b1c2;--faint:#748195;
  --accent:#5eead4;--accent-2:#7db4ff;--accent-text:#041012;--danger:#ff8da1;--success:#76e6b0;--warning:#ffd166;
  --radius:8px;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",system-ui,sans-serif;
}
*{box-sizing:border-box}html,body{min-height:100%}
body{margin:0;color:var(--text);background:linear-gradient(135deg,#090c11 0%,#10131a 48%,#0b1015 100%);font-size:14px}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background:radial-gradient(circle at 12% 8%,rgba(94,234,212,.13),transparent 24rem),radial-gradient(circle at 88% 10%,rgba(125,180,255,.12),transparent 26rem),linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px);background-size:auto,auto,100% 44px;mask-image:linear-gradient(to bottom,black,transparent 78%)}
button,input,select{font:inherit}.app{position:relative;z-index:1;min-height:100dvh;display:grid;grid-template-columns:248px minmax(0,1fr)}
.sidebar{position:sticky;top:0;height:100dvh;border-right:1px solid var(--line);background:rgba(9,12,17,.86);backdrop-filter:blur(18px);padding:22px;display:flex;flex-direction:column;gap:20px}
.brand{display:flex;align-items:center;gap:11px}.logo{width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,var(--accent),var(--accent-2));color:#051014;display:grid;place-items:center;font-weight:850;letter-spacing:0}.brand b{display:block;font-size:14px}.brand span{display:block;color:var(--faint);font-size:12px;margin-top:2px}
.nav-note{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:14px 0;color:var(--muted);font-size:12px;line-height:1.55}.nav-actions{margin-top:auto;display:grid;gap:9px}
.main{padding:28px;max-width:1440px;width:100%;margin:0 auto}.topbar{position:sticky;top:0;z-index:10;margin:-28px -28px 18px;padding:24px 28px 16px;background:linear-gradient(180deg,rgba(9,12,17,.97),rgba(9,12,17,.86) 72%,rgba(9,12,17,0));backdrop-filter:blur(14px)}
.topbar-row{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.kicker{margin:0 0 8px;color:var(--accent);font-size:12px;font-weight:760}.title{margin:0;font-size:28px;line-height:1.15;letter-spacing:0}.sub{margin:8px 0 0;color:var(--muted);line-height:1.55;max-width:72ch}.toolbar{display:flex;gap:9px;align-items:center;flex-wrap:wrap;justify-content:flex-end}
.btn{min-height:36px;padding:0 13px;border-radius:var(--radius);border:1px solid var(--line-strong);background:var(--panel-3);color:var(--text);font-size:13px;font-weight:720;cursor:pointer;white-space:nowrap;transition:background .16s ease,border-color .16s ease,transform .16s ease}.btn:hover{border-color:var(--accent)}.btn:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid rgba(94,234,212,.22);outline-offset:1px}.btn:active{transform:translateY(1px)}.btn-primary{background:var(--accent);border-color:transparent;color:var(--accent-text)}.btn-primary:hover{background:#8cf5e4}.btn-good{color:var(--success)}.btn-danger{color:var(--danger)}.btn-sm{min-height:30px;padding:0 9px;font-size:12px}.side-btn{text-align:left;width:100%}
.ops-strip{display:grid;grid-template-columns:minmax(260px,1.5fr) repeat(3,minmax(140px,1fr));gap:10px;margin-bottom:18px}.stat{border:1px solid var(--line);background:rgba(16,23,34,.82);border-radius:var(--radius);padding:13px 14px;min-width:0}.stat span{display:block;color:var(--faint);font-size:12px}.stat b{display:block;margin-top:6px;font-size:18px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.stat.current b{color:#fff}
.section{margin-top:20px}.section-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:10px}.section-head h2{margin:0;font-size:17px;letter-spacing:0}.section-head p{margin:5px 0 0;color:var(--muted);font-size:13px;line-height:1.45}.node-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:11px}.instance-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:11px}
.card{border:1px solid var(--line);background:linear-gradient(180deg,rgba(21,30,43,.92),rgba(14,20,30,.92));border-radius:var(--radius);padding:14px;display:grid;gap:12px;min-width:0}.card:hover{border-color:#44546e}.card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.card h3{margin:0;font-size:15px;line-height:1.3;letter-spacing:0}.caption{margin-top:4px;color:var(--muted);font-size:12px;line-height:1.45}.badge{display:inline-flex;align-items:center;gap:6px;border:1px solid rgba(118,230,176,.38);background:rgba(118,230,176,.08);color:var(--success);border-radius:999px;padding:4px 8px;font-size:11px;font-weight:760;white-space:nowrap}.badge.offline,.badge.unconfigured{border-color:rgba(255,141,161,.45);background:rgba(255,141,161,.08);color:var(--danger)}.badge.partial,.badge.reachable,.badge.unknown{border-color:rgba(255,209,102,.44);background:rgba(255,209,102,.08);color:var(--warning)}
.fields{display:grid;gap:7px}.field{display:flex;justify-content:space-between;gap:12px;border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.025);border-radius:var(--radius);padding:7px 9px;min-width:0}.field span:first-child{color:var(--faint);font-size:12px;white-space:nowrap}.field span:last-child{color:#d8e2ef;font-size:12px;text-align:right;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{border:1px solid rgba(125,180,255,.28);background:rgba(125,180,255,.07);color:#cfe0ff;border-radius:999px;padding:4px 7px;font-size:11px}.actions{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;margin-top:2px}.empty{grid-column:1/-1;border:1px dashed var(--line-strong);border-radius:var(--radius);padding:28px;text-align:center;color:var(--muted);background:rgba(16,23,34,.48)}
.controls{display:grid;grid-template-columns:minmax(220px,1fr) 190px auto auto;gap:9px;align-items:center;margin:0 0 12px}.search input,.controls select{width:100%;min-height:38px;border-radius:var(--radius);border:1px solid var(--line-strong);background:rgba(13,19,28,.92);color:var(--text);padding:0 11px}.result-count{color:var(--faint);font-size:12px;white-space:nowrap}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.68);z-index:30;align-items:center;justify-content:center;padding:18px}.modal-overlay.active{display:flex}.modal{width:min(680px,100%);max-height:calc(100dvh - 36px);overflow:auto;background:var(--panel);border:1px solid var(--line-strong);border-radius:var(--radius);box-shadow:0 24px 80px rgba(0,0,0,.5);padding:20px}.modal h2{margin:0 0 14px;font-size:20px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.form-group.full{grid-column:1/-1}.form-group label{display:block;margin-bottom:6px;color:#dfe8f4;font-size:12px;font-weight:700}.form-group input,.form-group select{width:100%;min-height:39px;border-radius:var(--radius);border:1px solid var(--line-strong);background:var(--panel-3);color:var(--text);padding:8px 10px}.form-group input[readonly]{color:var(--muted);background:#111824}.form-section{grid-column:1/-1;margin-top:2px;padding-top:12px;border-top:1px solid var(--line);color:var(--accent);font-size:12px;font-weight:800}.hint{margin-top:6px;color:var(--faint);font-size:12px;line-height:1.4}.form-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:18px}.toast{position:fixed;right:18px;top:18px;z-index:40;max-width:420px;border:1px solid var(--line-strong);background:var(--panel);color:var(--text);border-radius:var(--radius);padding:11px 13px;box-shadow:0 16px 46px rgba(0,0,0,.42);font-size:13px}.toast.success{border-color:rgba(118,230,176,.5)}.toast.error{border-color:rgba(255,141,161,.55)}
@media(max-width:1040px){.app{grid-template-columns:1fr}.sidebar{height:auto;position:sticky;z-index:20;border-right:0;border-bottom:1px solid var(--line);padding:14px 18px;display:grid;grid-template-columns:1fr auto;align-items:center}.nav-note{display:none}.nav-actions{margin:0;display:flex}.main{padding:22px}.topbar{top:65px;margin:-22px -22px 16px;padding:20px 22px 14px}.topbar-row{display:grid}.ops-strip{grid-template-columns:1fr 1fr}.controls{grid-template-columns:1fr 160px auto}.result-count{grid-column:1/-1}.form-grid{grid-template-columns:1fr}}
@media(max-width:620px){.sidebar{grid-template-columns:1fr}.nav-actions{display:grid;grid-template-columns:1fr 1fr}.topbar{top:120px}.toolbar{display:grid;grid-template-columns:1fr 1fr;width:100%}.toolbar .btn:first-child{grid-column:1/-1}.ops-strip,.controls,.node-grid,.instance-grid{grid-template-columns:1fr}.card-head{display:grid}.actions{justify-content:flex-start}.field{display:grid}.field span:last-child{text-align:left}.modal{padding:16px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition-duration:.01ms!important;animation-duration:.01ms!important}}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand"><div class="logo">N</div><div><b>Nekro User Panel</b><span>Denia headquarters</span></div></div>
    <div class="nav-note">节点是服务器归属和 HTTP 入口，实例是登录后实际进入的 NA 后端。总部不会通过 SSH 管理节点。</div>
    <div class="nav-actions">
      <button class="btn side-btn" onclick="location.href='/webui'">打开当前 WebUI</button>
      <button class="btn side-btn btn-danger" onclick="logout()">退出登录</button>
    </div>
  </aside>
  <main class="main">
    <div class="topbar">
      <div class="topbar-row">
        <div>
          <p class="kicker">总部控制台</p>
          <h1 class="title">多节点实例路由</h1>
          <p class="sub">Denia 作为总部维护节点、入口状态和用户实例映射。远端节点需要提供总部可访问的 HTTP 地址或 NA 隧道。</p>
        </div>
        <div class="toolbar">
          <button class="btn" onclick="loadAll()">刷新状态</button>
          <button class="btn" onclick="showCreateNodeModal()">添加节点</button>
          <button class="btn btn-primary" onclick="showCreateInstanceModal()">添加实例</button>
        </div>
      </div>
    </div>

    <section class="ops-strip" aria-label="运行态">
      <div class="stat current"><span>当前管理目标</span><b id="metric-current">未选择</b></div>
      <div class="stat"><span>节点</span><b id="metric-node-count">0</b></div>
      <div class="stat"><span>实例</span><b id="metric-count">0</b></div>
      <div class="stat"><span>最近刷新</span><b id="metric-updated">未刷新</b></div>
    </section>

    <section class="section" aria-label="节点">
      <div class="section-head">
        <div><h2>节点拓扑</h2><p>总部、苏州和后续服务器按节点维护，状态由 HTTP 探测确认。</p></div>
        <button class="btn" onclick="showCreateNodeModal()">添加节点</button>
      </div>
      <div id="nodes-list" class="node-grid"></div>
    </section>

    <section class="section" aria-label="实例">
      <div class="section-head">
        <div><h2>实例清单</h2><p>每个用户登录名会路由到一个具体 NA 后端。</p></div>
        <button class="btn btn-primary" onclick="showCreateInstanceModal()">添加实例</button>
      </div>
      <div class="controls" aria-label="筛选实例">
        <div class="search"><input id="search" type="search" placeholder="搜索实例、节点、后端、别名或备注" autocomplete="off" oninput="renderInstances()"></div>
        <select id="node-filter" onchange="renderInstances()"><option value="">全部节点</option></select>
        <button class="btn" onclick="clearSearch()">清空</button>
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
      <div class="form-group"><label>角色</label><select id="n-role"><option value="node">node</option><option value="headquarters">headquarters</option></select></div>
      <div class="form-group"><label>状态</label><select id="n-status"><option value="unknown">unknown</option><option value="online">online</option><option value="partial">partial</option><option value="offline">offline</option></select></div>
      <div class="form-section">HTTP 入口</div>
      <div class="form-group full"><label>Nekro User Panel 地址</label><input id="n-panel-url" placeholder="可选，例如 https://node.example.com"></div>
      <div class="form-group full"><label>节点管理 API 地址</label><input id="n-manager-url" placeholder="可选，例如 http://127.0.0.1:18000"></div>
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
const headers = {'Content-Type':'application/json'};
if (TOKEN) headers['Authorization'] = 'Bearer ' + TOKEN;
let editingId = null;
let editingNodeId = null;
let instancesCache = [];
let nodesCache = [];

function escapeHtml(v){return String(v ?? '').replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function nodeById(id){return nodesCache.find(n => n.id === id) || null;}
function statusClass(status){return String(status || 'unknown').toLowerCase().replace(/[^a-z0-9_-]/g,'') || 'unknown';}
function searchableText(i){return [i.id,i.comment,i.na_host,i.na_port,i.na_admin_user,i.cluster_id,i.cluster_name,i.node_id,i.node_name,i.na_base_url,i.na_backend_url,(i.login_aliases||[]).join(',')].map(v=>String(v ?? '').toLowerCase()).join(' ');}
function nowLabel(){return new Date().toLocaleTimeString('zh-CN',{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'});}

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
async function logout(){try{await fetch('/panel/logout',{method:'POST',headers});}catch(e){} clearAuthStorage(); location.href='/webui';}

async function loadCurrent(){
  try{
    const resp = await fetch('/panel/admin/current-instance',{headers});
    if(resp.ok){
      const data = await resp.json();
      document.getElementById('metric-current').textContent = data.instance_id ? `${data.instance_id} · ${data.route_label || data.na_backend_url || ''}` : '未选择';
    }
  }catch(e){}
}
async function loadNodes(){
  const resp = await fetch('/panel/admin/nodes',{headers});
  if(resp.status === 401 || resp.status === 403){ clearAuthStorage(); location.href='/webui'; return; }
  const data = await resp.json();
  nodesCache = data.sort((a,b)=>String(a.id).localeCompare(String(b.id),'zh-Hans-u-kn-true'));
  document.getElementById('metric-node-count').textContent = data.length;
  renderNodeOptions();
  renderNodes();
}
async function loadInstances(){
  const resp = await fetch('/panel/admin/instances',{headers});
  if(resp.status === 401 || resp.status === 403){ clearAuthStorage(); location.href='/webui'; return; }
  const data = await resp.json();
  instancesCache = data.sort((a,b)=>String(a.id).localeCompare(String(b.id),'zh-Hans-u-kn-true'));
  document.getElementById('metric-count').textContent = data.length;
  await loadCurrent();
  renderInstances();
}
async function loadAll(){await loadNodes(); await loadInstances(); document.getElementById('metric-updated').textContent = nowLabel();}

function renderNodeOptions(){
  const filter = document.getElementById('node-filter');
  filter.innerHTML = '<option value="">全部节点</option>' + nodesCache.map(n => `<option value="${escapeHtml(n.id)}">${escapeHtml(n.display_name || n.id)}</option>`).join('');
  const select = document.getElementById('f-node-select');
  if(select) select.innerHTML = nodesCache.map(n => `<option value="${escapeHtml(n.id)}">${escapeHtml(n.display_name || n.id)} · ${escapeHtml(n.route_label || n.cluster_id)}</option>`).join('');
}
function renderNodes(){
  const el = document.getElementById('nodes-list');
  if(!nodesCache.length){el.innerHTML='<div class="empty">暂无节点。</div>';return;}
  el.innerHTML = nodesCache.map(n => {
    const endpoint = n.manager_base_url || n.panel_base_url || '未配置';
    return `<article class="card">
      <div class="card-head">
        <div><h3>${escapeHtml(n.display_name || n.name || n.id)}</h3><div class="caption">${escapeHtml(n.id)} · ${escapeHtml(n.route_label || n.cluster_id || 'default')}</div></div>
        <span class="badge ${statusClass(n.status)}">${escapeHtml(n.status || 'unknown')}</span>
      </div>
      <div class="fields">
        <div class="field"><span>角色</span><span>${escapeHtml(n.role || 'node')}</span></div>
        <div class="field"><span>实例</span><span>${escapeHtml(n.instance_count || 0)}</span></div>
        <div class="field"><span>HTTP 入口</span><span title="${escapeHtml(endpoint)}">${escapeHtml(endpoint)}</span></div>
        <div class="field"><span>API Key</span><span>${n.manager_api_key_set ? '已设置' : '未设置'}</span></div>
      </div>
      ${n.comment ? `<div class="caption">${escapeHtml(n.comment)}</div>` : ''}
      <div class="actions">
        ${n.panel_base_url ? `<button class="btn btn-sm btn-good" onclick="openPanel('${escapeHtml(n.panel_base_url)}')">打开面板</button>` : ''}
        <button class="btn btn-sm" onclick="probeNode('${escapeHtml(n.id)}')">测试连接</button>
        <button class="btn btn-sm" onclick="editNode('${escapeHtml(n.id)}')">编辑</button>
        <button class="btn btn-sm btn-danger" onclick="deleteNode('${escapeHtml(n.id)}')">删除</button>
      </div>
    </article>`;
  }).join('');
}
function renderInstances(){
  const q = document.getElementById('search').value.trim().toLowerCase();
  const nodeFilter = document.getElementById('node-filter').value;
  let data = instancesCache;
  if(nodeFilter) data = data.filter(i => i.node_id === nodeFilter);
  if(q) data = data.filter(i => searchableText(i).includes(q));
  document.getElementById('result-count').textContent = `${data.length} / ${instancesCache.length} 个结果`;
  const el = document.getElementById('instances-list');
  if(!instancesCache.length){el.innerHTML='<div class="empty">暂无实例。</div>';return;}
  if(!data.length){el.innerHTML='<div class="empty">没有匹配的实例。</div>';return;}
  el.innerHTML = data.map(i => {
    const node = nodeById(i.node_id);
    const nodeName = node ? (node.display_name || node.id) : (i.node_name || i.node_id || '未登记节点');
    return `<article class="card">
      <div class="card-head">
        <div><h3>${escapeHtml(i.id)}</h3><div class="caption">${escapeHtml(i.comment || '无备注')}</div></div>
        <span class="badge unknown">未检测</span>
      </div>
      <div class="fields">
        <div class="field"><span>节点</span><span>${escapeHtml(nodeName)}</span></div>
        <div class="field"><span>路由</span><span>${escapeHtml(i.route_label || `${i.cluster_id || 'default'}/${i.node_id || 'local'}`)}</span></div>
        <div class="field"><span>后端</span><span title="${escapeHtml(i.na_backend_url || '')}">${escapeHtml(i.na_backend_url || i.na_base_url || `${i.na_host}:${i.na_port}`)}</span></div>
        <div class="field"><span>管理员</span><span>${escapeHtml(i.na_admin_user || 'admin')}</span></div>
      </div>
      ${(i.login_aliases || []).length ? `<div class="chips">${i.login_aliases.map(a => `<span class="chip">${escapeHtml(a)}</span>`).join('')}</div>` : ''}
      <div class="actions">
        <button class="btn btn-sm btn-good" onclick="enterInstance('${escapeHtml(i.id)}')">进入管理</button>
        <button class="btn btn-sm" onclick="copyText('${escapeHtml(i.na_backend_url || '')}')">复制后端</button>
        <button class="btn btn-sm" onclick="editInstance('${escapeHtml(i.id)}')">编辑</button>
        <button class="btn btn-sm btn-danger" onclick="deleteInstance('${escapeHtml(i.id)}')">删除</button>
      </div>
    </article>`;
  }).join('');
}
function clearSearch(){document.getElementById('search').value=''; document.getElementById('node-filter').value=''; renderInstances(); document.getElementById('search').focus();}
function openPanel(url){ if(url.includes('127.0.0.1:9054') || url.includes('localhost:9054')) location.href='/panel/admin'; else location.href=url; }
async function copyText(text){if(!text){toast('没有可复制的后端地址','error');return;} await navigator.clipboard.writeText(text); toast('已复制后端地址','success');}

function showCreateInstanceModal(){
  editingId=null; document.getElementById('modal-title').textContent='添加实例';
  ['f-id','f-password','f-port','f-comment','f-base-url','f-aliases','f-admin-pass'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('f-id').disabled=false; document.getElementById('f-admin-user').value='admin'; document.getElementById('f-host').value='127.0.0.1';
  renderNodeOptions(); document.getElementById('f-node-select').value=(nodesCache[0]||{}).id || ''; syncNodeSelection(); document.getElementById('modal').classList.add('active');
}
function syncNodeSelection(){
  const node = nodeById(document.getElementById('f-node-select').value) || nodesCache[0] || {};
  document.getElementById('f-cluster-id').value=node.cluster_id || 'default';
  document.getElementById('f-cluster-name').value=node.cluster_name || '';
  document.getElementById('f-node-id').value=node.id || 'local';
  document.getElementById('f-node-name').value=node.display_name || node.name || '';
}
async function editInstance(id){
  const resp = await fetch(`/panel/admin/instances/${encodeURIComponent(id)}`,{headers}); const data = await resp.json();
  editingId=id; document.getElementById('modal-title').textContent='编辑实例: '+id;
  document.getElementById('f-id').value=data.id; document.getElementById('f-id').disabled=false; document.getElementById('f-password').value=data.panel_password;
  document.getElementById('f-port').value=data.na_port || ''; document.getElementById('f-admin-user').value=data.na_admin_user || 'admin'; document.getElementById('f-admin-pass').value=data.na_admin_pass || '';
  document.getElementById('f-host').value=data.na_host || '127.0.0.1'; document.getElementById('f-base-url').value=data.na_base_url || ''; document.getElementById('f-aliases').value=(data.login_aliases || []).join(', ');
  document.getElementById('f-comment').value=data.comment || ''; renderNodeOptions(); document.getElementById('f-node-select').value=data.node_id || 'local';
  syncNodeSelection(); document.getElementById('f-cluster-id').value=data.cluster_id || document.getElementById('f-cluster-id').value; document.getElementById('f-cluster-name').value=data.cluster_name || document.getElementById('f-cluster-name').value;
  document.getElementById('f-node-id').value=data.node_id || document.getElementById('f-node-id').value; document.getElementById('f-node-name').value=data.node_name || document.getElementById('f-node-name').value; document.getElementById('modal').classList.add('active');
}
function closeModal(){document.getElementById('modal').classList.remove('active');}
async function submitForm(){
  const portValue=document.getElementById('f-port').value.trim(); const baseUrl=document.getElementById('f-base-url').value.trim();
  const body={id:document.getElementById('f-id').value.trim(),panel_password:document.getElementById('f-password').value,na_port:portValue?parseInt(portValue,10):null,na_admin_user:document.getElementById('f-admin-user').value.trim(),na_admin_pass:document.getElementById('f-admin-pass').value,na_host:document.getElementById('f-host').value.trim(),na_base_url:baseUrl || null,cluster_id:document.getElementById('f-cluster-id').value.trim() || 'default',cluster_name:document.getElementById('f-cluster-name').value.trim(),node_id:document.getElementById('f-node-id').value.trim() || 'local',node_name:document.getElementById('f-node-name').value.trim(),login_aliases:document.getElementById('f-aliases').value.split(',').map(v=>v.trim()).filter(Boolean),comment:document.getElementById('f-comment').value.trim()};
  if(!body.id || !body.panel_password || (!body.na_port && !body.na_base_url) || !body.na_admin_pass){toast('请填写用户 ID、面板密码、NA 地址/端口和 NA 管理员密码','error');return;}
  const url = editingId ? `/panel/admin/instances/${encodeURIComponent(editingId)}` : '/panel/admin/instances'; const method = editingId ? 'PUT' : 'POST';
  const resp = await fetch(url,{method,headers,body:JSON.stringify(body)}); const result = await resp.json().catch(()=>({}));
  if(resp.ok){toast(result.message || '已保存','success'); closeModal(); loadAll();} else {toast(result.detail || '操作失败','error');}
}
async function deleteInstance(id){if(!confirm(`确定删除实例 "${id}" 吗？`)) return; const resp = await fetch(`/panel/admin/instances/${encodeURIComponent(id)}`,{method:'DELETE',headers}); const result = await resp.json().catch(()=>({})); if(resp.ok){toast(result.message || '已删除','success'); loadAll();} else {toast(result.detail || '删除失败','error');}}
async function enterInstance(id){const resp = await fetch(`/panel/admin/switch-instance/${encodeURIComponent(id)}`,{method:'POST',headers}); if(resp.ok){syncWebuiAuthStorage(); toast('已切换到实例: '+id,'success'); await loadCurrent(); setTimeout(()=>{location.href='/webui#/dashboard';},350);} else {const err=await resp.json().catch(()=>({})); toast(err.detail || '切换失败','error');}}

function showCreateNodeModal(){
  editingNodeId=null; document.getElementById('node-modal-title').textContent='添加节点';
  ['n-id','n-name','n-cluster-name','n-panel-url','n-manager-url','n-manager-key','n-comment'].forEach(id=>document.getElementById(id).value='');
  document.getElementById('n-cluster-id').value='default'; document.getElementById('n-role').value='node'; document.getElementById('n-status').value='unknown'; document.getElementById('node-modal').classList.add('active');
}
async function editNode(id){
  const resp = await fetch(`/panel/admin/nodes/${encodeURIComponent(id)}`,{headers}); const data = await resp.json();
  editingNodeId=id; document.getElementById('node-modal-title').textContent='编辑节点: '+id;
  document.getElementById('n-id').value=data.id; document.getElementById('n-name').value=data.name || ''; document.getElementById('n-cluster-id').value=data.cluster_id || 'default'; document.getElementById('n-cluster-name').value=data.cluster_name || '';
  document.getElementById('n-role').value=data.role || 'node'; document.getElementById('n-status').value=data.status || 'unknown'; document.getElementById('n-panel-url').value=data.panel_base_url || ''; document.getElementById('n-manager-url').value=data.manager_base_url || '';
  document.getElementById('n-manager-key').value=''; document.getElementById('n-manager-key').placeholder=data.manager_api_key_set ? '已设置，留空保持原密钥' : '可选'; document.getElementById('n-comment').value=data.comment || ''; document.getElementById('node-modal').classList.add('active');
}
function closeNodeModal(){document.getElementById('node-modal').classList.remove('active');}
async function submitNodeForm(){
  const body={id:document.getElementById('n-id').value.trim(),name:document.getElementById('n-name').value.trim(),cluster_id:document.getElementById('n-cluster-id').value.trim() || 'default',cluster_name:document.getElementById('n-cluster-name').value.trim(),role:document.getElementById('n-role').value,status:document.getElementById('n-status').value,panel_base_url:document.getElementById('n-panel-url').value.trim() || null,manager_base_url:document.getElementById('n-manager-url').value.trim() || null,manager_api_key:document.getElementById('n-manager-key').value.trim(),comment:document.getElementById('n-comment').value.trim()};
  if(!body.id){toast('请填写节点 ID','error');return;}
  const url = editingNodeId ? `/panel/admin/nodes/${encodeURIComponent(editingNodeId)}` : '/panel/admin/nodes'; const method = editingNodeId ? 'PUT' : 'POST';
  const resp = await fetch(url,{method,headers,body:JSON.stringify(body)}); const result = await resp.json().catch(()=>({}));
  if(resp.ok){toast(result.message || '已保存','success'); closeNodeModal(); loadAll();} else {toast(result.detail || '操作失败','error');}
}
async function deleteNode(id){if(!confirm(`确定删除节点 "${id}" 吗？仍有实例引用的节点会被拒绝删除。`)) return; const resp = await fetch(`/panel/admin/nodes/${encodeURIComponent(id)}`,{method:'DELETE',headers}); const result = await resp.json().catch(()=>({})); if(resp.ok){toast(result.message || '已删除','success'); loadAll();} else {toast(result.detail || '删除失败','error');}}
async function probeNode(id){
  toast('正在测试节点连接','success');
  const resp = await fetch(`/panel/admin/nodes/${encodeURIComponent(id)}/probe`,{method:'POST',headers}); const result = await resp.json().catch(()=>({}));
  if(resp.ok){toast(result.message || `状态: ${result.status}`,(result.status === 'online' || result.status === 'reachable') ? 'success' : 'error');} else {toast(result.detail || '测试失败','error');}
}
function toast(msg,type){const el=document.createElement('div'); el.className='toast '+type; el.textContent=msg; document.body.appendChild(el); setTimeout(()=>el.remove(),3400);}
loadAll();
</script>
</body>
</html>"""
