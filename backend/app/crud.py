from sqlalchemy.orm import Session
import bcrypt

from app import models
from app.schemas import StudentCreate


def create_student(db: Session, student: StudentCreate):
    hashed_password = bcrypt.hashpw(
        student.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    db_student = models.Student(
        name=student.name,
        email=student.email,
        password=hashed_password,
        department=student.department
    )

    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student


def get_student_by_email(db: Session, email: str):
    return (
        db.query(models.Student)
        .filter(models.Student.email == email)
        .first()
    )