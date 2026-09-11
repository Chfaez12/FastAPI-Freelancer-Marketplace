from fastapi import APIRouter, Depends, HTTPException, status, Response,Cookie, Header
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
    summary="Rotate Supabase refresh token and update HttpOnly cookies",
)
def refresh(
    response: Response,
    data: TokenRefreshRequest = None,
    refresh_token: str | None = Cookie(None),
):
    token_to_use = data.refresh_token if (data and data.refresh_token) else refresh_token
    if not token_to_use:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing from cookie and request body.",
        )

    tokens = auth_service.rotate_refresh_token(token_to_use)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=False,  
        samesite="lax",
        max_age=3600,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=False,  
        samesite="lax",
        max_age=7 * 24 * 3600,
    )

    return tokens

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke session in Supabase Auth and clear HttpOnly cookies",
)
def logout(
    response: Response,
    access_token: str | None = Cookie(None),
    authorization: str | None = Header(None),
):
    token = access_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    auth_service.revoke_token(token)

    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}