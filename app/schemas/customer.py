import uuid
from pydantic import BaseModel, field_validator, EmailStr
from .validators import sanitize_html, validate_phone

# Base has loose types so legacy DB data won't crash on GET requests
class CustomerBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None

class CustomerCreate(CustomerBase):
    email: EmailStr | None = None

    @field_validator("name", "address", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str | None) -> str | None:
        return sanitize_html(v)

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        return validate_phone(v)

class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None

    @field_validator("name", "address", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str | None) -> str | None:
        return sanitize_html(v)

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        return validate_phone(v)

class CustomerResponse(CustomerBase):
    id: uuid.UUID
    org_id: uuid.UUID
    is_active: bool = True

    model_config = {"from_attributes": True}
