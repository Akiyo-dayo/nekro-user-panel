"""
Nekro User Panel - 前端适配中间件
处理前端登录流程的适配，确保面板认证与 NA 前端无缝衔接。
"""

from typing import Optional


def get_login_override_script() -> str:
    """
    生成登录页面覆盖脚本。
    NA 前端的登录流程：
    1. 用户在 /#/login 页面输入用户名密码
    2. 前端 POST /api/token (form-urlencoded)
    3. 收到 {access_token, token_type} 后存入 localStorage
    4. 跳转到 /#/dashboard

    我们的适配策略：
    - 拦截 /api/token 请求 → 转发到 /panel/login
    - 返回格式兼容 NA 原生格式
    - 后续所有 /api/* 请求自动带上面板 token（由面板网关验证后代理）
    """
    return """
<script>
(function() {
    'use strict';

    // ============ Token 管理 ============
    const TOKEN_KEY = 'nekro_user_panel_token';

    function syncPanelTokenCookie(token) {
        try {
            if (token) {
                document.cookie = 'panel_token=' + encodeURIComponent(token) + '; path=/; max-age=86400; SameSite=Lax';
            }
        } catch(e) {}
    }

    syncPanelTokenCookie(localStorage.getItem(TOKEN_KEY) || localStorage.getItem('token'));

    // 在 zustand hydrate 之前，预设 auth-storage
    // 这段代码在 NA 前端 JS 加载之前执行
    (function presetAuthStorage() {
        const panelToken = localStorage.getItem(TOKEN_KEY);
        if (panelToken) {
            // userInfo 必须非 null，否则 NA 前端认为未登录直接跳转 login
            const panelUsername = localStorage.getItem('nekro_user_panel_username') || 'user';
            const savedUserInfo = localStorage.getItem('nekro_user_panel_userinfo');
            const userInfo = savedUserInfo ? JSON.parse(savedUserInfo) : {
                username: panelUsername,
                userId: 1,
                perm_level: 2,
                perm_role: 'Admin',
            };
            // 始终用面板用户名覆盖
            userInfo.username = panelUsername;
            const authData = {
                state: { token: panelToken, userInfo: userInfo },
                version: 0,
            };
            localStorage.setItem('auth-storage', JSON.stringify(authData));
        }
    })();

    function getStoredToken() {
        return localStorage.getItem(TOKEN_KEY) || localStorage.getItem('token');
    }

    function setStoredToken(token) {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem('token', token);  // NA 前端使用的 key
        syncPanelTokenCookie(token);

        // 更新 zustand auth-storage（NA 前端的持久化 store）
        try {
            const panelUsername = localStorage.getItem('nekro_user_panel_username') || 'user';
            const authStorage = JSON.parse(localStorage.getItem('auth-storage') || '{}');
            if (!authStorage.state) authStorage.state = {};
            authStorage.state.token = token;
            // 保持 userInfo 不变，如果没有则设置默认值
            if (!authStorage.state.userInfo) {
                authStorage.state.userInfo = {
                    username: panelUsername,
                    userId: 1,
                    perm_level: 2,
                    perm_role: 'Admin',
                };
            } else {
                authStorage.state.userInfo.username = panelUsername;
            }
            localStorage.setItem('auth-storage', JSON.stringify(authStorage));
        } catch(e) {}

        // 异步获取真实的 userInfo 并保存（但用面板用户名覆盖）
        originalFetch('/api/user/me', {
            headers: { 'Authorization': 'Bearer ' + token }
        }).then(r => r.ok ? r.json() : null).then(info => {
            if (info) {
                const panelUsername = localStorage.getItem('nekro_user_panel_username') || 'user';
                info.username = panelUsername;
                localStorage.setItem('nekro_user_panel_userinfo', JSON.stringify(info));
                try {
                    const authStorage = JSON.parse(localStorage.getItem('auth-storage') || '{}');
                    if (!authStorage.state) authStorage.state = {};
                    authStorage.state.userInfo = info;
                    localStorage.setItem('auth-storage', JSON.stringify(authStorage));
                } catch(e) {}
            }
        }).catch(() => {});
    }

    // ============ 拦截 fetch 请求 ============
    const originalFetch = window.fetch;

    window.fetch = async function(input, init) {
        const url = typeof input === 'string' ? input : (input instanceof Request ? input.url : String(input));
        const options = init || {};

        // 1. 拦截登录请求
        if ((url.includes('/api/token') || url.includes('/api/user/login')) && options.method && options.method.toUpperCase() === 'POST') {
            return handleLoginRequest(options);
        }

        // 2. 对所有 /api/* 请求注入面板 token
        if (url.startsWith('/api/') || url.includes('/api/')) {
            const token = getStoredToken();
            if (token) {
                if (!options.headers) {
                    options.headers = {};
                }
                if (options.headers instanceof Headers) {
                    options.headers.set('Authorization', 'Bearer ' + token);
                } else if (typeof options.headers === 'object') {
                    options.headers['Authorization'] = 'Bearer ' + token;
                }
            }
        }

        const resp = await originalFetch.call(this, input, options);

        // 3. 拦截 /api/user/me 和 /api/user/info 响应，替换用户名为面板用户名
        if ((url.includes('/api/user/me') || url.includes('/api/user/info')) && resp.ok) {
            try {
                const panelUsername = localStorage.getItem('nekro_user_panel_username');
                if (panelUsername) {
                    const cloned = resp.clone();
                    const data = await cloned.json();
                    if (data && data.username) {
                        data.username = panelUsername;
                        // 同步更新 auth-storage
                        try {
                            const authStorage = JSON.parse(localStorage.getItem('auth-storage') || '{}');
                            if (authStorage.state && authStorage.state.userInfo) {
                                authStorage.state.userInfo.username = panelUsername;
                                localStorage.setItem('auth-storage', JSON.stringify(authStorage));
                            }
                        } catch(e) {}
                        return new Response(JSON.stringify(data), {
                            status: resp.status,
                            statusText: resp.statusText,
                            headers: resp.headers,
                        });
                    }
                }
            } catch(e) {}
        }

        return resp;
    };

    async function handleLoginRequest(options) {
        let username = '';
        let password = '';

        // 解析请求体
        const body = options.body;
        if (body instanceof URLSearchParams) {
            username = body.get('username') || '';
            password = body.get('password') || '';
        } else if (typeof body === 'string') {
            // 尝试JSON解析
            try {
                const jsonBody = JSON.parse(body);
                username = jsonBody.username || '';
                password = jsonBody.password || '';
            } catch(e) {
                // form-urlencoded
                const params = new URLSearchParams(body);
                username = params.get('username') || '';
                password = params.get('password') || '';
            }
        } else if (body instanceof FormData) {
            username = body.get('username') || '';
            password = body.get('password') || '';
        }

        // 调用面板登录接口
        const resp = await originalFetch('/panel/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        if (resp.ok) {
            const data = await resp.json();
            setStoredToken(data.access_token);

            // 保存面板用户名，用于覆盖 /api/user/me 返回的 NA admin 用户名
            localStorage.setItem('nekro_user_panel_username', username);

            if (data.role === 'admin' && data.redirect) {
                setTimeout(() => { window.location.href = data.redirect; }, 300);
                return new Response(JSON.stringify({
                    access_token: data.access_token,
                    refresh_token: data.access_token,
                    token_type: 'bearer',
                }), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' },
                });
            }

            // 普通用户 → 返回兼容 NA 前端格式的响应
            return new Response(JSON.stringify({
                access_token: data.access_token,
                refresh_token: data.access_token,
                token_type: 'bearer',
            }), {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
            });
        } else {
            // 登录失败
            const errData = await resp.json().catch(() => ({ detail: '登录失败' }));
            return new Response(JSON.stringify(errData), {
                status: resp.status,
                headers: { 'Content-Type': 'application/json' },
            });
        }
    }

    // ============ 拦截 XMLHttpRequest（axios 使用 XHR） ============
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;
    const originalXHRSetHeader = XMLHttpRequest.prototype.setRequestHeader;

    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        this._panelUrl = url;
        this._panelMethod = (method || 'GET').toUpperCase();
        this._panelHeaders = {};
        return originalXHROpen.call(this, method, url, ...args);
    };

    XMLHttpRequest.prototype.setRequestHeader = function(name, value) {
        this._panelHeaders[name] = value;
        // 如果是Authorization header，替换为面板token
        if (name.toLowerCase() === 'authorization') {
            const token = getStoredToken();
            if (token) {
                return originalXHRSetHeader.call(this, name, 'Bearer ' + token);
            }
        }
        return originalXHRSetHeader.call(this, name, value);
    };

    XMLHttpRequest.prototype.send = function(body) {
        const self = this;

        // 拦截登录请求 (POST /api/token 或 POST /api/user/login)
        const isTokenLogin = self._panelMethod === 'POST' && self._panelUrl && self._panelUrl.includes('/api/token');
        const isUserLogin = self._panelMethod === 'POST' && self._panelUrl && self._panelUrl.includes('/api/user/login');

        if (isTokenLogin || isUserLogin) {
            // 解析请求体获取用户名密码
            let username = '';
            let password = '';
            if (typeof body === 'string') {
                // 尝试JSON解析
                try {
                    const jsonBody = JSON.parse(body);
                    username = jsonBody.username || '';
                    password = jsonBody.password || '';
                } catch(e) {
                    // form-urlencoded
                    const params = new URLSearchParams(body);
                    username = params.get('username') || '';
                    password = params.get('password') || '';
                }
            } else if (body instanceof URLSearchParams) {
                username = body.get('username') || '';
                password = body.get('password') || '';
            } else if (body instanceof FormData) {
                username = body.get('username') || '';
                password = body.get('password') || '';
            }

            // 转发到面板登录接口
            originalFetch('/panel/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            }).then(async (resp) => {
                const respText = await resp.text();
                let finalText = respText;
                let isAdmin = false;
                let adminRedirect = '';

                if (resp.ok) {
                    try {
                        const data = JSON.parse(respText);
                        setStoredToken(data.access_token);

                        // 检查是否为管理员登录
                        if (data.role === 'admin' && data.redirect) {
                            isAdmin = true;
                            adminRedirect = data.redirect;
                        }

                        // 确保响应包含 refresh_token（NA前端需要）
                        finalText = JSON.stringify({
                            access_token: data.access_token,
                            refresh_token: data.access_token,
                            token_type: 'bearer',
                        });
                    } catch(e) {}
                }

                // 管理员登录 → 立即跳转，不触发 XHR 回调（避免 NA 前端抢先导航）
                if (isAdmin) {
                    // 设置 cookie 以便管理页面认证
                    document.cookie = 'panel_token=' + encodeURIComponent(localStorage.getItem(TOKEN_KEY)) + '; path=/; max-age=86400';
                    window.location.href = adminRedirect;
                    return; // 不触发任何 XHR 事件
                }

                // 伪造 XHR 响应（普通用户）
                Object.defineProperty(self, 'status', { get: () => resp.status });
                Object.defineProperty(self, 'statusText', { get: () => resp.statusText || 'OK' });
                Object.defineProperty(self, 'responseText', { get: () => finalText });
                Object.defineProperty(self, 'response', { get: () => finalText });
                Object.defineProperty(self, 'readyState', { get: () => 4 });
                Object.defineProperty(self, 'responseURL', { get: () => self._panelUrl });

                // 触发事件
                if (self.onreadystatechange) self.onreadystatechange();
                self.dispatchEvent(new Event('readystatechange'));
                if (self.onload) self.onload();
                self.dispatchEvent(new Event('load'));
                self.dispatchEvent(new Event('loadend'));

                // 普通用户 → 跳转到 dashboard
                if (resp.ok) {
                    setTimeout(() => { window.location.href = '/webui#/dashboard'; window.location.reload(); }, 500);
                }
            }).catch((err) => {
                if (self.onerror) self.onerror(err);
                self.dispatchEvent(new Event('error'));
                self.dispatchEvent(new Event('loadend'));
            });
            return; // 不调用原始 send
        }

        // 对所有 /api/* 请求注入面板 token
        const token = getStoredToken();
        if (token && self._panelUrl && (self._panelUrl.startsWith('/api/') || self._panelUrl.includes('/api/'))) {
            try {
                originalXHRSetHeader.call(self, 'Authorization', 'Bearer ' + token);
            } catch(e) {}
        }
        return originalXHRSend.call(this, body);
    };

    console.log('[Nekro User Panel] 登录适配脚本已加载 (fetch + XHR)');
})();
</script>
"""


def get_full_inject_html() -> str:
    """获取完整的注入 HTML（登录适配 + 导航裁剪）- 用于普通用户"""
    return get_login_override_script() + get_nav_filter_script()


def get_admin_toolbar_script(instance_id: str, instance_comment: str) -> str:
    """获取 admin 管理条脚本 - 显示当前管理的实例和返回按钮"""
    return f"""
<script>
(function() {{
    'use strict';
    const INSTANCE_ID = '{instance_id}';
    const INSTANCE_COMMENT = '{instance_comment}';

    function createToolbar() {{
        const bar = document.createElement('div');
        bar.id = 'admin-toolbar';
        bar.innerHTML = `
            <span style="margin-right:12px;">&#x1F6E0;&#xFE0F; <b>Admin</b> | &#x5B9E;&#x4F8B;: <b>${{INSTANCE_ID}}</b> (${{INSTANCE_COMMENT}})</span>
            <button onclick="location.href='/panel/admin'" style="padding:4px 12px;border:1px solid rgba(255,255,255,0.3);border-radius:4px;background:rgba(255,255,255,0.1);color:#fff;cursor:pointer;font-size:12px;">&#x2190; &#x8FD4;&#x56DE;&#x7BA1;&#x7406;&#x540E;&#x53F0;</button>
        `;
        bar.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:linear-gradient(90deg,#7c83fd,#6c63ff);color:#fff;padding:6px 16px;font-size:13px;display:flex;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,0.3);';
        document.body.prepend(bar);
        // 给 body 加 padding-top 避免遮挡内容
        document.body.style.paddingTop = '36px';
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', createToolbar);
    }} else {{
        createToolbar();
    }}
}})();
</script>
"""


def get_nav_filter_script() -> str:
    """导航过滤脚本"""
    return """
<script>
(function() {
    'use strict';

    // ============ 配置：需要隐藏的导航菜单项 ============
    const HIDDEN_NAV_KEYWORDS = [
        '适配器', 'Adapter', 'adapter',
        '重启', 'Restart', 'restart',
        '空间清理', 'Space Cleanup', 'space-cleanup',
        '定时任务', 'Timer', 'timer',
        '工作区', 'Workspace', 'workspace',
        '命令', 'Command', 'command',
        'Webhook', 'webhook',
        '云端', 'Cloud', 'cloud',
        'Nekro 云', 'Nekro Cloud',
        '主题', 'Theme', 'theme',
        '公告', 'Announcement', 'announcement',
        '个人中心', 'Profile', 'profile', 'Personal Center', 'personal-center',
        '社区账户', 'Community Account', 'community account',
        '插件编辑器', 'Plugin Editor', 'plugin editor',
    ];

    // 频道详情中需要隐藏的 Tab
    const HIDDEN_CHANNEL_TABS = [
        '覆盖配置', 'Override', 'override',
        '覆盖设置',
    ];

    // 设置页面中需要隐藏的项
    const HIDDEN_SETTINGS_ITEMS = [
        '空间清理', 'Space',
        '命令', 'Command',
        '主题', 'Theme',
        '调色盘', 'Palette', 'palette',
        '个人中心', 'Profile',
    ];

    function hideByAccessibleLabel(labelKeywords) {
        const targets = document.querySelectorAll('button, a, [role="button"], [aria-label], [title]');
        targets.forEach(el => {
            const label = [
                el.getAttribute('aria-label') || '',
                el.getAttribute('title') || '',
                (el.textContent || '').trim(),
            ].join(' ');
            for (const keyword of labelKeywords) {
                if (label.includes(keyword)) {
                    el.style.display = 'none';
                    break;
                }
            }
        });
    }

    // ============ 核心隐藏逻辑 ============
    function hideElements() {
        // 1. 隐藏侧边栏导航项
        const allClickable = document.querySelectorAll(
            'a, [role="button"], [role="menuitem"], [role="listitem"], ' +
            '[class*="ListItem"], [class*="MenuItem"], [class*="NavItem"], ' +
            '[class*="MuiListItemButton"], [class*="MuiButtonBase"]'
        );

        allClickable.forEach(el => {
            const text = (el.textContent || '').trim();
            const href = el.getAttribute('href') || '';

            // 检查是否包含需要隐藏的关键字
            for (const keyword of HIDDEN_NAV_KEYWORDS) {
                if (text === keyword || (text.length < 20 && text.includes(keyword))) {
                    // 隐藏该元素及其父级 ListItem
                    let target = el;
                    // 向上查找最近的 ListItem 容器
                    const parent = el.closest('[class*="MuiListItem"], [class*="nav-item"], li');
                    if (parent) target = parent;
                    target.style.display = 'none';
                    break;
                }
            }
        });

        // 1.1 隐藏顶部栏中与用户无关的快捷入口：调色盘/主题、社区账户、GitHub Stars 等
        hideByAccessibleLabel([
            '当前：浅色模式', '当前：暗色模式', '点击切换到暗色模式', '点击切换到浅色模式',
            '调色盘', 'Palette', 'palette', '主题', 'Theme',
            '社区账户', 'Community Account',
            'Stars',
        ]);

        // 2. 隐藏频道详情中的覆盖配置 Tab
        const tabs = document.querySelectorAll('[role="tab"], [class*="MuiTab"]');
        tabs.forEach(tab => {
            const text = (tab.textContent || '').trim();
            for (const keyword of HIDDEN_CHANNEL_TABS) {
                if (text.includes(keyword)) {
                    tab.style.display = 'none';
                    break;
                }
            }
        });

        // 3. 隐藏 MenuGroup 标题（如果其下所有子项都被隐藏了）
        const menuGroups = document.querySelectorAll('[class*="MenuGroup"], [class*="nav-group"]');
        menuGroups.forEach(group => {
            const visibleItems = group.querySelectorAll('[class*="ListItem"]:not([style*="display: none"]), [class*="MuiListItemButton"]:not([style*="display: none"])');
            if (visibleItems.length === 0) {
                group.style.display = 'none';
            }
        });
    }

    // ============ 路由守卫 ============
    const BLOCKED_HASH_ROUTES = [
        '#/plugins/editor',
        '#/plugin-editor',
        '#/adapters',
        '#/settings/theme',
        '#/profile',
        '#/user/profile',
        '#/personal-center',
        '#/settings/palette',
        '#/settings/space-cleanup',
        '#/settings/commands',
        '#/workspace',
        '#/cloud',
        '#/commands',
    ];

    function checkRoute() {
        const hash = window.location.hash;
        for (const blocked of BLOCKED_HASH_ROUTES) {
            if (hash.startsWith(blocked)) {
                window.location.hash = '#/dashboard';
                return;
            }
        }
    }

    // 监听路由变化
    window.addEventListener('hashchange', checkRoute);

    // ============ MutationObserver ============
    const observer = new MutationObserver(() => {
        hideElements();
    });

    function init() {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
        hideElements();
        checkRoute();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // 兜底定时器
    setInterval(hideElements, 2000);

    console.log('[Nekro User Panel] 导航裁剪脚本已加载');
})();
</script>
"""

