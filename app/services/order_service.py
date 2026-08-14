"""Business logic for Orders (Pricing, State Machine, Inventory Deduction)."""

import secrets
import uuid
from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory import InventoryItem
from app.models.order import Order, OrderItem, OrderStatus, OrderType
from app.models.product import Product
from app.schemas.order import OrderCreate


async def create_order(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, data: OrderCreate
) -> Order:
    """Create a new DRAFT order and calculate pricing."""
    
    order_number = f"ORD-{secrets.token_hex(4).upper()}"
    
    order = Order(
        order_number=order_number,
        order_type=data.order_type.value,
        status=OrderStatus.DRAFT.value, 
        notes=data.notes,
        total_amount=0, 
        org_id=org_id,
        created_by_id=user_id,
    )
    db.add(order)
    await db.flush()
    
    total = 0
    
    for item_data in data.items:
        prod_result = await db.execute(
            select(Product).where(Product.id == item_data.product_id, Product.org_id == org_id)
        )
        product = prod_result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found.")
            
        unit_price = product.price
        total_price = unit_price * item_data.quantity
        total += total_price
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )
        db.add(order_item)
        
    order.total_amount = total
    await db.commit()
    
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
    )
    return result.scalar_one()

async def get_orders(db: AsyncSession, org_id: uuid.UUID) -> Sequence[Order]:
    """Get all orders for an organization, including their items."""
    
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.org_id == org_id)
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()

async def confirm_order(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID) -> Order:
    """State Machine: Move order from DRAFT to CONFIRMED and deduct inventory."""
    
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id, Order.org_id == org_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
        
    if order.status != OrderStatus.DRAFT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot confirm order. Current status is {order.status}."
        )
        
    if order.order_type == OrderType.SALE.value:
        for item in order.items:
            inv_result = await db.execute(
                select(InventoryItem).where(
                    InventoryItem.product_id == item.product_id,
                    InventoryItem.quantity >= item.quantity
                )
            )
            inventory = inv_result.scalars().first()
            
            if not inventory:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Insufficient stock across all warehouses for product {item.product_id}."
                )

            inventory.quantity = InventoryItem.quantity - item.quantity
            
    order.status = OrderStatus.CONFIRMED.value
    await db.commit()
    
    return order