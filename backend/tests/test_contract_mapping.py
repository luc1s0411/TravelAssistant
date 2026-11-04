from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.catalog.schemas import Price
from app.db.enums import Category, CoordinateSystem
from app.db.mapping import category_to_api, category_to_db, coordinate_to_api, coordinate_to_db, price_to_api, price_to_db


def test_category_and_coordinate_mapping_rejects_mislabeling():
    assert category_to_db("dining") is Category.FOOD
    assert category_to_api(Category.FOOD) == "dining"
    assert coordinate_to_db("GCJ02") is CoordinateSystem.GCJ02
    assert coordinate_to_api(CoordinateSystem.GCJ02) == "GCJ02"
    with pytest.raises(ValueError):
        coordinate_to_api(CoordinateSystem.WGS84)
    with pytest.raises(ValueError):
        category_to_db("rest")


def test_price_mapping_preserves_range_and_conditions():
    price = Price(
        nature="quoted", unit="person", price_min_minor=30000, price_max_minor=50000,
        conditions={"basis": "per_meal"}, observed_at=datetime(2026, 11, 4, tzinfo=timezone.utc),
    )
    assert price_to_api(SimpleNamespace(**price_to_db(price))) == price
