from datetime import datetime, timedelta, timezone
import os

import bcrypt
import jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, models
from app.schemas import (
    StudentCreate,
    StudentResponse,
    StudentLogin
)


# =========================================
# ROUTER
# =========================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================================
# JWT CONFIGURATION
# =========================================

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "change-this-secret-before-production"
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


security = HTTPBearer()


# =========================================
# CREATE JWT TOKEN
# =========================================

def create_access_token(
    student_id: int
) -> str:

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(student_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# =========================================
# GET CURRENT STUDENT
# =========================================

def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db)
):
    """
    Read the JWT access token and return
    the authenticated student.
    """

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        student_id = payload.get("sub")

        if student_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
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

        student_id = int(student_id)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=401,
            detail="Invalid student identity"
        )


    student = (
        db.query(models.Student)
        .filter(
            models.Student.id == student_id
        )
        .first()
    )


    if not student:

        raise HTTPException(
            status_code=401,
            detail="Student account not found"
        )


    return student


# =========================================
# REGISTER
# =========================================

@router.post(
    "/register",
    response_model=StudentResponse
)
def register_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):

    # Check whether email already exists

    existing_student = crud.get_student_by_email(
        db,
        student.email
    )


    if existing_student:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # Create student account

    return crud.create_student(
        db,
        student
    )


# =========================================
# LOGIN
# =========================================

@router.post("/login")
def login_student(
    login_data: StudentLogin,
    db: Session = Depends(get_db)
):

    # Find student

    student = crud.get_student_by_email(
        db,
        login_data.email
    )


    if not student:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    # Verify password

    password_valid = bcrypt.checkpw(
        login_data.password.encode("utf-8"),
        student.password.encode("utf-8")
    )


    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    # Create JWT token

    access_token = create_access_token(
        student.id
    )


    # Return token + student information

    return {
        "message": "Login successful",

        "access_token": access_token,

        "token_type": "bearer",

        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "department": student.department,
            "created_at": student.created_at
        }
    }


# =========================================
# CURRENT STUDENT
# =========================================

@router.get("/me")
def get_current_student_profile(
    current_student: models.Student = Depends(
        get_current_student
    )
):

    return {
        "id": current_student.id,
        "name": current_student.name,
        "email": current_student.email,
        "department": current_student.department,
        "created_at": current_student.created_at
    }