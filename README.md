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
