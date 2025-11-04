"""
Anonymization Service
Remove personally identifiable information for bias-free screening
"""
import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class AnonymizationService:
    """Service for anonymizing resumes to remove PII"""
    
    # Patterns for PII detection
    PII_PATTERNS = {
        'name': [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # First Last
            r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?)\s+[A-Z][a-z]+\b',  # Title Name
        ],
        'email': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        'phone': [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        ],
        'address': [
            r'\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)',
            r'[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}',  # City, ST 12345
        ],
        'social_media': [
            r'linkedin\.com/in/[a-zA-Z0-9-]+',
            r'github\.com/[a-zA-Z0-9-]+',
            r'twitter\.com/[a-zA-Z0-9_]+',
        ],
        'date_of_birth': [
            r'\b(?:DOB|Date of Birth|Born)[:\s]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        ],
        'ssn': [
            r'\b\d{3}-\d{2}-\d{4}\b',
            r'\b\d{9}\b',
        ],
        'passport': [
            r'\b[A-Z]{1,2}\d{6,9}\b',
        ]
    }
    
    # Replacement placeholders
    REPLACEMENTS = {
        'name': '[NAME]',
        'email': '[EMAIL]',
        'phone': '[PHONE]',
        'address': '[ADDRESS]',
        'social_media': '[PROFILE]',
        'date_of_birth': '[DATE]',
        'ssn': '[SSN]',
        'passport': '[PASSPORT]'
    }
    
    def anonymize_text(self, text: str, remove_types: List[str] = None) -> Dict[str, Any]:
        """
        Anonymize text by removing PII
        
        Args:
            text: Text to anonymize
            remove_types: List of PII types to remove (None = all)
            
        Returns:
            Dictionary with anonymized text and removed items
        """
        if remove_types is None:
            remove_types = list(self.PII_PATTERNS.keys())
        
        anonymized_text = text
        removed_items = {}
        
        for pii_type in remove_types:
            if pii_type not in self.PII_PATTERNS:
                continue
            
            patterns = self.PII_PATTERNS[pii_type]
            replacement = self.REPLACEMENTS.get(pii_type, '[REDACTED]')
            found_items = []
            
            for pattern in patterns:
                matches = re.findall(pattern, anonymized_text, re.IGNORECASE)
                if matches:
                    found_items.extend(matches)
                    # Replace matches
                    anonymized_text = re.sub(pattern, replacement, anonymized_text, flags=re.IGNORECASE)
            
            if found_items:
                removed_items[pii_type] = list(set(found_items))
        
        return {
            "anonymized_text": anonymized_text,
            "removed_items": removed_items,
            "original_length": len(text),
            "anonymized_length": len(anonymized_text)
        }
    
    def anonymize_resume_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize parsed resume data
        
        Args:
            resume_data: Parsed resume data
            
        Returns:
            Anonymized resume data
        """
        anonymized = resume_data.copy()
        removed_pii = {}
        
        # Anonymize personal information
        if "personal_info" in anonymized:
            personal = anonymized["personal_info"].copy()
            
            # Store removed items
            removed_pii["personal"] = {}
            
            if personal.get("full_name"):
                removed_pii["personal"]["name"] = personal["full_name"]
                personal["full_name"] = "[NAME]"
            
            if personal.get("email"):
                removed_pii["personal"]["email"] = personal["email"]
                personal["email"] = "[EMAIL]"
            
            if personal.get("phone"):
                removed_pii["personal"]["phone"] = personal["phone"]
                personal["phone"] = "[PHONE]"
            
            if personal.get("location"):
                removed_pii["personal"]["location"] = personal["location"]
                personal["location"] = "[LOCATION]"
            
            if personal.get("linkedin"):
                removed_pii["personal"]["linkedin"] = personal["linkedin"]
                personal["linkedin"] = "[PROFILE]"
            
            if personal.get("github"):
                removed_pii["personal"]["github"] = personal["github"]
                personal["github"] = "[PROFILE]"
            
            anonymized["personal_info"] = personal
        
        # Anonymize experience (remove company names if needed)
        # Note: Usually company names are kept, but can be anonymized if required
        if "experience" in anonymized:
            for exp in anonymized["experience"]:
                # Optionally anonymize company names
                # if exp.get("company"):
                #     exp["company"] = "[COMPANY]"
                pass
        
        # Anonymize education (remove institution names if needed)
        # Note: Usually kept, but can be anonymized
        if "education" in anonymized:
            for edu in anonymized["education"]:
                # Optionally anonymize institutions
                # if edu.get("institution"):
                #     edu["institution"] = "[INSTITUTION]"
                pass
        
        return {
            "anonymized_data": anonymized,
            "removed_pii": removed_pii,
            "anonymization_applied": True
        }
    
    def create_anonymized_version(self, resume_data: Dict[str, Any], resume_text: str = None) -> Dict[str, Any]:
        """
        Create fully anonymized version of resume
        
        Args:
            resume_data: Parsed resume data
            resume_text: Raw resume text (optional)
            
        Returns:
            Complete anonymized version
        """
        result = {
            "anonymized_resume_data": None,
            "anonymized_text": None,
            "removed_items": {},
            "anonymization_complete": False
        }
        
        try:
            # Anonymize parsed data
            anonymized_data = self.anonymize_resume_data(resume_data)
            result["anonymized_resume_data"] = anonymized_data["anonymized_data"]
            result["removed_items"]["data"] = anonymized_data["removed_pii"]
            
            # Anonymize text if provided
            if resume_text:
                anonymized_text_result = self.anonymize_text(resume_text)
                result["anonymized_text"] = anonymized_text_result["anonymized_text"]
                result["removed_items"]["text"] = anonymized_text_result["removed_items"]
            
            result["anonymization_complete"] = True
            
        except Exception as e:
            logger.error(f"Error creating anonymized version: {e}")
        
        return result
    
    def get_anonymization_report(self, resume_data: Dict[str, Any], resume_text: str = None) -> Dict[str, Any]:
        """
        Generate anonymization report
        
        Args:
            resume_data: Parsed resume data
            resume_text: Raw resume text (optional)
            
        Returns:
            Report with anonymization details
        """
        report = {
            "pii_detected": {},
            "anonymization_recommended": False,
            "anonymization_applied": False,
            "removed_items_count": 0
        }
        
        # Check for PII in data
        personal = resume_data.get("personal_info", {})
        if personal.get("full_name"):
            report["pii_detected"]["name"] = True
        if personal.get("email"):
            report["pii_detected"]["email"] = True
        if personal.get("phone"):
            report["pii_detected"]["phone"] = True
        if personal.get("location"):
            report["pii_detected"]["location"] = True
        
        # Check text if provided
        if resume_text:
            for pii_type, patterns in self.PII_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, resume_text, re.IGNORECASE):
                        report["pii_detected"][pii_type] = True
                        break
        
        report["anonymization_recommended"] = len(report["pii_detected"]) > 0
        report["removed_items_count"] = len(report["pii_detected"])
        
        return report



