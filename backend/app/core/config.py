from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    database_url: SecretStr = SecretStr(
        "mysql+pymysql://travel:local-dev-change-me@127.0.0.1:3306/travel_assistant?charset=utf8mb4"
    )
    session_secret: SecretStr = SecretStr("development-only-change-before-production")
    auth_mode: Literal["password", "demo"] = "password"
    catalog_provider_mode: Literal["real", "demo"] = "demo"
    amap_web_service_key: SecretStr = SecretStr("")
    qweather_api_host: str = ""
    qweather_auth_mode: str = "jwt"
    qweather_private_key_path: str = ""
    model_provider: str = "demo"
    model_base_url: str = ""
    model_name: str = ""
    model_api_key: SecretStr = SecretStr("")
    upstream_timeout_seconds: int = Field(default=15, ge=1, le=120)
    plan_timeout_seconds: int = Field(default=120, ge=1, le=600)
    plan_concurrency_limit: int = Field(default=3, ge=1, le=100)
    model_max_retries: int = Field(default=1, ge=0, le=3)

    @model_validator(mode="after")
    def check_environment(self):
        if not self.database_url.get_secret_value().startswith("mysql+pymysql://"):
            raise ValueError("本工程固定使用 MySQL + PyMySQL，请设置 mysql+pymysql:// 连接")
        if self.app_env == "production":
            if self.auth_mode == "demo":
                raise ValueError("正式环境禁止演示身份")
            if len(self.session_secret.get_secret_value()) < 32 or self.session_secret.get_secret_value().startswith("development-only"):
                raise ValueError("正式环境必须配置独立 SESSION_SECRET，长度至少 32")
            if "local-dev-change-me" in self.database_url.get_secret_value():
                raise ValueError("正式环境不能使用示例数据库密码")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
