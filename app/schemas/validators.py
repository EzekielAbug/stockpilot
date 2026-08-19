import re
import phonenumbers
from typing import Any

def sanitize_html(value: Any) -> Any:
    """Strips HTML tags from strings to prevent basic XSS."""
    if isinstance(value, str):
        # Remove any HTML tags
        sanitized = re.sub(r'<[^>]+>', '', value)
        return sanitized.strip()
    return value

def validate_phone(value: Any) -> Any:
    """Validates international phone numbers using Google's phonenumbers library."""
    if not value or not isinstance(value, str):
        return value
    try:
        # Parse the phone number, assume it has a country code (+xx)
        parsed_number = phonenumbers.parse(value)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Invalid phone number")
        # Format to strict E164 international standard (+639123456789)
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        raise ValueError("Invalid phone number format. Must include country code.")
