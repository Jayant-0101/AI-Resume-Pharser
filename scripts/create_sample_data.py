"""
Script to create sample resume data for testing
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Resume, ParsedResumeData
from datetime import datetime

def create_sample_data():
    """Create sample resume records"""
    db: Session = SessionLocal()
    
    try:
        # Sample resume 1
        resume1 = Resume(
            filename="john_doe_resume.pdf",
            file_type="application/pdf",
            file_size=245000,
            raw_text="""
            John Doe
            Email: john.doe@example.com
            Phone: +1-234-567-8900
            Location: San Francisco, CA
            LinkedIn: linkedin.com/in/johndoe
            GitHub: github.com/johndoe
            
            SUMMARY
            Experienced software engineer with 5+ years in full-stack development.
            Specialized in Python, FastAPI, and cloud technologies.
            
            EXPERIENCE
            Senior Software Engineer | Tech Corp Inc.
            January 2020 - Present
            • Developed scalable REST APIs using FastAPI
            • Led team of 3 junior developers
            • Implemented CI/CD pipelines
            
            Software Engineer | StartupXYZ
            June 2018 - December 2019
            • Built web applications using Python and Django
            • Optimized database queries, improving performance by 40%
            
            EDUCATION
            Bachelor of Science in Computer Science
            University of California, Berkeley
            Graduated: 2018
            
            SKILLS
            Python, JavaScript, FastAPI, Django, PostgreSQL, AWS, Docker, Kubernetes, Git, Agile
            """,
            parsed_data={
                "personal_info": {
                    "full_name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1-234-567-8900",
                    "location": "San Francisco, CA",
                    "linkedin": "linkedin.com/in/johndoe",
                    "github": "github.com/johndoe"
                },
                "experience": [
                    {
                        "title": "Senior Software Engineer",
                        "company": "Tech Corp Inc.",
                        "start_date": "January 2020",
                        "end_date": "Present",
                        "description": "Developed scalable REST APIs using FastAPI"
                    },
                    {
                        "title": "Software Engineer",
                        "company": "StartupXYZ",
                        "start_date": "June 2018",
                        "end_date": "December 2019",
                        "description": "Built web applications using Python and Django"
                    }
                ],
                "education": [
                    {
                        "degree": "Bachelor of Science in Computer Science",
                        "institution": "University of California, Berkeley",
                        "year": "2018"
                    }
                ],
                "skills": ["Python", "JavaScript", "FastAPI", "Django", "PostgreSQL", "AWS", "Docker"],
                "summary": "Experienced software engineer with 5+ years in full-stack development.",
                "confidence_score": 92.5
            },
            confidence_score=92.5,
            processing_time=2.1,
            status="completed"
        )
        
        db.add(resume1)
        db.commit()
        db.refresh(resume1)
        
        parsed1 = ParsedResumeData(
            resume_id=resume1.id,
            full_name="John Doe",
            email="john.doe@example.com",
            phone="+1-234-567-8900",
            location="San Francisco, CA",
            linkedin="linkedin.com/in/johndoe",
            github="github.com/johndoe",
            experience=resume1.parsed_data["experience"],
            education=resume1.parsed_data["education"],
            skills=resume1.parsed_data["skills"],
            summary=resume1.parsed_data["summary"],
            total_years_experience=5.5,
            extraction_confidence=92.5
        )
        
        db.add(parsed1)
        db.commit()
        
        print(f"✓ Created sample resume 1 (ID: {resume1.id})")
        
        # Sample resume 2
        resume2 = Resume(
            filename="jane_smith_resume.docx",
            file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size=189000,
            raw_text="""
            Jane Smith
            jane.smith@email.com
            (555) 123-4567
            New York, NY
            
            PROFESSIONAL SUMMARY
            Data scientist with expertise in machine learning and statistical analysis.
            
            WORK EXPERIENCE
            Data Scientist | DataCorp
            March 2019 - Present
            • Developed ML models for predictive analytics
            • Used Python, TensorFlow, and scikit-learn
            
            Junior Data Analyst | Analytics Inc.
            July 2017 - February 2019
            • Performed data analysis and visualization
            
            EDUCATION
            Master of Science in Data Science
            Stanford University, 2017
            
            Bachelor of Science in Mathematics
            MIT, 2015
            
            SKILLS
            Python, R, TensorFlow, PyTorch, SQL, Machine Learning, Deep Learning, Statistics
            """,
            parsed_data={
                "personal_info": {
                    "full_name": "Jane Smith",
                    "email": "jane.smith@email.com",
                    "phone": "(555) 123-4567",
                    "location": "New York, NY"
                },
                "experience": [
                    {
                        "title": "Data Scientist",
                        "company": "DataCorp",
                        "start_date": "March 2019",
                        "end_date": "Present"
                    }
                ],
                "education": [
                    {
                        "degree": "Master of Science in Data Science",
                        "institution": "Stanford University",
                        "year": "2017"
                    }
                ],
                "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning"],
                "summary": "Data scientist with expertise in machine learning",
                "confidence_score": 88.0
            },
            confidence_score=88.0,
            processing_time=1.8,
            status="completed"
        )
        
        db.add(resume2)
        db.commit()
        db.refresh(resume2)
        
        parsed2 = ParsedResumeData(
            resume_id=resume2.id,
            full_name="Jane Smith",
            email="jane.smith@email.com",
            phone="(555) 123-4567",
            location="New York, NY",
            experience=resume2.parsed_data["experience"],
            education=resume2.parsed_data["education"],
            skills=resume2.parsed_data["skills"],
            summary=resume2.parsed_data["summary"],
            total_years_experience=4.0,
            extraction_confidence=88.0
        )
        
        db.add(parsed2)
        db.commit()
        
        print(f"✓ Created sample resume 2 (ID: {resume2.id})")
        print("\nSample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()

