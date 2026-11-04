"""C 的规划服务入口。生成和修改实现前必须完成：

1. 复核用户归属、确认快照和草稿 revision；
2. 幂等键与请求摘要检查；
3. 模型输出经过 Pydantic、时间、预算和必选条件验证；
4. 成功时原子保存 Plan 与 PlanVersion，失败保留原数据；
5. 修改预览不覆盖当前计划，确认时校验 expected_version 和到期时间。
"""
from sqlalchemy.orm import Session

from app.core.errors import not_implemented
from app.planner.schemas import PlanOut


class PlannerService:
    def __init__(self, session: Session):
        self.session = session

    def generate(self, user_id: str, confirmation_id: str, idempotency_key: str) -> PlanOut:
        not_implemented("PlannerService.generate")
