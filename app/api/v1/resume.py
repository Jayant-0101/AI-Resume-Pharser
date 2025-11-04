"""
Resume API endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.resume_service import ResumeService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service lazily to avoid blocking on import
_resume_service = None

def get_resume_service():
    """Get resume service instance (lazy initialization)"""
    global _resume_service
    if _resume_service is None:
        _resume_service = ResumeService()
    return _resume_service

resume_service = None  # Will be initialized on first use


class ResumeResponse(BaseModel):
    """Resume response model - matches standardized JSON structure"""
    success: bool = True
    resume_id: int = None
    id: str = None  # UUID
    metadata: dict = None
    personalInfo: dict = None
    summary: dict = None
    experience: list = None
    education: list = None
    skills: dict = None
    certifications: list = None
    aiEnhancements: dict = None
    parsed_data: dict = None
    confidence_score: float = None
    processing_time: float = None
    file_info: dict = None
    error: str = None
    
    class Config:
        extra = "allow"  # Allow extra fields


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a resume file
    
    Supports multiple formats:
    - PDF (.pdf)
    - Word documents (.doc, .docx)
    - Text files (.txt)
    - Images (.png, .jpg, .jpeg) with OCR
    
    Returns parsed resume data with structured information.
    """
    try:
        # Validate file size (max 10MB)
        file_content = await file.read()
        from app.services.document_processor import MAX_FILE_SIZE
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {MAX_FILE_SIZE / (1024*1024):.1f}MB limit"
            )
        
        # Process resume
        service = get_resume_service()
        result = service.process_resume(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            db=db
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to process resume")
            )
        
        # Return the result directly (don't force it into ResumeResponse model)
        # This allows all fields to pass through
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{resume_id}", status_code=status.HTTP_200_OK)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get parsed resume data by ID
    
    Returns complete resume information including:
    - Personal information
    - Work experience
    - Education
    - Skills
    - Summary and additional details
    """
    service = get_resume_service()
    resume = service.get_resume(resume_id, db)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )
    
    return resume


@router.get("/", status_code=status.HTTP_200_OK)
async def list_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all resumes with pagination
    
    Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    """
    if limit > 1000:
        limit = 1000
    
    service = get_resume_service()
    return service.list_resumes(skip=skip, limit=limit, db=db)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a resume by ID
    """
    from app.db.models import Resume, ParsedResumeData
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} not found"
        )
    
    # Delete parsed data first
    db.query(ParsedResumeData).filter(
        ParsedResumeData.resume_id == resume_id
    ).delete()
    
    # Delete resume
    db.delete(resume)
    db.commit()
    
    return None


@router.post("/{resume_id}/match", status_code=status.HTTP_200_OK)
async def match_resume_to_job(
    resume_id: int,
    job_description: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Match resume to job description with AI-powered relevancy scoring
    
    Body should contain job_description as JSON string.
    
    Example:
    ```json
    {
      "job_description": "We are looking for a Python developer with 5+ years experience..."
    }
    ```
    
    Returns detailed matching scores including skill match, experience match, 
    education match, and semantic similarity.
    """
    try:
        service = get_resume_service()
        result = service.match_resume_to_job(resume_id, job_description, db)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        return {
            "resume_id": resume_id,
            "matching_results": result,
            "match_summary": result.get("match_summary", "Analysis complete")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error matching resume: {str(e)}"
        )


@router.get("/{resume_id}/anonymized", status_code=status.HTTP_200_OK)
async def get_anonymized_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Get anonymized version of resume (PII removed)
    
    Returns resume data with personally identifiable information removed
    for bias-free screening.
    """
    try:
        service = get_resume_service()
        result = service.get_anonymized_resume(resume_id, db)
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting anonymized resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/health/check", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "resume-parser-api",
        "version": "1.0.0"
    }

