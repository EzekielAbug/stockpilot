"""Pydantic schemas for Warehouses and Inventory tracking."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# WAREHOUSE

class WarehouseBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: Optional[str] = None
    is_active: bool = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseResponse(WarehouseBase):
    id: uuid.UUID
    org_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# INVENTORY ITEM

class StockAdjustment(BaseModel):
    """Schema for adding or removing stock."""
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity_change: int = Field(
        description="Positive to add stock, negative to remove stock"
    )

    min_stock_level: Optional[int] = Field(10, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    
class InventoryItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    quantity: int
    min_stock_level: int
    max_stock_level: Optional[int]
    last_restocked: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)