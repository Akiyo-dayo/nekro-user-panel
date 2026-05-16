"""
Nekro User Panel - 管理员页面
提供一个简洁的 WebUI 用于管理 instances.json 配置。
"""


def get_admin_html() -> str:
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nekro User Panel - 管理后台</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 24px; }
h1 { margin-bottom: 24px; color: #7c83fd; font-size: 1.5rem; }
.card { background: #16213e; border-radius: 12px; padding: 20px; margin-bottom: 16px; border: 1px solid #0f3460; }
.card:hover { border-color: #7c83fd; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-header h3 { color: #7c83fd; font-size: 1.1rem; }
.card-body { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.9rem; }
.card-body .field { color: #aaa; }
.card-body .value { color: #eee; word-break: break-all; }
.btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s; }
.btn-primary { background: #7c83fd; color: #fff; }
.btn-primary:hover { background: #6c73ed; }
.btn-danger { background: #e94560; color: #fff; }
.btn-danger:hover { background: #d93550; }
.btn-sm { padding: 5px 12px; font-size: 0.8rem; }
.btn-success { background: #27ae60; color: #fff; }
.btn-success:hover { background: #219a52; }
.actions { display: flex; gap: 8px; }
.modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); z-index: 100; justify-content: center; align-items: center; }
.modal-overlay.active { display: flex; }
.modal { background: #16213e; border-radius: 12px; padding: 24px; width: 90%; max-width: 500px; border: 1px solid #0f3460; }
.modal h2 { margin-bottom: 16px; color: #7c83fd; font-size: 1.2rem; }
.form-group { margin-bottom: 12px; }
.form-group label { display: block; margin-bottom: 4px; color: #aaa; font-size: 0.85rem; }
.form-group input { width: 100%; padding: 8px 12px; border: 1px solid #0f3460; border-radius: 6px; background: #1a1a2e; color: #eee; font-size: 0.9rem; }
.form-group input:focus { outline: none; border-color: #7c83fd; }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }
.btn-cancel { background: #333; color: #aaa; }
.empty { text-align: center; padding: 40px; color: #666; }
.toast { position: fixed; top: 20px; right: 20px; padding: 12px 20px; border-radius: 8px; color: #fff; font-size: 0.9rem; z-index: 200; animation: fadeIn 0.3s; }
.toast.success { background: #27ae60; }
.toast.error { background: #e94560; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>
</head>
<body>
<div class="container">
    <h1>🛠️ Nekro User Panel 管理后台</h1>
    <div style="margin-bottom: 16px;">
        <button class="btn btn-primary" onclick="showCreateModal()">+ 添加实例</button>
        <button class="btn btn-cancel" onclick="location.href='/webui'" style="margin-left:8px;">← 返回面板</button>
    </div>
    <div id="instances-list"></div>
</div>

<!-- 编辑/创建弹窗 -->
<div class="modal-overlay" id="modal">
    <div class="modal">
        <h2 id="modal-title">添加实例</h2>
        <div class="form-group"><label>用户ID (登录名)</label><input id="f-id" placeholder="如: user1"></div>
        <div class="form-group"><label>面板登录密码</label><input id="f-password" type="text" placeholder="用户登录面板的密码"></div>
        <div class="form-group"><label>NA 实例端口</label><input id="f-port" type="number" placeholder="如: 8021"></div>
        <div class="form-group"><label>NA 管理员用户名</label><input id="f-admin-user" value="admin"></div>
        <div class="form-group"><label>NA 管理员密码</label><input id="f-admin-pass" type="text" placeholder="NA后台的admin密码"></div>
        <div class="form-group"><label>NA 主机地址</label><input id="f-host" value="127.0.0.1"></div>
        <div class="form-group"><label>备注</label><input id="f-comment" placeholder="可选"></div>
        <div class="form-actions">
            <button class="btn btn-cancel" onclick="closeModal()">取消</button>
            <button class="btn btn-primary" id="modal-submit" onclick="submitForm()">保存</button>
        </div>
    </div>
</div>

<script>
const TOKEN = document.cookie.split(';').map(c=>c.trim()).find(c=>c.startsWith('panel_token='))?.split('=')[1]
    || localStorage.getItem('nekro_user_panel_token');
const headers = {'Content-Type':'application/json'};
if(TOKEN) headers['Authorization'] = 'Bearer ' + TOKEN;

let editingId = null;

async function loadInstances() {
    const resp = await fetch('/panel/admin/instances', {headers});
    if(resp.status === 403) { location.href='/webui'; return; }
    const data = await resp.json();
    const el = document.getElementById('instances-list');
    if(!data.length) { el.innerHTML='<div class="empty">暂无实例，点击上方按钮添加</div>'; return; }
    el.innerHTML = data.map(i => `
        <div class="card">
            <div class="card-header">
                <h3>${i.id}</h3>
                <div class="actions">
                    <button class="btn btn-success btn-sm" onclick="enterInstance('${i.id}')">进入管理</button>
                    <button class="btn btn-primary btn-sm" onclick="editInstance('${i.id}')">编辑</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteInstance('${i.id}')">删除</button>
                </div>
            </div>
            <div class="card-body">
                <span class="field">端口:</span><span class="value">${i.na_host}:${i.na_port}</span>
                <span class="field">管理员:</span><span class="value">${i.na_admin_user}</span>
                <span class="field">备注:</span><span class="value">${i.comment || '-'}</span>
            </div>
        </div>
    `).join('');
}

function showCreateModal() {
    editingId = null;
    document.getElementById('modal-title').textContent = '添加实例';
    document.getElementById('f-id').value = '';
    document.getElementById('f-id').disabled = false;
    document.getElementById('f-password').value = '';
    document.getElementById('f-port').value = '';
    document.getElementById('f-admin-user').value = 'admin';
    document.getElementById('f-admin-pass').value = '';
    document.getElementById('f-host').value = '127.0.0.1';
    document.getElementById('f-comment').value = '';
    document.getElementById('modal').classList.add('active');
}

async function editInstance(id) {
    const resp = await fetch(`/panel/admin/instances/${id}`, {headers});
    const data = await resp.json();
    editingId = id;
    document.getElementById('modal-title').textContent = '编辑实例: ' + id;
    document.getElementById('f-id').value = data.id;
    document.getElementById('f-id').disabled = true;
    document.getElementById('f-password').value = data.panel_password;
    document.getElementById('f-port').value = data.na_port;
    document.getElementById('f-admin-user').value = data.na_admin_user;
    document.getElementById('f-admin-pass').value = data.na_admin_pass;
    document.getElementById('f-host').value = data.na_host;
    document.getElementById('f-comment').value = data.comment || '';
    document.getElementById('modal').classList.add('active');
}

function closeModal() { document.getElementById('modal').classList.remove('active'); }

async function submitForm() {
    const body = {
        id: document.getElementById('f-id').value.trim(),
        panel_password: document.getElementById('f-password').value,
        na_port: parseInt(document.getElementById('f-port').value),
        na_admin_user: document.getElementById('f-admin-user').value.trim(),
        na_admin_pass: document.getElementById('f-admin-pass').value,
        na_host: document.getElementById('f-host').value.trim(),
        comment: document.getElementById('f-comment').value.trim(),
    };
    if(!body.id || !body.panel_password || !body.na_port || !body.na_admin_pass) {
        toast('请填写所有必填字段', 'error'); return;
    }
    let resp;
    if(editingId) {
        resp = await fetch(`/panel/admin/instances/${editingId}`, {method:'PUT', headers, body:JSON.stringify(body)});
    } else {
        resp = await fetch('/panel/admin/instances', {method:'POST', headers, body:JSON.stringify(body)});
    }
    const result = await resp.json();
    if(resp.ok) { toast(result.message, 'success'); closeModal(); loadInstances(); }
    else { toast(result.detail || '操作失败', 'error'); }
}

async function deleteInstance(id) {
    if(!confirm(`确定删除实例 "${id}" 吗？`)) return;
    const resp = await fetch(`/panel/admin/instances/${id}`, {method:'DELETE', headers});
    const result = await resp.json();
    if(resp.ok) { toast(result.message, 'success'); loadInstances(); }
    else { toast(result.detail || '删除失败', 'error'); }
}

function toast(msg, type) {
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

async function enterInstance(id) {
    const resp = await fetch(`/panel/admin/switch-instance/${id}`, {method:'POST', headers});
    if(resp.ok) {
        toast('已切换到实例: ' + id, 'success');
        setTimeout(() => { window.location.href = '/webui#/dashboard'; }, 500);
    } else {
        const err = await resp.json();
        toast(err.detail || '切换失败', 'error');
    }
}

loadInstances();
</script>
</body>
</html>"""
