from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from app.dependencies.auth import get_db
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UnifiedRegisterRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user via Supabase Auth",
)
def register(data: UnifiedRegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register_user(db, data)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate user via Supabase Auth",
)
def login(data: LoginRequest, db: Session = Depends(get_db), response: Response = None):
    result = auth_service.login_user(db, data)
    
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,       
        secure=False,     
        samesite="lax",
        max_age=3600,       
    )
    
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 3600, 
    )
    
    return result

@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    summary="Rotate Supabase refresh token",
)
def refresh(data: TokenRefreshRequest):
    return auth_service.rotate_refresh_token(data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke session in Supabase Auth",
)
def logout():
    auth_service.revoke_token()
    return {"message": "Logged out successfully"}