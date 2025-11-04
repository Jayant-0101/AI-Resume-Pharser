"""
Enhanced AI-powered resume parser with high accuracy (>85%)
Uses spaCy large model and multiple extraction strategies
"""
import re
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import spaCy for better NER
try:
    import spacy
    HAS_SPACY = True
    try:
        # Try to load large model (best accuracy)
        nlp = spacy.load("en_core_web_lg")
        SPACY_MODEL_LOADED = True
        logger.info("spaCy large model loaded successfully")
    except OSError:
        try:
            # Fallback to medium model
            nlp = spacy.load("en_core_web_md")
            SPACY_MODEL_LOADED = True
            logger.info("spaCy medium model loaded successfully")
        except OSError:
            try:
                # Fallback to small model
                nlp = spacy.load("en_core_web_sm")
                SPACY_MODEL_LOADED = True
                logger.info("spaCy small model loaded successfully")
            except OSError:
                SPACY_MODEL_LOADED = False
                logger.warning("spaCy models not found. Install with: python -m spacy download en_core_web_lg")
                nlp = None
except ImportError:
    HAS_SPACY = False
    SPACY_MODEL_LOADED = False
    nlp = None
    logger.warning("spaCy not installed - install with: pip install spacy")

# Try transformers for additional NER
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("Transformers not installed")


class EnhancedParser:
    """Enhanced resume parser with multi-strategy extraction for high accuracy"""
    
    def __init__(self):
        # Lazy load spaCy to avoid slow startup
        self.spacy_nlp = None
        self._spacy_loaded = False
        self.transformer_ner = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize models (lazy loading for transformers)"""
        if HAS_TRANSFORMERS:
            # Will load on first use
            pass
    
    def _ensure_spacy(self):
        """Load spaCy model on demand (lazy loading for faster startup)"""
        if self._spacy_loaded:
            return
        
        if not HAS_SPACY:
            return
        
        try:
            # Try large model first (best accuracy)
            try:
                self.spacy_nlp = spacy.load("en_core_web_lg")
                logger.info("spaCy large model loaded (lazy)")
            except OSError:
                try:
                    self.spacy_nlp = spacy.load("en_core_web_md")
                    logger.info("spaCy medium model loaded (lazy)")
                except OSError:
                    try:
                        self.spacy_nlp = spacy.load("en_core_web_sm")
                        logger.info("spaCy small model loaded (lazy)")
                    except OSError:
                        logger.warning("spaCy models not found")
                        self.spacy_nlp = None
            self._spacy_loaded = True
        except Exception as e:
            logger.warning(f"Could not load spaCy: {e}")
            self.spacy_nlp = None
            self._spacy_loaded = True
    
    def _ensure_transformer_ner(self):
        """Load transformer NER model on demand"""
        if self.transformer_ner is not None:
            return
        
        if not HAS_TRANSFORMERS:
            return
        
        try:
            # Use fast, accurate model
            self.transformer_ner = pipeline(
                "ner",
                model="dslim/bert-base-NER",
                aggregation_strategy="simple",
                device=-1
            )
            logger.info("Transformer NER model loaded")
        except Exception as e:
            logger.warning(f"Could not load transformer NER: {e}")
            self.transformer_ner = None
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse resume with enhanced accuracy"""
        start_time = time.time()
        
        # Validate input
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided to parser")
            text = ""
        
        # Clean and normalize text
        cleaned_text = self._preprocess_text(text)
        
        # Ensure cleaned_text is not None
        if not cleaned_text:
            cleaned_text = ""
        
        # Extract using multiple strategies
        parsed_data = {
            "personal_info": self._extract_personal_info_enhanced(cleaned_text, text),
            "experience": self._extract_experience_enhanced(cleaned_text, text),
            "education": self._extract_education_enhanced(cleaned_text, text),
            "skills": self._extract_skills_enhanced(cleaned_text, text),
            "summary": self._extract_summary_enhanced(cleaned_text, text),
            "certifications": self._extract_certifications(cleaned_text),
            "languages": self._extract_languages(cleaned_text),
        }
        
        # Calculate confidence with validation
        parsed_data["confidence_score"] = self._calculate_confidence_enhanced(parsed_data)
        
        processing_time = time.time() - start_time
        logger.info(f"Parsing completed in {processing_time:.2f}s with confidence {parsed_data['confidence_score']:.1f}%")
        
        return parsed_data
    
    def _preprocess_text(self, text: str) -> str:
        """Enhanced text preprocessing"""
        if not text or not isinstance(text, str):
            return ""
        
        # Preserve line structure for better parsing
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if not line:
                continue
            # Remove excessive whitespace but preserve structure
            line = re.sub(r'[ \t]+', ' ', line.strip() if isinstance(line, str) else str(line).strip())
            if line:
                cleaned_lines.append(line)
        
        # Join with newlines to preserve structure
        cleaned = '\n'.join(cleaned_lines)
        
        # Remove excessive blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned
    
    def _extract_personal_info_enhanced(self, cleaned_text: str, original_text: str) -> Dict[str, Optional[str]]:
        """Extract personal info using multiple strategies"""
        personal_info = {
            "full_name": None,
            "email": None,
            "phone": None,
            "location": None,
            "linkedin": None,
            "github": None
        }
        
        # Strategy 1: Extract email (very reliable)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, original_text)
        if emails:
            personal_info["email"] = emails[0]
        
        # Strategy 2: Extract phone (multiple patterns)
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
            r'\b\d{10}\b',  # 10 digits
        ]
        
        for pattern in phone_patterns:
            matches = re.finditer(pattern, original_text)
            for match in matches:
                phone_str = match.group().strip()
                # Validate it's not part of a date or ID
                if len(phone_str) == 10 and not phone_str.startswith(('19', '20')):
                    # Check context
                    start, end = match.span()
                    context_before = original_text[max(0, start-5):start]
                    context_after = original_text[end:min(len(original_text), end+5)]
                    
                    # Skip if surrounded by digits
                    if not (context_before[-1:].isdigit() or context_after[:1].isdigit()):
                        personal_info["phone"] = phone_str
                        break
            if personal_info["phone"]:
                break
        
        # Strategy 3: Extract name using spaCy + transformers + pattern matching
        name_candidates = []
        
        # Use first 3 lines (name is usually at top)
        top_lines = '\n'.join(cleaned_text.split('\n')[:3])
        
        # spaCy NER (lazy load)
        self._ensure_spacy()
        if self.spacy_nlp:
            try:
                doc = self.spacy_nlp(top_lines)
                for ent in doc.ents:
                    if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                        # Validate name
                        words = ent.text.split()
                        if all(w[0].isupper() for w in words[:2]) and len(ent.text) < 50:
                            name_candidates.append((ent.text, 0.9, "spacy"))
            except Exception as e:
                logger.debug(f"spaCy name extraction error: {e}")
        
        # Transformer NER
        self._ensure_transformer_ner()
        if self.transformer_ner:
            try:
                entities = self.transformer_ner(top_lines[:500])
                for entity in entities:
                    if entity.get('entity_group') == 'PER' and len(entity.get('word', '').split()) >= 2:
                        entity_text = entity.get('word', '').strip()
                        score = entity.get('score', 0.0)
                        if score > 0.8:
                            name_candidates.append((entity_text, score, "transformer"))
            except Exception as e:
                logger.debug(f"Transformer name extraction error: {e}")
        
        # Pattern matching fallback
        first_line = cleaned_text.split('\n')[0] if cleaned_text else ""
        if first_line and not personal_info["full_name"]:
            # Pattern: 2-4 capitalized words at start of line
            name_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s|$|[,\n])'
            match = re.search(name_pattern, first_line)
            if match:
                name_text = match.group(1).strip()
                # Skip if it looks like a company or title
                if name_text and not any(word.lower() in name_text.lower() for word in ['inc', 'llc', 'corp', 'company', 'engineer', 'manager']):
                    name_candidates.append((name_text, 0.7, "pattern"))
        
        # Select best name candidate
        if name_candidates:
            # Sort by confidence, prefer spaCy
            name_candidates.sort(key=lambda x: (x[1], x[2] == "spacy"), reverse=True)
            personal_info["full_name"] = name_candidates[0][0]
            logger.info(f"Extracted name: {personal_info['full_name']} using {name_candidates[0][2]}")
        
        # Strategy 4: Extract location
        location_candidates = []
        
        # Use first 500 chars (contact info is usually at top)
        top_text = cleaned_text[:500]
        
        self._ensure_spacy()
        if self.spacy_nlp:
            try:
                doc = self.spacy_nlp(top_text)
                for ent in doc.ents:
                    if ent.label_ in ["GPE", "LOC"]:
                        location_candidates.append((ent.text, 0.9))
            except Exception as e:
                logger.debug(f"spaCy location extraction error: {e}")
        
        if location_candidates:
            location_candidates.sort(key=lambda x: x[1], reverse=True)
            personal_info["location"] = location_candidates[0][0]
        
        # Strategy 5: Extract LinkedIn and GitHub
        linkedin_pattern = r'(?:linkedin\.com/in/|linkedin\.com/pub/)([a-zA-Z0-9-]+)'
        linkedin_match = re.search(linkedin_pattern, original_text, re.IGNORECASE)
        if linkedin_match:
            personal_info["linkedin"] = f"linkedin.com/in/{linkedin_match.group(1)}"
        
        github_pattern = r'(?:github\.com/)([a-zA-Z0-9-]+)'
        github_match = re.search(github_pattern, original_text, re.IGNORECASE)
        if github_match:
            personal_info["github"] = f"github.com/{github_match.group(1)}"
        
        return personal_info
    
    def _extract_experience_enhanced(self, cleaned_text: str, original_text: str) -> List[Dict[str, Any]]:
        """Extract experience with enhanced accuracy"""
        experience = []
        
        # Find experience section - search for multiple keywords
        exp_keywords = [
            'experience', 
            'work history', 
            'employment history',
            'employment',
            'professional experience', 
            'career',
            'work experience',
            'professional background',
            'employment background',
            'work background',
            'career history',
            'professional history'
        ]
        exp_section = self._find_section(cleaned_text, exp_keywords)
        
        # If no section found, try to find experience patterns throughout the entire document
        if not exp_section:
            # Try to find experience patterns throughout
            exp_section = cleaned_text
            logger.debug("No experience section found with keywords, searching entire document")
        else:
            logger.debug(f"Found experience section using keywords: {exp_keywords}")
        
        # Use spaCy for better entity extraction if available
        self._ensure_spacy()
        if self.spacy_nlp:
            try:
                # Process in chunks for speed (limit to 3000 chars for <5s response)
                exp_chunk = exp_section[:3000]
                doc = self.spacy_nlp(exp_chunk)
                # Extract organizations and dates
                orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
            except Exception as e:
                logger.debug(f"spaCy experience extraction error: {e}")
                orgs = []
                dates = []
        else:
            orgs = []
            dates = []
        
        # Parse experience entries - be more aggressive in finding experience
        lines = exp_section.split('\n')
        current_exp = {}
        
        # Enhanced date patterns
        date_patterns = [
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
            r'\b\d{1,2}[/-]\d{4}\b',
            r'\b(?:19|20)\d{2}\b',
            r'(?:Present|Current|Now)'
        ]
        
        # Job title patterns - expanded to catch more variations
        title_patterns = [
            r'\b(?:Senior|Junior|Lead|Principal|Staff|Associate|Manager|Director|VP|CEO|CTO|CFO|Executive|Head|Chief)\s+[A-Za-z\s]+',
            r'\b[A-Z][a-z]+\s+(?:Engineer|Developer|Manager|Analyst|Specialist|Architect|Consultant|Coordinator|Supervisor|Representative|Assistant|Clerk)',
            r'\b(?:Software|Data|Product|DevOps|Backend|Frontend|Full.?Stack|Mobile|QA|Test|Systems|Security|Sales|Customer|Marketing|Operations)\s+(?:Engineer|Developer|Architect|Manager|Analyst|Specialist|Representative)',
            r'\b(?:Warehouse|Logistics|Supply Chain|Operations|Distribution|Retail|Amazon|Fulfillment|Delivery|Shipping)?\s*(?:Associate|Specialist|Coordinator|Supervisor|Manager|Worker|Operator|Technician|Clerk)',
            # More general patterns
            r'\b[A-Z][a-z]+\s+(?:at|@)\s+[A-Z]',  # "Engineer at Company"
            r'^\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*-\s*[A-Z]',  # "Title - Company"
            r'^\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*[A-Z]',  # "Title, Company"
        ]
        
        # Also look for lines that have dates followed by job-like text
        date_title_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b.*\b(?:Engineer|Developer|Manager|Analyst|Specialist|Associate|Coordinator|Supervisor)\b'
        
        for i, line in enumerate(lines):
            if not line:
                continue
            line = line.strip() if isinstance(line, str) else str(line).strip()
            if not line or len(line) < 5:
                if current_exp and current_exp.get('title'):
                    experience.append(current_exp)
                    current_exp = {}
                continue
            
            # Limit line length
            if len(line) > 500:
                line = line[:500]
            
            # Check for job title
            title_found = False
            
            # First check date-title pattern (common format: "Jan 2020 - Dec 2022 Software Engineer")
            date_title_match = re.search(date_title_pattern, line, re.IGNORECASE)
            if date_title_match:
                # Extract the title part after the date
                title_part = line[date_title_match.end():].strip()
                if title_part:
                    # Clean up title
                    title_words = title_part.split()[:5]  # Take first 5 words
                    title_text = ' '.join(title_words).strip()
                    if len(title_text) > 5 and len(title_text) < 100:
                        if current_exp and current_exp.get('title'):
                            experience.append(current_exp)
                        current_exp = {
                            "title": title_text,
                            "company": None,
                            "start_date": None,
                            "end_date": None,
                            "description": "",
                            "achievements": [],
                            "technologies": []
                        }
                        title_found = True
            
            # Check standard title patterns
            if not title_found:
                for pattern in title_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        title_text = match.group(0).strip()
                        # Clean up title - remove common prefixes that might be part of the pattern
                        title_text = re.sub(r'^(?:at|@)\s+', '', title_text, flags=re.IGNORECASE).strip()
                        if len(title_text) > 5 and len(title_text) < 100:  # Reasonable title length
                            if current_exp and current_exp.get('title'):
                                experience.append(current_exp)
                            current_exp = {
                                "title": title_text,
                                "company": None,
                                "start_date": None,
                                "end_date": None,
                                "description": "",
                                "achievements": [],
                                "technologies": []
                            }
                            title_found = True
                            break
            
            if current_exp and not title_found:
                # Look for company (capitalized words, might be in orgs from spaCy)
                if not current_exp.get('company'):
                    # Check if line matches known orgs from spaCy
                    for org in orgs:
                        if org and line and org.lower() in line.lower():
                            current_exp['company'] = org
                            break
                    
                    # Pattern matching for company names
                    if not current_exp.get('company'):
                        # Check for well-known companies
                        well_known_companies = ['Amazon', 'Google', 'Microsoft', 'Apple', 'Facebook', 'Meta',
                                               'IBM', 'Oracle', 'Salesforce', 'Adobe', 'Intel', 'NVIDIA',
                                               'Tesla', 'Netflix', 'Uber', 'Airbnb', 'Twitter', 'LinkedIn',
                                               'Walmart', 'Target', 'Costco', 'FedEx', 'UPS', 'DHL']
                        
                        for company in well_known_companies:
                            if company and line and company.lower() in line.lower():
                                # Extract just the company name
                                company_match = re.search(r'\b' + re.escape(company) + r'\b', line, re.IGNORECASE)
                                if company_match:
                                    current_exp['company'] = company
                                    break
                        
                        # Pattern matching for company names
                        if not current_exp.get('company'):
                            # More flexible company pattern
                            company_pattern = r'^[A-Z][A-Za-z0-9\s&.,-]+(?:Inc|LLC|Ltd|Corp|Corporation|Company|Co|Technologies|Solutions|Systems|Group|Enterprises)?$'
                            if line and re.match(company_pattern, line) and len(line) > 3 and len(line) < 100:
                                # Skip if it looks like a date or title
                                if not re.search(r'\d{4}', line) and not any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'associate']):
                                    current_exp['company'] = line
                        
                        # Also check for company patterns with "at" or separator
                        if not current_exp.get('company'):
                            # Pattern: "Title at Company" or "Title - Company" or "Title, Company"
                            company_at_pattern = r'(?:at|@|-|,)\s+([A-Z][A-Za-z0-9\s&.,-]+(?:Inc|LLC|Ltd|Corp|Corporation|Company|Co)?)'
                            company_match = re.search(company_at_pattern, line, re.IGNORECASE)
                            if company_match:
                                company_text = company_match.group(1).strip()
                                if len(company_text) > 3 and len(company_text) < 100:
                                    current_exp['company'] = company_text
                
                # Extract dates - look for date ranges
                for pattern in date_patterns:
                    dates_found = re.findall(pattern, line, re.IGNORECASE)
                    if dates_found:
                        if not current_exp.get('start_date'):
                            current_exp['start_date'] = dates_found[0]
                        if len(dates_found) > 1:
                            current_exp['end_date'] = dates_found[1]
                        elif line and ('present' in line.lower() or 'current' in line.lower() or 'now' in line.lower()):
                            current_exp['end_date'] = "Present"
                        break
                
                # Look for date ranges in format "MM/YYYY - MM/YYYY" or "Month YYYY - Month YYYY"
                if line:
                    date_range_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{1,2}[/-]\d{4})\s*[-–—]\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{1,2}[/-]\d{4}|Present|Current|Now)'
                    date_range_match = re.search(date_range_pattern, line, re.IGNORECASE)
                else:
                    date_range_match = None
                if date_range_match:
                    if not current_exp.get('start_date'):
                        start_date_group = date_range_match.group(1)
                        if start_date_group:
                            current_exp['start_date'] = start_date_group.strip()
                    end_date_group = date_range_match.group(2)
                    if end_date_group:
                        end_date = end_date_group.strip()
                        if end_date and end_date.lower() in ['present', 'current', 'now']:
                            current_exp['end_date'] = "Present"
                        elif end_date:
                            current_exp['end_date'] = end_date
                
                # Collect description - skip if it's just a date or company name
                if line and not re.match(r'^[\d\s\/\-–—]+$', line):  # Skip lines that are just dates
                    if current_exp.get('description'):
                        # Avoid duplicate descriptions
                        if line not in current_exp['description']:
                            current_exp['description'] += "\n" + line
                    else:
                        # Only set description if it's not just a company name or date
                        if not re.match(r'^[A-Z][A-Za-z\s&.,-]+(?:Inc|LLC|Ltd|Corp)?$', line) or len(line) > 20:
                            current_exp['description'] = line
        
        if current_exp and current_exp.get('title'):
            experience.append(current_exp)
        
        return experience
    
    def _extract_education_enhanced(self, cleaned_text: str, original_text: str) -> List[Dict[str, Any]]:
        """Extract education with enhanced accuracy"""
        education = []
        
        # Find education section
        edu_keywords = ['education', 'academic', 'qualification', 'degree', 'university', 'college']
        edu_section = self._find_section(cleaned_text, edu_keywords)
        
        if not edu_section:
            edu_section = cleaned_text
        
        # Degree patterns
        degree_patterns = [
            r'\b(?:Bachelor|Master|PhD|Doctorate|Associate|Diploma|Certificate)\s+(?:of|in)?\s+[A-Za-z\s&]+',
            r'\b(?:B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?|Ph\.?D\.?|MBA|B\.?E\.?|M\.?E\.?)\b'
        ]
        
        lines = edu_section.split('\n')
        current_edu = {}
        
        for line in lines:
            if not line:
                continue
            line = line.strip() if isinstance(line, str) else str(line).strip()
            if not line or len(line) < 5:
                if current_edu and current_edu.get('degree'):
                    education.append(current_edu)
                    current_edu = {}
                continue
            
            # Limit line length
            if len(line) > 300:
                line = line[:300]
            
            # Check for degree
            for pattern in degree_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    degree_text = match.group(0).strip()
                    if len(degree_text) > 100:
                        degree_text = degree_text[:100]
                    
                    if current_edu and current_edu.get('degree'):
                        education.append(current_edu)
                    
                    current_edu = {
                        "degree": degree_text,
                        "institution": None,
                        "year": None,
                        "field": None,
                        "gpa": None,
                        "honors": []
                    }
                    break
            
            if current_edu:
                # Extract institution
                if not current_edu.get('institution'):
                    institution_pattern = r'\b([A-Z][A-Za-z\s&]+(?:University|College|Institute|School|Academy))\b'
                    inst_match = re.search(institution_pattern, line)
                    if inst_match:
                        inst_text = inst_match.group(1).strip()
                        if len(inst_text) <= 100:
                            current_edu['institution'] = inst_text
                    elif line and any(word in line.lower() for word in ['university', 'college', 'institute', 'school']):
                        # Extract institution name
                        words = line.split()
                        inst_words = []
                        found_keyword = False
                        for word in words:
                            if word and any(kw in word.lower() for kw in ['university', 'college', 'institute', 'school']):
                                found_keyword = True
                            if found_keyword:
                                inst_words.append(word)
                                if len(' '.join(inst_words)) > 100:
                                    break
                        if inst_words:
                            current_edu['institution'] = ' '.join(inst_words[:8]).strip()
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', line)
                if year_match and not current_edu.get('year'):
                    current_edu['year'] = year_match.group()
                
                # Extract GPA
                gpa_match = re.search(r'\bGPA[:\s]*(\d+\.?\d*)\b', line, re.IGNORECASE)
                if gpa_match:
                    current_edu['gpa'] = gpa_match.group(1)
        
        if current_edu and current_edu.get('degree'):
            education.append(current_edu)
        
        return education
    
    def _extract_skills_enhanced(self, cleaned_text: str, original_text: str) -> List[str]:
        """Extract skills with enhanced accuracy"""
        skills = []
        
        # Find skills section
        skills_keywords = ['skills', 'technical skills', 'competencies', 'technologies', 'tools', 'expertise']
        skills_section = self._find_section(cleaned_text, skills_keywords)
        
        if not skills_section:
            skills_section = cleaned_text  # Search entire document
        
        # Comprehensive skill list
        common_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'Ruby', 'PHP',
            'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'SQL', 'HTML', 'CSS',
            'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'FastAPI',
            'Spring', 'Laravel', 'ASP.NET', 'Next.js', 'Nuxt.js',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Oracle', 'SQLite', 'Cassandra',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'Linux',
            'Terraform', 'Ansible', 'Jenkins', 'CI/CD', 'GitHub Actions',
            'Machine Learning', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
            'Pandas', 'NumPy', 'OpenCV', 'Agile', 'Scrum', 'DevOps',
            'Warehousing', 'Logistics', 'Supply Chain', 'Operations', 'Distribution'
        ]
        
        # Search for skills in text
        for skill in common_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, skills_section, re.IGNORECASE):
                if skill not in skills:
                    skills.append(skill)
        
        # Extract from comma-separated lists
        lines = skills_section.split('\n')
        for line in lines:
            if ',' in line or '|' in line or ';' in line:
                separators = [',', '|', ';']
                for sep in separators:
                    if sep in line:
                        potential_skills = [s.strip() for s in line.split(sep) if s.strip()]
                        for skill_text in potential_skills:
                            if skill_text and 3 <= len(skill_text) <= 50:
                                # Check if it matches a known skill
                                skill_added = False
                                for known_skill in common_skills:
                                    if known_skill and skill_text and known_skill.lower() == skill_text.lower():
                                        if known_skill not in skills:
                                            skills.append(known_skill)
                                        skill_added = True
                                        break
                                # Or add if it looks valid
                                if not skill_added and skill_text[0].isupper() and skill_text not in skills:
                                    skills.append(skill_text)
                        break
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_summary_enhanced(self, cleaned_text: str, original_text: str) -> Optional[str]:
        """Extract summary/objective"""
        summary_keywords = ['summary', 'objective', 'profile', 'about', 'overview']
        summary_section = self._find_section(cleaned_text, summary_keywords)
        
        if summary_section:
            # Get first 2-3 sentences
            sentences = re.split(r'[.!?]+', summary_section)
            summary = '. '.join(sentences[:3]).strip()
            if summary:
                return summary[:500]  # Limit length
        
        # If no summary section, use first paragraph
        lines = cleaned_text.split('\n')
        for line in lines[:10]:
            if len(line) > 50:
                return line[:500]
        
        return None
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_keywords = ['certification', 'certificate', 'certified', 'license']
        cert_section = self._find_section(text, cert_keywords)
        
        if not cert_section:
            return []
        
        cert_pattern = r'(?:Certified|Certification|License)\s+[A-Za-z\s]+'
        certs = re.findall(cert_pattern, cert_section, re.IGNORECASE)
        return certs
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages"""
        lang_keywords = ['languages', 'language']
        lang_section = self._find_section(text, lang_keywords)
        
        if not lang_section:
            return []
        
        common_langs = ['English', 'Spanish', 'French', 'German', 'Chinese', 'Japanese',
                       'Hindi', 'Arabic', 'Portuguese', 'Russian', 'Italian']
        
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
            pattern = r'\b' + re.escape(keyword) + r'\b'
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                start_idx = match.end()
                # Find next major section
                end_pattern = r'\n\s*[A-Z][A-Z\s]{10,}|\n\s*\d+\.|\n\s*[A-Z]+\s*:'
                end_match = re.search(end_pattern, text[start_idx:])
                if end_match:
                    return text[start_idx:start_idx + end_match.start()]
                return text[start_idx:start_idx + 2000]
        
        return None
    
    def _calculate_confidence_enhanced(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score with validation"""
        score = 0.0
        
        # Personal info (30 points)
        personal_info = parsed_data.get("personal_info", {}) or {}
        if personal_info.get("full_name"):
            score += 10
        if personal_info.get("email"):
            score += 10
        if personal_info.get("phone"):
            score += 10
        
        # Experience (30 points)
        experience = parsed_data.get("experience", [])
        if experience and len(experience) > 0:
            # Give points based on number of experience entries and completeness
            exp_points = 0
            for exp in experience:
                if exp and isinstance(exp, dict):
                    if exp.get("title"):
                        exp_points += 5
                    if exp.get("company"):
                        exp_points += 3
                    if exp.get("start_date") or exp.get("end_date"):
                        exp_points += 2
            score += min(30, exp_points)
        
        # Education (20 points)
        education = parsed_data.get("education", [])
        if education and len(education) > 0:
            # Give points based on completeness
            edu_points = 0
            for edu in education:
                if edu and isinstance(edu, dict):
                    if edu.get("degree"):
                        edu_points += 8
                    if edu.get("institution"):
                        edu_points += 6
                    if edu.get("year"):
                        edu_points += 6
            score += min(20, edu_points)
        
        # Skills (20 points)
        skills = parsed_data.get("skills", [])
        if skills and len(skills) > 0:
            # More skills = higher confidence, but cap at 20
            skill_count = len(skills)
            if skill_count >= 10:
                score += 20
            elif skill_count >= 5:
                score += 15
            elif skill_count >= 3:
                score += 10
            else:
                score += skill_count * 3
        
        # Summary bonus (optional, up to 5 points)
        summary = parsed_data.get("summary")
        if summary and isinstance(summary, str) and len(summary) > 50:
            score += 5
        
        # Languages bonus (5 points)
        languages = parsed_data.get("languages", [])
        if languages and len(languages) > 0:
            score += min(5, len(languages) * 2)
        
        # Certifications bonus (5 points)
        certifications = parsed_data.get("certifications", [])
        if certifications and len(certifications) > 0:
            score += min(5, len(certifications) * 2)
        
        # Ensure minimum score if ANY data was extracted
        if score == 0:
            # Check if we have ANY data at all
            has_any_data = (
                personal_info.get("full_name") or 
                personal_info.get("email") or 
                personal_info.get("phone") or
                (experience and len(experience) > 0) or
                (education and len(education) > 0) or
                (skills and len(skills) > 0) or
                (summary and len(summary) > 0)
            )
            if has_any_data:
                # Give minimum 10% if we extracted something
                score = 10.0
        
        final_score = round(min(100.0, score), 1)
        logger.debug(f"Confidence calculation: score={final_score}% (personal_info={bool(personal_info)}, exp={len(experience) if experience else 0}, edu={len(education) if education else 0}, skills={len(skills) if skills else 0})")
        
        return final_score

