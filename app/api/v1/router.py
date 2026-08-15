"""API v1 router"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.orders import router as order_router
from app.api.v1.products import router as products_router
from app.api.v1.uploads import router as uploads_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)

api_v1_router.include_router(products_router)

api_v1_router.include_router(inventory_router)

api_v1_router.include_router(order_router)

api_v1_router.include_router(dashboard_router)

api_v1_router.include_router(uploads_router)