# Project Organization

This document describes the organized structure of the Resume Parser project.

## Root Directory Structure

```
resume-parser/
├── README.md                    # Main documentation and setup guide
├── .env.example                 # Environment configuration template
├── setup.sh                     # Complete setup automation script
├── setup.ps1                    # Windows PowerShell setup script
├── start.py                     # Main startup script (redirects to simple_start)
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── requirements-minimal.txt     # Minimal dependencies
├── alembic.ini                  # Database migration configuration
├── Makefile                     # Make commands
├── .gitignore                   # Git ignore rules
│
├── app/                         # Main application package
│   ├── main.py                  # FastAPI application entry point
│   ├── api/                     # API routes
│   ├── core/                    # Configuration
│   ├── db/                      # Database models
│   └── services/                # Business logic
│
├── scripts/                     # Utility scripts
│   ├── startup/                 # Server startup scripts
│   │   ├── simple_start.py      # Recommended startup script
│   │   ├── fast_start.py        # Fast startup
│   │   ├── start_server.py       # Standard startup
│   │   ├── run_local.py         # Local startup
│   │   ├── start_server.bat     # Windows startup
│   │   └── start_server.sh      # Linux/Mac startup
│   ├── init_db.py               # Initialize database
│   ├── create_sample_data.py    # Create sample data
│   ├── reset_ids.py             # Reset document IDs
│   ├── reset_db.py              # Reset database
│   ├── install_enhanced_parser.bat
│   ├── install_windows.bat
│   └── check_spacy.py
│
├── tests/                        # Test files
│   ├── test_api.py              # API tests
│   └── test_server.py           # Server tests
│
├── static/                       # Frontend files
│   ├── index.html               # Main web interface
│   ├── dashboard.html           # Dashboard page
│   ├── script.js                # Frontend JavaScript
│   ├── dashboard.js             # Dashboard JavaScript
│   ├── styles.css               # Main stylesheet
│   ├── dashboard.css            # Dashboard stylesheet
│   └── theme.js                 # Theme toggle
│
├── docs/                         # Documentation
│   ├── api-specification.yaml   # OpenAPI 3.1 specification
│   ├── architecture.md          # System architecture
│   ├── deployment-guide.md      # Deployment instructions
│   ├── PROJECT_STRUCTURE.md      # Project structure details
│   ├── USAGE.md                 # Usage examples
│   ├── TROUBLESHOOTING.md       # Troubleshooting guide
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   └── archive/                 # Archived development docs
│       └── [old development files]
│
├── docker/                       # Docker configuration
│   ├── Dockerfile               # Docker image definition
│   └── docker-compose.yml      # Docker Compose configuration
│
├── alembic/                      # Database migrations
│   ├── env.py
│   └── script.py.mako
│
└── models/                       # AI model cache (gitignored)
```

## Quick Start

### Start Server

```bash
# Recommended
python start.py

# Or directly
python scripts/startup/simple_start.py
```

### Setup Project

```bash
# Linux/Mac
chmod +x setup.sh
./setup.sh

# Windows
.\setup.ps1
```

## Key Directories

### `/app`
Main application code - FastAPI routes, services, database models

### `/scripts`
- `/startup` - Server startup scripts
- Utility scripts for database, testing, installation

### `/docs`
- Current documentation
- `/archive` - Old development documentation (for reference only)

### `/static`
Frontend web interface files

### `/docker`
Docker configuration files

### `/tests`
Test files for API and server functionality

## File Organization Principles

1. **Root Directory**: Only essential files for quick access
2. **Scripts**: All utility scripts organized by purpose
3. **Documentation**: Current docs in `/docs`, archived in `/docs/archive`
4. **Docker**: All Docker files in `/docker` folder
5. **Tests**: All test files in `/tests` folder

## Maintenance

- Keep root directory clean with only essential files
- Archive old development docs instead of deleting
- Group related scripts in subdirectories
- Update this document when structure changes

