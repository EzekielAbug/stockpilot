"""Base model with common fields shared by all database tables.

Every model in StockPilot inherits from this base, which
provides:
- UUID primary key
- created_at timestamp
- updated_at timestamp

This follows the DRY principles: Don't Repeat Yourself!!
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models. 

    All db inherits from this
    """
    pass

class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class BaseModel(Base, TimestampMixin):
    """Abstract base model with UUID primary key and timestamps"""

    __abstract__= True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )