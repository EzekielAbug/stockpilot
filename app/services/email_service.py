"""Email sending service."""

import asyncio


async def send_welcome_email(email: str, name: str) -> bool:
    """Simulates sending a welcome email to a new user."""
    
    print(f"📧 Connecting to SMTP server to email {email}...")
    
    await asyncio.sleep(2.0)
    
    print(f"SUCCESS: Welcome email sent to {name} ({email})!")
    return True
