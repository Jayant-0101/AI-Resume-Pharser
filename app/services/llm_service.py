"""
LLM Service using Open-Source Models
Provides context understanding, summarization, and intelligent analysis
"""
import logging
from typing import Dict, List, Optional, Any
import torch

logger = logging.getLogger(__name__)

# Try to import transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification
    from transformers import TextGenerationPipeline, TextClassificationPipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("Transformers not available - LLM features will be limited")


class LLMService:
    """Service for LLM-powered context understanding"""
    
    def __init__(self):
        """Initialize LLM service with open-source models"""
        self.text_generator = None
        self.text_classifier = None
        self.summarizer = None
        self._models_loaded = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize LLM models (non-blocking, will load on demand)"""
        if not HAS_TRANSFORMERS:
            logger.warning("Transformers not installed - LLM features disabled")
            return
        
        # Don't load models on startup - load them on demand to avoid hanging
        logger.info("LLM models will be loaded on first use (lazy loading)")
        # Models will be initialized when first needed
        self._models_loaded = False
    
    def _ensure_models_loaded(self):
        """Ensure models are loaded (lazy loading)"""
        if self._models_loaded:
            return
        
        if not HAS_TRANSFORMERS:
            return
        
        try:
            # Try to load summarization model (most useful)
            try:
                self.summarizer = pipeline("summarization", device=-1)
                logger.info("LLM summarization model loaded")
            except Exception as e:
                logger.warning(f"Could not load summarization model: {e}")
            
            self._models_loaded = True
        except Exception as e:
            logger.warning(f"Error loading LLM models: {e}")
            # Continue without models
    
    def generate_summary(self, text: str, max_length: int = 150) -> Optional[str]:
        """
        Generate a summary of the resume using LLM
        
        Args:
            text: Resume text
            max_length: Maximum summary length
            
        Returns:
            Summary text or None
        """
        # Lazy load models
        if not self._models_loaded:
            self._ensure_models_loaded()
        
        if not self.summarizer:
            return None
        
        try:
            # Truncate if too long
            text = text[:2000]  # Limit input length
            
            result = self.summarizer(text, max_length=max_length, min_length=50, do_sample=False)
            return result[0].get('summary_text', '') if result else None
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def analyze_context(self, text: str, context_type: str = "resume") -> Dict[str, Any]:
        """
        Analyze text context using LLM
        
        Args:
            text: Text to analyze
            context_type: Type of context (resume, job_description, etc.)
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "context_type": context_type,
            "summary": None,
            "key_points": [],
            "tone": None,
            "completeness": None
        }
        
        if not self.summarizer:
            return analysis
        
        try:
            # Generate summary
            summary = self.generate_summary(text)
            if summary:
                analysis["summary"] = summary
                # Extract key points (simple extraction)
                sentences = summary.split('. ')
                analysis["key_points"] = [s.strip() for s in sentences[:3] if s.strip()]
            
            # Analyze tone if classifier available
            if self.text_classifier:
                try:
                    text_sample = text[:512]  # Limit input
                    result = self.text_classifier(text_sample)
                    if result:
                        analysis["tone"] = result[0].get('label', 'unknown')
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
        
        return analysis
    
    def extract_insights(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract insights from parsed resume data using LLM
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Dictionary with insights
        """
        insights = {
            "career_progression": None,
            "strengths": [],
            "growth_areas": [],
            "recommendations": []
        }
        
        try:
            # Build context from resume
            experience = resume_data.get("experience", [])
            skills = resume_data.get("skills", [])
            education = resume_data.get("education", [])
            
            # Create analysis text
            analysis_text = f"Experience: {len(experience)} positions. "
            analysis_text += f"Skills: {', '.join(skills[:10])}. "
            analysis_text += f"Education: {len(education)} degrees."
            
            # Analyze career progression
            if len(experience) > 1:
                titles = [exp.get("title", "") for exp in experience]
                insights["career_progression"] = "Progressive career with increasing responsibilities" if len(titles) > 2 else "Early career"
            
            # Identify strengths
            if skills:
                insights["strengths"] = skills[:5]  # Top skills
            
            # Generate summary if possible
            if self.summarizer:
                summary = self.generate_summary(analysis_text)
                if summary:
                    insights["summary"] = summary
        
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
        
        return insights
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.summarizer is not None or self.text_generator is not None

