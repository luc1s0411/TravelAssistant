from datetime import date, datetime, time
from typing import Literal

from pydantic import Field, model_validator

from app.catalog.schemas import Location, Price
from app.core.schemas import StrictModel
from app.drafts.schemas import Amount, Category, CompleteTripInput, TripInput


class MessageRequest(StrictModel):
    message: str = Field(min_length=1, max_length=4000)


class AssistantReply(StrictModel):
    message: str
    intent: Literal["clarify", "propose_requirements", "query", "propose_revision"]
    proposed_trip: TripInput | None = None
    questions: list[str] = Field(default_factory=list, max_length=3)
    suggested_windows: list[Category] = Field(default_factory=list)
    # 模型仅提出建议，用户通过草稿接口确认；此对象不能直接写库。


class ConfirmRequest(StrictModel):
    expected_revision: int = Field(ge=1)
    selection_ids: list[str]
    accepted_missing_categories: list[Category] = Field(default_factory=list)


class ConfirmedInput(StrictModel):
    confirmation_id: str
    draft_id: str
    draft_revision: int
    selection_ids: list[str]
    trip: CompleteTripInput


class PlanCreate(StrictModel):
    draft_id: str
    confirmation_id: str


class PlanningRequestOut(StrictModel):
    request_id: str
    status: Literal["pending", "running", "succeeded", "failed"]
    plan_id: str | None = None
    error_code: str | None = None

    @model_validator(mode="after")
    def check_result(self):
        if (self.status == "succeeded") != (self.plan_id is not None):
            raise ValueError("只有成功的任务才包含计划编号")
        return self


class PlanRename(StrictModel):
    title: str = Field(min_length=1, max_length=128)
    expected_version: int = Field(ge=1)


class PlanItem(StrictModel):
    plan_item_id: str
    selection_id: str | None = None
    date: date
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    category: Literal["lodging", "dining", "attraction", "rest", "free_time"]
    name: str
    location: Location | None = None
    price: Price | None = None
    quantity: int = Field(ge=1)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_interval(self):
        if self.end_date is not None and self.end_date < self.date:
            raise ValueError("活动结束日期不得早于开始日期")
        if self.start_time and self.end_time and self.end_time <= self.start_time and (self.end_date is None or self.end_date == self.date):
            raise ValueError("跨日活动必须提供晚于开始日期的结束日期")
        return self


class RouteSegment(StrictModel):
    from_item_id: str
    to_item_id: str
    status: Literal["verified", "unverified", "schematic"]
    duration_minutes: int | None = Field(default=None, ge=0)
    distance_meters: int | None = Field(default=None, ge=0)
    coordinates: list[Location] = Field(default_factory=list)
    source: str | None = None


class CostSummary(StrictModel):
    currency: Literal["CNY"] = "CNY"
    known_subtotal_min_minor: Amount
    known_subtotal_max_minor: Amount | None = None
    unknown_item_ids: list[str]
    budget_status: Literal["within_known_limits", "exceeded", "incomplete"]

    @model_validator(mode="after")
    def check_subtotal(self):
        if self.known_subtotal_max_minor is not None and self.known_subtotal_max_minor < self.known_subtotal_min_minor:
            raise ValueError("已知小计上限不得小于下限")
        return self


class PlanSummary(StrictModel):
    plan_id: str
    version: int
    title: str
    start_date: date
    end_date: date
    status: Literal["draft", "ready", "needs_adjustment"]


class PlanOut(PlanSummary):
    confirmation_id: str
    timezone: str
    items: list[PlanItem]
    routes: list[RouteSegment]
    costs: CostSummary
    warnings: list[str]
    unplanned_selection_ids: list[str] = Field(default_factory=list)


class RevisionRequest(StrictModel):
    expected_version: int = Field(ge=1)
    instruction: str = Field(min_length=1, max_length=2000)
    target_date: date | None = None


class RevisionPreview(StrictModel):
    preview_id: str
    plan_id: str
    base_version: int
    change_summary: list[str]
    impacts: list[str]
    expires_at: datetime
    proposed_plan: PlanOut


class RevisionConfirm(StrictModel):
    expected_version: int = Field(ge=1)
