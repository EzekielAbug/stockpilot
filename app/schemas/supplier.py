import uuid
from pydantic import BaseModel, field_validator, EmailStr
from .validators import sanitize_html, validate_phone

class SupplierBase(BaseModel):
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None

class SupplierCreate(SupplierBase):
    email: EmailStr | None = None

    @field_validator("name", "contact_name", "address", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str | None) -> str | None:
        return sanitize_html(v)

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        return validate_phone(v)

class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None

    @field_validator("name", "contact_name", "address", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str | None) -> str | None:
        return sanitize_html(v)

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        return validate_phone(v)

class SupplierResponse(SupplierBase):
    id: uuid.UUID
    org_id: uuid.UUID
    is_active: bool = True

    model_config = {"from_attributes": True}
