"""Order and OrderItem models

cycle: draft - confirmed - processing - shipped - delivered
        |        |                                     |
    cancelled  cancelled                            returned
    """
import uuid
from enum import Enum
from typing import Optional
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel
class OrderStatus(str, Enum):
    """Order lifecycle states."""
    DRAFT = "draft"             
    CONFIRMED = "confirmed"      
    PROCESSING = "processing"    
    SHIPPED = "shipped"          
    DELIVERED = "delivered"      
    CANCELLED = "cancelled"      
    RETURNED = "returned"        
class OrderType(str, Enum):
    """Type of order."""
    PURCHASE = "purchase"    
    SALE = "sale"            
class Order(BaseModel):
    """A purchase or sales order.
    Attributes: order_number, order_type, status, notes, total_amount,
    org_id, created_by_id
    """
    __tablename__ = "orders"
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    order_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=OrderStatus.DRAFT.value,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0,
    )
    # ─── Foreign Keys ───
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    # ─── Relationships ───
    organization: Mapped["Organization"] = relationship(
        back_populates="orders",
    )
    created_by_user: Mapped["User"] = relationship(
        back_populates="orders",
    )
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",  # Delete items when order is deleted
    )
    def __repr__(self) -> str:
        return f"Order(number='{self.order_number}', status='{self.status}')"
class OrderItem(BaseModel):
    """A single line item within an order.

    Attributes: quantity, unit_price, total_price, order_id,
    product_id
    """

    __tablename__ = "order_items"
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    total_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    # ─── Foreign Keys ───
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
    )
    # ─── Relationships ───
    order: Mapped["Order"] = relationship(
        back_populates="items",
    )
    product: Mapped["Product"] = relationship(
        back_populates="order_items",
    )
    def __repr__(self) -> str:
        return f"OrderItem(qty={self.quantity}, unit_price={self.unit_price})"