"""
Budgets-Alerts Service - Budget monitoring and alerting with detectors.
"""

import os
import sys
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../packages/common-py/src"))

from finops_common import create_app, get_logger

from .database import get_db
from .models.models import Budget, BudgetPeriod, BudgetStatus, AlertSeverity
from .crud.budgets import BudgetCRUD
from .detectors import DETECTOR_REGISTRY, DetectionResult

# Initialize logger
logger = get_logger(__name__)

# Pydantic models for API
class BudgetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    amount: float = Field(gt=0)
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    tenant_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    thresholds: Optional[List[int]] = Field(default=[50, 80, 90, 100])


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    status: Optional[BudgetStatus] = None
    thresholds: Optional[List[int]] = None


class BudgetResponse(BaseModel):
    id: str
    org_id: str
    tenant_id: Optional[str]
    name: str
    description: Optional[str]
    amount: float
    period: str
    start_date: datetime
    end_date: datetime
    current_spend: float
    thresholds: List[int]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DetectorRunRequest(BaseModel):
    detector_name: Optional[str] = None  # Run specific detector or all
    budget_id: Optional[str] = None  # Run for specific budget or all
    test_mode: bool = True  # Don't emit events in test mode


class DetectorRunResult(BaseModel):
    budget_id: str
    budget_name: str
    detector_name: str
    detected: bool
    severity: Optional[str] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class DetectorRunResponse(BaseModel):
    results: List[DetectorRunResult]
    total_detections: int
    events_emitted: int


# Create FastAPI app
app = create_app(
    title="Budgets-Alerts Service",
    version="1.0.0",
    port=int(os.getenv("PORT", "8009")),
)


# Helper function to get org_id
def get_org_id(x_org_id: Optional[str] = Header(None)) -> str:
    """Extract org_id from header."""
    if not x_org_id:
        raise HTTPException(status_code=400, detail="X-Org-ID header required")
    return x_org_id


# Helper function to emit event (placeholder - integrates with event-bus)
async def emit_budget_event(
    event_type: str,
    org_id: str,
    budget: Budget,
    detection: DetectionResult,
) -> str:
    """
    Emit budget event to Kafka.
    
    This is a placeholder that will integrate with the event-bus package.
    """
    event_id = str(uuid.uuid4())
    
    # Build canonical event following event.schema.json
    event = {
        "event_id": event_id,
        "event_type": event_type,
        "event_version": "1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "budgets-alerts-service",
        "org_id": org_id,
        "tenant_id": budget.tenant_id,
        "payload": {
            "budget_id": budget.id,
            "budget_name": budget.name,
            "budget_amount": budget.amount,
            "current_spend": budget.current_spend,
            "severity": detection.severity,
            "message": detection.message,
            **detection.details,
        },
        "routing": {
            "priority": "high" if detection.severity in ["high", "critical"] else "normal",
            "channels": ["workflow", "notification"],
        },
    }
    
    logger.info(f"Would emit event: {event_type}", extra={"event_id": event_id, "org_id": org_id})
    
    # TODO: Use event-bus package to emit to Kafka
    # from event_bus import EventProducer
    # producer = EventProducer(...)
    # await producer.send(topic="budget-events", event=event)
    
    return event_id


# Budget CRUD endpoints
@app.post("/api/v1/budgets", response_model=BudgetResponse, status_code=201)
async def create_budget(
    budget: BudgetCreate,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new budget."""
    try:
        new_budget = await BudgetCRUD.create(
            db=db,
            org_id=org_id,
            name=budget.name,
            description=budget.description,
            amount=budget.amount,
            period=budget.period,
            start_date=budget.start_date,
            end_date=budget.end_date,
            tenant_id=budget.tenant_id,
            filters=budget.filters,
            thresholds=budget.thresholds,
        )
        return new_budget
    except Exception as e:
        logger.error(f"Error creating budget: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/budgets", response_model=List[BudgetResponse])
async def list_budgets(
    org_id: str = Depends(get_org_id),
    tenant_id: Optional[str] = None,
    status: Optional[BudgetStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List budgets with filters."""
    try:
        budgets = await BudgetCRUD.list(
            db=db,
            org_id=org_id,
            tenant_id=tenant_id,
            status=status,
            skip=skip,
            limit=limit,
        )
        return budgets
    except Exception as e:
        logger.error(f"Error listing budgets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/budgets/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """Get budget by ID."""
    budget = await BudgetCRUD.get_by_id(db, budget_id, org_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@app.put("/api/v1/budgets/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_update: BudgetUpdate,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """Update budget."""
    updated_budget = await BudgetCRUD.update(
        db=db,
        budget_id=budget_id,
        org_id=org_id,
        **budget_update.dict(exclude_unset=True),
    )
    if not updated_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return updated_budget


@app.delete("/api/v1/budgets/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: str,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete budget (soft delete)."""
    success = await BudgetCRUD.delete(db, budget_id, org_id)
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")


@app.get("/api/v1/budgets/{budget_id}/alerts")
async def get_budget_alerts(
    budget_id: str,
    org_id: str = Depends(get_org_id),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get alerts for a budget."""
    alerts = await BudgetCRUD.get_alerts(db, budget_id, org_id, skip, limit)
    return [
        {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value,
            "message": alert.message,
            "details": alert.details,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]


# Detector endpoints
@app.post("/api/v1/detectors/run", response_model=DetectorRunResponse)
async def run_detectors(
    request: DetectorRunRequest,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Run budget detectors.
    
    This endpoint allows testing detector logic without emitting events.
    """
    try:
        # Get budgets to check
        if request.budget_id:
            budget = await BudgetCRUD.get_by_id(db, request.budget_id, org_id)
            if not budget:
                raise HTTPException(status_code=404, detail="Budget not found")
            budgets = [budget]
        else:
            budgets = await BudgetCRUD.list(db, org_id, status=BudgetStatus.ACTIVE)
        
        # Get detectors to run
        if request.detector_name:
            if request.detector_name not in DETECTOR_REGISTRY:
                raise HTTPException(status_code=400, detail=f"Unknown detector: {request.detector_name}")
            detectors = {request.detector_name: DETECTOR_REGISTRY[request.detector_name]}
        else:
            detectors = DETECTOR_REGISTRY
        
        results = []
        events_emitted = 0
        
        # Run detectors on budgets
        for budget in budgets:
            # Generate synthetic cost data for testing
            # In production, this would query actual cost data from a cost database
            cost_data = _generate_synthetic_cost_data(budget)
            
            for detector_name, detector_class in detectors.items():
                detector = detector_class(db)
                
                try:
                    detection = await detector.detect(budget, cost_data)
                    
                    if detection and detection.detected:
                        # Create alert record
                        alert = await BudgetCRUD.create_alert(
                            db=db,
                            budget_id=budget.id,
                            org_id=org_id,
                            alert_type=detector_name,
                            severity=detection.severity,
                            actual_spend=budget.current_spend,
                            budget_amount=budget.amount,
                            message=detection.message,
                            details=detection.details,
                        )
                        
                        # Emit event if not in test mode
                        if not request.test_mode:
                            event_id = await emit_budget_event(
                                event_type=f"budget.{detector_name}",
                                org_id=org_id,
                                budget=budget,
                                detection=detection,
                            )
                            alert.event_id = event_id
                            alert.event_sent = True
                            alert.event_sent_at = datetime.utcnow()
                            await db.commit()
                            events_emitted += 1
                        
                        results.append(DetectorRunResult(
                            budget_id=budget.id,
                            budget_name=budget.name,
                            detector_name=detector_name,
                            detected=True,
                            severity=detection.severity,
                            message=detection.message,
                            details=detection.details,
                        ))
                    else:
                        results.append(DetectorRunResult(
                            budget_id=budget.id,
                            budget_name=budget.name,
                            detector_name=detector_name,
                            detected=False,
                        ))
                except Exception as e:
                    logger.error(f"Error running detector {detector_name} on budget {budget.id}: {e}")
                    results.append(DetectorRunResult(
                        budget_id=budget.id,
                        budget_name=budget.name,
                        detector_name=detector_name,
                        detected=False,
                        message=f"Error: {str(e)}",
                    ))
        
        total_detections = sum(1 for r in results if r.detected)
        
        return DetectorRunResponse(
            results=results,
            total_detections=total_detections,
            events_emitted=events_emitted,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running detectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/detectors")
async def list_detectors():
    """List available detectors."""
    return {
        "detectors": [
            {
                "name": name,
                "description": detector_class(None).get_description(),
            }
            for name, detector_class in DETECTOR_REGISTRY.items()
        ]
    }


def _generate_synthetic_cost_data(budget: Budget) -> List[Dict[str, Any]]:
    """
    Generate synthetic cost data for testing.
    
    In production, this would be replaced with actual cost data from database.
    """
    from datetime import timedelta
    import random
    
    cost_data = []
    current_date = budget.start_date
    days = (budget.end_date - budget.start_date).days
    
    # Generate daily costs that trend upward
    daily_budget = budget.amount / days if days > 0 else budget.amount
    
    for i in range(min(days, 30)):  # Generate up to 30 days
        # Add some variance and upward trend
        variance = random.uniform(0.8, 1.5)
        trend = 1 + (i * 0.02)  # 2% daily increase
        daily_cost = daily_budget * variance * trend
        
        cost_data.append({
            "date": current_date + timedelta(days=i),
            "amount": daily_cost,
        })
    
    return cost_data


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8009"))
    uvicorn.run(app, host="0.0.0.0", port=port)
