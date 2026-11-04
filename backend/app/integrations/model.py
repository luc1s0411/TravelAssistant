from app.core.config import Settings
from app.core.errors import not_implemented
from app.drafts.schemas import TripInput
from app.planner.schemas import AssistantReply


class ModelClient:
    """C：供应商未冻结。只接收必要输入，输出经验证，不授予数据库工具。"""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def propose_requirements(self, message: str, current: TripInput | None) -> AssistantReply:
        not_implemented("integrations.model.propose_requirements")
