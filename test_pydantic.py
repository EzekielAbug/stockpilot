from pydantic import BaseModel, Field, ValidationError
from typing import Optional

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    price: float = Field(ge=0)

print("Test 1: Omitted SKU")
try:
    p1 = ProductCreate.model_validate({"name": "Test", "price": 10.99})
    print("Success:", p1)
except ValidationError as e:
    print("Validation Error:", e.json())

print("\nTest 2: Empty string SKU")
try:
    p2 = ProductCreate.model_validate({"name": "Test", "sku": "", "price": 10.99})
    print("Success:", p2)
except ValidationError as e:
    print("Validation Error:", e.json())
