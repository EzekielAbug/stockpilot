"""AuditLog - tracks every change made in the system"""

import uuid
from typing import Optional
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class AuditLog(BaseModel):
    """Record of a single action performed
    
    Attributes: action, resource_type, resource_id, changes,
    ip_address, user_agent, user_id
    """

    __tablename__ = "audit_logs"
    action: Mapped[str] = mapped_column(
        String(20),        # CREATE, UPDATE, DELETE
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(
        String(50),        # "product", "order", "user", etc.
        nullable=False,
        index=True,
    )
    resource_id: Mapped[str] = mapped_column(
        String(50),        # The UUID of the affected record (stored as string)
        nullable=False,
    )
    changes: Mapped[Optional[dict]] = mapped_column(
        JSON,              # Stores the before/after diff as JSON
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),        # Supports both IPv4 and IPv6
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    # ─── Foreign Key ───
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    # ─── Relationships ───
    user: Mapped["User"] = relationship(
        back_populates="audit_logs",
    )
    def __repr__(self) -> str:
        return f"AuditLog(action='{self.action}', resource='{self.resource_type}')"
