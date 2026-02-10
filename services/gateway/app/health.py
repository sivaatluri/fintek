"""Health check endpoints."""

from fastapi import APIRouter, Response
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "gateway",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # In production, check dependencies (database, redis, etc.)
    return {
        "status": "ready",
        "service": "gateway",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
async def liveness_check():
    """Liveness check endpoint."""
    return {
        "status": "alive",
        "service": "gateway",
        "timestamp": datetime.utcnow().isoformat(),
    }
