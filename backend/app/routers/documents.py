from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException
)

from sqlalchemy.orm import Session

from pathlib import Path
import shutil
import json

from app.database import get_db
from app import models

from app.routers.admin_auth import get_current_admin

from app.services.document_service import (
    extract_text_from_pdf,
    split_text_into_chunks
)

from app.services.embedding_service import (
    generate_embedding
)


router = APIRouter(
    prefix="/documents",
    tags=["College Documents"]
)


UPLOAD_DIR = Path("data/documents")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("/upload")
def upload_document(

    title: str = Form(...),

    file: UploadFile = File(...),

    current_admin: models.Admin = Depends(
        get_current_admin
    ),

    db: Session = Depends(get_db)
):

    # -----------------------------------------
    # Validate file type
    # -----------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was selected."
        )


    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )


    # -----------------------------------------
    # Validate document title
    # -----------------------------------------

    title = title.strip()

    if not title:

        raise HTTPException(
            status_code=400,
            detail="Document title is required."
        )


    # -----------------------------------------
    # Create safe file name
    # -----------------------------------------

    safe_file_name = Path(
        file.filename
    ).name


    file_path = (
        UPLOAD_DIR /
        safe_file_name
    )


    # -----------------------------------------
    # Save uploaded PDF
    # -----------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=(
                "Unable to save the uploaded file: "
                + str(error)
            )
        )


    # -----------------------------------------
    # Extract PDF text
    # -----------------------------------------

    try:

        extracted_text = (
            extract_text_from_pdf(
                str(file_path)
            )
        )

    except Exception as error:

        # Remove invalid uploaded file

        if file_path.exists():

            file_path.unlink()

        raise HTTPException(

            status_code=400,

            detail=(
                "Unable to read the PDF file: "
                + str(error)
            )
        )


    # -----------------------------------------
    # Check extracted content
    # -----------------------------------------

    if not extracted_text.strip():

        if file_path.exists():

            file_path.unlink()

        raise HTTPException(

            status_code=400,

            detail=(
                "The PDF does not contain readable text."
            )
        )


    # -----------------------------------------
    # Create document record
    # -----------------------------------------

    document = models.CollegeDocument(

        title=title,

        file_name=safe_file_name,

        file_path=str(file_path),

        content=extracted_text
    )


    db.add(document)

    db.commit()

    db.refresh(document)


    # -----------------------------------------
    # Split document into chunks
    # -----------------------------------------

    chunks = split_text_into_chunks(
        extracted_text
    )


    # -----------------------------------------
    # Generate lightweight embeddings
    # -----------------------------------------

    for index, chunk in enumerate(chunks):

        embedding = generate_embedding(
            chunk
        )


        document_chunk = models.DocumentChunk(

            document_id=document.id,

            chunk_index=index,

            content=chunk,

            embedding=json.dumps(
                embedding
            )
        )


        db.add(document_chunk)


    db.commit()


    # -----------------------------------------
    # Return upload result
    # -----------------------------------------

    return {

        "message": (
            "Document uploaded, "
            "text extracted, "
            "chunks created, "
            "and embeddings generated successfully"
        ),

        "document_id":
            document.id,

        "title":
            document.title,

        "file_name":
            document.file_name,

        "text_length":
            len(extracted_text),

        "chunks_created":
            len(chunks)
    }