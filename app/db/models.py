"""
Database models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.sql import func
from app.db.database import Base


class Resume(Base):
    """Resume model"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Parsed data
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Metadata
    processing_time = Column(Float, nullable=True)
    status = Column(String(50), default="pending")


class ParsedResumeData(Base):
    """Structured parsed resume data"""
    __tablename__ = "parsed_resume_data"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, nullable=False, index=True)
    
    # Personal Information
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    github = Column(String(255), nullable=True)
    
    # Experience
    experience = Column(JSON, nullable=True)  # List of experience objects
    total_years_experience = Column(Float, nullable=True)
    
    # Education
    education = Column(JSON, nullable=True)  # List of education objects
    
    # Skills
    skills = Column(JSON, nullable=True)  # List of skills
    
    # Additional
    summary = Column(Text, nullable=True)
    certifications = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)
    
    # Metadata
    parsed_date = Column(DateTime(timezone=True), server_default=func.now())
    extraction_confidence = Column(Float, nullable=True)

