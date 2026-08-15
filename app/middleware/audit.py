"""Audit Logging Middleware (Custom API Route)."""

from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask

from app.core.security import decode_token
from app.services.audit_service import log_audit_event


class AuditRoute(APIRoute):
    """A custom route class that intercepts requests and logs them."""
    
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            req_body = None
            try:
                req_body = await request.body()
            except Exception:
                pass
                
            response = await original_route_handler(request)
            
            if request.method in ["POST", "PUT", "PATCH", "DELETE"] and 200 <= response.status_code < 300:
                
                user_id = None
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    try:
                        token = auth_header.split(" ")[1]
                        payload = decode_token(token)
                        if payload:
                            user_id = payload.get("sub")
                    except Exception:
                        pass
                
                if user_id:
                    ip = request.client.host if request.client else "unknown"
                    user_agent = request.headers.get("user-agent", "unknown")
                    
                    response.background = BackgroundTask(
                        log_audit_event,
                        user_id=user_id,
                        action=request.method,
                        path=request.url.path,
                        payload=req_body,
                        ip=ip,
                        user_agent=user_agent
                    )
                    
            return response
        return custom_route_handler