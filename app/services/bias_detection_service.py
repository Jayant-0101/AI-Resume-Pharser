"""
Bias Detection Service
Identify and flag potential hiring biases in resume screening
"""
import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BiasDetectionService:
    """Service for detecting potential hiring biases"""
    
    # Protected characteristics that should not influence hiring
    PROTECTED_CHARACTERISTICS = {
        'age': {
            'patterns': [
                r'\b\d{2}\s*years?\s*old\b',
                r'born\s+in\s+\d{4}',
                r'age[:\s]*\d{2}',
                r'graduated\s+\d{4}',  # Can infer age
            ],
            'indicators': ['birth year', 'age', 'graduation year']
        },
        'gender': {
            'patterns': [
                r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Miss|Mr\.)\b',
                r'\b(?:he|she|his|her)\b',
            ],
            'indicators': ['gender pronouns', 'title']
        },
        'race_ethnicity': {
            'patterns': [
                r'\b(?:African|Asian|Hispanic|Latino|Native|Caucasian|White|Black)\b',
            ],
            'indicators': ['ethnicity mention']
        },
        'religion': {
            'patterns': [
                r'\b(?:Christian|Muslim|Jewish|Hindu|Buddhist|Catholic|Protestant)\b',
            ],
            'indicators': ['religion mention']
        },
        'marital_status': {
            'patterns': [
                r'\b(?:married|single|divorced|widowed|spouse)\b',
            ],
            'indicators': ['marital status']
        },
        'nationality': {
            'patterns': [
                r'\b(?:citizen|citizenship|nationality|passport)\b',
            ],
            'indicators': ['citizenship status']
        },
        'disability': {
            'patterns': [
                r'\b(?:disability|disabled|handicap)\b',
            ],
            'indicators': ['disability mention']
        }
    }
    
    # Potentially biased language patterns
    BIASED_LANGUAGE = {
        'gender_biased': {
            'patterns': [
                r'\b(?:aggressive|assertive|dominant|nurturing|emotional)\b',
            ],
            'description': 'Gender-stereotyped language'
        },
        'age_biased': {
            'patterns': [
                r'\b(?:young|fresh|energetic|experienced|seasoned|mature)\b',
            ],
            'description': 'Age-related language'
        },
        'cultural_biased': {
            'patterns': [
                r'\b(?:cultural fit|fit in|team player)\b',
            ],
            'description': 'Potentially exclusionary language'
        }
    }
    
    def detect_bias(self, resume_data: Dict[str, Any], resume_text: str = None) -> Dict[str, Any]:
        """
        Detect potential biases in resume
        
        Args:
            resume_data: Parsed resume data
            resume_text: Raw resume text (optional)
            
        Returns:
            Dictionary with bias detection results
        """
        detection_results = {
            "bias_detected": False,
            "protected_characteristics": {},
            "biased_language": [],
            "recommendations": [],
            "anonymization_suggested": False,
            "risk_level": "low"  # low, medium, high
        }
        
        try:
            # Combine text sources
            text_to_analyze = resume_text or ""
            if not text_to_analyze:
                # Reconstruct from parsed data
                text_to_analyze = self._reconstruct_text(resume_data)
            
            text_lower = text_to_analyze.lower()
            
            # Check for protected characteristics
            for char_type, config in self.PROTECTED_CHARACTERISTICS.items():
                matches = []
                for pattern in config['patterns']:
                    found = re.findall(pattern, text_lower, re.IGNORECASE)
                    if found:
                        matches.extend(found)
                
                if matches:
                    detection_results["bias_detected"] = True
                    detection_results["protected_characteristics"][char_type] = {
                        "detected": True,
                        "matches": list(set(matches)),
                        "indicators": config['indicators'],
                        "severity": "high"
                    }
            
            # Check for biased language
            for bias_type, config in self.BIASED_LANGUAGE.items():
                matches = []
                for pattern in config['patterns']:
                    found = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        matches.extend(found)
                
                if matches:
                    detection_results["biased_language"].append({
                        "type": bias_type,
                        "description": config['description'],
                        "matches": list(set(matches)),
                        "severity": "medium"
                    })
            
            # Determine risk level
            protected_count = len(detection_results["protected_characteristics"])
            biased_lang_count = len(detection_results["biased_language"])
            
            if protected_count > 0:
                detection_results["risk_level"] = "high"
                detection_results["anonymization_suggested"] = True
            elif biased_lang_count > 2:
                detection_results["risk_level"] = "medium"
            else:
                detection_results["risk_level"] = "low"
            
            # Generate recommendations
            detection_results["recommendations"] = self._generate_recommendations(detection_results)
            
        except Exception as e:
            logger.error(f"Error detecting bias: {e}")
        
        return detection_results
    
    def _reconstruct_text(self, resume_data: Dict[str, Any]) -> str:
        """Reconstruct text from parsed data for analysis"""
        text_parts = []
        
        # Personal info
        personal = resume_data.get("personal_info", {})
        if personal.get("full_name"):
            text_parts.append(personal["full_name"])
        if personal.get("email"):
            text_parts.append(personal["email"])
        
        # Experience
        for exp in resume_data.get("experience", []):
            if exp.get("title"):
                text_parts.append(exp["title"])
            if exp.get("description"):
                text_parts.append(exp["description"])
        
        # Education
        for edu in resume_data.get("education", []):
            if edu.get("degree"):
                text_parts.append(edu["degree"])
        
        return " ".join(text_parts)
    
    def _generate_recommendations(self, detection: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on detected biases"""
        recommendations = []
        
        if detection["risk_level"] == "high":
            recommendations.append("⚠️ HIGH RISK: Protected characteristics detected. Consider anonymization.")
            recommendations.append("Remove identifiable information before screening.")
        
        if detection["protected_characteristics"]:
            char_types = list(detection["protected_characteristics"].keys())
            recommendations.append(f"Detected characteristics: {', '.join(char_types)}")
        
        if detection["biased_language"]:
            recommendations.append("Review language for potential bias indicators.")
        
        if detection["risk_level"] == "low":
            recommendations.append("✓ Low bias risk - Resume appears bias-free")
        
        return recommendations
    
    def flag_potential_bias(self, resume_data: Dict[str, Any]) -> List[str]:
        """
        Quick flag check for potential biases
        
        Returns:
            List of flagged issues
        """
        flags = []
        detection = self.detect_bias(resume_data)
        
        if detection["bias_detected"]:
            flags.append("Protected characteristics present")
        
        if detection["biased_language"]:
            flags.append("Potentially biased language detected")
        
        if detection["risk_level"] == "high":
            flags.append("HIGH RISK - Anonymization recommended")
        
        return flags



