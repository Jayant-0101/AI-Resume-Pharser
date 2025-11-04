"""
AI Classification and Enhancement Service
Provides intelligent classification, context understanding, and data enrichment
"""
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ClassificationService:
    """Service for AI-powered classification and enhancement"""
    
    # Job role categories
    JOB_ROLES = {
        'software_engineer': ['software engineer', 'developer', 'programmer', 'coder', 'dev'],
        'data_scientist': ['data scientist', 'data analyst', 'data engineer', 'ml engineer'],
        'product_manager': ['product manager', 'pm', 'product owner'],
        'devops': ['devops', 'sre', 'site reliability', 'infrastructure engineer'],
        'qa': ['qa engineer', 'test engineer', 'quality assurance', 'sdet'],
        'designer': ['designer', 'ui/ux', 'graphic designer', 'product designer'],
        'manager': ['manager', 'lead', 'director', 'head of', 'vp', 'cto', 'ceo'],
        'analyst': ['business analyst', 'systems analyst', 'financial analyst'],
        'consultant': ['consultant', 'advisor', 'architect'],
        'other': []
    }
    
    # Seniority levels
    SENIORITY_KEYWORDS = {
        'entry': ['intern', 'junior', 'entry', 'associate', 'trainee', 'graduate'],
        'mid': ['mid-level', 'professional', 'specialist', 'analyst'],
        'senior': ['senior', 'sr.', 'lead', 'principal', 'staff'],
        'executive': ['director', 'vp', 'vice president', 'cto', 'ceo', 'cfo', 'chief', 'head of']
    }
    
    # Industry keywords
    INDUSTRIES = {
        'technology': ['software', 'tech', 'it', 'saas', 'cloud', 'ai', 'fintech'],
        'finance': ['bank', 'financial', 'investment', 'trading', 'fintech'],
        'healthcare': ['health', 'medical', 'pharma', 'hospital', 'clinic'],
        'education': ['education', 'university', 'school', 'academic'],
        'consulting': ['consulting', 'advisory', 'professional services'],
        'retail': ['retail', 'e-commerce', 'commerce', 'shopping'],
        'manufacturing': ['manufacturing', 'production', 'industrial'],
        'other': []
    }
    
    def classify_job_role(self, job_titles: List[str], descriptions: List[str] = None) -> Dict[str, Any]:
        """
        Classify job roles from titles and descriptions
        
        Args:
            job_titles: List of job titles
            descriptions: Optional list of job descriptions
            
        Returns:
            Dictionary with classification results
        """
        all_text = ' '.join(job_titles).lower()
        if descriptions:
            all_text += ' ' + ' '.join([d.lower() for d in descriptions if d])
        
        role_scores = {}
        for role, keywords in self.JOB_ROLES.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                role_scores[role] = score
        
        primary_role = max(role_scores.items(), key=lambda x: x[1])[0] if role_scores else 'other'
        
        return {
            'primary_role': primary_role,
            'role_confidence': role_scores.get(primary_role, 0) / max(len(job_titles), 1),
            'possible_roles': list(role_scores.keys()),
            'role_scores': role_scores
        }
    
    def assess_seniority_level(self, job_titles: List[str], experience_years: float = None) -> Dict[str, Any]:
        """
        Assess seniority level from job titles and experience
        
        Args:
            job_titles: List of job titles
            experience_years: Total years of experience
            
        Returns:
            Dictionary with seniority assessment
        """
        all_text = ' '.join(job_titles).lower()
        
        seniority_scores = {}
        for level, keywords in self.SENIORITY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                seniority_scores[level] = score
        
        # Use experience years if available
        if experience_years is not None:
            if experience_years < 2:
                seniority_scores['entry'] = seniority_scores.get('entry', 0) + 2
            elif experience_years < 5:
                seniority_scores['mid'] = seniority_scores.get('mid', 0) + 2
            elif experience_years < 10:
                seniority_scores['senior'] = seniority_scores.get('senior', 0) + 2
            else:
                seniority_scores['executive'] = seniority_scores.get('executive', 0) + 1
        
        if seniority_scores:
            primary_level = max(seniority_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_level = 'mid'  # Default
        
        return {
            'level': primary_level,
            'confidence': seniority_scores.get(primary_level, 0) / max(len(job_titles), 1),
            'breakdown': seniority_scores
        }
    
    def classify_industry(self, companies: List[str], job_descriptions: List[str] = None) -> Dict[str, Any]:
        """
        Classify industry from company names and job descriptions
        
        Args:
            companies: List of company names
            job_descriptions: Optional list of job descriptions
            
        Returns:
            Dictionary with industry classification
        """
        all_text = ' '.join(companies).lower()
        if job_descriptions:
            all_text += ' ' + ' '.join([d.lower() for d in job_descriptions if d])
        
        industry_scores = {}
        for industry, keywords in self.INDUSTRIES.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                industry_scores[industry] = score
        
        primary_industry = max(industry_scores.items(), key=lambda x: x[1])[0] if industry_scores else 'other'
        
        return {
            'primary_industry': primary_industry,
            'confidence': industry_scores.get(primary_industry, 0) / max(len(companies), 1),
            'possible_industries': list(industry_scores.keys())
        }
    
    def calculate_implied_experience(self, experience_items: List[Dict]) -> float:
        """
        Calculate implied years of experience from job history
        
        Args:
            experience_items: List of experience dictionaries
            
        Returns:
            Total years of experience
        """
        total_years = 0.0
        
        for exp in experience_items:
            start_date = exp.get('start_date')
            end_date = exp.get('end_date', 'Present')
            
            # Try to parse dates
            start_year = self._extract_year(start_date)
            end_year = self._extract_year(end_date) if end_date != 'Present' else datetime.now().year
            
            if start_year and end_year:
                years = end_year - start_year
                if years > 0:
                    total_years += years
        
        return round(total_years, 1)
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string"""
        if not date_str:
            return None
        
        # Look for 4-digit year
        year_match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
        if year_match:
            return int(year_match.group())
        
        return None
    
    def score_skill_relevance(self, skills: List[str], job_role: str) -> List[Dict[str, Any]]:
        """
        Score skill relevance based on job role
        
        Args:
            skills: List of skills
            job_role: Classified job role
            
        Returns:
            List of skills with relevance scores
        """
        # Role-specific skill priorities
        role_skills = {
            'software_engineer': ['python', 'java', 'javascript', 'react', 'node', 'sql', 'git'],
            'data_scientist': ['python', 'r', 'sql', 'machine learning', 'pandas', 'numpy', 'tensorflow'],
            'devops': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'terraform'],
            'product_manager': ['agile', 'scrum', 'product management', 'stakeholder'],
        }
        
        priority_skills = role_skills.get(job_role, [])
        
        scored_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            relevance = 0.5  # Default
            
            # Check if skill matches priority skills
            for priority in priority_skills:
                if priority in skill_lower:
                    relevance = 1.0
                    break
            
            scored_skills.append({
                'skill': skill,
                'relevance_score': relevance,
                'is_core': relevance >= 0.8
            })
        
        return sorted(scored_skills, key=lambda x: x['relevance_score'], reverse=True)
    
    def standardize_skill(self, skill: str) -> str:
        """
        Standardize skill names (e.g., "JS" → "JavaScript")
        
        Args:
            skill: Skill name to standardize
            
        Returns:
            Standardized skill name
        """
        skill_lower = skill.lower().strip()
        
        # Skill mappings
        skill_map = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'ml': 'Machine Learning',
            'dl': 'Deep Learning',
            'ai': 'Artificial Intelligence',
            'db': 'Database',
            'ui': 'UI/UX',
            'ux': 'UI/UX',
            'api': 'REST API',
            'aws': 'Amazon Web Services',
            'gcp': 'Google Cloud Platform',
            'azure': 'Microsoft Azure',
        }
        
        if skill_lower in skill_map:
            return skill_map[skill_lower]
        
        # Capitalize properly
        return skill.title()
    
    def enrich_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Enrich company information (placeholder - can integrate with external APIs)
        
        Args:
            company_name: Company name
            
        Returns:
            Dictionary with company information
        """
        # This is a placeholder - in production, you'd integrate with:
        # - Company database APIs
        # - LinkedIn Company API
        # - Crunchbase API
        # etc.
        
        return {
            'name': company_name,
            'enriched': False,  # Set to True when actual enrichment is implemented
            'note': 'Company enrichment requires external API integration'
        }



