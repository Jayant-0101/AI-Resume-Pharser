"""
Resume-Job Matching Service
AI-powered matching between resumes and job descriptions with relevancy scoring
"""
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import transformers for embeddings
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("Transformers not available - matching will use basic keyword matching")


class MatchingService:
    """Service for matching resumes to job descriptions"""
    
    def __init__(self):
        """Initialize matching service"""
        self.embedding_model = None
        self._embedding_model_loaded = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding models for semantic matching (lazy loading)"""
        if not HAS_TRANSFORMERS:
            return
        
        # Don't load on startup - load on demand
        logger.info("Embedding models will load on first use")
        self._embedding_model_loaded = False
    
    def _ensure_embedding_model(self):
        """Ensure embedding model is loaded (lazy loading)"""
        if self._embedding_model_loaded:
            return
        
        if not HAS_TRANSFORMERS:
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self._embedding_model_loaded = True
            logger.info("Embedding model loaded for semantic matching")
        except ImportError:
            logger.warning("sentence-transformers not installed - using basic matching")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e} - using basic matching")
    
    def calculate_relevancy_score(
        self,
        resume_data: Dict[str, Any],
        job_description: str
    ) -> Dict[str, Any]:
        """
        Calculate relevancy score between resume and job description
        
        Args:
            resume_data: Parsed resume data
            job_description: Job description text
            
        Returns:
            Dictionary with matching scores and analysis
        """
        scores = {
            "overall_score": 0.0,
            "skill_match": 0.0,
            "experience_match": 0.0,
            "education_match": 0.0,
            "title_match": 0.0,
            "detailed_scores": {}
        }
        
        try:
            # Extract resume components
            skills = [s.lower() for s in resume_data.get("skills", [])]
            experience = resume_data.get("experience", [])
            education = resume_data.get("education", [])
            job_titles = [exp.get("title", "").lower() for exp in experience if exp.get("title")]
            
            job_desc_lower = job_description.lower()
            
            # 1. Skill Matching (40% weight)
            skill_matches = self._match_skills(skills, job_desc_lower)
            scores["skill_match"] = skill_matches["score"]
            scores["detailed_scores"]["skill_match"] = skill_matches
            
            # 2. Experience Matching (30% weight)
            exp_matches = self._match_experience(experience, job_desc_lower)
            scores["experience_match"] = exp_matches["score"]
            scores["detailed_scores"]["experience_match"] = exp_matches
            
            # 3. Education Matching (15% weight)
            edu_matches = self._match_education(education, job_desc_lower)
            scores["education_match"] = edu_matches["score"]
            scores["detailed_scores"]["education_match"] = edu_matches
            
            # 4. Title Matching (15% weight)
            title_matches = self._match_titles(job_titles, job_desc_lower)
            scores["title_match"] = title_matches["score"]
            scores["detailed_scores"]["title_match"] = title_matches
            
            # Calculate overall weighted score
            scores["overall_score"] = (
                scores["skill_match"] * 0.40 +
                scores["experience_match"] * 0.30 +
                scores["education_match"] * 0.15 +
                scores["title_match"] * 0.15
            )
            
            # Add semantic matching if available (lazy load)
            self._ensure_embedding_model()
            if self.embedding_model:
                semantic_score = self._semantic_match(resume_data, job_description)
                # Blend semantic score with keyword-based score
                scores["semantic_score"] = semantic_score
                scores["overall_score"] = (scores["overall_score"] * 0.7 + semantic_score * 0.3)
            
            # Generate match summary
            scores["match_summary"] = self._generate_match_summary(scores)
            
        except Exception as e:
            logger.error(f"Error calculating relevancy score: {e}")
        
        return scores
    
    def _match_skills(self, resume_skills: List[str], job_desc: str) -> Dict[str, Any]:
        """Match skills between resume and job description"""
        # Extract required skills from job description
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'sql', 'postgresql', 'mongodb', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'git', 'agile', 'scrum', 'ci/cd',
            'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch'
        ]
        
        required_skills = []
        for skill in common_skills:
            if skill in job_desc:
                required_skills.append(skill)
        
        # Calculate match
        matched_skills = [skill for skill in resume_skills if any(req in skill or skill in req for req in required_skills)]
        
        score = len(matched_skills) / max(len(required_skills), 1) if required_skills else 0.0
        score = min(score, 1.0)  # Cap at 1.0
        
        return {
            "score": round(score, 2),
            "matched_skills": matched_skills,
            "required_skills": required_skills,
            "missing_skills": [s for s in required_skills if not any(s in rs or rs in s for rs in matched_skills)]
        }
    
    def _match_experience(self, experience: List[Dict], job_desc: str) -> Dict[str, Any]:
        """Match experience level and relevance"""
        if not experience:
            return {"score": 0.0, "matched_positions": 0, "total_positions": 0}
        
        # Extract experience requirements from job description
        years_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?experience'
        years_match = re.search(years_pattern, job_desc)
        required_years = int(years_match.group(1)) if years_match else 0
        
        # Calculate total experience
        total_years = sum(
            self._calculate_years_from_exp(exp) for exp in experience
        )
        
        # Score based on experience match
        if required_years == 0:
            score = 0.8  # Default if no requirement specified
        else:
            score = min(total_years / required_years, 1.0)
        
        # Check for relevant industry/role keywords
        relevant_keywords = ['engineer', 'developer', 'manager', 'analyst', 'designer']
        relevant_experience = [
            exp for exp in experience
            if any(kw in exp.get("title", "").lower() for kw in relevant_keywords)
        ]
        
        relevance_score = len(relevant_experience) / max(len(experience), 1)
        final_score = (score * 0.6 + relevance_score * 0.4)
        
        return {
            "score": round(final_score, 2),
            "total_years": round(total_years, 1),
            "required_years": required_years,
            "matched_positions": len(relevant_experience),
            "total_positions": len(experience)
        }
    
    def _calculate_years_from_exp(self, exp: Dict) -> float:
        """Calculate years from a single experience entry"""
        start_date = exp.get("start_date", "")
        end_date = exp.get("end_date", "Present")
        
        # Extract years
        start_year = self._extract_year(start_date)
        end_year = self._extract_year(end_date) if end_date != "Present" else datetime.now().year
        
        if start_year and end_year:
            return max(0, end_year - start_year)
        return 1.0  # Default estimate
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
        return int(year_match.group()) if year_match else None
    
    def _match_education(self, education: List[Dict], job_desc: str) -> Dict[str, Any]:
        """Match education requirements"""
        if not education:
            return {"score": 0.0, "matched_degrees": 0}
        
        # Extract education requirements
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'degree']
        required_degree = None
        for keyword in degree_keywords:
            if keyword in job_desc:
                required_degree = keyword
                break
        
        if not required_degree:
            return {"score": 0.8, "matched_degrees": len(education)}  # Default if no requirement
        
        # Check if resume has required degree
        matched = any(
            required_degree in edu.get("degree", "").lower()
            for edu in education
        )
        
        score = 1.0 if matched else 0.3
        
        return {
            "score": score,
            "required_degree": required_degree,
            "matched_degrees": len(education),
            "has_required": matched
        }
    
    def _match_titles(self, job_titles: List[str], job_desc: str) -> Dict[str, Any]:
        """Match job titles"""
        if not job_titles:
            return {"score": 0.0, "matched_titles": []}
        
        # Extract job title from description
        title_keywords = ['engineer', 'developer', 'manager', 'analyst', 'designer', 'architect']
        desc_title_keywords = [kw for kw in title_keywords if kw in job_desc]
        
        matched_titles = [
            title for title in job_titles
            if any(kw in title for kw in desc_title_keywords)
        ]
        
        score = len(matched_titles) / max(len(job_titles), 1)
        
        return {
            "score": round(score, 2),
            "matched_titles": matched_titles,
            "relevant_keywords": desc_title_keywords
        }
    
    def _semantic_match(self, resume_data: Dict, job_desc: str) -> float:
        """Calculate semantic similarity using embeddings"""
        if not self.embedding_model:
            return 0.0
        
        try:
            # Create resume summary
            resume_text = f"{resume_data.get('summary', '')} "
            resume_text += " ".join(resume_data.get("skills", []))
            resume_text += " " + " ".join([exp.get("title", "") for exp in resume_data.get("experience", [])])
            
            # Generate embeddings
            resume_embedding = self.embedding_model.encode(resume_text, convert_to_tensor=True)
            job_embedding = self.embedding_model.encode(job_desc, convert_to_tensor=True)
            
            # Calculate cosine similarity
            from torch.nn.functional import cosine_similarity
            similarity = cosine_similarity(resume_embedding.unsqueeze(0), job_embedding.unsqueeze(0))
            
            return float(similarity.item())
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            return 0.0
    
    def _generate_match_summary(self, scores: Dict) -> str:
        """Generate human-readable match summary"""
        overall = scores.get("overall_score", 0.0)
        
        if overall >= 0.8:
            return "Excellent match - Strong candidate for this position"
        elif overall >= 0.6:
            return "Good match - Candidate meets most requirements"
        elif overall >= 0.4:
            return "Moderate match - Some gaps in requirements"
        else:
            return "Weak match - Significant gaps in requirements"

