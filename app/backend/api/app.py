from fastapi import FastAPI

from app.backend.api.routers import health, screener

app = FastAPI(title="Fresh ARA Screener")
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(screener.router, prefix="/api/v1", tags=["screener"])
