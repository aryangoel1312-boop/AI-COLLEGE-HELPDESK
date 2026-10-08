from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import StudentCreate, StudentResponse


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=StudentResponse)
def register_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    existing_student = crud.get_student_by_email(
        db,
        student.email
    )

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return crud.create_student(db, student)