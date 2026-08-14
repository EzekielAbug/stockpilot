"""InventoryItem model - tracker"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

class InventoryItem(BaseModel):
    """Stock level for specific prod
    
    Attributes: quantity, min_stock_level, max_stock_level,
    last_restocked, product_id, warehouse_id
    """

    __tablename__ = "inventory_items"
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    min_stock_level: Mapped[int] = mapped_column(
        Integer,
        default=10,        # Default alert threshold
        nullable=False,
    )
    max_stock_level: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,     # Max capacity is optional
    )
    last_restocked: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # FKeys
    
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id"),
        nullable=False,
    )
    # relationships 

    product: Mapped["Product"] = relationship(
        back_populates="inventory_items",
    )
    warehouse: Mapped["Warehouse"] = relationship(
        back_populates="inventory_items",
    )
    def __repr__(self) -> str:
        return f"InventoryItem(product_id='{self.product_id}', qty={self.quantity})"