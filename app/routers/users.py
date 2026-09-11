from fastapi import APIRouter, Depends, HTTPException, status,File, UploadFile
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import ChangePasswordRequest, UpdateAccountRequest
from app.services import user_service as auth_service
from app.services.storage_service import delete_supabase_storage_file, upload_file_to_supabase, ALLOWED_IMAGE_TYPES


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserResponse, summary="Get current authenticated user account")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("", response_model=UserResponse, summary="Update permitted account information")
def update_me(
    data: UpdateAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return auth_service.update_account(db, current_user, data)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change account password",
)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_service.change_password(db, current_user, data)
    return {"message": "Password updated successfully"}

@router.delete("", status_code=status.HTTP_200_OK, summary="Delete current authenticated user account")
def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_service.delete_user_account(db, current_user)
    auth_service.revoke_token()
    return {"message": "Account deactivated and deleted successfully"}

@router.post(
    "/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload profile picture for the current authenticated user",
)
def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    upload_meta = upload_file_to_supabase(
        file=file,
        bucket="avatars",
        path_prefix=f"users/{current_user.id}",
        allowed_types=ALLOWED_IMAGE_TYPES,
    )

    current_user.avatar_url = upload_meta["file_url"]
    db.commit()
    db.refresh(current_user)

    return current_user

@router.delete("/avatar", status_code=status.HTTP_200_OK)
def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have an avatar to delete.",
        )

    delete_supabase_storage_file(
        file_url=current_user.avatar_url,
        bucket_name="avatars", 
    )

    current_user.avatar_url = None
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Avatar deleted successfully from storage and database"}