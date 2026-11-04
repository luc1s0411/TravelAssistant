"""V1 数据库模型。只定义结构，不连接数据库、不实现业务接口。

复合外键保护跨草稿/跨版本关联；用户授权与状态转换仍须服务层验证。
所有外键采用 RESTRICT，禁止删除用户或草稿时意外级联清空计划历史。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (BigInteger, Boolean, CheckConstraint, Date, ForeignKey,
                        ForeignKeyConstraint, Index, Integer, JSON, Numeric,
                        String, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, ID_TYPE, IdentityMixin, TABLE_OPTIONS, UpdatedMixin, UTCDateTime
from .enums import (ActivityKind, BudgetCategory, BudgetMode, Category, CoordinateSystem,
                    DraftStatus, PreviewStatus, PriceKind, PriceUnit, RequestStatus,
                    RouteStatus, TransportMode, enum_type)


def positive(field: str):
    return CheckConstraint(f"{field} > 0", name=f"{field}_positive")


def money_checks():
    return (
        CheckConstraint("price_min_minor IS NULL OR price_min_minor >= 0", name="price_min_nonnegative"),
        CheckConstraint("price_max_minor IS NULL OR price_max_minor >= 0", name="price_max_nonnegative"),
        CheckConstraint("price_max_minor IS NULL OR price_min_minor IS NULL OR price_max_minor >= price_min_minor", name="price_range"),
        CheckConstraint("(price_kind = 'unknown' AND price_min_minor IS NULL AND price_max_minor IS NULL) OR (price_kind = 'reference' AND price_min_minor IS NOT NULL) OR (price_kind IN ('quoted','user_entered') AND price_min_minor IS NOT NULL AND price_max_minor IS NOT NULL)", name="price_known_pair"),
        CheckConstraint("currency = 'CNY'", name="currency_cny"),
    )


def location_checks():
    return (
        CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="longitude_range"),
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="latitude_range"),
        CheckConstraint("(longitude IS NULL AND latitude IS NULL AND coordinate_system IS NULL) OR (longitude IS NOT NULL AND latitude IS NOT NULL AND coordinate_system IS NOT NULL)", name="coordinate_pair"),
    )


class LocationMixin:
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    coordinate_system: Mapped[CoordinateSystem | None] = mapped_column(enum_type(CoordinateSystem, "coordinate_system"))
    address: Mapped[str | None] = mapped_column(String(512), comment="仅保存获授权内容或用户填写地址")


class PriceMixin:
    currency: Mapped[str] = mapped_column(String(3), default="CNY", server_default="CNY")
    price_kind: Mapped[PriceKind] = mapped_column(enum_type(PriceKind, "price_kind"), default=PriceKind.UNKNOWN, server_default="unknown")
    price_unit: Mapped[PriceUnit] = mapped_column(enum_type(PriceUnit, "price_unit"))
    price_min_minor: Mapped[int | None] = mapped_column(BigInteger, comment="单价下限，整数分；未知为 NULL")
    price_max_minor: Mapped[int | None] = mapped_column(BigInteger, comment="单价上限，整数分；明确免费为 0")
    price_queried_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    price_conditions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, comment="获准保存的日期、规格等计价条件")


class User(IdentityMixin, UpdatedMixin, Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(64), unique=True, comment="账号规范化由认证服务负责")
    password_hash: Mapped[str] = mapped_column(String(255), comment="成熟密码算法生成的哈希，禁止明文密码")
    display_name: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name="is_active_bool"), default=True, server_default="1")
    __table_args__ = (TABLE_OPTIONS,)


class TripDraft(IdentityMixin, UpdatedMixin, Base):
    __tablename__ = "trip_drafts"
    user_id: Mapped[str] = mapped_column(ID_TYPE, ForeignKey("users.id", ondelete="RESTRICT"))
    revision: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    status: Mapped[DraftStatus] = mapped_column(enum_type(DraftStatus, "draft_status"), default=DraftStatus.COLLECTING, server_default="collecting")
    destination: Mapped[str | None] = mapped_column(String(128))
    departure_city: Mapped[str | None] = mapped_column(String(128))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    arrival_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    departure_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    timezone_name: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai", server_default="Asia/Shanghai")
    traveler_count: Mapped[int | None] = mapped_column(Integer)
    room_count: Mapped[int | None] = mapped_column(Integer)
    transport_mode: Mapped[TransportMode | None] = mapped_column(enum_type(TransportMode, "transport_mode"))
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, comment="兴趣、饮食、节奏、用户确认的限制")
    __table_args__ = (
        UniqueConstraint("id", "user_id", name="uq_draft_owner"),
        positive("revision"), positive("traveler_count"), positive("room_count"),
        CheckConstraint("start_date IS NULL OR end_date IS NULL OR end_date >= start_date", name="date_range"),
        CheckConstraint("arrival_at IS NULL OR departure_at IS NULL OR departure_at >= arrival_at", name="arrival_range"),
        Index("ix_drafts_user_updated", "user_id", "updated_at"), TABLE_OPTIONS,
    )


class DraftBudget(IdentityMixin, UpdatedMixin, Base):
    __tablename__ = "draft_budgets"
    draft_id: Mapped[str] = mapped_column(ID_TYPE, ForeignKey("trip_drafts.id", ondelete="RESTRICT"))
    category: Mapped[BudgetCategory] = mapped_column(enum_type(BudgetCategory, "budget_category"))
    mode: Mapped[BudgetMode] = mapped_column(enum_type(BudgetMode, "budget_mode"), default=BudgetMode.UNKNOWN, server_default="unknown")
    unit: Mapped[PriceUnit] = mapped_column(enum_type(PriceUnit, "budget_unit"))
    currency: Mapped[str] = mapped_column(String(3), default="CNY", server_default="CNY")
    cap_minor: Mapped[int | None] = mapped_column(BigInteger)
    __table_args__ = (
        UniqueConstraint("draft_id", "category", name="uq_budget_category"),
        CheckConstraint("(mode = 'limited' AND cap_minor IS NOT NULL AND cap_minor >= 0) OR (mode IN ('unknown', 'unlimited') AND cap_minor IS NULL)", name="budget_mode_amount"),
        CheckConstraint("currency = 'CNY'", name="currency_cny"),
        CheckConstraint("(category = 'total' AND unit = 'total') OR (category = 'lodging' AND unit = 'room_night') OR (category = 'food' AND unit = 'person_day') OR (category = 'attraction' AND unit = 'person_trip')", name="budget_category_unit"),
        TABLE_OPTIONS,
    )


class TripSelection(IdentityMixin, UpdatedMixin, LocationMixin, PriceMixin, Base):
    __tablename__ = "trip_selections"
    draft_id: Mapped[str] = mapped_column(ID_TYPE, ForeignKey("trip_drafts.id", ondelete="RESTRICT"))
    category: Mapped[Category] = mapped_column(enum_type(Category, "category"))
    source_provider: Mapped[str] = mapped_column(String(32))
    source_item_id: Mapped[str | None] = mapped_column(String(255), comment="仅保存获得授权的外部引用")
    source_product_id: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255), comment="获准保存的名称或用户自定标签")
    source_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    usage_key: Mapped[str] = mapped_column(String(64), comment="服务端生成的幂等使用实例键；重复添加复用，跨天使用用新键")
    use_start_date: Mapped[date | None] = mapped_column(Date)
    use_end_date: Mapped[date | None] = mapped_column(Date, comment="住宿离店日为不含当日，其他项目按业务说明")
    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1", comment="计价数量，不自动等于人数或晚数")
    is_mandatory: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name="is_mandatory_bool"), default=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name="is_active_bool"), default=True, server_default="1", comment="移除选择只置为 false，保留历史确认关联")
    user_note: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        UniqueConstraint("id", "draft_id", name="uq_selection_draft"),
        UniqueConstraint("draft_id", "usage_key", name="uq_selection_usage"),
        positive("quantity"),
        CheckConstraint("use_start_date IS NULL OR use_end_date IS NULL OR use_end_date >= use_start_date", name="use_date_range"),
        *money_checks(), *location_checks(),
        Index("ix_selection_draft_active_category", "draft_id", "is_active", "category"), TABLE_OPTIONS,
    )


class ConfirmedInput(IdentityMixin, Base):
    __tablename__ = "confirmed_inputs"
    draft_id: Mapped[str] = mapped_column(ID_TYPE, ForeignKey("trip_drafts.id", ondelete="RESTRICT"))
    draft_revision: Mapped[int] = mapped_column(Integer)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, comment="不可变的需求和预算快照，不保存原始供应商响应")
    snapshot_hash: Mapped[str] = mapped_column(String(64), comment="规范化快照 SHA256，小写十六进制")
    __table_args__ = (
        UniqueConstraint("id", "draft_id", name="uq_confirmation_draft"),
        positive("draft_revision"), Index("ix_confirmation_revision", "draft_id", "draft_revision"), TABLE_OPTIONS,
    )


class ConfirmedSelection(IdentityMixin, Base):
    __tablename__ = "confirmed_selections"
    confirmation_id: Mapped[str] = mapped_column(ID_TYPE)
    draft_id: Mapped[str] = mapped_column(ID_TYPE)
    selection_id: Mapped[str] = mapped_column(ID_TYPE)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, comment="本次确认时的选择快照，后续候选修改不改变此内容")
    __table_args__ = (
        ForeignKeyConstraint(["confirmation_id", "draft_id"], ["confirmed_inputs.id", "confirmed_inputs.draft_id"], ondelete="RESTRICT", name="fk_confirmed_selection_input"),
        ForeignKeyConstraint(["selection_id", "draft_id"], ["trip_selections.id", "trip_selections.draft_id"], ondelete="RESTRICT", name="fk_confirmed_selection_draft"),
        UniqueConstraint("confirmation_id", "selection_id", name="uq_confirmed_selection"), TABLE_OPTIONS,
    )


class Plan(IdentityMixin, UpdatedMixin, Base):
    __tablename__ = "plans"
    user_id: Mapped[str] = mapped_column(ID_TYPE)
    draft_id: Mapped[str] = mapped_column(ID_TYPE)
    confirmation_id: Mapped[str] = mapped_column(ID_TYPE)
    title: Mapped[str] = mapped_column(String(128))
    current_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0", comment="0 为尚无成功版本；发布必须在事务内更新")
    is_archived: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name="is_archived_bool"), default=False, server_default="0")
    __table_args__ = (
        ForeignKeyConstraint(["draft_id", "user_id"], ["trip_drafts.id", "trip_drafts.user_id"], ondelete="RESTRICT", name="fk_plan_draft_owner"),
        ForeignKeyConstraint(["confirmation_id", "draft_id"], ["confirmed_inputs.id", "confirmed_inputs.draft_id"], ondelete="RESTRICT", name="fk_plan_confirmation"),
        UniqueConstraint("id", "draft_id", name="uq_plan_draft"),
        CheckConstraint("current_version >= 0", name="current_version_nonnegative"),
        Index("ix_plans_user_updated", "user_id", "is_archived", "updated_at"), TABLE_OPTIONS,
    )


class PlanVersion(IdentityMixin, Base):
    __tablename__ = "plan_versions"
    plan_id: Mapped[str] = mapped_column(ID_TYPE, ForeignKey("plans.id", ondelete="RESTRICT"))
    version: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    timezone_name: Mapped[str] = mapped_column(String(64))
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    budget_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, comment="已知小计、区间、未知项目；金额仍使用分")
    warnings: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    change_summary: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        UniqueConstraint("plan_id", "version", name="uq_plan_version_number"),
        UniqueConstraint("id", "plan_id", name="uq_version_plan"),
        positive("version"), CheckConstraint("end_date >= start_date", name="version_date_range"), TABLE_OPTIONS,
    )


class PlanItem(IdentityMixin, LocationMixin, Base):
    __tablename__ = "plan_items"
    plan_version_id: Mapped[str] = mapped_column(ID_TYPE)
    plan_id: Mapped[str] = mapped_column(ID_TYPE)
    draft_id: Mapped[str] = mapped_column(ID_TYPE)
    selection_id: Mapped[str | None] = mapped_column(ID_TYPE, comment="休息或留空可无选择；新增商家须先经用户确认")
    category: Mapped[ActivityKind] = mapped_column(enum_type(ActivityKind, "activity_kind"))
    title: Mapped[str] = mapped_column(String(255))
    activity_date: Mapped[date] = mapped_column(Date)
    sequence_no: Mapped[int] = mapped_column(Integer)
    starts_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    ends_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), comment="住宿可跨夜；按明确区间查询")
    is_time_fixed: Mapped[bool] = mapped_column(Boolean(create_constraint=True, name="is_time_fixed_bool"), default=False, server_default="0")
    source_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    notes: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        ForeignKeyConstraint(["plan_version_id", "plan_id"], ["plan_versions.id", "plan_versions.plan_id"], ondelete="RESTRICT", name="fk_item_version"),
        ForeignKeyConstraint(["plan_id", "draft_id"], ["plans.id", "plans.draft_id"], ondelete="RESTRICT", name="fk_item_plan_draft"),
        ForeignKeyConstraint(["selection_id", "draft_id"], ["trip_selections.id", "trip_selections.draft_id"], ondelete="RESTRICT", name="fk_item_selection"),
        UniqueConstraint("id", "plan_version_id", name="uq_item_version"),
        UniqueConstraint("plan_version_id", "activity_date", "sequence_no", name="uq_item_sequence"),
        positive("sequence_no"),
        CheckConstraint("starts_at IS NULL OR ends_at IS NULL OR ends_at > starts_at", name="activity_time_range"),
        *location_checks(), Index("ix_item_version_date_category", "plan_version_id", "activity_date", "category"), TABLE_OPTIONS,
    )


class PlanRoute(IdentityMixin, Base):
    __tablename__ = "plan_routes"
    plan_version_id: Mapped[str] = mapped_column(ID_TYPE, ForeignKey("plan_versions.id", ondelete="RESTRICT"))
    from_item_id: Mapped[str] = mapped_column(ID_TYPE)
    to_item_id: Mapped[str] = mapped_column(ID_TYPE)
    transport_mode: Mapped[TransportMode] = mapped_column(enum_type(TransportMode, "transport_mode"))
    status: Mapped[RouteStatus] = mapped_column(enum_type(RouteStatus, "route_status"))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    distance_meters: Mapped[int | None] = mapped_column(Integer)
    queried_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    source_provider: Mapped[str | None] = mapped_column(String(32))
    geometry: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment="仅获准保存时提供折线和坐标类型，否则查询后展示")
    __table_args__ = (
        ForeignKeyConstraint(["from_item_id", "plan_version_id"], ["plan_items.id", "plan_items.plan_version_id"], ondelete="RESTRICT", name="fk_route_from_version"),
        ForeignKeyConstraint(["to_item_id", "plan_version_id"], ["plan_items.id", "plan_items.plan_version_id"], ondelete="RESTRICT", name="fk_route_to_version"),
        UniqueConstraint("plan_version_id", "from_item_id", "to_item_id", "transport_mode", name="uq_route_pair_mode"),
        CheckConstraint("from_item_id <> to_item_id", name="route_distinct_endpoints"),
        CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0", name="duration_nonnegative"),
        CheckConstraint("distance_meters IS NULL OR distance_meters >= 0", name="distance_nonnegative"),
        CheckConstraint("status <> 'verified' OR (duration_seconds IS NOT NULL AND distance_meters IS NOT NULL AND queried_at IS NOT NULL AND source_provider IS NOT NULL)", name="verified_route_fields"), TABLE_OPTIONS,
    )


class PlanCost(IdentityMixin, PriceMixin, Base):
    __tablename__ = "plan_costs"
    plan_version_id: Mapped[str] = mapped_column(ID_TYPE, ForeignKey("plan_versions.id", ondelete="RESTRICT"))
    plan_item_id: Mapped[str | None] = mapped_column(ID_TYPE)
    category: Mapped[str] = mapped_column(String(32), comment="lodging/food/attraction/transport/other")
    title: Mapped[str] = mapped_column(String(255))
    multiplier: Mapped[int] = mapped_column(Integer, comment="明确计价份数；房晚、人数等由服务计算")
    source_refs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    __table_args__ = (
        ForeignKeyConstraint(["plan_item_id", "plan_version_id"], ["plan_items.id", "plan_items.plan_version_id"], ondelete="RESTRICT", name="fk_cost_item_version"),
        CheckConstraint("category IN ('lodging','food','attraction','transport','other')", name="cost_category"),
        positive("multiplier"), *money_checks(), Index("ix_cost_version_category", "plan_version_id", "category"), TABLE_OPTIONS,
    )


class RevisionPreview(IdentityMixin, Base):
    __tablename__ = "revision_previews"
    plan_id: Mapped[str] = mapped_column(ID_TYPE)
    base_version: Mapped[int] = mapped_column(Integer)
    status: Mapped[PreviewStatus] = mapped_column(enum_type(PreviewStatus, "preview_status"), default=PreviewStatus.PENDING, server_default="pending")
    proposed_plan: Mapped[dict[str, Any]] = mapped_column(JSON, comment="仅结构化变更提案；确认前不发布")
    change_summary: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    applied_version: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (
        ForeignKeyConstraint(["plan_id", "base_version"], ["plan_versions.plan_id", "plan_versions.version"], ondelete="RESTRICT", name="fk_preview_base_version"),
        ForeignKeyConstraint(["plan_id", "applied_version"], ["plan_versions.plan_id", "plan_versions.version"], ondelete="RESTRICT", name="fk_preview_applied_version"),
        UniqueConstraint("plan_id", "applied_version", name="uq_preview_applied_version"),
        CheckConstraint("(status = 'applied' AND applied_version IS NOT NULL AND applied_version > base_version) OR (status <> 'applied' AND applied_version IS NULL)", name="preview_applied_state"),
        Index("ix_preview_plan_status", "plan_id", "status"), TABLE_OPTIONS,
    )


class PlanningRequest(IdentityMixin, UpdatedMixin, Base):
    __tablename__ = "planning_requests"
    user_id: Mapped[str] = mapped_column(ID_TYPE)
    draft_id: Mapped[str] = mapped_column(ID_TYPE)
    confirmation_id: Mapped[str] = mapped_column(ID_TYPE)
    idempotency_key: Mapped[str] = mapped_column(String(64))
    request_hash: Mapped[str] = mapped_column(String(64), comment="规范化请求 SHA256，不存原始对话")
    status: Mapped[RequestStatus] = mapped_column(enum_type(RequestStatus, "request_status"), default=RequestStatus.PENDING, server_default="pending")
    plan_id: Mapped[str | None] = mapped_column(ID_TYPE)
    error_code: Mapped[str | None] = mapped_column(String(64))
    __table_args__ = (
        ForeignKeyConstraint(["draft_id", "user_id"], ["trip_drafts.id", "trip_drafts.user_id"], ondelete="RESTRICT", name="fk_request_draft_owner"),
        ForeignKeyConstraint(["confirmation_id", "draft_id"], ["confirmed_inputs.id", "confirmed_inputs.draft_id"], ondelete="RESTRICT", name="fk_request_confirmation"),
        ForeignKeyConstraint(["plan_id", "draft_id"], ["plans.id", "plans.draft_id"], ondelete="RESTRICT", name="fk_request_plan_draft"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_request_user_key"),
        CheckConstraint("status <> 'succeeded' OR plan_id IS NOT NULL", name="request_success_plan"),
        Index("ix_request_user_status", "user_id", "status"), TABLE_OPTIONS,
    )
