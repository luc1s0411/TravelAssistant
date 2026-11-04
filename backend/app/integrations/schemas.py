from datetime import date, datetime
from typing import Literal

from app.catalog.schemas import Location
from app.core.schemas import StrictModel


class RouteRequest(StrictModel):
    origin: Location
    destination: Location
    mode: Literal["walking", "driving", "transit"]
    city: str


class RouteResult(StrictModel):
    status: Literal["verified", "unverified", "schematic"]
    duration_seconds: int | None = None
    distance_meters: int | None = None
    coordinates: list[Location]
    fetched_at: datetime
    warning: str | None = None


class WeatherResult(StrictModel):
    date: date
    status: Literal["available", "unknown"]
    summary: str | None = None
    source: str
    fetched_at: datetime
    warning: str | None = None
