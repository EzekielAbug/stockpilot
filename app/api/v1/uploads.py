"""API endpoints for file uploads."""

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import RoleChecker
from app.models.user import User, UserRole
from app.services import upload_service

router = APIRouter(tags=["Uploads"])

# Only Managers, Admins, and Owners can upload product images

manager_role = RoleChecker(UserRole.MANAGER)

@router.post("/uploads/image")
async def upload_image_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(manager_role),
) -> dict[str, str]:
    """Upload a product image. Returns the secure S3 URL."""
    
    # Pass the file to our service layer
    url = await upload_service.upload_image(file)
    
    return {
        "url": url,
        "filename": file.filename
    }