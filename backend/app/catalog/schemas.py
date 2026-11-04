from datetime import date, datetime
from typing import Any, Literal

from pydantic import AwareDatetime, Field, model_validator

from app.core.schemas import Pagination, StrictModel
from app.drafts.schemas import Amount, Category


class Location(StrictModel):
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)
    coordinate_system: Literal["GCJ02"] = "GCJ02"
    address: str | None = None


class Price(StrictModel):
    price_min_minor: Amount | None = None
    price_max_minor: Amount | None = None
    currency: Literal["CNY"] = "CNY"
    nature: Literal["reference", "quoted", "user_entered", "unknown"] = "unknown"
    unit: Literal["room_night", "person_day", "person_trip", "person", "item", "vehicle", "total"]
    # 如按人计的每餐或每次参观，写入明确计价条件，不得猜测。
    conditions: dict[str, Any] = Field(default_factory=dict)
    observed_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def check_unknown(self):
        low, high = self.price_min_minor, self.price_max_minor
        if self.nature == "unknown" and (low is not None or high is not None):
            raise ValueError("未知价格的上下限必须为 null")
        if self.nature == "reference" and low is None:
            raise ValueError("参考价格必须提供下限")
        if self.nature in ("quoted", "user_entered") and (low is None or high is None):
            raise ValueError("报价和用户填写价格必须提供上下限；单一价格上下限相同")
        if low is not None and high is not None and high < low:
            raise ValueError("价格上限不得小于下限")
        return self


class Source(StrictModel):
    provider: str
    mode: Literal["demo", "real"]
    source_id: str
    fetched_at: datetime
    attribution: str


class CatalogItem(StrictModel):
    item_ref: str
    category: Category
    name: str
    city: str
    area: str | None = None
    location: Location | None = None
    price: Price
    source: Source
    opening_hours: str | None = None
    image_url: str | None = None
    rating: float | None = None


class CatalogSearch(Pagination):
    draft_id: str
    category: Category
    area: str | None = None
    use_date: date | None = None
