# Architecture Documentation

**Intelligent Resume Parser - AI-Powered Resume Analysis & Extraction Platform**  
**GEMINI SOLUTION**

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web UI     │  │  Mobile App  │  │  API Client  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   FastAPI API   │
                    │  (Port 8000)    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼──────┐    ┌──────▼──────┐    ┌─────▼──────┐
    │   Resume   │    │  Document   │    │   AI/NLP   │
    │  Service   │    │ Processor   │    │  Services  │
    └─────┬──────┘    └──────┬──────┘    └─────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │   PostgreSQL    │
                    │   / SQLite      │
                    └─────────────────┘
```

## Component Architecture

### 1. API Layer (`app/api/`)

**Purpose:** RESTful API endpoints for all operations

**Components:**
- `app/api/v1/resume.py` - Resume CRUD operations
- `app/api/v1/status.py` - Processing status endpoints
- `app/api/v1/job_matching.py` - Job matching endpoints

**Responsibilities:**
- Request validation
- Response formatting
- Error handling
- Authentication (future)

### 2. Service Layer (`app/services/`)

**Purpose:** Business logic and orchestration

**Components:**

#### Document Processor (`document_processor.py`)
- Extracts text from multiple file formats
- Supports: PDF, DOCX, TXT, Images (OCR)
- Handles file validation and size limits
- Returns extracted text and file metadata

#### AI Parser (`enhanced_parser.py`, `ai_parser.py`)
- Multi-strategy extraction using:
  - spaCy NLP models
  - Hugging Face Transformers
  - Regex patterns
  - Voting/consensus mechanism
- Extracts: Personal info, Experience, Education, Skills
- Confidence scoring

#### Resume Service (`resume_service.py`)
- Orchestrates the parsing workflow
- Coordinates document processing and AI parsing
- Manages database operations
- Returns formatted responses

#### Additional Services:
- `bias_detection_service.py` - Detects bias in resumes
- `anonymization_service.py` - Removes PII
- `classification_service.py` - Job role classification
- `matching_service.py` - Job-resume matching
- `llm_service.py` - LLM-powered insights
- `response_formatter.py` - Standardizes response format

### 3. Database Layer (`app/db/`)

**Purpose:** Data persistence and management

**Components:**
- `database.py` - Database connection and session management
- `models.py` - SQLAlchemy ORM models

**Models:**
- `Resume` - Main resume record
- `ParsedResumeData` - Structured parsed data

**Database Options:**
- SQLite (default, for development)
- PostgreSQL (production)

### 4. Core Configuration (`app/core/`)

**Purpose:** Application settings and configuration

**Components:**
- `config.py` - Environment-based configuration
- `logging_config.py` - Logging setup

## Data Flow

### Resume Upload Flow

```
1. Client Upload
   ↓
2. API Endpoint (POST /api/v1/resumes/upload)
   ↓
3. File Validation (size, type)
   ↓
4. Document Processor
   ├─ Extract text from file
   ├─ OCR for images
   └─ Return text + metadata
   ↓
5. AI Parser
   ├─ Preprocess text
   ├─ Extract entities (NER)
   ├─ Parse sections
   └─ Structure data
   ↓
6. Resume Service
   ├─ Calculate confidence
   ├─ Apply enhancements
   ├─ Save to database
   └─ Format response
   ↓
7. Return to Client
```

### Job Matching Flow

```
1. Client Request (POST /api/v1/resumes/{id}/match)
   ↓
2. Retrieve Resume Data
   ↓
3. Matching Service
   ├─ Extract skills from resume
   ├─ Extract skills from job description
   ├─ Calculate skill match %
   ├─ Calculate experience match
   ├─ Calculate semantic similarity
   └─ Generate overall score
   ↓
4. Return Matching Results
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations

### AI/ML
- **spaCy** - NLP library for entity recognition
- **Hugging Face Transformers** - Pre-trained models
- **PyTorch** - Deep learning framework
- **Sentence Transformers** - Semantic similarity

### Document Processing
- **PyPDF2/pdfplumber** - PDF text extraction
- **python-docx** - DOCX processing
- **Tesseract OCR** - Image text extraction
- **Pillow** - Image processing

### Database
- **PostgreSQL** - Production database
- **SQLite** - Development database

### Frontend
- **HTML/CSS/JavaScript** - Web interface
- **Font Awesome** - Icons
- **LocalStorage** - Client-side data storage

## Scalability Considerations

### Horizontal Scaling
- Stateless API design allows multiple instances
- Load balancer can distribute requests
- Database connection pooling

### Performance Optimization
- Lazy loading of AI models
- Text chunking for large documents
- Caching of parsed results
- Async processing for heavy operations

### Resource Management
- Model caching to reduce memory usage
- File size limits (10MB)
- Connection pooling for database

## Security Architecture

### File Upload Security
- File type validation
- File size limits (10MB)
- Content scanning

### Data Protection
- PII anonymization
- Bias detection
- Secure database connections

### API Security
- CORS configuration
- Input validation
- SQL injection protection
- XSS prevention

## Deployment Architecture

### Development
- SQLite database (no setup required)
- Single server instance
- Local file storage

### Production
- PostgreSQL database (Docker)
- Multiple API instances (scalable)
- Persistent storage volumes
- Reverse proxy (Nginx)
- HTTPS/SSL

## Monitoring & Logging

### Health Checks
- `/health` - Basic health check
- `/api/v1/resumes/health/check` - Detailed health

### Logging
- Application logs
- Error tracking
- Performance metrics

### Metrics
- Processing time
- Confidence scores
- Success/failure rates

## Future Enhancements

1. **Authentication** - JWT tokens, OAuth
2. **Rate Limiting** - Prevent abuse
3. **Caching** - Redis for performance
4. **Queue System** - Async job processing
5. **Multi-language Support** - International resumes
6. **Cloud Storage** - S3 for file storage
7. **Microservices** - Split into services

---

**Developer:** JAYANT SHARMA  
**Roll No:** CO24529  
**Email:** co24529@ccet.ac.in  
**Organization:** GEMINI SOLUTION

