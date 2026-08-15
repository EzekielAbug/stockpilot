"""API endpoints for the Analytics Dashboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.cache import get_cache, set_cache
from app.database import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DashboardResponse:
    """Get the full dashboard data, cached for 5 minutes to prevent DB overload."""
    
    cache_key = f"dashboard_data:{current_user.org_id}"
    
    cached_data = await get_cache(cache_key)
    if cached_data:
        return DashboardResponse(**cached_data)
        
    kpis = await dashboard_service.get_kpi_stats(db, current_user.org_id)
    alerts = await dashboard_service.get_low_stock_alerts(db, current_user.org_id)
    chart_data = await dashboard_service.get_chart_data(db, current_user.org_id)
    
    response_data = DashboardResponse(kpis=kpis, low_stock_alerts=alerts, chart_data=chart_data)

    await set_cache(cache_key, response_data.model_dump(), expire_seconds=300)
    
    return response_data