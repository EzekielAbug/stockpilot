"""Product model - item being tracked (SKU)"""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

class Product(BaseModel):
    """Product in catalog
    
    Attributes: name, sku, description, price, cost_price, 
    image_url, is_active, org_id, category_id
    """
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    cost_price: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )

    # Fkey

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
    )

    # relationship

    organization: Mapped["Organization"] = relationship(
            back_populates="products",
    )
    category: Mapped[Optional["Category"]] = relationship(
            back_populates="products",
    )
    inventory_items: Mapped[list["InventoryItem"]] = relationship(
            back_populates="product",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
            back_populates="product",
    )
    
    def __repr__(self) -> str:
        return f"Product(name='{self.name}', sku='{self.sku}')"