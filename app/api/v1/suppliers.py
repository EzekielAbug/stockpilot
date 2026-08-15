from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.deps import RoleChecker, get_current_active_user
from app.database import get_db
from app.models.user import User, UserRole
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(tags=["CRM - Suppliers"])

@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    supplier = Supplier(**data.model_dump(), org_id=current_user.org_id)
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier

@router.post("/suppliers/bulk-import")
async def bulk_import_suppliers(
    data: list[SupplierCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    """Import multiple suppliers from CSV."""
    created_count = 0
    for item in data:
        supplier = Supplier(**item.model_dump(), org_id=current_user.org_id)
        db.add(supplier)
        created_count += 1
    await db.commit()
    return {"message": f"Successfully imported {created_count} suppliers."}

@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Supplier).where(
        Supplier.org_id == current_user.org_id,
        Supplier.is_active == True
    )
    result = await db.execute(query)
    return list(result.scalars().all())

@router.patch("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: uuid.UUID,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    query = select(Supplier).where(
        Supplier.id == supplier_id, 
        Supplier.org_id == current_user.org_id
    )
    result = await db.execute(query)
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supplier, key, value)
        
    await db.commit()
    await db.refresh(supplier)
    return supplier

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    query = select(Supplier).where(
        Supplier.id == supplier_id, 
        Supplier.org_id == current_user.org_id
    )
    result = await db.execute(query)
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
        
    # Soft delete
    supplier.is_active = False
    await db.commit()
    return None
