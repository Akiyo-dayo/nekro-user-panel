# Nekro User Panel

一个轻量级反向代理网关，为多个 [Nekro Agent](https://github.com/KroMiose/nekro-agent) 实例提供受限的用户端管理面板。每个用户绑定一个 NA 实例，登录后所有请求自动路由到对应实例。

## 功能特性

### 多实例管理
- 支持同时管理数十个 NA 实例，每个用户绑定独立实例
- 管理员可自由切换查看/管理任意实例
- 实例配置热重载，无需重启服务

### 权限隔离
| 功能 | 普通用户 | 管理员 |
|------|---------|--------|
| 仪表盘 | ✅ 仅自己实例 | ✅ 任意实例 |
| 频道管理 | ✅ | ✅ |
| 用户管理 | ✅ | ✅ |
| 人设管理 | ✅ | ✅ |
| 系统日志 | ✅ 只读 | ✅ |
| 沙盒日志 | ✅ 只读 | ✅ |
| 基本配置 | ✅ 仅模型相关项 | ✅ 全部 |
| 模型管理 | ✅ 仅自己的模型组 | ✅ 全部 |
| 插件管理 | ❌ | ✅ |
| 适配器 | ❌ | ✅ |
| 工作区 | ❌ | ✅ |

### 安全特性
- **模型组隔离**：用户只能看到和操作自己的模型组，管理员的 API Key 完全不可见
- **API Key 脱敏**：模型组响应中的密钥字段自动清空
- **配置项过滤**：基本配置仅暴露模型选择相关字段，系统级敏感配置不可见
- **路由白名单**：未授权的 API 路径一律返回 403
- **前端导航裁剪**：通过 JS 注入隐藏用户无权访问的菜单项

## 架构

```
┌─────────────────────────────────────────────────────┐
│                   用户浏览器                          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Nekro User Panel (FastAPI)              │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌───────┐  │
│  │  Auth   │ │  Proxy   │ │  Filters  │ │ Admin │  │
│  │  (JWT)  │ │ (httpx)  │ │(响应过滤) │ │ Page  │  │
│  └─────────┘ └──────────┘ └───────────┘ └───────┘  │
│  ┌──────────────┐ ┌────────────────────────────┐    │
│  │Route Whitelist│ │  Frontend Inject (JS注入)  │    │
│  └──────────────┘ └────────────────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐┌──────────────┐┌──────────────┐
│ NA Instance 1││ NA Instance 2││ NA Instance N│
│  (port 8021) ││  (port 8022) ││  (port 80xx) │
└──────────────┘└──────────────┘└──────────────┘
```

## 文件结构

```
nekro-user-panel/
├── main.py              # FastAPI 应用入口 + WebUI 注入 + 管理员 API
├── auth.py              # 面板独立认证（JWT）+ NA 后端 token 缓存
├── config.py            # 配置管理（实例加载、环境变量）
├── proxy.py             # 反向代理核心（httpx 异步 + 权限检查）
├── filters.py           # 响应数据过滤器（模型组隔离 + 配置脱敏）
├── route_whitelist.py   # API 路由白名单（正则匹配）
├── frontend_inject.py   # 前端 JS 注入（登录适配 + 导航裁剪 + Admin 工具条）
├── admin_page.py        # 管理员后台页面（HTML）
├── instances.json       # 实例配置文件（不入库，含密码）
├── requirements.txt     # Python 依赖
├── Dockerfile           # Docker 构建文件
├── docker-compose.yml   # Docker Compose 编排
├── .env.example         # 环境变量模板
└── README.md            # 本文件
```

## 快速开始

### 环境要求
- Python 3.10+
- 一个或多个运行中的 Nekro Agent 实例

### 安装

```bash
git clone https://github.com/Akiyo-dayo/nekro-user-panel.git
cd nekro-user-panel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 创建实例配置文件 `instances.json`：
```json
[
  {
    "id": "user1",
    "panel_password": "user1_password",
    "na_port": 8021,
    "na_admin_user": "admin",
    "na_admin_pass": "na_admin_password",
    "na_host": "127.0.0.1",
    "allowed_model_groups": [],
    "comment": "用户1的实例"
  }
]
```

字段说明：
| 字段 | 说明 |
|------|------|
| `id` | 用户登录名（唯一标识） |
| `panel_password` | 用户面板登录密码 |
| `na_port` | NA 实例端口 |
| `na_admin_user` | NA 管理员用户名 |
| `na_admin_pass` | NA 管理员密码 |
| `na_host` | NA 实例主机地址 |
| `allowed_model_groups` | 允许用户管理的模型组名列表（空=自动推断） |
| `comment` | 备注 |

3. 配置环境变量（`.env`）：
```env
# 面板 JWT 密钥（务必修改）
PANEL_JWT_SECRET=your-secret-key-change-me

# 管理员账号
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password

# 服务端口
PANEL_PORT=9054
```

### 启动

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 9054
```

### Docker 部署

```bash
docker-compose up -d
```

## 模型组隔离

### 工作原理

1. 用户请求 `GET /api/config/model-groups` 时，响应会被过滤：
   - 隐藏内置管理员分组（`default`、`default-draw`、`default-draw-chat`、`text-embedding`、`CLI`）
   - 只展示用户专属的模型组
   - API Key 等敏感字段自动清空

2. 用户尝试 `POST/DELETE /api/config/model-groups/{name}` 时：
   - 如果目标分组不在允许列表中，返回 403

3. 管理员完全不受限制，可以看到和操作所有模型组

### 使用建议

在 NA 后台为每个用户创建专用的模型组（如 `用户自费`），让用户在里面填写自己的 API Key。你自己的模型组（如 `default`、`CLI` 等）对用户完全不可见。

### 自定义隐藏分组

如需修改默认隐藏的分组列表，编辑 `filters.py` 中的 `PRIVATE_GROUP_NAMES`：

```python
PRIVATE_GROUP_NAMES = {
    "default",
    "default-draw",
    "default-draw-chat",
    "text-embedding",
    "CLI",
}
```

### 显式指定允许的分组

在 `instances.json` 中为用户配置 `allowed_model_groups`：

```json
{
  "id": "user1",
  "allowed_model_groups": ["user1_openai", "user1_claude"]
}
```

留空时系统自动推断（隐藏内置分组，展示其余所有）。

## 管理员功能

- 访问 `/panel/admin` 进入管理后台
- 可查看所有实例列表、切换管理目标实例
- 切换实例后，WebUI 中的所有操作都路由到选中的实例
- 管理员拥有完整权限，不受白名单和过滤器限制
- Admin 工具条显示当前管理的实例名称

## 请求流程

```
用户请求 → Panel JWT 认证 → 确定目标实例 → 路由白名单检查
    → 模型组权限检查 → 系统配置权限检查 → 获取 NA Token
    → 转发到 NA 后端 → 响应过滤 → 返回给用户
```

## API 端点

### 面板自有接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/panel/login` | 面板登录 |
| GET | `/panel/user-info` | 获取当前用户信息 |
| GET | `/panel/nav-config` | 获取导航配置 |
| POST | `/panel/reload-instances` | 热重载实例配置（管理员） |

### 管理员接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/panel/admin` | 管理后台页面 |
| GET | `/panel/admin/instances` | 实例列表 |
| POST | `/panel/admin/switch-instance/{id}` | 切换管理实例 |
| GET | `/panel/admin/current-instance` | 当前管理实例 |

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 基本配置打不开 | NA 2.3.x 使用 `system` 作为配置键，面板已自动兼容 `basic_config` → `system` 映射 |
| 模型组为空 | 检查 NA 后台是否为用户创建了专属模型组（非内置分组） |
| 管理员看不到全部内容 | 硬刷新浏览器（Ctrl+Shift+R）清除旧注入脚本缓存 |
| 用户能看到管理员 API Key | 检查 `filters.py` 中 `PRIVATE_GROUP_NAMES` 是否包含你的分组名 |

## License

MIT

## 登录页与实例路由策略

### 未登录访问

访问 `/webui` 时，如果请求没有有效的 `panel_token`，面板会直接返回内置登录页。

此阶段不会读取 `instances.json` 的第一个实例，也不会请求任何 Nekro Agent 后端的 `/api/token`。这样可以避免某个默认实例离线时，导致所有用户都打不开登录页。

### 普通用户登录后

普通用户登录成功后，JWT 中会写入绑定的 `instance_id`。后续 `/webui` 和 `/api/*` 请求只会路由到该用户绑定的实例。

如果绑定实例不可用，面板会返回可读的 `502` 错误页，而不是抛出 `Internal Server Error`。

### 管理员登录后

管理员登录后不会自动回退到实例列表第一项。管理员需要在 `/panel/admin` 中显式选择一个实例，面板才会把 `/webui` 请求路由到对应 Nekro Agent。

这能避免第一个实例离线时影响管理员进入面板，也能避免误操作到非预期实例。

### 设计说明

登录页采用产品型管理后台设计：

- 暗色低噪声界面，减少装饰性元素
- 明确说明“未登录不连接默认实例”
- 表单具备 hover、focus、loading、error 状态
- 移动端自动降为单列布局
- 遵守 `prefers-reduced-motion`，不使用无意义入场动画

### 排障建议

如果浏览器仍看到旧的 `Internal Server Error`，通常是旧 cookie 或 localStorage 里残留了过期 token。可以清理当前站点数据后重新访问 `/webui`。

如果登录后出现“实例暂时不可用”，说明账号绑定的 Nekro Agent 后端端口不可达，只影响该账号绑定的实例，不影响其他用户登录。


## 退出登录行为

面板提供 `POST /panel/logout` 用于清理认证状态。该接口会删除：

- `panel_token`：面板 JWT Cookie
- `admin_instance`：管理员当前选择的实例

前端注入脚本会同步清理浏览器本地状态：

- `nekro_user_panel_token`
- `token`
- `panel_token`
- `auth-storage`
- `nekro_user_panel_username`
- `nekro_user_panel_userinfo`

因此用户在 NA WebUI 点击“退出登录”后，不会因为 localStorage 或 Cookie 中残留 token 而继续保持登录态。管理员后台也提供独立的“退出登录”按钮。

## 管理员后台设计

管理员后台采用产品型控制台布局：

- 左侧固定操作区，包含返回 WebUI 和退出登录
- 右侧实例列表与概览指标
- 管理员必须显式选择实例后才能进入对应 WebUI
- 移动端自动切换为单列布局
- 所有管理请求均携带面板 token，401/403 时会清理本地认证状态并返回登录页

## 实例不可用错误页

当用户或管理员已经登录，但绑定的 Nekro Agent 后端无法连接时，面板会返回统一设计的 `502` 错误页，而不是裸 HTML 或 FastAPI 默认错误。

错误页会展示：

- HTTP 状态码
- 明确的实例不可用说明
- 当前实例 ID 与后端地址
- 返回登录页 / 管理后台的操作按钮
- “只影响当前实例，不影响其他用户”的提示

这能让实例级故障和面板级故障区分开，方便用户判断是否需要联系管理员。

### 错误页操作按钮

普通用户看到实例不可用、无绑定实例等错误时，错误页只提供返回面板入口 / 重试操作，不显示“打开管理后台”。

如果非管理员直接访问 `/panel/admin`，面板会返回同款 `403` HTML 错误页，提示“仅管理员可操作”，而不是默认 JSON 或裸错误文本。

### 返回登录页按钮

实例不可用错误页提供“返回登录页”按钮。该按钮不是普通跳转，会先调用 `/panel/logout`，并清理浏览器中的面板 token、NA token、`auth-storage` 和管理员实例选择 Cookie，然后再回到 `/webui`。

错误页同时保留“重新尝试”作为次级操作，用于实例恢复后直接重试当前路由。

### 管理后台列表布局与搜索

管理员后台的实例列表支持客户端搜索，搜索范围包括实例 ID、备注、主机、端口和 NA 管理员用户名。

布局策略：

- 桌面端使用两列或多列卡片网格，减少纵向滚动
- 顶部标题和主要操作区使用 sticky 布局，刷新 / 添加实例按钮始终靠近视口顶部
- 移动端将侧栏压缩为顶部工具条，避免“打开当前 WebUI / 退出登录”按钮被推到页面底部
- 搜索栏显示当前匹配数，支持一键清空

### 错误页文案规范

错误页避免使用调试式描述。面向用户的状态文案应简短、明确，并避免暴露实现细节：

- 使用“当前实例暂不可达”说明实例状态
- 使用“当前账号绑定的 Nekro Agent 实例暂时无法访问”说明故障范围
- 使用“请联系管理员检查实例状态或后端端口”作为处理建议

### 登录页文案规范

登录页面向普通用户，避免展示实现细节或调试语气。文案应聚焦访问控制台本身：

- 标题使用“Nekro 控制台入口”
- 描述使用“统一访问你的 Nekro Agent 控制台”
- 技术实现细节，如默认实例、`/api/token`、fallback 策略，只保留在 README，不直接暴露给终端用户

### 管理员进入实例的登录态同步

管理员在 `/panel/admin` 点击“进入管理”时，面板会先写入 `admin_instance` Cookie，并同步 WebUI 所需的浏览器登录态：

- `nekro_user_panel_token`
- `panel_token`
- `token`
- `auth-storage`
- `nekro_user_panel_username`

这样进入 `/webui#/dashboard` 后，NA 前端不会因为缺少本地 token 而跳回登录页。
