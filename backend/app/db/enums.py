"""枚举使用字符串入库；变更取值必须新增迁移。"""

from enum import StrEnum

from sqlalchemy import Enum


class Category(StrEnum):
    LODGING = "lodging"
    FOOD = "food"
    ATTRACTION = "attraction"


class BudgetCategory(StrEnum):
    TOTAL = "total"
    LODGING = "lodging"
    FOOD = "food"
    ATTRACTION = "attraction"


class BudgetMode(StrEnum):
    UNKNOWN = "unknown"
    LIMITED = "limited"
    UNLIMITED = "unlimited"


class PriceKind(StrEnum):
    UNKNOWN = "unknown"
    REFERENCE = "reference"
    QUOTED = "quoted"
    USER_ENTERED = "user_entered"


class PriceUnit(StrEnum):
    ROOM_NIGHT = "room_night"
    PERSON_DAY = "person_day"
    PERSON_TRIP = "person_trip"
    PERSON = "person"
    ITEM = "item"
    VEHICLE = "vehicle"
    TOTAL = "total"


class CoordinateSystem(StrEnum):
    GCJ02 = "gcj02"
    WGS84 = "wgs84"


class DraftStatus(StrEnum):
    COLLECTING = "collecting"
    SELECTING = "selecting"
    CONFIRMED = "confirmed"
    ARCHIVED = "archived"


class ActivityKind(StrEnum):
    LODGING = "lodging"
    FOOD = "food"
    ATTRACTION = "attraction"
    REST = "rest"
    FREE_TIME = "free_time"


class RequestStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class PreviewStatus(StrEnum):
    PENDING = "pending"
    APPLIED = "applied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class RouteStatus(StrEnum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    FAILED = "failed"


class TransportMode(StrEnum):
    WALKING = "walking"
    DRIVING = "driving"
    TRANSIT = "transit"
    BICYCLING = "bicycling"


def enum_type(enum_class: type[StrEnum], name: str) -> Enum:
    return Enum(enum_class, values_callable=lambda cls: [value.value for value in cls],
                name=name, native_enum=False, create_constraint=True,
                validate_strings=True, length=32)
