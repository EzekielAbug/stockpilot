"""Business logic and database operations for catalog management."""

import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.schemas.product import CategoryCreate, ProductCreate, ProductUpdate


async def create_category(
    db: AsyncSession, org_id: uuid.UUID, data: CategoryCreate
) -> Category:
    """Create a new category for an organization."""

    category = Category(
        name=data.name,
        description=data.description,
        parent_id=data.parent_id,
        org_id=org_id,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

async def get_categories(
    db: AsyncSession, org_id: uuid.UUID
) -> Sequence[Category]:
    """Get all categories for an organization."""
    result = await db.execute(
        select(Category).where(Category.org_id == org_id)
    )
    return result.scalars().all()

async def create_product(
    db: AsyncSession, org_id: uuid.UUID, data: ProductCreate
) -> Product:
    """Create a new product, ensuring the SKU is unique within the org."""
    
    existing = await db.execute(
        select(Product).where(
            Product.org_id == org_id, 
            Product.sku == data.sku
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{data.sku}' already exists.",
        )
    
    if data.category_id:
        cat = await db.execute(
            select(Category).where(
                Category.id == data.category_id,
                Category.org_id == org_id
            )
        )
        if not cat.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
    
    product = Product(
        name=data.name,
        sku=data.sku,
        description=data.description,
        price=data.price,
        cost_price=data.cost_price,
        image_url=data.image_url,
        category_id=data.category_id,
        is_active=data.is_active,
        org_id=org_id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

async def get_products(
    db: AsyncSession, 
    org_id: uuid.UUID, 
    page: int = 1, 
    size: int = 50,
    search: str | None = None,
) -> tuple[Sequence[Product], int]:
    """Get a paginated list of products, optionally filtered by search."""
    
    query = select(Product).where(Product.org_id == org_id)
    count_query = select(func.count()).where(Product.org_id == org_id)
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.where(Product.name.ilike(search_term) | Product.sku.ilike(search_term))
        count_query = count_query.where(Product.name.ilike(search_term) | Product.sku.ilike(search_term))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    query = query.offset((page - 1) * size).limit(size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    return items, total

async def get_product_by_id(
    db: AsyncSession, org_id: uuid.UUID, product_id: uuid.UUID
) -> Product:
    """Get a single product by ID."""
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.org_id == org_id
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )
    return product