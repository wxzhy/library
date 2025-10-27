# 图书馆管理系统（FastAPI + Vue3）

这是一个基于 FastAPI（后端）和 Vue3 + Vite（前端）的图书馆管理系统示例工程，包含用户认证、图书管理、借阅记录等基本功能。后端代码位于 `app/`，前端位于 `web/`，数据库初始化脚本在项目根目录的 `init.sql`。

## 目录结构（重要部分）

- `app/` — FastAPI 后端，包含路由、数据库连接与依赖（见 `app/main.py`、`app/database.py`、`app/routers/`）
- `web/` — Vue3 前端（基于 Vite + TypeScript + ElementPlus）
- `init.sql` — MySQL 数据库初始化脚本（建表与示例数据）
- `add_data.py` / `test.py` — 用于抓取或插入示例数据的脚本（示例，仅供参考）

## 技术栈

- 后端：Python + FastAPI + aiomysql + Uvicorn
- 前端：Vue 3 + Vite + TypeScript + Element Plus
- 数据库：MySQL / MariaDB

## 先决条件

- Python 版本：>= 3.13（请参考 `app/pyproject.toml` 中的 `requires-python`）
- Node.js：>= 18.20.0
- pnpm：>= 8.7.0（前端使用 pnpm 管理）
- MySQL / MariaDB 服务已安装并可访问

注意：仓库中部分示例脚本（如 `app/database.py`、`add_data.py`、`test.py`）包含明文示例密码，请勿在生产环境中直接使用；建议改为使用环境变量或安全的配置管理方案。

## 快速开始（本地开发）

下面的步骤假设你在 Windows（PowerShell / pwsh）环境下进行开发。将命令在对应目录下执行。

1) 初始化数据库（MySQL）

  - 启动 MySQL 服务后，在终端运行：

```powershell
# 使用 root 登录并执行初始化脚本（根据提示输入密码）
mysql -u root -p < init.sql
```

  - 或者使用 MySQL 客户端 / Workbench 手动执行 `init.sql`。

2) 后端（FastAPI）

  - 创建并激活虚拟环境：

```powershell
# 在项目根或 app 目录创建 venv（示例在项目根）
python -m venv .venv
# PowerShell 激活
.\.venv\Scripts\Activate.ps1
# 升级 pip
python -m pip install --upgrade pip
```

  - 安装后端依赖（两种方式，任选其一）：

```powershell
# 方式 A：使用 pip 安装 pyproject.toml 中声明的依赖（显式列出依赖以兼容不同 pip 版本）
python -m pip install aiomysql cryptography "fastapi[standard]" passlib "pydantic[email]" pyjwt python-multipart uvicorn

# 方式 B（如果你使用 Poetry）：
# cd app
# poetry install
```

  - 配置数据库连接：

    - 当前示例代码在 `app/database.py` 中有 `DB_CONFIG` 字典（包含 host/port/user/password/db），你可以直接编辑该文件以指向你的数据库，或将其改造为从环境变量读取（推荐）。

  - 启动后端开发服务器：

```powershell
# 在项目根或任意位置（确保虚拟环境已激活）
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

  - 打开接口文档：

    - Swagger UI: http://127.0.0.1:8000/docs
    - ReDoc: http://127.0.0.1:8000/redoc

3) 前端（Vue3 + Vite）

  - 进入前端目录并安装依赖：

```powershell
cd web
pnpm install
```

  - 配置前端 API 基础地址：

    - 前端使用 Vite 的环境变量 `VITE_SERVICE_BASE_URL` 指定后端 base URL。可在 `web/` 下创建一个 `.env` 或 `.env.test` 文件，例如：

```text
VITE_SERVICE_BASE_URL="http://127.0.0.1:8000"
VITE_BASE_URL=/
VITE_APP_TITLE="图书馆管理系统"
```

  - 启动开发服务器：

```powershell
pnpm run dev
# 或 简写：pnpm dev
```

  - 打开浏览器访问前端（默认 Vite 端口通常是 5173）：

    - http://localhost:5173

4) 可选：插入示例数据

  - 你可以运行仓库根目录下的 `add_data.py` 或 `test.py` 来做示例数据插入。在运行前，请务必检查并更新脚本中的数据库配置（或改为复用 `app/database.py` 的配置）：

```powershell
# 示例：在虚拟环境中
python add_data.py
# 或
python test.py
```

## 生产构建

1) 前端构建并预览：

```powershell
cd web
pnpm run build
pnpm run preview
```

2) 后端部署：

- 推荐使用生产级 ASGI 服务器（例如 uvicorn 或 gunicorn + uvicorn workers）。示例（直接用 uvicorn）：

```powershell
# 在生产上通常使用--workers 并配合进程管理器（如 systemd 或 supervisor）
uvicorn app.main:app --port 8000 --workers 4
```
 - Windows上可使用 winloop 提升性能
```powershell
uvicorn app.main:app --port 8000 --workers 4 --http httptools --ws websockets-sansio --loop winloop:new_event_loop
```
 - Linux上使用uvloop
```bash
uvicorn app.main:app --port 8000 --workers 4 --http httptools --ws websockets-sansio --loop uvloop
```

## 配置与注意事项

- 数据库密码与敏感配置：当前仓库示例把数据库连接写在 `app/database.py` 中（明文），这只是演示，请改为使用环境变量或安全配置管理。示例（用 os.environ）：

```python
import os
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "db": os.getenv("DB_NAME", "library_management"),
}
```

- 如果你修改了配置文件或依赖，请确保重启后端服务以使更改生效。

## 常见问题（快速排查）

- 后端启动报错找不到依赖：确认已在虚拟环境中安装依赖并激活虚拟环境。
- 前端无法请求后端：确认 `VITE_SERVICE_BASE_URL` 指向后端地址且跨域（CORS）已允许（后端示例允许所有来源）。
- 数据库连接失败：确认 MySQL 服务已启动、`init.sql` 已执行并且 `DB_CONFIG` 正确。
