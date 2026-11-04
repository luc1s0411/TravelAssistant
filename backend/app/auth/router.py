from fastapi import APIRouter

from app.auth.schemas import LoginRequest, LoginResult, UserOut
from app.core.dependencies import CurrentUser
from app.core.errors import not_implemented
from app.core.schemas import Envelope

router = APIRouter(prefix="/auth", tags=["auth · B"])


@router.post("/login", response_model=Envelope[LoginResult])
def login(body: LoginRequest):
    not_implemented("auth.login")


@router.post("/logout", response_model=Envelope[None])
def logout(user: CurrentUser):
    not_implemented("auth.logout")


@router.get("/me", response_model=Envelope[UserOut])
def me(user: CurrentUser):
    not_implemented("auth.me")
