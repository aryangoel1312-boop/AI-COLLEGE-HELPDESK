from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import ChatRequest, ChatResponse
from app.services.ai_service import generate_answer
from app.routers.auth import get_current_student


router = APIRouter(
    prefix="/chat",
    tags=["AI Chatbot"]
)


@router.post(
    "/",
    response_model=ChatResponse
)
def chat(
    chat_request: ChatRequest,
    current_student: models.Student = Depends(
        get_current_student
    ),
    db: Session = Depends(get_db)
):

    answer = generate_answer(
        db,
        chat_request.question
    )

    chat_message = models.ChatMessage(
        student_id=current_student.id,
        question=chat_request.question,
        answer=answer
    )

    db.add(chat_message)
    db.commit()

    return {
        "question": chat_request.question,
        "answer": answer
    }