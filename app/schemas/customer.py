import re
import uuid
from pydantic import BaseModel, field_validator

class CustomerBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if not v:
            return v
        # Basic E.164 standard or minimum digits (at least 7, max 15, optional +)
        if not re.match(r"^\+?[0-9]{7,15}$", re.sub(r"[\s\-\(\)]", "", v)):
            raise ValueError("Invalid phone number format")
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if not v:
            return v
        if not re.match(r"^\+?[0-9]{7,15}$", re.sub(r"[\s\-\(\)]", "", v)):
            raise ValueError("Invalid phone number format")
        return v

class CustomerResponse(CustomerBase):
    id: uuid.UUID
    org_id: uuid.UUID
    is_active: bool = True

    model_config = {"from_attributes": True}
