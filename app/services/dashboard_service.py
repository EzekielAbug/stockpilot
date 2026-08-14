"""Business logic for calculating Analytics and KPIs."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem
from app.models.order import Order, OrderStatus, OrderType
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.dashboard import KPIStats, LowStockAlert


async def get_kpi_stats(db: AsyncSession, org_id: uuid.UUID) -> KPIStats:
    """Calculate Total Revenue and Order Count for Sales."""
    
    valid_statuses = [
        OrderStatus.CONFIRMED.value, 
        OrderStatus.PROCESSING.value, 
        OrderStatus.SHIPPED.value, 
        OrderStatus.DELIVERED.value
    ]
    
    query = select(
        func.sum(Order.total_amount).label("total_revenue"),
        func.count(Order.id).label("total_orders")
    ).where(
        Order.org_id == org_id,
        Order.order_type == OrderType.SALE.value,
        Order.status.in_(valid_statuses)
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        return KPIStats(total_revenue=0.0, total_orders=0, average_order_value=0.0)
        
    total_revenue = float(row.total_revenue or 0.0)
    total_orders = int(row.total_orders or 0)
    
    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    
    return KPIStats(
        total_revenue=total_revenue,
        total_orders=total_orders,
        average_order_value=round(aov, 2)
    )
async def get_low_stock_alerts(db: AsyncSession, org_id: uuid.UUID) -> list[LowStockAlert]:
    """Find all inventory items that are at or below their minimum stock level."""

    query = select(
        Product.name.label("product_name"),
        Warehouse.name.label("warehouse_name"),
        InventoryItem.quantity,
        InventoryItem.min_stock_level
    ).join(
        Product, InventoryItem.product_id == Product.id
    ).join(
        Warehouse, InventoryItem.warehouse_id == Warehouse.id
    ).where(
        Product.org_id == org_id,
        InventoryItem.quantity <= InventoryItem.min_stock_level
    )
    
    result = await db.execute(query)
    
    alerts = []
    for row in result:
        alerts.append(LowStockAlert(
            product_name=row.product_name,
            warehouse_name=row.warehouse_name,
            quantity=row.quantity,
            min_stock_level=row.min_stock_level
        ))
        
    return alerts