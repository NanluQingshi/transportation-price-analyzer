import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.alerts import router as alerts_router
from src.api.chat import router as chat_router
from src.api.dashboard import router as dashboard_router
from src.api.health import router as health_router
from src.api.routes import router as routes_router
from src.api.search import router as search_router
from src.api.trends import router as trends_router
from src.config import settings
from src.scheduler.jobs import create_scheduler

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.log_level)
    ),
)

_scheduler = create_scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    _scheduler.start()
    yield
    _scheduler.shutdown(wait=False)


app = FastAPI(
    title="Flight Price Analyzer",
    version="0.1.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url=None,
    lifespan=lifespan,
)

# 开发环境允许本地前端，生产环境由 Nginx 同域代理，不需要 CORS
_cors_origins = ["http://localhost:3000"] if settings.debug else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(routes_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
