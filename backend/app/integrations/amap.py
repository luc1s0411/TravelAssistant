from app.core.config import Settings
from app.core.errors import not_implemented
from app.integrations.schemas import RouteRequest, RouteResult


class AmapClient:
    """B：统一服务端 Key、超时、GCJ02 坐标与上游错误。"""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def estimate_route(self, request: RouteRequest) -> RouteResult:
        not_implemented("integrations.amap.estimate_route")
