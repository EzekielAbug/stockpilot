from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.api.deps import RoleChecker, get_current_active_user
from app.database import get_db
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter(tags=["CRM - Customers"])

@router.post("/customers", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    customer = Customer(**data.model_dump(), org_id=current_user.org_id)
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer

@router.post("/customers/bulk-import")
async def bulk_import_customers(
    data: list[CustomerCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    """Import multiple customers from CSV."""
    created_count = 0
    for item in data:
        customer = Customer(**item.model_dump(), org_id=current_user.org_id)
        db.add(customer)
        created_count += 1
    await db.commit()
    return {"message": f"Successfully imported {created_count} customers."}

@router.get("/customers", response_model=list[CustomerResponse])
async def list_customers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Customer).where(
        Customer.org_id == current_user.org_id,
        Customer.is_active == True
    )
    result = await db.execute(query)
    return list(result.scalars().all())

@router.patch("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    query = select(Customer).where(
        Customer.id == customer_id, 
        Customer.org_id == current_user.org_id
    )
    result = await db.execute(query)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(customer, key, value)
        
    await db.commit()
    await db.refresh(customer)
    return customer

@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(UserRole.MANAGER)),
):
    query = select(Customer).where(
        Customer.id == customer_id, 
        Customer.org_id == current_user.org_id
    )
    result = await db.execute(query)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        
    # Soft delete
    customer.is_active = False
    await db.commit()
    return None
