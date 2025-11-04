"""
Resume processing service with enhanced features
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.document_processor import DocumentProcessor, MAX_FILE_SIZE
from app.services.ai_parser import AIParser
from app.services.enhanced_parser import EnhancedParser
from app.services.classification_service import ClassificationService
from app.services.llm_service import LLMService
from app.services.matching_service import MatchingService
from app.services.bias_detection_service import BiasDetectionService
from app.services.anonymization_service import AnonymizationService
from app.services.response_formatter import ResponseFormatter
from app.db.models import Resume, ParsedResumeData

logger = logging.getLogger(__name__)


class ResumeService:
    """Service for processing resumes with advanced AI capabilities"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        # Initialize Enhanced parser (high accuracy) with fallback to basic parser
        try:
            self.ai_parser = EnhancedParser()
            logger.info("Enhanced parser initialized for high accuracy (>85%)")
        except Exception as e:
            logger.warning(f"Enhanced parser initialization failed: {e}, falling back to basic parser")
            try:
                self.ai_parser = AIParser()
            except Exception as e2:
                logger.warning(f"AI Parser initialization had issues: {e2}, continuing with basic mode")
                self.ai_parser = AIParser()  # Will still work without models
        
        self.classifier = ClassificationService()
        
        # Initialize LLM service (lazy loading, won't block)
        try:
            self.llm_service = LLMService()
        except Exception as e:
            logger.warning(f"LLM service initialization had issues: {e}")
            self.llm_service = None
        
        # Initialize matching service (lazy loading)
        try:
            self.matching_service = MatchingService()
        except Exception as e:
            logger.warning(f"Matching service initialization had issues: {e}")
            self.matching_service = MatchingService()  # Will work without embeddings
        
        self.bias_detector = BiasDetectionService()
        self.anonymizer = AnonymizationService()
    
    def process_resume(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Process a resume file and extract structured data
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type
            db: Database session
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract text from document with validation
            logger.info(f"Extracting text from {filename}")
            text, error, file_info = self.document_processor.process_document(
                file_content, filename, content_type
            )
            
            
            if error:
                return {
                    "success": False,
                    "error": error,
                    "processing_time": time.time() - start_time,
                    "file_info": file_info if 'file_info' in locals() else {}
                }
            
            if not text or len(text.strip()) < 50:
                return {
                    "success": False,
                    "error": "Could not extract sufficient text from document",
                    "processing_time": time.time() - start_time,
                    "file_info": file_info if 'file_info' in locals() else {}
                }
            
            # Step 2: Save raw resume to database
            resume_record = Resume(
                filename=filename,
                file_type=content_type,
                file_size=len(file_content),
                raw_text=text,
                status="processing"
            )
            db.add(resume_record)
            db.commit()
            db.refresh(resume_record)
            
            # Step 3: Parse with AI
            logger.info(f"Parsing resume with AI for {filename}")
            parse_start = time.time()
            parsed_data = self.ai_parser.parse(text)
            parse_time = time.time() - parse_start
            
            # Ensure confidence_score exists
            if "confidence_score" not in parsed_data or parsed_data.get("confidence_score") is None:
                logger.warning("Confidence score not calculated by parser, calculating now...")
                # Calculate it if missing
                if hasattr(self.ai_parser, '_calculate_confidence_enhanced'):
                    parsed_data["confidence_score"] = self.ai_parser._calculate_confidence_enhanced(parsed_data)
                elif hasattr(self.ai_parser, '_calculate_confidence'):
                    parsed_data["confidence_score"] = self.ai_parser._calculate_confidence(parsed_data)
                else:
                    parsed_data["confidence_score"] = 0.0
            
            confidence = parsed_data.get("confidence_score", 0.0)
            logger.info(f"Parsing completed in {parse_time:.2f}s with confidence {confidence:.1f}%")
            logger.debug(f"Parsed data summary: name={bool(parsed_data.get('personal_info', {}).get('full_name'))}, email={bool(parsed_data.get('personal_info', {}).get('email'))}, exp_count={len(parsed_data.get('experience', []))}, edu_count={len(parsed_data.get('education', []))}, skills_count={len(parsed_data.get('skills', []))}")
            
            # Step 4: AI Enhancement - Classification and Enrichment
            logger.info(f"Applying AI classification and enrichment")
            enhanced_data = self._apply_ai_enhancement(parsed_data)
            parsed_data.update(enhanced_data)
            
            # Step 5: Advanced AI Features - LLM, Bias Detection, Anonymization
            logger.info(f"Applying advanced AI features")
            advanced_features = self._apply_advanced_ai_features(parsed_data, text)
            parsed_data.update(advanced_features)
            
            # Step 6: Save parsed data
            resume_record.parsed_data = parsed_data
            resume_record.confidence_score = parsed_data.get("confidence_score", 0.0)
            resume_record.status = "completed"
            total_processing_time = time.time() - start_time
            resume_record.processing_time = total_processing_time
            logger.info(f"Total processing time: {total_processing_time:.2f}s, Confidence: {resume_record.confidence_score:.1f}%")
            
            db.commit()
            
            # Step 5: Save structured data
            personal_info = parsed_data.get("personal_info", {})
            parsed_resume = ParsedResumeData(
                resume_id=resume_record.id,
                full_name=personal_info.get("full_name"),
                email=personal_info.get("email"),
                phone=personal_info.get("phone"),
                location=personal_info.get("location"),
                linkedin=personal_info.get("linkedin"),
                github=personal_info.get("github"),
                experience=parsed_data.get("experience"),
                education=parsed_data.get("education"),
                skills=parsed_data.get("skills"),
                summary=parsed_data.get("summary"),
                certifications=parsed_data.get("certifications"),
                languages=parsed_data.get("languages"),
                extraction_confidence=parsed_data.get("confidence_score", 0.0)
            )
            
            # Calculate total years of experience
            if parsed_data.get("experience"):
                parsed_resume.total_years_experience = self._calculate_total_years(
                    parsed_data.get("experience")
                )
            
            db.add(parsed_resume)
            db.commit()
            
            # Format response using ResponseFormatter
            final_processing_time = time.time() - start_time
            uploaded_at = resume_record.upload_date if hasattr(resume_record, 'upload_date') else datetime.utcnow()
            formatted_response = ResponseFormatter.format_resume_response(
                parsed_data=parsed_data,
                file_info=file_info,
                resume_id=resume_record.id,
                processing_time=final_processing_time,
                uploaded_at=uploaded_at,
                processed_at=datetime.utcnow()
            )
            
            
            # Ensure confidence_score is a valid number
            confidence = parsed_data.get("confidence_score", 0.0)
            if confidence is None:
                confidence = 0.0
            confidence = float(confidence)
            
            # Ensure processing_time is a valid number
            if final_processing_time is None:
                final_processing_time = 0.0
            final_processing_time = float(final_processing_time)
            
            logger.info(f"Response prepared: Confidence={confidence:.1f}%, Processing Time={final_processing_time:.2f}s")
            
            # Build result with all necessary data
            result = {
                "success": True,
                "resume_id": resume_record.id,
                "parsed_data": parsed_data,  # Include raw parsed data for UI compatibility
                "confidence_score": confidence,
                "processing_time": final_processing_time,
                **formatted_response  # Unpack the formatted response
            }
            
            # Include file_info in the response
            result['file_info'] = file_info if file_info else {}
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}", exc_info=True)
            db.rollback()
            return {
                "success": False,
                "error": f"Error processing resume: {str(e)}",
                "processing_time": time.time() - start_time
            }
    
    def _calculate_total_years(self, experience: list) -> Optional[float]:
        """Calculate total years of experience from experience list"""
        if not experience:
            return 0.0
        return self.classifier.calculate_implied_experience(experience)
    
    def _apply_ai_enhancement(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply AI classification and data enrichment
        
        Args:
            parsed_data: Parsed resume data
            
        Returns:
            Dictionary with enhancement data
        """
        enhancement = {}
        
        try:
            # Extract job titles and companies
            experience_items = parsed_data.get("experience", [])
            job_titles = [exp.get("title", "") for exp in experience_items if exp.get("title")]
            companies = [exp.get("company", "") for exp in experience_items if exp.get("company")]
            descriptions = [exp.get("description", "") for exp in experience_items if exp.get("description")]
            
            # Classify job role
            if job_titles:
                role_classification = self.classifier.classify_job_role(job_titles, descriptions)
                enhancement["role_classification"] = role_classification
            
            # Assess seniority level
            total_years = self._calculate_total_years(experience_items)
            seniority = self.classifier.assess_seniority_level(job_titles, total_years)
            enhancement["seniority"] = seniority
            
            # Classify industry
            if companies:
                industry = self.classifier.classify_industry(companies, descriptions)
                enhancement["industry"] = industry
            
            # Score skill relevance
            skills = parsed_data.get("skills", [])
            if skills and job_titles:
                primary_role = enhancement.get("role_classification", {}).get("primary_role", "other")
                scored_skills = self.classifier.score_skill_relevance(skills, primary_role)
                enhancement["skill_relevance"] = scored_skills
            
            # Standardize skills
            if skills:
                standardized_skills = [self.classifier.standardize_skill(skill) for skill in skills]
                enhancement["standardized_skills"] = standardized_skills
            
            # Enrich company information
            enriched_companies = []
            for company in companies:
                if company:
                    company_info = self.classifier.enrich_company_info(company)
                    enriched_companies.append(company_info)
            enhancement["company_enrichment"] = enriched_companies
            
            # Calculate implied experience
            enhancement["implied_experience_years"] = total_years
            
            return {
                "classification": {
                    "job_role": enhancement.get("role_classification", {}),
                    "seniority": enhancement.get("seniority", {}),
                    "industry": enhancement.get("industry", {})
                },
                "enhancement": {
                    "skill_relevance": enhancement.get("skill_relevance", []),
                    "standardized_skills": enhancement.get("standardized_skills", []),
                    "company_info": enhancement.get("company_enrichment", []),
                    "experience_years": enhancement.get("implied_experience_years", 0.0)
                }
            }
        except Exception as e:
            logger.error(f"Error applying AI enhancement: {e}", exc_info=True)
            return {
                "classification": {},
                "enhancement": {}
            }
    
    def _apply_advanced_ai_features(self, parsed_data: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
        """
        Apply advanced AI features: LLM, bias detection, anonymization
        
        Args:
            parsed_data: Parsed resume data
            resume_text: Raw resume text
            
        Returns:
            Dictionary with advanced AI features
        """
        advanced_features = {}
        
        try:
            # 1. LLM Insights (only if service is available)
            if self.llm_service and hasattr(self.llm_service, 'is_available') and self.llm_service.is_available():
                try:
                    logger.info("Generating LLM insights")
                    llm_insights = self.llm_service.extract_insights(parsed_data)
                    llm_analysis = self.llm_service.analyze_context(resume_text[:2000] if resume_text else "")
                    advanced_features["llm_insights"] = {
                        "insights": llm_insights,
                        "context_analysis": llm_analysis,
                        "summary": llm_analysis.get("summary")
                    }
                except Exception as e:
                    logger.warning(f"LLM insights generation failed: {e}")
                    advanced_features["llm_insights"] = {
                        "available": False,
                        "note": "LLM insights unavailable"
                    }
            else:
                advanced_features["llm_insights"] = {
                    "available": False,
                    "note": "LLM service not available (models loading on demand)"
                }
            
            # 2. Bias Detection
            logger.info("Detecting potential biases")
            bias_detection = self.bias_detector.detect_bias(parsed_data, resume_text)
            advanced_features["bias_detection"] = bias_detection
            
            # 3. Anonymization Report
            logger.info("Generating anonymization report")
            anonymization_report = self.anonymizer.get_anonymization_report(parsed_data, resume_text)
            advanced_features["anonymization"] = {
                "report": anonymization_report,
                "anonymized_version": None  # Generate on demand
            }
            
        except Exception as e:
            logger.error(f"Error applying advanced AI features: {e}", exc_info=True)
            advanced_features = {
                "llm_insights": {},
                "bias_detection": {},
                "anonymization": {}
            }
        
        return advanced_features
    
    def match_resume_to_job(self, resume_id: int, job_description: str, db: Session) -> Dict[str, Any]:
        """
        Match resume to job description
        
        Args:
            resume_id: Resume ID
            job_description: Job description text
            db: Database session
            
        Returns:
            Matching scores and analysis
        """
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return {"error": "Resume not found"}
        
        parsed_data = resume.parsed_data or {}
        if not self.matching_service:
            return {"error": "Matching service not available"}
        
        try:
            return self.matching_service.calculate_relevancy_score(parsed_data, job_description)
        except Exception as e:
            logger.error(f"Error in matching: {e}")
            return {"error": f"Matching failed: {str(e)}"}
    
    def get_anonymized_resume(self, resume_id: int, db: Session) -> Dict[str, Any]:
        """
        Get anonymized version of resume
        
        Args:
            resume_id: Resume ID
            db: Database session
            
        Returns:
            Anonymized resume data
        """
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return {"error": "Resume not found"}
        
        parsed_data = resume.parsed_data or {}
        anonymized_text = resume.raw_text or ""
        
        return self.anonymizer.create_anonymized_version(parsed_data, anonymized_text)
    
    def get_resume(self, resume_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Get resume by ID"""
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return None
        
        parsed_data = db.query(ParsedResumeData).filter(
            ParsedResumeData.resume_id == resume_id
        ).first()
        
        result = {
            "id": resume.id,
            "filename": resume.filename,
            "file_type": resume.file_type,
            "upload_date": resume.upload_date.isoformat() if resume.upload_date else None,
            "status": resume.status,
            "confidence_score": resume.confidence_score,
            "processing_time": resume.processing_time,
            "parsed_data": resume.parsed_data
        }
        
        if parsed_data:
            result["structured_data"] = {
                "full_name": parsed_data.full_name,
                "email": parsed_data.email,
                "phone": parsed_data.phone,
                "location": parsed_data.location,
                "linkedin": parsed_data.linkedin,
                "github": parsed_data.github,
                "experience": parsed_data.experience,
                "education": parsed_data.education,
                "skills": parsed_data.skills,
                "summary": parsed_data.summary,
                "certifications": parsed_data.certifications,
                "languages": parsed_data.languages,
                "total_years_experience": parsed_data.total_years_experience
            }
        
        return result
    
    def list_resumes(
        self,
        skip: int = 0,
        limit: int = 100,
        db: Session = None
    ) -> Dict[str, Any]:
        """List all resumes with pagination"""
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
                    "file_type": r.file_type,
                    "upload_date": r.upload_date.isoformat() if r.upload_date else None,
                    "status": r.status,
                    "confidence_score": r.confidence_score
                }
                for r in resumes
            ]
        }

