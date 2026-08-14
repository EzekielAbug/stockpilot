"""Pydantic schemas for Orders and Line Items."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus, OrderType


# ORDER ITEMS
class OrderItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0, description="Must be greater than 0")

class OrderItemResponse(OrderItemBase):
    id: uuid.UUID
    unit_price: float
    total_price: float
    model_config = ConfigDict(from_attributes=True)

# ORDERS

class OrderCreate(BaseModel):
    order_type: OrderType
    notes: Optional[str] = None
    items: list[OrderItemBase] = Field(min_length=1)
    
class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    order_type: OrderType
    status: OrderStatus
    total_amount: float
    notes: Optional[str]
    org_id: uuid.UUID
    created_by_id: uuid.UUID
    created_at: datetime
    items: list[OrderItemResponse]
    model_config = ConfigDict(from_attributes=True)