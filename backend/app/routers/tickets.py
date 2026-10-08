from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import TicketCreate, TicketResponse
from app.routers.auth import get_current_student
from app.routers.admin_auth import get_current_admin


router = APIRouter(
    prefix="/tickets",
    tags=["Support Tickets"]
)


def detect_category(
    subject: str,
    description: str
) -> str:

    text = (
        subject + " " + description
    ).lower()


    if any(word in text for word in [
        "wifi",
        "wi-fi",
        "internet",
        "network",
        "computer",
        "login",
        "password",
        "technical"
    ]):

        return "IT Support"


    if any(word in text for word in [
        "fee",
        "fees",
        "payment",
        "refund",
        "accounts",
        "scholarship"
    ]):

        return "Accounts"


    if any(word in text for word in [
        "exam",
        "examination",
        "marks",
        "result",
        "hall ticket",
        "admit card"
    ]):

        return "Examination"


    if any(word in text for word in [
        "admission",
        "admissions",
        "registration",
        "enrollment",
        "enrolment"
    ]):

        return "Admissions"


    if any(word in text for word in [
        "hostel",
        "room",
        "mess",
        "accommodation"
    ]):

        return "Hostel"


    if any(word in text for word in [
        "library",
        "book",
        "books"
    ]):

        return "Library"


    return "General Support"


# --------------------------------------------------
# STUDENT ROUTES
# --------------------------------------------------

@router.post(
    "/",
    response_model=TicketResponse
)
def create_ticket(
    ticket: TicketCreate,

    current_student: models.Student = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)
):

    category = detect_category(
        ticket.subject,
        ticket.description
    )


    db_ticket = models.SupportTicket(

        student_id=current_student.id,

        subject=ticket.subject,

        description=ticket.description,

        category=category,

        status="Pending"
    )


    db.add(db_ticket)

    db.commit()

    db.refresh(db_ticket)


    return db_ticket


@router.get(
    "/",
    response_model=list[TicketResponse]
)
def get_student_tickets(

    current_student: models.Student = Depends(
        get_current_student
    ),

    db: Session = Depends(get_db)
):

    tickets = (

        db.query(
            models.SupportTicket
        )

        .filter(
            models.SupportTicket.student_id ==
            current_student.id
        )

        .order_by(
            models.SupportTicket.created_at.desc()
        )

        .all()
    )


    return tickets


# --------------------------------------------------
# ADMIN ROUTES
# --------------------------------------------------

@router.get(
    "/admin/stats"
)
def get_admin_stats(

    current_admin: models.Admin = Depends(
        get_current_admin
    ),

    db: Session = Depends(get_db)
):

    total_tickets = (
        db.query(
            models.SupportTicket
        ).count()
    )


    pending_tickets = (

        db.query(
            models.SupportTicket
        )

        .filter(
            models.SupportTicket.status ==
            "Pending"
        )

        .count()
    )


    in_progress_tickets = (

        db.query(
            models.SupportTicket
        )

        .filter(
            models.SupportTicket.status ==
            "In Progress"
        )

        .count()
    )


    resolved_tickets = (

        db.query(
            models.SupportTicket
        )

        .filter(
            models.SupportTicket.status ==
            "Resolved"
        )

        .count()
    )


    closed_tickets = (

        db.query(
            models.SupportTicket
        )

        .filter(
            models.SupportTicket.status ==
            "Closed"
        )

        .count()
    )


    total_documents = (

        db.query(
            models.CollegeDocument
        ).count()
    )


    return {

        "total_tickets":
            total_tickets,

        "pending_tickets":
            pending_tickets,

        "in_progress_tickets":
            in_progress_tickets,

        "resolved_tickets":
            resolved_tickets,

        "closed_tickets":
            closed_tickets,

        "total_documents":
            total_documents
    }


@router.get(
    "/admin/all",
    response_model=list[TicketResponse]
)
def get_all_tickets(

    current_admin: models.Admin = Depends(
        get_current_admin
    ),

    db: Session = Depends(get_db)
):

    tickets = (

        db.query(
            models.SupportTicket
        )

        .order_by(
            models.SupportTicket.created_at.desc()
        )

        .all()
    )


    return tickets


@router.put(
    "/admin/{ticket_id}/status"
)
def update_ticket_status(

    ticket_id: int,

    status: str,

    current_admin: models.Admin = Depends(
        get_current_admin
    ),

    db: Session = Depends(get_db)
):

    ticket = (

        db.query(
            models.SupportTicket
        )

        .filter(
            models.SupportTicket.id ==
            ticket_id
        )

        .first()
    )


    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )


    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved",
        "Closed"
    ]


    if status not in allowed_statuses:

        raise HTTPException(

            status_code=400,

            detail=(
                "Invalid status. Use one of: "
                +
                ", ".join(
                    allowed_statuses
                )
            )
        )


    ticket.status = status


    db.commit()

    db.refresh(ticket)


    return {

        "message":
            "Ticket status updated successfully",

        "ticket_id":
            ticket.id,

        "status":
            ticket.status
    }