"""
Budget CRUD operations with org_id enforcement.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Budget, BudgetAlert, BudgetPeriod, BudgetStatus


class BudgetCRUD:
    """CRUD operations for Budget model."""

    @staticmethod
    async def create(
        db: AsyncSession,
        org_id: str,
        name: str,
        amount: float,
        start_date: datetime,
        end_date: datetime,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        tenant_id: Optional[str] = None,
        description: Optional[str] = None,
        filters: Optional[dict] = None,
        thresholds: Optional[List[int]] = None,
        created_by: Optional[str] = None,
    ) -> Budget:
        """Create a new budget."""
        budget = Budget(
            id=str(uuid.uuid4()),
            org_id=org_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            amount=amount,
            period=period,
            start_date=start_date,
            end_date=end_date,
            filters=filters or {},
            thresholds=thresholds or [50, 80, 90, 100],
            alert_state={},
            created_by=created_by,
        )
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget

    @staticmethod
    async def get_by_id(db: AsyncSession, budget_id: str, org_id: str) -> Optional[Budget]:
        """Get budget by ID with org enforcement."""
        query = select(Budget).where(
            and_(
                Budget.id == budget_id,
                Budget.org_id == org_id,
                Budget.is_active == True
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        org_id: str,
        tenant_id: Optional[str] = None,
        status: Optional[BudgetStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Budget]:
        """List budgets with filters."""
        conditions = [Budget.org_id == org_id, Budget.is_active == True]
        
        if tenant_id:
            conditions.append(Budget.tenant_id == tenant_id)
        if status:
            conditions.append(Budget.status == status)
        
        query = select(Budget).where(and_(*conditions)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        budget_id: str,
        org_id: str,
        **kwargs
    ) -> Optional[Budget]:
        """Update budget."""
        budget = await BudgetCRUD.get_by_id(db, budget_id, org_id)
        if not budget:
            return None
        
        for key, value in kwargs.items():
            if value is not None and hasattr(budget, key):
                setattr(budget, key, value)
        
        budget.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(budget)
        return budget

    @staticmethod
    async def delete(db: AsyncSession, budget_id: str, org_id: str) -> bool:
        """Soft delete budget."""
        budget = await BudgetCRUD.get_by_id(db, budget_id, org_id)
        if not budget:
            return False
        
        budget.is_active = False
        budget.updated_at = datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def get_alerts(
        db: AsyncSession,
        budget_id: str,
        org_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BudgetAlert]:
        """Get alerts for a budget."""
        query = select(BudgetAlert).where(
            and_(
                BudgetAlert.budget_id == budget_id,
                BudgetAlert.org_id == org_id
            )
        ).order_by(BudgetAlert.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_alert(
        db: AsyncSession,
        budget_id: str,
        org_id: str,
        alert_type: str,
        severity: str,
        actual_spend: float,
        budget_amount: float,
        message: str,
        **kwargs
    ) -> BudgetAlert:
        """Create a budget alert."""
        alert = BudgetAlert(
            id=str(uuid.uuid4()),
            budget_id=budget_id,
            org_id=org_id,
            alert_type=alert_type,
            severity=severity,
            actual_spend=actual_spend,
            budget_amount=budget_amount,
            message=message,
            **kwargs
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert
