"""Celery tasks for email operations."""

import asyncio

from app.services.email_service import send_welcome_email
from app.workers.celery_app import celery_app


@celery_app.task(name="send_welcome_email_task")
def send_welcome_email_task(email: str, name: str):
    """Background task to send a welcome email."""
    
    asyncio.run(send_welcome_email(email, name))
    
    return f"Welcome email processed for {email}"