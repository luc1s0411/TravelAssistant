from datetime import date, time
from typing import Annotated, Literal

from pydantic import Field, model_validator

from app.core.schemas import StrictModel

Category = Literal["lodging", "dining", "attraction"]
Amount = Annotated[int, Field(strict=True, ge=0, le=1_000_000_000_000)]


class BudgetLimit(StrictModel):
    amount_minor: Amount | None = None
    unlimited: bool = False

    @model_validator(mode="after")
    def check_unlimited(self):
        if self.unlimited and self.amount_minor is not None:
            raise ValueError("不限预算时 amount_minor 必须为 null")
        return self


class Budget(StrictModel):
    currency: Literal["CNY"] = "CNY"
    total: BudgetLimit = Field(default_factory=BudgetLimit)
    lodging_per_room_night: BudgetLimit = Field(default_factory=BudgetLimit)
    dining_per_person_day: BudgetLimit = Field(default_factory=BudgetLimit)
    attraction_per_person_trip: BudgetLimit = Field(default_factory=BudgetLimit)


class TripInput(StrictModel):
    # 草稿允许逐步补全；确认时必须使用完整输入。
    destination: str | None = Field(default=None, min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    timezone: Literal["Asia/Shanghai"] = "Asia/Shanghai"
    travelers: int = Field(default=1, ge=1, le=50)
    rooms: int = Field(default=1, ge=1, le=50)
    arrival_time: time | None = None
    departure_time: time | None = None
    transport_mode: Literal["walking", "driving", "transit"] = "transit"
    budget: Budget = Field(default_factory=Budget)
    preferences: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("结束日期不得早于开始日期")
        if self.start_date is not None and self.start_date == self.end_date and self.arrival_time and self.departure_time and self.arrival_time >= self.departure_time:
            raise ValueError("同日出行的离开时间必须晚于到达时间")
        return self


class CompleteTripInput(TripInput):
    destination: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date


class DraftCreate(StrictModel):
    trip: TripInput = Field(default_factory=TripInput)


class DraftUpdate(DraftCreate):
    expected_revision: int = Field(ge=1)


class SelectionCreate(StrictModel):
    item_ref: str = Field(min_length=1, max_length=200)
    expected_revision: int = Field(ge=1)
    use_date: date
    end_date: date | None = None
    start_time: time | None = None
    quantity: int = Field(default=1, ge=1, le=100)
    mandatory: bool = True
    notes: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def check_interval(self):
        if self.end_date is not None and self.end_date <= self.use_date:
            raise ValueError("住宿离店日期必须晚于入住日期")
        return self


class SelectionOut(StrictModel):
    selection_id: str
    draft_id: str
    item_ref: str
    category: Category
    name: str
    use_date: date
    end_date: date | None = None
    start_time: time | None = None
    quantity: int
    mandatory: bool
    notes: str


class DraftOut(StrictModel):
    draft_id: str
    revision: int
    trip: TripInput
    status: Literal["needs_input", "selecting", "awaiting_confirmation", "generating", "ready", "needs_adjustment", "failed"]
    selections: list[SelectionOut] = Field(default_factory=list)
