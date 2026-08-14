"""WH model - physical loc"""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

class Warehouse(BaseModel):
    """Physical storage location
    
    Attributes: name, location, is_active, org_id
    """
    __tablename__ = "warehouses"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    location: Mapped[Optional[str]] = mapped_column(
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

    # relationship

    organization: Mapped["Organization"] = relationship(
        back_populates="warehouses",
    )
    inventory_items: Mapped[list["InventoryItem"]] = relationship(
        back_populates="warehouse",
    )

    def __repr__(self) -> str:
        return f"Warehouse(name='{self.name}')"
