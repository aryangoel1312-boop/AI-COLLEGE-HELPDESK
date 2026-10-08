from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    name: str
    email: str
    password: str
    department: str | None = None


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    department: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentLogin(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    message: str
    student: StudentResponse


class TicketCreate(BaseModel):
    subject: str
    description: str
    category: str | None = None


class TicketResponse(BaseModel):
    id: int
    student_id: int
    subject: str
    description: str
    category: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str