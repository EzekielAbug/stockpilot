import re
import uuid
from pydantic import BaseModel, field_validator

class SupplierBase(BaseModel):
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if not v:
            return v
        if not re.match(r"^\+?[0-9]{7,15}$", re.sub(r"[\s\-\(\)]", "", v)):
            raise ValueError("Invalid phone number format")
        return v

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
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

class SupplierResponse(SupplierBase):
    id: uuid.UUID
    org_id: uuid.UUID
    is_active: bool = True

    model_config = {"from_attributes": True}
