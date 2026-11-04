from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser
from app.core.errors import not_implemented
from app.core.schemas import Envelope
from app.integrations.schemas import RouteRequest, RouteResult, WeatherResult

router = APIRouter(tags=["integrations · B"])


@router.post("/routes/estimate", response_model=Envelope[RouteResult])
def route_estimate(body: RouteRequest, user: CurrentUser):
    not_implemented("routes.estimate")


@router.get("/weather", response_model=Envelope[WeatherResult])
def weather(user: CurrentUser, date: date, longitude: Annotated[float, Query(ge=-180, le=180)], latitude: Annotated[float, Query(ge=-90, le=90)]):
    not_implemented("weather.forecast")
