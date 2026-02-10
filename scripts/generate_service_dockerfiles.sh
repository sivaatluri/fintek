#!/bin/bash
# Generate standardized Dockerfiles for all services

set -e

SERVICES=(
    "billing-service:8003"
    "cost-ingestion-service:8004"
    "cost-normalization-service:8005"
    "virtual-tagging-service:8006"
    "allocation-service:8007"
    "recommendations-service:8008"
    "budgets-alerts-service:8009"
    "workflows-service:8010"
    "integrations-service:8011"
    "reporting-service:8012"
    "query-service:8013"
    "data-quality-service:8014"
    "metering-service:8015"
    "audit-service:8016"
    "admin-ops-service:8017"
)

for service_port in "${SERVICES[@]}"; do
    IFS=':' read -r SERVICE PORT <<< "$service_port"
    
    echo "Generating Dockerfile for $SERVICE on port $PORT..."
    
    # Create directories
    mkdir -p "services/$SERVICE/src"
    mkdir -p "services/$SERVICE/tests"
    
    # Generate Dockerfile
    cat > "services/$SERVICE/Dockerfile" <<EOF
# Multi-stage Dockerfile for $SERVICE
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY packages/common-py /app/packages/common-py
COPY services/$SERVICE/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /app/packages/common-py /app/packages/common-py
COPY --chown=appuser:appuser services/$SERVICE/src /app/src

USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
EOF

    # Generate requirements.txt if it doesn't exist
    if [ ! -f "services/$SERVICE/requirements.txt" ]; then
        cat > "services/$SERVICE/requirements.txt" <<EOF
# $SERVICE Requirements
-e ../../packages/common-py

fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6
EOF
    fi
    
    # Generate basic main.py if it doesn't exist
    if [ ! -f "services/$SERVICE/src/main.py" ]; then
        SERVICE_TITLE=$(echo "$SERVICE" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')
        cat > "services/$SERVICE/src/main.py" <<EOF
"""$SERVICE_TITLE - Main application."""
from fastapi import APIRouter

from finops_common import Settings, create_app, get_logger

logger = get_logger(__name__)

settings = Settings(
    service_name="$SERVICE",
    service_version="1.0.0",
    port=$PORT,
)

app = create_app(
    title="FinOps $SERVICE_TITLE",
    version="1.0.0",
    description="$SERVICE_TITLE for FinOps SaaS Platform",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["$SERVICE_TITLE"])


@router.get("/status")
async def get_status():
    """Get service status."""
    logger.info("Status endpoint called")
    return {
        "service": "$SERVICE",
        "status": "operational",
        "version": "1.0.0",
    }


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("$SERVICE_TITLE starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("$SERVICE_TITLE shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
EOF
    fi
    
done

echo "✅ Dockerfiles generated for all services"
