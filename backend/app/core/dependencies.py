from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.schemas import UserOut
from app.core.errors import AppError, not_implemented

bearer = HTTPBearer(auto_error=False)
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)]


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> UserOut:
    """B：验证服务端会话并读取用户；不得从请求体 user_id 推导身份。"""
    if credentials is None:
        raise AppError(401, "UNAUTHENTICATED", "请先登录")
    # 骨架阶段拒绝所有令牌，不能把任意 bearer 值当作合法用户。
    not_implemented("auth.verify_session")


CurrentUser = Annotated[UserOut, Depends(get_current_user)]
