"""Service for saving Audit Logs to the database."""

import json
import uuid

from app.database import async_session_factory
from app.models.audit_log import AuditLog


async def log_audit_event(
    user_id: str,
    action: str,
    path: str,
    payload: bytes,
    ip: str,
    user_agent: str
):
    """Background task that actually writes the log to the database."""
    
    parts = [p for p in path.split("/") if p]
    resource_type = parts[2] if len(parts) >= 3 else path
    resource_id = parts[3] if len(parts) >= 4 else "new"
    changes = None
    if payload:
        try:
            changes = json.loads(payload)
        except json.JSONDecodeError:
            pass

    async with async_session_factory() as db:
        try:
            audit_log = AuditLog(
                user_id=uuid.UUID(user_id),
                action=action, 
                resource_type=resource_type,
                resource_id=resource_id,
                changes=changes,
                ip_address=ip,
                user_agent=user_agent
            )
            db.add(audit_log)
            await db.commit()
            
        except Exception as e:
            print(f"Failed to save audit log: {e}")
