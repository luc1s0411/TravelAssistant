from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


class AppError(Exception):
    def __init__(self, status: int, code: str, message: str, data=None):
        self.status, self.code, self.message, self.data = status, code, message, data


def not_implemented(feature: str):
    raise AppError(501, "NOT_IMPLEMENTED", "该能力尚未实现，当前仅为工程骨架", {"feature": feature})


def response(request: Request, data, *, status=200, code="OK", message="成功"):
    return JSONResponse(status_code=status, content={
        "code": code, "message": message, "data": data,
        "request_id": getattr(request.state, "request_id", uuid4().hex),
    })


def register_error_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error(request: Request, exc: AppError):
        return response(request, exc.data, status=exc.status, code=exc.code, message=exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # 不回显原始 input，避免密码、对话和其他输入进入错误响应。
        fields = [{"field": ".".join(str(p) for p in e["loc"]), "message": e["msg"]} for e in exc.errors()]
        return response(request, {"fields": fields}, status=422, code="VALIDATION_ERROR", message="请求字段校验失败")

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return response(request, None, status=exc.status_code, code=f"HTTP_{exc.status_code}", message=str(exc.detail))

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        return response(request, None, status=500, code="INTERNAL_ERROR", message="服务器内部错误，请提供 request_id 排查")
