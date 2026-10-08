from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routers import (
    auth,
    student,
    tickets,
    chat,
    documents,
    admin_auth
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI College Help Desk",
    description="AI-powered college support system",
    version="1.0.0"
)


# Allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(student.router)
app.include_router(tickets.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(admin_auth.router)


@app.get("/")
def home():
    return {
        "message": "AI College Help Desk API is running"
    }