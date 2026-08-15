"""Org model - multi-tenant container

Every piece of data belongs to an organization.
"""

import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

class Organization(BaseModel):
    """Business or a Company using this
    
    Attributes: name, slug, plan_tier, is_active
    """
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    plan_tier: Mapped[str] = mapped_column(
        String(50),
        default="free",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )

# relationships (navigate between objs)

    users: Mapped[list["User"]] = relationship (
        back_populates="organization",
    )
    products: Mapped[list["Product"]] = relationship (
        back_populates="organization",
    )
    categories: Mapped[list["Category"]] = relationship (
        back_populates="organization",
    )
    warehouses: Mapped[list["Warehouse"]] = relationship (
        back_populates="organization",
    )
    orders: Mapped[list["Order"]] = relationship (
        back_populates="organization",
    )
    suppliers: Mapped[list["Supplier"]] = relationship (
        back_populates="organization",
    )
    customers: Mapped[list["Customer"]] = relationship (
        back_populates="organization",
    )
    def __repr__(self) -> str:
        return f"Organization(name='{self.name}', slug='{self.slug}')"