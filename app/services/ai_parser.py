"""
AI-powered resume parsing using NLP and ML techniques
"""
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import torch

logger = logging.getLogger(__name__)


class AIParser:
    """AI-powered resume parser using NLP and ML"""
    
    def __init__(self):
        """Initialize AI parser with models"""
        self.nlp = None
        self.ner_model = None
        self.tokenizer = None
        self._models_initialized = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize NLP models"""
        try:
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model not found, downloading...")
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")
            
            # Load NER model (using a lightweight model for efficiency)
            # This is optional - we'll use spaCy if this fails
            try:
                model_name = "dslim/bert-base-NER"
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.ner_model = AutoModelForTokenClassification.from_pretrained(model_name)
                logger.info("NER model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load NER model: {str(e)}, using spaCy only")
                self.ner_model = None
                self.tokenizer = None
            
            self._models_initialized = True
                
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            # Don't raise - allow graceful degradation
            if not self.nlp:
                logger.warning("Running without NLP models - accuracy may be reduced")
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured data
        
        Args:
            text: Raw resume text
            
        Returns:
            Dictionary with parsed resume data
        """
        if not text:
            return {}
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Extract different sections
        parsed_data = {
            "personal_info": self._extract_personal_info(cleaned_text),
            "experience": self._extract_experience(cleaned_text),
            "education": self._extract_education(cleaned_text),
            "skills": self._extract_skills(cleaned_text),
            "summary": self._extract_summary(cleaned_text),
            "certifications": self._extract_certifications(cleaned_text),
            "languages": self._extract_languages(cleaned_text),
        }
        
        # Calculate confidence score
        parsed_data["confidence_score"] = self._calculate_confidence(parsed_data)
        
        return parsed_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep essential ones
        text = re.sub(r'[^\w\s@\.\-\+\(\)\/]', ' ', text)
        return text.strip()
    
    def _extract_personal_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract personal information"""
        personal_info = {
            "full_name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin": None,
            "github": None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            personal_info["email"] = emails[0]
        
        # Extract phone numbers
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(\d{3}\)\s?\d{3}-\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                personal_info["phone"] = phones[0]
                break
        
        # Extract LinkedIn
        linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)([a-zA-Z0-9-]+)'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            personal_info["linkedin"] = f"linkedin.com/in/{linkedin_match.group(1)}"
        
        # Extract GitHub
        github_pattern = r'(?:github\.com/)([a-zA-Z0-9-]+)'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            personal_info["github"] = f"github.com/{github_match.group(1)}"
        
        # Extract location
        if self.nlp:
            doc = self.nlp(text[:500])  # Process first 500 chars for efficiency
            for ent in doc.ents:
                if ent.label_ == "GPE" or ent.label_ == "LOC":
                    personal_info["location"] = ent.text
                    break
        
        # Extract name (first few words, capitalized, at the start)
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if len(line) > 0 and len(line.split()) <= 4:
                # Check if it looks like a name (capitalized words)
                words = line.split()
                if len(words) >= 2 and all(word[0].isupper() for word in words if word):
                    personal_info["full_name"] = line
                    break
        
        return personal_info
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience"""
        experience = []
        
        # Keywords to identify experience section
        experience_keywords = [
            r'experience', r'work history', r'employment', 
            r'professional experience', r'career', r'positions? held'
        ]
        
        # Find experience section
        exp_section = self._find_section(text, experience_keywords)
        
        if not exp_section:
            return experience
        
        # Use NLP to extract entities
        if self.nlp:
            doc = self.nlp(exp_section)
            
            # Extract dates
            date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\b'
            dates = re.findall(date_pattern, exp_section, re.IGNORECASE)
            
            # Extract job titles and companies
            lines = exp_section.split('\n')
            current_exp = {}
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 10:
                    continue
                
                # Look for job titles (common patterns)
                title_patterns = [
                    r'(?:Senior|Junior|Lead|Principal)?\s*(?:Software|Data|Product|DevOps|Backend|Frontend|Full Stack|Mobile|QA|Test)?\s*(?:Engineer|Developer|Architect|Manager|Analyst|Scientist|Specialist)',
                    r'(?:CTO|CEO|CFO|VP|Director|Manager|Head of|Team Lead)'
                ]
                
                for pattern in title_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        if current_exp:
                            experience.append(current_exp)
                        current_exp = {
                            "title": line,
                            "company": None,
                            "start_date": None,
                            "end_date": None,
                            "description": None
                        }
                        break
            
            if current_exp:
                experience.append(current_exp)
        
        # Calculate total years of experience
        total_years = self._calculate_years_experience(text)
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        
        education_keywords = [
            r'education', r'academic', r'qualification', 
            r'degree', r'university', r'college', r'school'
        ]
        
        edu_section = self._find_section(text, education_keywords)
        
        if not edu_section:
            return education
        
        # Extract degree information
        degree_patterns = [
            r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Diploma|Certificate)\s+(?:of|in)?\s+[A-Za-z\s]+',
            r'\b(?:B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|Ph\.?D\.?|MBA)\b'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, edu_section, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match,
                    "institution": None,
                    "year": None,
                    "field": None
                })
        
        return education
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills"""
        skills = []
        
        skills_keywords = [
            r'skills?', r'technical skills?', r'competencies?', 
            r'technologies?', r'tools?', r'expertise'
        ]
        
        skills_section = self._find_section(text, skills_keywords)
        
        if not skills_section:
            # Try to find skills throughout the document
            skills_section = text
        
        # Common technical skills
        common_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'Linux',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQL',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
            'Agile', 'Scrum', 'CI/CD', 'DevOps', 'Microservices'
        ]
        
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', skills_section, re.IGNORECASE):
                skills.append(skill)
        
        # Extract skills from comma-separated lists
        lines = skills_section.split('\n')
        for line in lines:
            if ',' in line and len(line.split(',')) > 2:
                potential_skills = [s.strip() for s in line.split(',')]
                for skill in potential_skills:
                    if len(skill) > 2 and len(skill) < 50:
                        if skill not in skills:
                            skills.append(skill)
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """Extract summary/objective"""
        summary_keywords = [
            r'summary', r'objective', r'profile', r'about', r'overview'
        ]
        
        summary_section = self._find_section(text, summary_keywords)
        
        if summary_section:
            # Get first 2-3 sentences
            sentences = re.split(r'[.!?]+', summary_section)
            return '. '.join(sentences[:3]).strip()
        
        # If no summary section, return first paragraph
        lines = text.split('\n')
        for line in lines[:5]:
            if len(line) > 50:
                return line[:500]
        
        return None
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_keywords = [
            r'certification', r'certificate', r'certified', r'license'
        ]
        
        cert_section = self._find_section(text, cert_keywords)
        
        if not cert_section:
            return []
        
        # Look for certification patterns
        cert_pattern = r'(?:Certified|Certification|License)\s+[A-Za-z\s]+'
        certs = re.findall(cert_pattern, cert_section, re.IGNORECASE)
        
        return certs
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages"""
        lang_keywords = [r'languages?']
        
        lang_section = self._find_section(text, lang_keywords)
        
        if not lang_section:
            return []
        
        # Common languages
        common_langs = [
            'English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese',
            'Hindi', 'Arabic', 'Portuguese', 'Russian', 'Italian'
        ]
        
        languages = []
        for lang in common_langs:
            if re.search(r'\b' + re.escape(lang) + r'\b', lang_section, re.IGNORECASE):
                languages.append(lang)
        
        return languages
    
    def _find_section(self, text: str, keywords: List[str]) -> Optional[str]:
        """Find a section based on keywords"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        for keyword in keywords:
            if not keyword:
                continue
            pattern = r'\b' + keyword + r'\b'
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Get text after the keyword
                start_idx = match.end()
                # Find next major section (uppercase word or new line pattern)
                end_pattern = r'\n\s*[A-Z][A-Z\s]{10,}|\n\s*\d+\.|\n\s*[A-Z]+\s*:'
                end_match = re.search(end_pattern, text[start_idx:])
                if end_match:
                    return text[start_idx:start_idx + end_match.start()]
                return text[start_idx:start_idx + 2000]  # Limit to 2000 chars
        
        return None
    
    def _calculate_years_experience(self, text: str) -> float:
        """Calculate total years of experience"""
        # Extract all years mentioned
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        
        if len(years) >= 2:
            years_int = sorted([int(y) for y in years])
            return years_int[-1] - years_int[0]
        
        return 0.0
    
    def _calculate_confidence(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate confidence score for parsed data"""
        score = 0.0
        max_score = 0.0
        
        # Personal info (30 points)
        max_score += 30
        if parsed_data.get("personal_info", {}).get("email"):
            score += 10
        if parsed_data.get("personal_info", {}).get("phone"):
            score += 10
        if parsed_data.get("personal_info", {}).get("full_name"):
            score += 10
        
        # Experience (30 points)
        max_score += 30
        if parsed_data.get("experience"):
            score += min(30, len(parsed_data["experience"]) * 10)
        
        # Education (20 points)
        max_score += 20
        if parsed_data.get("education"):
            score += min(20, len(parsed_data["education"]) * 10)
        
        # Skills (20 points)
        max_score += 20
        if parsed_data.get("skills"):
            score += min(20, len(parsed_data["skills"]) * 2)
        
        return (score / max_score * 100) if max_score > 0 else 0.0

