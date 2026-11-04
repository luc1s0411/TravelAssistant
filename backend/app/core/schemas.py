from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Envelope(BaseModel, Generic[T]):
    code: str = "OK"
    message: str = "成功"
    data: T
    request_id: str


class Page(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False


class Pagination(StrictModel):
    cursor: str | None = None
    limit: int = Field(default=20, ge=1, le=50)
