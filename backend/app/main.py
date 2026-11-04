from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.auth.router import router as auth_router
from app.catalog.router import router as catalog_router
from app.core.config import get_settings
from app.core.errors import AppError, register_error_handlers, response
from app.db.session import get_engine
from app.drafts.router import router as drafts_router
from app.integrations.router import router as integrations_router
from app.planner.router import router as planner_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="旅行助手 API · 工程骨架",
        version="0.1.0",
        description="接口和类型占位。业务接口尚未实现，返回 501；ORM 模型由用户维护。",
        responses={
            401: {"description": "未登录"},
            404: {"description": "资源不存在或不可访问"},
            409: {"description": "版本或幂等冲突"},
            501: {"description": "骨架接口尚未实现"},
        },
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins,
        allow_credentials=False, allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        request.state.request_id = uuid4().hex
        result = await call_next(request)
        result.headers["X-Request-ID"] = request.state.request_id
        return result

    register_error_handlers(app)
    for router in (auth_router, drafts_router, catalog_router, planner_router, integrations_router):
        app.include_router(router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    def health(request: Request):
        return response(request, {"status": "alive", "stage": "scaffold"})

    @app.get("/health/db", tags=["health"])
    def database_health(request: Request):
        try:
            with get_engine().connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError:
            raise AppError(503, "DATABASE_UNAVAILABLE", "MySQL 连接失败，请检查本地配置及服务") from None
        return response(request, {"status": "connected", "schema_verified": False})

    return app


app = create_app()
