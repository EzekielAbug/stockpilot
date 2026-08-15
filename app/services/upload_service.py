"""AWS S3 Upload service with validation and local-dev mocking."""

import uuid
from typing import Optional

import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import HTTPException, UploadFile, status

from app.config import settings

# Initialize the AWS S3

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)
# Security Constants
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 Megabytes
async def upload_image(file: UploadFile) -> str:
    """Validates an image and uploads it to S3, returning the public URL."""
    
    # 1. Validate File Type (Security)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only JPEG, PNG, and WEBP are allowed."
        )
        
    # 2. Validate File Size (Security)
    # We read the file into memory to check its exact size
    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="File too large. Maximum size is 5MB."
        )
        
    # 3. Generate a secure, unique filename (e.g. e4d909c2... .png)
    # We NEVER use the user's original filename, as it might contain malicious scripts
    extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    
    # 4. Upload to S3 (With Local Dev Mocking)
    if not settings.AWS_ACCESS_KEY_ID:
        # Because we don't have AWS keys yet, we simulate a successful upload!
        # We return a real, working placeholder image so your frontend UI doesn't look broken!
        print(f"⚠️ LOCAL DEV: Simulating upload of {unique_filename} to S3...")
        return f"https://ui-avatars.com/api/?name=Product&background=random&size=128"
        
    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=unique_filename,
            Body=contents,
            ContentType=file.content_type
        )
        return f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
        
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not configured.")
def get_presigned_url(filename: str) -> str:
    """Generates a temporary, secure URL to download a private file (like an invoice)."""
    
    if not settings.AWS_ACCESS_KEY_ID:
        return f"https://mock-presigned-url.com/download/{filename}"
        
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": filename},
        ExpiresIn=3600 # URL expires in 1 hour
    )
    return url