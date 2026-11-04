"""API 与用户提供的 ORM 之间的无数据库副作用的转换。"""

from typing import Any

from app.catalog.schemas import Price
from app.db.enums import Category, CoordinateSystem, PriceKind, PriceUnit

_API_TO_DB_CATEGORY = {
    "lodging": Category.LODGING,
    "dining": Category.FOOD,
    "attraction": Category.ATTRACTION,
}
_DB_TO_API_CATEGORY = {value: key for key, value in _API_TO_DB_CATEGORY.items()}


def category_to_db(value: str) -> Category:
    try:
        return _API_TO_DB_CATEGORY[value]
    except KeyError:
        raise ValueError(f"不支持的 API 分类: {value}") from None


def category_to_api(value: Category) -> str:
    try:
        return _DB_TO_API_CATEGORY[value]
    except KeyError:
        raise ValueError(f"不支持的数据库分类: {value}") from None


def coordinate_to_db(value: str) -> CoordinateSystem:
    if value != "GCJ02":
        raise ValueError("当前 API 仅支持 GCJ02 坐标")
    return CoordinateSystem.GCJ02


def coordinate_to_api(value: CoordinateSystem) -> str:
    if value != CoordinateSystem.GCJ02:
        raise ValueError("WGS84 坐标须先经过实际坐标转换，不能直接标为 GCJ02")
    return "GCJ02"


def price_to_db(value: Price) -> dict[str, Any]:
    """返回可用于 ORM 价格字段的值；不执行写入或单位换算。"""
    return {
        "currency": value.currency,
        "price_kind": PriceKind(value.nature),
        "price_unit": PriceUnit(value.unit),
        "price_min_minor": value.price_min_minor,
        "price_max_minor": value.price_max_minor,
        "price_queried_at": value.observed_at,
        "price_conditions": dict(value.conditions),
    }


def price_to_api(value: Any) -> Price:
    """读取具有 PriceMixin 字段的 ORM 对象；保留区间和计价条件。"""
    return Price(
        currency=value.currency,
        nature=value.price_kind,
        unit=value.price_unit,
        price_min_minor=value.price_min_minor,
        price_max_minor=value.price_max_minor,
        observed_at=value.price_queried_at,
        conditions=value.price_conditions,
    )
