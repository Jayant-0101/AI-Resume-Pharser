"""
Job Matching API endpoints
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.resume_service import ResumeService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy initialization
_resume_service_instance = None

def get_service():
    global _resume_service_instance
    if _resume_service_instance is None:
        _resume_service_instance = ResumeService()
    return _resume_service_instance


class JobDescription(BaseModel):
    """Job description model"""
    job_description: str
    job_title: str = None
    required_skills: list = None
    required_experience_years: int = None


@router.post("/match/{resume_id}", status_code=status.HTTP_200_OK)
async def match_resume(
    resume_id: int,
    job: JobDescription,
    db: Session = Depends(get_db)
):
    """
    Match a resume to a job description with AI-powered relevancy scoring
    
    Returns detailed matching scores including:
    - Overall relevancy score (0-1.0)
    - Skill matching score
    - Experience matching score
    - Education matching score
    - Title matching score
    - Semantic similarity score
    - Detailed breakdown and recommendations
    """
    try:
        service = get_service()
        result = service.match_resume_to_job(
            resume_id,
            job.job_description,
            db
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return {
            "resume_id": resume_id,
            "job_title": job.job_title,
            "job_description_preview": job.job_description[:200] + "..." if len(job.job_description) > 200 else job.job_description,
            "matching_results": result,
            "recommendation": result.get("match_summary", "Match analysis complete")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error matching resume: {str(e)}"
        )

