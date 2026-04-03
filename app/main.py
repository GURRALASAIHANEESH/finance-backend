from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.api.v1.router import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Finance Data Processing and Access Control API",
        description=(
            "A role-based finance dashboard backend supporting "
            "financial record management, access control, and "
            "dashboard-level aggregations."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        redirect_slashes=False,
    )


    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS if not settings.DEBUG else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": " → ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "Validation failed",
                "errors": errors,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=409,
            content={
                "status": "error",
                "message": "A database conflict occurred. The record may already exist.",
            },
        )

    app.include_router(router)

    @app.get("/health", tags=["System"], summary="Health check")
    def health_check():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "environment": settings.APP_ENV,
        }

    return app


app = create_app()