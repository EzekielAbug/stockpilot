"""Pydantic schemas for Dashboard Analytics."""

from pydantic import BaseModel


class KPIStats(BaseModel):
    total_revenue: float
    total_orders: int
    average_order_value: float

class LowStockAlert(BaseModel):
    product_name: str
    warehouse_name: str
    quantity: int
    min_stock_level: int

class ChartData(BaseModel):
    date: str
    revenue: float
    orders: int

class DashboardResponse(BaseModel):
    """The master schema that combines all dashboard sections."""
    kpis: KPIStats
    low_stock_alerts: list[LowStockAlert]
    chart_data: list[ChartData]
