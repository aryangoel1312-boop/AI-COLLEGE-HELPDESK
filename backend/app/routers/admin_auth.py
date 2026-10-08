from datetime import datetime, timedelta, timezone
import os

import bcrypt
import jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app import models


router = APIRouter(
    prefix="/admin/auth",
    tags=["Admin Authentication"]
)


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-secret-before-production"
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


security = HTTPBearer()


# ---------------------------------------------------------
# CREATE ADMIN TOKEN
# ---------------------------------------------------------

def create_admin_access_token(
    admin_id: int
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(admin_id),
        "role": "admin",
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# ---------------------------------------------------------
# GET CURRENT ADMIN
# ---------------------------------------------------------

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        admin_id = payload.get("sub")
        role = payload.get("role")

        if admin_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        if role != "admin":

            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Authentication token has expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    try:

        admin_id = int(admin_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=401,
            detail="Invalid admin identity"
        )

    admin = (
        db.query(models.Admin)
        .filter(
            models.Admin.id == admin_id
        )
        .first()
    )

    if not admin:

        raise HTTPException(
            status_code=401,
            detail="Admin account not found"
        )

    return admin


# ---------------------------------------------------------
# ADMIN LOGIN
# ---------------------------------------------------------

@router.post("/login")
def admin_login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    admin = (
        db.query(models.Admin)
        .filter(
            models.Admin.email == email
        )
        .first()
    )

    if not admin:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_valid = bcrypt.checkpw(
        password.encode("utf-8"),
        admin.password.encode("utf-8")
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_admin_access_token(
        admin.id
    )

    return {

        "message": "Admin login successful",

        "access_token": access_token,

        "token_type": "bearer",

        "admin": {

            "id": admin.id,

            "name": admin.name,

            "email": admin.email,

            "created_at": admin.created_at
        }
    }


# ---------------------------------------------------------
# ADMIN PROFILE
# ---------------------------------------------------------

@router.get("/me")
def get_admin_profile(
    current_admin: models.Admin = Depends(
        get_current_admin
    )
):

    return {

        "id": current_admin.id,

        "name": current_admin.name,

        "email": current_admin.email,

        "created_at": current_admin.created_at
    }