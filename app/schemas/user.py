"""Pydantic schema for user data"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """User data return in API response"""

    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    org_id: uuid.UUID
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }