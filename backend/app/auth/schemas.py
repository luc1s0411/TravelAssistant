from datetime import datetime

from pydantic import Field, SecretStr

from app.core.schemas import StrictModel


class LoginRequest(StrictModel):
    username: str = Field(min_length=1, max_length=80)
    password: SecretStr = Field(min_length=8, max_length=128)


class UserOut(StrictModel):
    user_id: str
    display_name: str
    auth_mode: str


class LoginResult(StrictModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserOut
