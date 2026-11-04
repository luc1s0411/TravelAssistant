from typing import Annotated

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, IdempotencyKey
from app.core.errors import not_implemented
from app.core.schemas import Envelope
from app.drafts.schemas import DraftCreate, DraftOut, DraftUpdate, SelectionCreate

router = APIRouter(prefix="/drafts", tags=["drafts · B"])


@router.post("", response_model=Envelope[DraftOut], status_code=201)
def create_draft(body: DraftCreate, user: CurrentUser):
    not_implemented("drafts.create")


@router.get("/{draft_id}", response_model=Envelope[DraftOut])
def get_draft(draft_id: str, user: CurrentUser):
    not_implemented("drafts.get_owned")


@router.patch("/{draft_id}", response_model=Envelope[DraftOut])
def update_draft(draft_id: str, body: DraftUpdate, user: CurrentUser):
    not_implemented("drafts.update_with_revision")


@router.post("/{draft_id}/selections", response_model=Envelope[DraftOut])
def add_selection(draft_id: str, body: SelectionCreate, user: CurrentUser, idempotency_key: IdempotencyKey):
    not_implemented("drafts.add_selection_idempotently")


@router.delete("/{draft_id}/selections/{selection_id}", response_model=Envelope[DraftOut])
def remove_selection(draft_id: str, selection_id: str, user: CurrentUser, expected_revision: Annotated[int, Query(ge=1)]):
    not_implemented("drafts.remove_selection_with_revision")
