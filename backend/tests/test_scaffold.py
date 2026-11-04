import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.auth.schemas import UserOut
from app.catalog.schemas import Price
from app.core.config import Settings
from app.core.dependencies import get_current_user
from app.drafts.schemas import BudgetLimit, CompleteTripInput, TripInput
from app.planner.schemas import CostSummary, PlanItem, PlanningRequestOut
from app.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


def test_liveness_has_envelope_and_request_id(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "alive", "stage": "scaffold"}
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_auth_does_not_accept_arbitrary_token(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer arbitrary"})
    assert response.status_code == 501
    assert response.json()["code"] == "NOT_IMPLEMENTED"


def test_business_placeholder_cannot_report_success(client):
    client.app.dependency_overrides[get_current_user] = lambda: UserOut(user_id="test-user", display_name="测试", auth_mode="password")
    try:
        response = client.get("/api/v1/plans")
        assert response.status_code == 501
        assert response.json()["data"]["feature"] == "planner.list_owned"
    finally:
        client.app.dependency_overrides.clear()


def test_invalid_login_does_not_echo_password(client):
    response = client.post("/api/v1/auth/login", json={"username": "", "password": "secret"})
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert "secret" not in response.text


def test_unknown_zero_and_unlimited_are_distinct():
    assert BudgetLimit().amount_minor is None
    assert BudgetLimit(amount_minor=0).amount_minor == 0
    assert BudgetLimit(unlimited=True).unlimited
    with pytest.raises(ValidationError):
        BudgetLimit(amount_minor=0, unlimited=True)


@pytest.mark.parametrize("amount", [-1, 0.5, True, "100"])
def test_money_requires_nonnegative_integer_minor_units(amount):
    with pytest.raises(ValidationError):
        BudgetLimit(amount_minor=amount)


def test_unknown_price_cannot_be_zero():
    with pytest.raises(ValidationError):
        Price(price_min_minor=0, nature="unknown", unit="person")
    assert Price(price_min_minor=0, price_max_minor=0, nature="reference", unit="person").price_min_minor == 0


def test_partial_draft_requires_complete_trip_at_confirmation():
    assert TripInput().destination is None
    with pytest.raises(ValidationError):
        CompleteTripInput.model_validate(TripInput().model_dump())
    with pytest.raises(ValidationError):
        TripInput(start_date="2026-12-03", end_date="2026-12-01")


def test_price_range_preserves_unknown_free_and_bounds():
    assert Price(unit="room_night").price_min_minor is None
    quote = Price(nature="quoted", unit="room_night", price_min_minor=30000, price_max_minor=50000)
    assert (quote.price_min_minor, quote.price_max_minor) == (30000, 50000)
    with pytest.raises(ValidationError):
        Price(nature="quoted", unit="room_night", price_min_minor=50000, price_max_minor=30000)
    with pytest.raises(ValidationError):
        Price(nature="user_entered", unit="person", price_min_minor=100)


def test_free_time_can_exist_without_selection_or_price():
    item = PlanItem(plan_item_id="i", date="2026-12-01", category="free_time", name="自由活动", quantity=1)
    assert item.selection_id is None and item.price is None


def test_overnight_item_and_cost_range_are_unambiguous():
    item = dict(plan_item_id="i", date="2026-12-01", category="lodging", name="住宿", quantity=1, start_time="22:00", end_time="08:00")
    with pytest.raises(ValidationError):
        PlanItem(**item)
    assert PlanItem(**item, end_date="2026-12-02").end_date.isoformat() == "2026-12-02"
    with pytest.raises(ValidationError):
        CostSummary(known_subtotal_min_minor=200, known_subtotal_max_minor=100, unknown_item_ids=[], budget_status="incomplete")


def test_planning_request_requires_result_only_when_succeeded():
    assert PlanningRequestOut(request_id="r", status="pending").plan_id is None
    assert PlanningRequestOut(request_id="r", status="succeeded", plan_id="p").plan_id == "p"
    with pytest.raises(ValidationError):
        PlanningRequestOut(request_id="r", status="succeeded")


def test_new_plan_contract_routes_remain_placeholders(client):
    client.app.dependency_overrides[get_current_user] = lambda: UserOut(user_id="test-user", display_name="测试", auth_mode="password")
    try:
        requests = [
            client.post("/api/v1/plans", json={"draft_id": "d", "confirmation_id": "c"}, headers={"Idempotency-Key": "key-12345678"}),
            client.get("/api/v1/planning-requests/r"),
            client.patch("/api/v1/plans/p", json={"title": "新名称", "expected_version": 1}),
            client.delete("/api/v1/plans/p?expected_version=1"),
        ]
        assert all(response.status_code == 501 for response in requests)
    finally:
        client.app.dependency_overrides.clear()


def test_fixture_and_invalid_dates():
    root = Path(__file__).resolve().parents[2]
    fixture = json.loads((root / "docs/fixtures/trip_input.json").read_text(encoding="utf-8"))
    trip = TripInput.model_validate(fixture)
    assert trip.travelers == 2 and trip.rooms == 1
    assert trip.budget.lodging_per_room_night.amount_minor == 50000
    fixture["end_date"] = "2026-11-01"
    with pytest.raises(ValidationError):
        TripInput.model_validate(fixture)


def test_production_rejects_demo_identity():
    with pytest.raises(ValidationError, match="正式环境禁止演示身份"):
        Settings(_env_file=None, app_env="production", auth_mode="demo")


def test_openapi_covers_contract_paths(client):
    schema = client.get("/openapi.json").json()
    for path in ["/api/v1/drafts/{draft_id}/confirm", "/api/v1/plans/{plan_id}/revisions/{preview_id}/confirm", "/api/v1/catalog/search", "/api/v1/routes/estimate", "/api/v1/weather", "/api/v1/planning-requests/{planning_request_id}"]:
        assert path in schema["paths"]
    assert schema["paths"]["/api/v1/plans"]["post"]["parameters"][0]["name"] == "Idempotency-Key"
    assert "202" in schema["paths"]["/api/v1/plans"]["post"]["responses"]
    assert {"get", "patch", "delete"} <= schema["paths"]["/api/v1/plans/{plan_id}"].keys()
