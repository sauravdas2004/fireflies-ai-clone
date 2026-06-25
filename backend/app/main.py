from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.database import init_db
from app.seed import seed_database
from app.routers.action_items import router as action_items_router
from app.routers.meetings import router as meetings_router
from app.routers.search import router as search_router
from app.routers.summaries import router as summaries_router
from app.routers.transcripts import router as transcripts_router
from app.routers.tags import router as tags_router
from app.routers.ask import router as ask_router


def _parse_cors_origins() -> list[str]:
    raw_value = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


def error_payload(code: str, message: str, details: Any | None = None) -> dict[str, Any]:
    payload = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


app = FastAPI(
    title="Fireflies Clone API",
    version="1.0.0",
    description="FastAPI backend for the Fireflies.ai clone assignment.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_payload("VALIDATION_ERROR", "Request validation failed", exc.errors()),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content=error_payload("DATABASE_ERROR", "A database error occurred"),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_SERVER_ERROR", "An unexpected error occurred"),
    )



@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_database()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(meetings_router)
app.include_router(transcripts_router)
app.include_router(action_items_router)
app.include_router(summaries_router)
app.include_router(search_router)
app.include_router(tags_router)
app.include_router(ask_router)
