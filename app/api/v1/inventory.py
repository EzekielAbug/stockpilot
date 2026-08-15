"""API endpoints for Warehouses and Inventory."""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker, get_current_active_user
from app.core.cache import invalidate_cache
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.inventory import (
    InventoryItemResponse,
    StockAdjustment,
    WarehouseCreate,
    WarehouseResponse,
)
from app.services import inventory_service

router = APIRouter(tags=["Inventory"])

# Permissions

admin_role = RoleChecker(UserRole.ADMIN)
manager_role = RoleChecker(UserRole.MANAGER)
staff_role = RoleChecker(UserRole.STAFF)

# WAREHOUSES

@router.post("/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    data: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_role), # Only admins can create warehouses
) -> WarehouseResponse:
    """Create a new warehouse location."""
    return await inventory_service.create_warehouse(db, current_user.org_id, data)

@router.post("/warehouses/bulk-import")
async def bulk_import_warehouses(
    data: list[WarehouseCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_role),
):
    """Import multiple warehouses from CSV."""
    created_count = 0
    for item in data:
        await inventory_service.create_warehouse(db, current_user.org_id, item)
        created_count += 1
    return {"message": f"Successfully imported {created_count} warehouses."}

@router.get("/warehouses", response_model=list[WarehouseResponse])
async def list_warehouses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[WarehouseResponse]:
    """List all warehouses for the organization."""
    
    return list(await inventory_service.get_warehouses(db, current_user.org_id))

@router.patch("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: uuid.UUID,
    data: WarehouseCreate, # Using Create for simplicity, fields are optional in Update
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_role),
) -> WarehouseResponse:
    """Update a warehouse location."""
    return await inventory_service.update_warehouse(db, current_user.org_id, warehouse_id, data)

@router.delete("/warehouses/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_role),
) -> None:
    """Soft delete a warehouse location."""
    await inventory_service.delete_warehouse(db, current_user.org_id, warehouse_id)

# INVENTORY 

@router.post("/inventory/adjust", response_model=InventoryItemResponse)
async def adjust_stock(
    data: StockAdjustment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(staff_role), # Staff and above can adjust stock
) -> InventoryItemResponse:
    """Add or remove stock for a product in a specific warehouse."""
    result = await inventory_service.adjust_stock(db, current_user.org_id, data)
    await invalidate_cache(f"dashboard_data:{current_user.org_id}")
    return result

@router.get("/products/{product_id}/inventory", response_model=list[InventoryItemResponse])
async def get_product_stock(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[InventoryItemResponse]:
    """View stock levels for a specific product across all warehouses."""

    return list(await inventory_service.get_inventory_for_product(db, product_id))
