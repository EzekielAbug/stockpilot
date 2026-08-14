"""Cat model with self-referential parent-child hierarchy"""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

class Category(BaseModel):
    """Prod cat with optional parent for nesting
    
    Attributes: name, description, org_id, parent_id
    """
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Fkey

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
    )

    # relationship

    organization: Mapped["Organization"] = relationship(
        back_populates="categories",
    )
    parent: Mapped["Category"] = relationship(
        back_populates="children",
        remote_side="Category.id",
    )
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent",
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
    )

    def __repr__(self) -> str:
        return f"Category(name='{self.name}')"