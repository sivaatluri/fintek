"""Query service for fintek platform."""

from fastapi import FastAPI
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from .health import router as health_router

app = FastAPI(
    title="Fintek Query Service",
    description="Query execution service using Trino",
    version="0.1.0",
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])


class QueryRequest(BaseModel):
    """Query request."""
    tenant_id: str
    sql: str
    parameters: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Query response."""
    query_id: str
    status: str
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: int


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "fintek-query",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/query/execute", response_model=QueryResponse)
async def execute_query(query: QueryRequest):
    """Execute a query (placeholder).
    
    In production, this would:
    - Validate query
    - Execute on Trino
    - Apply tenant isolation
    - Return results
    """
    return {
        "query_id": "query-123",
        "status": "completed",
        "columns": ["resource_id", "cost", "date"],
        "rows": [],
        "row_count": 0,
        "execution_time_ms": 150,
    }


@app.get("/query/{query_id}")
async def get_query_status(query_id: str):
    """Get query status (placeholder)."""
    return {
        "query_id": query_id,
        "status": "completed",
        "created_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
    }


@app.post("/query/cancel/{query_id}")
async def cancel_query(query_id: str):
    """Cancel a running query (placeholder)."""
    return {
        "query_id": query_id,
        "status": "cancelled",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
