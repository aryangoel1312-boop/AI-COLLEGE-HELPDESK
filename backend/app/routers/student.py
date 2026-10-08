from fastapi import APIRouter, Depends

from app import models
from app.routers.auth import get_current_student


router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@router.get("/profile")
def get_student_profile(
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
    