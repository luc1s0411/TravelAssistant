from datetime import date

from app.catalog.schemas import Location
from app.core.config import Settings
from app.core.errors import not_implemented
from app.integrations.schemas import WeatherResult


class QWeatherClient:
    """B：账号专属主机、认证、日期范围与未知天气；不得内嵌私钥。"""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def forecast(self, location: Location, on_date: date) -> WeatherResult:
        not_implemented("integrations.qweather.forecast")
