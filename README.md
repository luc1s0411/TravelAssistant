# 旅行助手 H5 · 代码框架

依据 [原始 README](docs/reference/README.md) 和 [需求说明书](docs/reference/需求说明书.md) 搭建。

**当前项目是工程骨架：目录、API 类型、接口占位、页面路由和配置已提供，用户提供的 ORM 与初始迁移已接入。默认数据库为 MySQL 8.4；尚未在数据库中执行迁移或创建业务表。**

## 已提供与待实现

| 范围 | 当前状态 |
| --- | --- |
| Vue 3 / TypeScript / Vite / Pinia / Element Plus | 脚手架、路由、模块占位页、请求封装、共享状态已提供 |
| FastAPI / Pydantic | 应用入口、21 个业务操作、请求响应类型、统一错误已提供 |
| 健康检查 | `/health` 检查存活；`/health/db` 单独验证 MySQL 连接，不验证表结构 |
| MySQL / SQLAlchemy / Alembic | 连接、事务依赖、13 张业务表的 ORM 和初始迁移已提供；尚未验证真实数据库或执行迁移 |
| 认证、选择保存、规划、查询修改 | 尚未实现，接口占位；没有登录成功或保存成功的假结果 |
| 高德、和风、模型 | 独立适配类与配置占位；没有调用真实服务 |
| 前后端共享类型 | 后端导出 OpenAPI，前端从快照生成 TypeScript 类型 |

页面可打开浏览模块，但当前不能完成旅行规划业务流程。配置中的 demo/real 仅是预留选项，不表示对应适配器已实现。原始文档是产品目标，不等于本轮已实现范围。

## 目录与分工

```text
frontend/src/
  api/                # A：请求封装、OpenAPI 生成类型、分组 API
  stores/             # A：身份与当前草稿状态
  router/             # A：助手、登录、分类窗口、确认、计划路由
  views/              # A：模块占位页面
  components/         # A：占位提示、时间线和地图接入点
backend/app/
  core/               # 公共配置、错误、身份依赖、分页与响应
  db/                 # MySQL 连接、事务与用户提供的业务 ORM
  auth/               # B：登录接口和 DTO
  drafts/             # B：草稿、预算、选择接口和服务入口
  catalog/            # B：候选、价格、来源和坐标类型
  integrations/       # B：高德、和风；C：模型适配
  planner/            # C：确认、生成、查询、修改和版本 DTO
backend/migrations/   # Alembic 配置和用户提供的初始迁移
backend/tests/        # 骨架冒烟与契约校验
docs/
  contracts.md        # 公共约定、样例及未冻结事项
  openapi.json        # 自动生成的 API 快照
  fixtures/           # 人工输入样例，不是供应商数据
  reference/          # 两份原始文档（保留原文）
  acceptance/         # 本轮检查结果及后续验收边界
scripts/
  export_openapi.py    # 无需数据库即可导出契约
```

`schemas.py` 中是 API 请求/响应 DTO，不是数据库 ORM。业务服务需要处理两者间的转换和尚待协调的表达差异，详见 [公共接口契约](docs/contracts.md)。

## 环境

- Python 3.12；`.python-version` 已固定版本系列。
- Node.js 24.22.1；`.node-version` 已记录。常规 Node 安装应同时提供 npm。
- MySQL 8.4，可连接已有实例，或使用可选的 Docker Compose。
- 后端 `requirements.in` 记录直接依赖，`requirements.lock` 固定当前完整解析结果，`requirements.txt` 引用锁文件。
- 前端准确版本在 `package.json` 和 `package-lock.json` 中固定。使用 `npm ci` 安装。

## 配置与启动（PowerShell）

在仓库根目录执行。只在目标不存在时复制配置，避免覆盖已有凭据：

```powershell
if (!(Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
if (!(Test-Path -LiteralPath 'frontend/.env')) { Copy-Item -LiteralPath 'frontend/.env.example' -Destination 'frontend/.env' }
```

编辑根目录 `.env` 中的 `DATABASE_URL`，默认格式：

```text
mysql+pymysql://用户名:密码@127.0.0.1:3306/travel_assistant?charset=utf8mb4
```

密码中的 `@`、`#`、`%` 等 URL 特殊字符需要 URL 编码。示例密码仅用于本地配置；使用已有数据库时填写你自己的连接信息。后端从仓库根目录读取 `.env`，与启动工作目录无关。

可选：没有现成 MySQL 且已安装 Docker 时启动本地数据库：

```powershell
docker compose up -d mysql
```

Compose 从 `.env` 读取 MYSQL_* 变量，`DATABASE_URL` 要与它们对应。已有实例时无需执行这一步。

后端：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe backend/main.py
```

也可以在 PyCharm 等 IDE 中选择项目的 `.venv` 解释器，右键运行 `backend/main.py`。这个入口适合直接运行和调试；需要代码修改后自动重载时，可以改用：

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

另开终端，从仓库根目录启动前端：

```powershell
Set-Location frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

访问：

- 前端：[http://127.0.0.1:5173](http://127.0.0.1:5173)
- 交互 API 文档：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 进程存活：[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- 数据库连接：[http://127.0.0.1:8000/health/db](http://127.0.0.1:8000/health/db)

前端默认用 Vite 将 `/api` 代理到本机 8000 端口。修改后端端口时同步调整 `frontend/vite.config.ts`。页面占位不自动请求业务 API，因此可以单独浏览前端。后端可在 MySQL 未启动时打开 `/health` 和 `/docs`，数据库检查会明确返回 503。

## ORM 与迁移

用户提供的 ORM、Base、枚举和初始迁移 `20261104_0001` 已接入，业务模块应使用 `app.db.session.DBSession`。应用启动时不调用 `create_all()`。用户确认初始迁移尚未执行；本次也没有连接或修改数据库。

在 `backend` 目录可执行 `..\.venv\Scripts\python.exe -m alembic upgrade head --sql` 离线检查 SQL。实际执行迁移前，需配置并确认目标 MySQL 实例、数据库及其现有数据；不要重新生成一套初始迁移。详见 [数据层说明](backend/app/db/README.md)。

## 接口行为与开发顺序

业务路径使用 `/api/v1`。未登录返回 401；认证、业务接口尚未实现的部分返回 501 `NOT_IMPLEMENTED`；字段错误返回 422。前端禁用发送等业务按钮，并明确标为待实现。

建议按下面顺序接入：

1. 先协调 [契约中的 ORM 差异](docs/contracts.md)，B 实现认证、草稿和选择持久化，完成用户隔离与事务。
2. B 完成候选来源与真实/演示标记；A 接入窗口、草稿状态及确认表单。
3. C 实现确认快照、生成、金额与时间校验、幂等和版本，再接模型。
4. A 接入计划页面、地图与时间线，按原需求执行真实流程验收。

当前 revision/version 和幂等键只是请求契约，尚未实现并发控制或持久化去重；超时、并发和重试配置也需要在适配器/规划服务中落实。

## 检查与类型更新

在仓库根目录：

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/export_openapi.py
```

在 `frontend` 目录：

```powershell
npm run api:types
npm run typecheck
npm run build
```

共享 DTO 修改后，提交 OpenAPI 快照、生成的 TS 类型和依赖调用方变更。日期的输入/输出 schema 可能被 Pydantic 分成两类，前端别名通过 `DraftCreate['trip']` 引用输入类型。

原骨架验证范围见 [检查记录](docs/acceptance/scaffold.md)。正式业务、真实服务、MySQL 实例连接和实际执行 ORM 迁移仍未完成。

## 配置与资料边界

`.env`、私钥、本地数据库、`.venv`、`node_modules` 已在 `.gitignore` 中排除。`VITE_` 变量会进入浏览器，不能放服务端 Key 或数据库密码。本轮没有创建或推送 Git 仓库。

框架组织参考 [FastAPI 官方数据库文档](https://fastapi.tiangolo.com/tutorial/sql-databases/)、[SQLAlchemy 版本控制说明](https://docs.sqlalchemy.org/en/20/orm/versioning.html) 和 [Vite 入门文档](https://vite.dev/guide/)。实际业务仍以本仓库契约和你后续接入的实现为准。
