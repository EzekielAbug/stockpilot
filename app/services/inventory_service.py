"""Business logic and database operations for inventory management."""

import uuid
from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory import StockAdjustment, WarehouseCreate

# WAREHOUSES

async def create_warehouse(
    db: AsyncSession, org_id: uuid.UUID, data: WarehouseCreate
) -> Warehouse:
    """Create a new warehouse for an organization."""
    warehouse = Warehouse(
        name=data.name,
        location=data.location,
        is_active=data.is_active,
        org_id=org_id,
    )
    db.add(warehouse)
    await db.commit()
    await db.refresh(warehouse)
    return warehouse

async def get_warehouses(
    db: AsyncSession, org_id: uuid.UUID
) -> Sequence[Warehouse]:
    """Get all warehouses for an organization."""
    result = await db.execute(
        select(Warehouse).where(Warehouse.org_id == org_id)
    )
    return result.scalars().all()

async def get_warehouse_by_id(
    db: AsyncSession, org_id: uuid.UUID, warehouse_id: uuid.UUID
) -> Warehouse:
    """Get a single warehouse by ID."""
    result = await db.execute(
        select(Warehouse).where(
            Warehouse.id == warehouse_id,
            Warehouse.org_id == org_id
        )
    )
    wh = result.scalar_one_or_none()
    if not wh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found.",
        )
    return wh

async def update_warehouse(
    db: AsyncSession, org_id: uuid.UUID, warehouse_id: uuid.UUID, data: WarehouseCreate
) -> Warehouse:
    """Update an existing warehouse."""
    wh = await get_warehouse_by_id(db, org_id, warehouse_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(wh, key, value)
        
    await db.commit()
    await db.refresh(wh)
    return wh

async def delete_warehouse(
    db: AsyncSession, org_id: uuid.UUID, warehouse_id: uuid.UUID
) -> None:
    """Soft delete a warehouse."""
    wh = await get_warehouse_by_id(db, org_id, warehouse_id)
    wh.is_active = False
    await db.commit()

# INVENTORY 

async def adjust_stock(
    db: AsyncSession, org_id: uuid.UUID, data: StockAdjustment
) -> InventoryItem:
    """Safely adjust stock levels (add or remove)."""
    
    prod = await db.execute(
        select(Product).where(Product.id == data.product_id, Product.org_id == org_id)
    )
    if not prod.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found.")
    
    wh = await db.execute(
        select(Warehouse).where(Warehouse.id == data.warehouse_id, Warehouse.org_id == org_id)
    )
    if not wh.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Warehouse not found.")
    
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.product_id == data.product_id,
            InventoryItem.warehouse_id == data.warehouse_id
        )
    )
    item = result.scalar_one_or_none()
    if item is None:

        if data.quantity_change < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove stock from empty warehouse.",
            )
            
        item = InventoryItem(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            quantity=data.quantity_change,
            min_stock_level=data.min_stock_level,
            max_stock_level=data.max_stock_level,
            last_restocked=datetime.now(timezone.utc) if data.quantity_change > 0 else None
        )
        db.add(item)
    else:
        if item.quantity + data.quantity_change < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock. Current quantity: {item.quantity}",
            )
            
        item.quantity = InventoryItem.quantity + data.quantity_change
        

        if data.quantity_change > 0:
            item.last_restocked = datetime.now(timezone.utc)
            
    await db.commit()
    await db.refresh(item)
    return item

async def get_inventory_for_product(
    db: AsyncSession, product_id: uuid.UUID
) -> Sequence[InventoryItem]:
    """Get stock levels across all warehouses for a specific product."""
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.product_id == product_id)
    )
    return result.scalars().all()