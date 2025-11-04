"""
Resume processing status endpoints
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Resume

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{resume_id}/status", status_code=status.HTTP_200_OK)
async def get_processing_status(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get real-time processing status of a resume
    
    Returns:
    - status: pending, processing, completed, failed
    - progress: 0-100 percentage
    - message: Current processing stage
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )
    
    # Determine progress based on status
    progress = 0
    message = ""
    
    if resume.status == "pending":
        progress = 0
        message = "File uploaded, waiting to process"
    elif resume.status == "processing":
        progress = 50
        message = "Extracting and parsing resume data"
    elif resume.status == "completed":
        progress = 100
        message = "Processing completed successfully"
    elif resume.status == "failed":
        progress = 0
        message = "Processing failed"
    else:
        progress = 0
        message = "Unknown status"
    
    return {
        "resume_id": resume.id,
        "status": resume.status,
        "progress": progress,
        "message": message,
        "filename": resume.filename,
        "upload_date": resume.upload_date.isoformat() if resume.upload_date else None,
        "processing_time": resume.processing_time,
        "confidence_score": resume.confidence_score
    }


@router.get("/status/list", status_code=status.HTTP_200_OK)
async def list_all_statuses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all resumes with their processing status
    """
    total = db.query(Resume).count()
    resumes = db.query(Resume).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "resumes": [
            {
                "id": r.id,
                "filename": r.filename,
                "status": r.status,
                "upload_date": r.upload_date.isoformat() if r.upload_date else None,
                "confidence_score": r.confidence_score
            }
            for r in resumes
        ]
    }



