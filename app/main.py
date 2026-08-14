"""StockPilot API - Main Application Entry Point

This module creates and configures the FastAPI application instance.
It's the first file that runs when you start the server.

Run with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.config import settings
from app.exceptions import register_exception_handlers

# fastapi application
app = FastAPI(
    title=settings.APP_NAME,
    description="Inventory and Business Management Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Cors middleware
# CORS = Cross-Origin Resource Sharing
# allows frontend apps running on different domains to access the API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

register_exception_handlers(app)
app.include_router(api_v1_router, prefix="/api/v1")

# health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> dict:
    """Check if the API is running.
    
    This endpoint is used by:
    - Docker health checks
    - Load balancers
    - Monitoring systems

    Returns:
        A dict with service status, name, and current timestamp.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.APP_ENV,
    }

# root endpoint
@app.get("/", tags=["System"])
async def root() -> dict:
    """API root - basic information about the service."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API!",
        "version": "0.1.0",
        "docs":"/docs",
    }