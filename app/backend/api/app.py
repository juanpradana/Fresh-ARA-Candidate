from fastapi import FastAPI

from app.backend.api.routers import alerts, health, screener, watchlist

app = FastAPI(title="Fresh ARA Screener")
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(screener.router, prefix="/api/v1", tags=["screener"])
app.include_router(watchlist.router, prefix="/api/v1", tags=["watchlist"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])
