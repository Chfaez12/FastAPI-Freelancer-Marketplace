import hashlib
import secrets
import bcrypt
from fastapi import HTTPException,status
from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings
from app.core.supabase_client import supabase

def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_random_token() -> str:
    return secrets.token_urlsafe(64)

def verify_supabase_token(token: str) -> dict:

    try:
        response = supabase.auth.get_user(token)

        if hasattr(response, 'user'):
            user = response.user
        else:
            user = response

        if not user or not hasattr(user, 'id'):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")

        return {
            "sub": str(user.id),
            "email": getattr(user, 'email', None),
            "user_metadata": getattr(user, 'user_metadata', {}) or {}
        }

    except HTTPException:
        raise
    except Exception as e:
       
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )



def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode.update({
        "exp": expire,
        "aud": "authenticated",  
    })

    secret = settings.SUPABASE_JWT_SECRET
    algorithm = getattr(settings, "JWT_ALGORITHM", "HS256")
    if algorithm.startswith("ES") or algorithm.startswith("RS"):
        algorithm = "HS256"

    return jwt.encode(to_encode, secret, algorithm=algorithm)