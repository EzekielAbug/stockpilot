"""API endpoints for Orders."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.audit import AuditRoute

from app.api.deps import RoleChecker, get_current_active_user
from app.core.rate_limit import RateLimiter
from app.core.cache import invalidate_cache
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderResponse
from app.services import order_service

router = APIRouter(tags=["Orders"], route_class=AuditRoute)
manager_role = RoleChecker(UserRole.MANAGER)

@router.post(
    "/orders", 
    response_model=OrderResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(requests=10, window_seconds=60))] # SECURITY: Max 10 orders per minute
)

async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(manager_role),
) -> OrderResponse:
    
    """Create a new DRAFT order."""

    return await order_service.create_order(db, current_user.org_id, current_user.id, data)

@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[OrderResponse]:
    """List all orders for the organization."""

    return list(await order_service.get_orders(db, current_user.org_id))

@router.post("/orders/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(manager_role),
) -> OrderResponse:
    """Confirm a DRAFT order. If it's a SALE, this deducts inventory."""
    
    order = await order_service.confirm_order(db, current_user.org_id, order_id)
    await invalidate_cache(f"dashboard_data:{current_user.org_id}")
    return order