# Project Structure

```
resume-parser/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   │
│   ├── api/                      # API routes
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── resume.py         # Resume API endpoints
│   │
│   ├── core/                     # Core configuration
│   │   ├── config.py             # Application settings
│   │   └── logging_config.py     # Logging setup
│   │
│   ├── db/                       # Database layer
│   │   ├── database.py           # Database connection & session
│   │   └── models.py             # SQLAlchemy models
│   │
│   └── services/                 # Business logic services
│       ├── ai_parser.py          # AI-powered resume parsing
│       ├── document_processor.py # Document text extraction
│       └── resume_service.py     # Resume processing service
│
├── alembic/                      # Database migrations
│   ├── env.py
│   └── script.py.mako
│
├── scripts/                      # Utility scripts
│   ├── init_db.py                # Initialize database
│   └── create_sample_data.py     # Create sample data
│
├── tests/                        # Test files
│   ├── __init__.py
│   └── test_api.py               # API tests
│
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker image definition
├── requirements.txt              # Python dependencies
├── alembic.ini                   # Alembic configuration
├── Makefile                      # Make commands
├── .gitignore                    # Git ignore rules
│
├── README.md                     # Main documentation
├── USAGE.md                      # Usage examples
├── CONTRIBUTING.md               # Contribution guidelines
└── PROJECT_STRUCTURE.md          # This file
```

## Key Components

### API Layer (`app/api/`)
- RESTful endpoints for resume operations
- Request/response validation
- Error handling

### Services Layer (`app/services/`)
- **DocumentProcessor**: Extracts text from PDF, DOCX, TXT, images
- **AIParser**: Uses NLP/ML to parse resume text into structured data
- **ResumeService**: Orchestrates the parsing workflow

### Database Layer (`app/db/`)
- SQLAlchemy models for data persistence
- Database connection management
- Migrations via Alembic

### Configuration (`app/core/`)
- Environment-based configuration
- Logging setup
- Application settings

## Data Flow

1. **Upload**: Client sends resume file → API endpoint
2. **Extract**: DocumentProcessor extracts text from file
3. **Parse**: AIParser extracts structured data from text
4. **Store**: ResumeService saves to database
5. **Return**: API returns parsed data to client

## Technology Stack

- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM for database operations
- **Hugging Face Transformers**: AI/ML models
- **spaCy**: NLP library
- **PyPDF2/pdfplumber**: PDF processing
- **python-docx**: DOCX processing
- **Tesseract OCR**: Image text extraction
- **Docker**: Containerization

