"""
API v1 routes
"""
from fastapi import APIRouter
from app.api.v1 import resume, status, job_matching

router = APIRouter()

router.include_router(resume.router, prefix="/resumes", tags=["resumes"])
router.include_router(status.router, prefix="/resumes", tags=["status"])
router.include_router(job_matching.router, prefix="/resumes", tags=["job-matching"])
