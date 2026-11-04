from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, IdempotencyKey
from app.core.errors import not_implemented
from app.core.schemas import Envelope, Page, Pagination
from app.drafts.schemas import Category
from app.planner.schemas import (
    AssistantReply, ConfirmedInput, ConfirmRequest, MessageRequest, PlanCreate,
    PlanItem, PlanOut, PlanRename, PlanSummary, PlanningRequestOut,
    RevisionConfirm, RevisionPreview, RevisionRequest,
)

router = APIRouter(tags=["planner · C"])


@router.post("/drafts/{draft_id}/assistant/messages", response_model=Envelope[AssistantReply])
def draft_message(draft_id: str, body: MessageRequest, user: CurrentUser):
    not_implemented("planner.propose_requirements")


@router.post("/drafts/{draft_id}/confirm", response_model=Envelope[ConfirmedInput])
def confirm(draft_id: str, body: ConfirmRequest, user: CurrentUser):
    not_implemented("planner.confirm_snapshot")


@router.post("/plans", response_model=Envelope[PlanningRequestOut], status_code=202)
def generate(body: PlanCreate, user: CurrentUser, idempotency_key: IdempotencyKey):
    not_implemented("planner.generate_idempotently")


@router.get("/planning-requests/{planning_request_id}", response_model=Envelope[PlanningRequestOut])
def get_planning_request(planning_request_id: str, user: CurrentUser):
    not_implemented("planner.get_owned_request")


@router.get("/plans", response_model=Envelope[Page[PlanSummary]])
def list_plans(user: CurrentUser, pagination: Annotated[Pagination, Depends()]):
    not_implemented("planner.list_owned")


@router.get("/plans/{plan_id}", response_model=Envelope[PlanOut])
def get_plan(plan_id: str, user: CurrentUser):
    not_implemented("planner.get_owned")


@router.patch("/plans/{plan_id}", response_model=Envelope[PlanSummary])
def rename_plan(plan_id: str, body: PlanRename, user: CurrentUser):
    not_implemented("planner.rename_owned")


@router.delete("/plans/{plan_id}", response_model=Envelope[None])
def archive_plan(plan_id: str, user: CurrentUser, expected_version: Annotated[int, Query(ge=1)]):
    not_implemented("planner.archive_owned")


@router.get("/plans/{plan_id}/items", response_model=Envelope[list[PlanItem]])
def get_items(plan_id: str, user: CurrentUser, on_date: Annotated[date | None, Query(alias="date")] = None, category: Category | None = None):
    not_implemented("planner.query_items")


@router.post("/plans/{plan_id}/assistant/messages", response_model=Envelope[AssistantReply])
def plan_message(plan_id: str, body: MessageRequest, user: CurrentUser):
    not_implemented("planner.query_or_propose_revision")


@router.post("/plans/{plan_id}/revisions/preview", response_model=Envelope[RevisionPreview])
def preview(plan_id: str, body: RevisionRequest, user: CurrentUser):
    not_implemented("planner.preview_revision")


@router.post("/plans/{plan_id}/revisions/{preview_id}/confirm", response_model=Envelope[PlanOut])
def confirm_revision(plan_id: str, preview_id: str, body: RevisionConfirm, user: CurrentUser, idempotency_key: IdempotencyKey):
    not_implemented("planner.confirm_revision_idempotently")
