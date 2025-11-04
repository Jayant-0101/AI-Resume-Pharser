"""
Response formatter to transform parsed data into standardized JSON structure
"""
import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime


class ResponseFormatter:
    """Formats resume parsing results into standardized JSON structure"""
    
    @staticmethod
    def format_resume_response(
        parsed_data: Dict[str, Any],
        file_info: Dict[str, Any],
        resume_id: int,
        processing_time: float,
        uploaded_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Format resume parsing results into standardized JSON structure
        
        Args:
            parsed_data: Parsed resume data from AI parser
            file_info: File metadata
            resume_id: Resume database ID
            processing_time: Processing time in seconds
            uploaded_at: Upload timestamp
            processed_at: Processing completion timestamp
            
        Returns:
            Formatted response matching the requested structure
        """
        if uploaded_at is None:
            uploaded_at = datetime.utcnow()
        if processed_at is None:
            processed_at = datetime.utcnow()
        
        # Generate UUID for resume
        resume_uuid = f"resume-{uuid.uuid4().hex[:8]}"
        
        # Format metadata
        metadata = {
            "fileName": file_info.get("filename", "unknown"),
            "fileSize": file_info.get("size", 0),
            "uploadedAt": uploaded_at.isoformat() + "Z",
            "processedAt": processed_at.isoformat() + "Z",
            "processingTime": round(processing_time, 2)
        }
        
        # Format personal info
        personal_info = ResponseFormatter._format_personal_info(
            parsed_data.get("personal_info", {})
        )
        
        # Format summary
        summary = ResponseFormatter._format_summary(
            parsed_data.get("summary"),
            parsed_data.get("classification", {})
        )
        
        # Format experience
        experience = ResponseFormatter._format_experience(
            parsed_data.get("experience", [])
        )
        
        # Format education
        education = ResponseFormatter._format_education(
            parsed_data.get("education", [])
        )
        
        # Format skills
        skills = ResponseFormatter._format_skills(
            parsed_data.get("skills", []),
            parsed_data.get("languages", [])
        )
        
        # Format certifications
        certifications = ResponseFormatter._format_certifications(
            parsed_data.get("certifications", [])
        )
        
        # Format AI enhancements
        ai_enhancements = ResponseFormatter._format_ai_enhancements(parsed_data)
        
        return {
            "id": resume_uuid,
            "metadata": metadata,
            "personalInfo": personal_info,
            "summary": summary,
            "experience": experience,
            "education": education,
            "skills": skills,
            "certifications": certifications,
            "aiEnhancements": ai_enhancements
        }
    
    @staticmethod
    def _format_personal_info(personal_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format personal information"""
        full_name = personal_info.get("full_name", "")
        name_parts = full_name.split() if full_name else []
        
        # Split name into first and last
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        # Parse address if location is provided
        location = personal_info.get("location", "")
        address = ResponseFormatter._parse_address(location)
        
        # Extract website from linkedin or github if available
        website = None
        linkedin = personal_info.get("linkedin", "")
        github = personal_info.get("github", "")
        
        if linkedin:
            if not linkedin.startswith("http"):
                linkedin = f"https://{linkedin}"
        if github:
            if not github.startswith("http"):
                github = f"https://{github}"
            website = github  # Use GitHub as website if available
        
        return {
            "name": {
                "first": first_name,
                "last": last_name,
                "full": full_name
            },
            "contact": {
                "email": personal_info.get("email"),
                "phone": personal_info.get("phone"),
                "address": address,
                "linkedin": linkedin,
                "website": website
            }
        }
    
    @staticmethod
    def _parse_address(location: str) -> Dict[str, Optional[str]]:
        """Parse location string into address components"""
        if not location:
            return {
                "street": None,
                "city": None,
                "state": None,
                "zipCode": None,
                "country": None
            }
        
        # Try to parse common formats
        # Format: "City, State ZIP" or "City, State" or "City, State, Country"
        parts = [p.strip() for p in location.split(",")]
        
        address = {
            "street": None,
            "city": parts[0] if len(parts) > 0 else None,
            "state": None,
            "zipCode": None,
            "country": None
        }
        
        if len(parts) > 1:
            # Try to extract state and zip
            state_zip = parts[1].strip()
            zip_match = re.search(r'\b\d{5}(-\d{4})?\b', state_zip)
            if zip_match:
                address["zipCode"] = zip_match.group(0)
                address["state"] = state_zip[:zip_match.start()].strip()
            else:
                address["state"] = state_zip
        
        if len(parts) > 2:
            address["country"] = parts[2].strip()
        
        return address
    
    @staticmethod
    def _format_summary(summary_text: Optional[str], classification: Dict[str, Any]) -> Dict[str, Any]:
        """Format summary section"""
        # Get career level from classification
        seniority = classification.get("seniority", {})
        level = seniority.get("level", "mid-level")
        
        # Map to standard levels
        level_mapping = {
            "entry": "entry-level",
            "junior": "entry-level",
            "mid": "mid-level",
            "senior": "senior",
            "executive": "executive"
        }
        career_level = level_mapping.get(level.lower() if level else "", "mid-level")
        
        # Get industry from classification
        industry = classification.get("industry", {})
        industry_focus = industry.get("primary_industry", "technology")
        
        return {
            "text": summary_text or "",
            "careerLevel": career_level,
            "industryFocus": industry_focus
        }
    
    @staticmethod
    def _format_experience(experience_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format experience list"""
        formatted_experience = []
        
        for idx, exp in enumerate(experience_list, 1):
            # Parse dates
            start_date = ResponseFormatter._parse_date(exp.get("start_date"))
            end_date_str = exp.get("end_date", "") or ""
            is_current = end_date_str and ("present" in end_date_str.lower() or "current" in end_date_str.lower())
            end_date = None if is_current else ResponseFormatter._parse_date(end_date_str)
            
            # Calculate duration
            duration = ResponseFormatter._calculate_duration(start_date, end_date, is_current)
            
            # Extract achievements (already in list or extract from description)
            achievements = exp.get("achievements", [])
            if not achievements and exp.get("description"):
                # Try to extract bullet points or achievements from description
                desc = exp.get("description", "")
                lines = desc.split("\n")
                achievements = [line.strip("- •*").strip() for line in lines if line.strip() and len(line.strip()) > 10]
            
            formatted_exp = {
                "id": f"exp-{idx}",
                "title": exp.get("title", ""),
                "company": exp.get("company"),
                "location": exp.get("location"),
                "startDate": start_date.isoformat() if start_date else None,
                "endDate": end_date.isoformat() if end_date else None,
                "current": is_current,
                "duration": duration,
                "description": exp.get("description", ""),
                "achievements": achievements[:5] if achievements else [],  # Limit to 5
                "technologies": exp.get("technologies", [])
            }
            
            formatted_experience.append(formatted_exp)
        
        return formatted_experience
    
    @staticmethod
    def _format_education(education_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format education list"""
        formatted_education = []
        
        for edu in education_list:
            # Parse graduation date
            year = edu.get("year")
            graduation_date = None
            if year:
                try:
                    # Assume May graduation if only year provided
                    graduation_date = datetime(int(year), 5, 15)
                except:
                    pass
            
            # Extract honors
            honors = edu.get("honors", [])
            if isinstance(honors, str):
                honors = [honors]
            
            formatted_edu = {
                "degree": edu.get("degree", ""),
                "field": edu.get("field"),
                "institution": edu.get("institution"),
                "location": None,  # Could be extracted from institution name
                "graduationDate": graduation_date.isoformat() if graduation_date else None,
                "gpa": float(edu.get("gpa")) if edu.get("gpa") else None,
                "honors": honors
            }
            
            formatted_education.append(formatted_edu)
        
        return formatted_education
    
    @staticmethod
    def _format_skills(skills_list: List[str], languages_list: List[str]) -> Dict[str, Any]:
        """Format skills into categorized structure"""
        # Categorize technical skills
        programming_languages = []
        frameworks = []
        tools = []
        
        # Common categorizations
        lang_keywords = ["python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "ruby", "php", "swift", "kotlin", "scala", "r"]
        framework_keywords = ["django", "flask", "react", "angular", "vue", "node", "express", "spring", "laravel", "rails", "fastapi", "next"]
        tool_keywords = ["docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "git", "postgresql", "mongodb", "redis", "elasticsearch"]
        
        for skill in skills_list:
            skill_lower = skill.lower()
            if any(kw in skill_lower for kw in lang_keywords):
                programming_languages.append(skill)
            elif any(kw in skill_lower for kw in framework_keywords):
                frameworks.append(skill)
            elif any(kw in skill_lower for kw in tool_keywords):
                tools.append(skill)
            else:
                # Default to programming languages if can't categorize
                programming_languages.append(skill)
        
        technical = []
        if programming_languages:
            technical.append({
                "category": "Programming Languages",
                "items": programming_languages
            })
        if frameworks:
            technical.append({
                "category": "Frameworks",
                "items": frameworks
            })
        if tools:
            technical.append({
                "category": "Tools & Technologies",
                "items": tools
            })
        
        # Format languages
        formatted_languages = []
        for lang in languages_list:
            if isinstance(lang, dict):
                formatted_languages.append(lang)
            elif isinstance(lang, str):
                # Try to parse language proficiency
                parts = lang.split("-")
                language_name = parts[0].strip()
                proficiency = parts[1].strip() if len(parts) > 1 else "Conversational"
                formatted_languages.append({
                    "language": language_name,
                    "proficiency": proficiency
                })
        
        return {
            "technical": technical,
            "soft": [],  # Soft skills would need to be extracted separately
            "languages": formatted_languages
        }
    
    @staticmethod
    def _format_certifications(certifications_list: List[str]) -> List[Dict[str, Any]]:
        """Format certifications"""
        formatted_certs = []
        
        for cert in certifications_list:
            if isinstance(cert, dict):
                formatted_certs.append(cert)
            elif isinstance(cert, str):
                # Try to parse certification string
                # Format: "Name - Issuer" or just "Name"
                parts = cert.split("-")
                name = parts[0].strip()
                issuer = parts[1].strip() if len(parts) > 1 else None
                
                formatted_certs.append({
                    "name": name,
                    "issuer": issuer,
                    "issueDate": None,
                    "expiryDate": None,
                    "credentialId": None
                })
        
        return formatted_certs
    
    @staticmethod
    def _format_ai_enhancements(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format AI enhancements"""
        confidence_score = parsed_data.get("confidence_score", 0.0)
        quality_score = int(confidence_score)
        
        # Calculate completeness score
        completeness = 0
        if parsed_data.get("personal_info", {}).get("full_name"):
            completeness += 10
        if parsed_data.get("personal_info", {}).get("email"):
            completeness += 10
        if parsed_data.get("experience"):
            completeness += 30
        if parsed_data.get("education"):
            completeness += 20
        if parsed_data.get("skills"):
            completeness += 20
        if parsed_data.get("summary"):
            completeness += 10
        
        # Get suggestions from enhancement
        suggestions = []
        enhancement = parsed_data.get("enhancement", {})
        if not enhancement.get("skill_relevance"):
            suggestions.append("Add quantifiable achievements to work experience")
        if not parsed_data.get("certifications"):
            suggestions.append("Include relevant technical certifications")
        
        # Get industry fit from classification
        industry_fit = {}
        classification = parsed_data.get("classification", {})
        job_role = classification.get("job_role", {})
        primary_role = job_role.get("primary_role", "software_engineering")
        role_confidence = job_role.get("role_confidence", 0.95)
        
        industry_fit[primary_role] = role_confidence
        
        # Add other possible roles
        possible_roles = job_role.get("possible_roles", [])
        for role in possible_roles[:2]:  # Limit to top 2
            if isinstance(role, dict):
                industry_fit[role.get("role", "")] = role.get("confidence", 0.5)
            else:
                industry_fit[role] = 0.5
        
        return {
            "qualityScore": quality_score,
            "completenessScore": completeness,
            "suggestions": suggestions,
            "industryFit": industry_fit
        }
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string into datetime object"""
        if not date_str:
            return None
        
        date_str = date_str.lower().strip()
        
        # Handle "present", "current", "now"
        if any(word in date_str for word in ["present", "current", "now"]):
            return None
        
        # Try common date formats
        formats = [
            "%Y-%m-%d",
            "%m/%Y",
            "%m-%Y",
            "%Y/%m",
            "%B %Y",
            "%b %Y",
            "%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        # Try to extract year only
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            try:
                return datetime(int(year_match.group()), 1, 1)
            except:
                pass
        
        return None
    
    @staticmethod
    def _calculate_duration(start_date: Optional[datetime], end_date: Optional[datetime], is_current: bool) -> str:
        """Calculate duration string"""
        if not start_date:
            return ""
        
        if is_current:
            end_date = datetime.utcnow()
        elif not end_date:
            return ""
        
        delta = end_date - start_date
        years = delta.days // 365
        months = (delta.days % 365) // 30
        
        if years > 0 and months > 0:
            return f"{years} year{'s' if years > 1 else ''} {months} month{'s' if months > 1 else ''}"
        elif years > 0:
            return f"{years} year{'s' if years > 1 else ''}"
        elif months > 0:
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            return "Less than 1 month"



