from typing import Annotated

from fastapi import APIRouter, Depends

from app.catalog.schemas import CatalogItem, CatalogSearch
from app.core.dependencies import CurrentUser
from app.core.errors import not_implemented
from app.core.schemas import Envelope, Page

router = APIRouter(prefix="/catalog", tags=["catalog · B"])


@router.get("/search", response_model=Envelope[Page[CatalogItem]])
def search(user: CurrentUser, query: Annotated[CatalogSearch, Depends()]):
    not_implemented("catalog.search")


@router.get("/items/{item_ref}", response_model=Envelope[CatalogItem])
def detail(item_ref: str, user: CurrentUser):
    not_implemented("catalog.get_item")
