import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.dashboard import router as dashboard_router
from src.api.health import router as health_router
from src.api.search import router as search_router
from src.api.trends import router as trends_router
from src.config import settings
from src.scheduler.jobs import create_scheduler

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(__import__("logging"), settings.log_level)
    ),
)

app = FastAPI(
    title="Flight Price Analyzer",
    version="0.1.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(trends_router, prefix="/api")


@app.on_event("startup")
async def startup() -> None:
    scheduler = create_scheduler()
    scheduler.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    pass
