"""Common schemas reused across multiple domains."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")
class PaginatedResponse(BaseModel, Generic[T]):
    """Generic wrapper for paginated lists of data.
    
    Example: PaginatedResponse[ProductResponse]
    """
    items: list[T]
    total: int
    page: int
    size: int
    pages: int