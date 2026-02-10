"""Budget management service for fintek platform."""

from fastapi import FastAPI
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from enum import Enum

from .health import router as health_router

app = FastAPI(
    title="Fintek Budget Service",
    description="Budget management and alerting service",
    version="0.1.0",
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])


class BudgetPeriod(str, Enum):
    """Budget period."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetCreate(BaseModel):
    """Budget creation request."""
    tenant_id: str
    name: str
    amount: Decimal
    currency: str = "USD"
    period: BudgetPeriod
    alert_threshold: int = 80  # Percentage


class BudgetResponse(BaseModel):
    """Budget response."""
    id: str
    tenant_id: str
    name: str
    amount: Decimal
    currency: str
    period: BudgetPeriod
    alert_threshold: int
    current_spend: Decimal
    created_at: datetime


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "fintek-budgets",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/budgets", response_model=List[BudgetResponse])
async def list_budgets(tenant_id: str, skip: int = 0, limit: int = 100):
    """List budgets for a tenant (placeholder)."""
    return []


@app.post("/budgets", response_model=BudgetResponse, status_code=201)
async def create_budget(budget: BudgetCreate):
    """Create a new budget (placeholder)."""
    return {
        "id": "budget-123",
        "tenant_id": budget.tenant_id,
        "name": budget.name,
        "amount": budget.amount,
        "currency": budget.currency,
        "period": budget.period,
        "alert_threshold": budget.alert_threshold,
        "current_spend": Decimal("0"),
        "created_at": datetime.utcnow(),
    }


@app.get("/budgets/{budget_id}", response_model=BudgetResponse)
async def get_budget(budget_id: str):
    """Get budget by ID (placeholder)."""
    return {
        "id": budget_id,
        "tenant_id": "tenant-123",
        "name": "Monthly AWS Budget",
        "amount": Decimal("10000.00"),
        "currency": "USD",
        "period": BudgetPeriod.MONTHLY,
        "alert_threshold": 80,
        "current_spend": Decimal("7500.00"),
        "created_at": datetime.utcnow(),
    }


@app.put("/budgets/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: str, budget: BudgetCreate):
    """Update budget (placeholder)."""
    return {
        "id": budget_id,
        "tenant_id": budget.tenant_id,
        "name": budget.name,
        "amount": budget.amount,
        "currency": budget.currency,
        "period": budget.period,
        "alert_threshold": budget.alert_threshold,
        "current_spend": Decimal("0"),
        "created_at": datetime.utcnow(),
    }


@app.delete("/budgets/{budget_id}")
async def delete_budget(budget_id: str):
    """Delete budget (placeholder)."""
    return {"message": f"Budget {budget_id} deleted"}


@app.get("/budgets/{budget_id}/alerts")
async def get_budget_alerts(budget_id: str):
    """Get budget alerts (placeholder)."""
    return {
        "budget_id": budget_id,
        "alerts": [],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
