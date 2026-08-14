"""User with role-based access"""

import uuid
from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class UserRole(str, Enum):
    """Available user roles for RBAC
    
    OWNER - ADMIN - MANAGER - STAFF - VIEWER
    """
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"

class User(BaseModel):
    """User account in the system
    
    Attributes: email, hashed_pass, full_name, role, is_active, org_id
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        default=UserRole.STAFF.value,
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
        back_populates="users",
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="created_by_user",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user",
    )

    def __repr__(self) -> str:
        return f"User(email='{self.email}', role='{self.role}')"



    
