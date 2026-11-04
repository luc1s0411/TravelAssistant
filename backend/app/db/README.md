# 数据层

`base.py`、`enums.py` 和 `models.py` 是用户提供的 ORM 定义；`migrations/versions/20261104_0001_initial_schema.py` 是配套的冻结初始迁移。模型导入本身不连接数据库，也不创建表；Alembic 通过 `migrations/env.py` 注册全部模型。会话统一使用 `session.py` 中的 `DBSession`。

用户确认该迁移尚未执行。项目当前没有配置实际数据库连接；在执行迁移前仍需确认目标实例和库名，以及库内是否已有同名表或需要保留的数据。初始迁移的降级会删除业务表及其数据。

离线查看迁移 SQL（不会连接数据库）：在 `backend` 目录运行 `..\.venv\Scripts\python.exe -m alembic upgrade head --sql`。后续结构变化应新增迁移，不应改写已使用的初始迁移。

## 业务接入边界

API 的 Pydantic `schemas.py` 与 ORM 是不同层次；服务层须明确转换并验证，不能把两者当成相同结构。已知差异和待定事项见 `docs/contracts.md`。业务实现仍须保证用户隔离、原子版本检查、幂等、时间与预算校验。
