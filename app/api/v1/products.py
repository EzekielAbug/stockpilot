"""API endpoints for Categories and Products."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker, get_current_active_user
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.product import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductResponse,
)
from app.services import product_service

router = APIRouter(tags=["Catalog"])

write_role = RoleChecker(UserRole.MANAGER)

# CATEGORIES

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(write_role),
) -> CategoryResponse:
    """Create a new category."""
    return await product_service.create_category(db, current_user.org_id, data)

@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[CategoryResponse]:
    """List all categories for the organization."""
    return list(await product_service.get_categories(db, current_user.org_id))

# PRODUCTS

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(write_role),
) -> ProductResponse:
    """Create a new product."""
    return await product_service.create_product(db, current_user.org_id, data)

@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def list_products(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[ProductResponse]:
    """List products with pagination and optional search."""
    
    items, total = await product_service.get_products(
        db=db, 
        org_id=current_user.org_id, 
        page=page, 
        size=size, 
        search=search
    )
    
    import math
    pages = math.ceil(total / size) if total > 0 else 1
    return PaginatedResponse(
        items=list(items),
        total=total,
        page=page,
        size=size,
        pages=pages,
    )

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProductResponse:
    """Get a specific product by its ID."""
    return await product_service.get_product_by_id(db, current_user.org_id, product_id)