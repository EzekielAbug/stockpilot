"""Pydantic schemas for Categories and Products."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from .validators import sanitize_html

# CATEGORY

class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None

class CategoryCreate(CategoryBase):
    @field_validator("name", "description", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str | None) -> str | None:
        return sanitize_html(v)

class CategoryResponse(CategoryBase):
    id: uuid.UUID
    org_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# PRODUCT

class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: float = Field(ge=0)  # Greater than or equal to 0
    cost_price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    is_active: bool = True

class ProductCreate(ProductBase):
    @field_validator("name", "sku", "description", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str | None) -> str | None:
        return sanitize_html(v)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None

    @field_validator("name", "description", mode="before")
    @classmethod
    def sanitize_fields(cls, v: str | None) -> str | None:
        return sanitize_html(v)
    
class ProductResponse(ProductBase):
    id: uuid.UUID
    org_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)