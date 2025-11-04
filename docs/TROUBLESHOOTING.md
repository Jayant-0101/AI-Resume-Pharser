# Troubleshooting Guide

## Localhost Not Working

### Common Issues and Solutions

#### 1. Server Won't Start

**Error**: `Address already in use` or `Port 8000 is already in use`

**Solution**:
```bash
# Find what's using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Kill the process or use a different port:
uvicorn app.main:app --reload --port 8001
```

#### 2. Database Connection Error

**Error**: `could not connect to server` or `connection refused`

**Solutions**:

**Option A: Start PostgreSQL with Docker**
```bash
docker-compose up -d db
# Wait 30 seconds for database to be ready
```

**Option B: Use SQLite for Development**
Create `.env` file:
```env
DATABASE_URL=sqlite:///./resume_parser.db
```

**Option C: Check Database Credentials**
Verify `.env` file has correct connection string:
```env
DATABASE_URL=postgresql://resume_user:resume_pass@localhost:5432/resume_parser
```

#### 3. Missing Dependencies

**Error**: `ModuleNotFoundError` or `No module named 'fastapi'`

**Solution**:
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### 4. spaCy Model Not Found

**Error**: `Can't find model 'en_core_web_sm'`

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

#### 5. Import Errors

**Error**: `ImportError` or `cannot import name`

**Solution**:
1. Ensure you're in the project root directory
2. Check Python path includes the project directory
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

#### 6. Tesseract OCR Not Found (Windows)

**Error**: `TesseractNotFoundError`

**Solution**:
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install it
3. Add to PATH or set environment variable:
   ```bash
   setx TESSDATA_PREFIX "C:\Program Files\Tesseract-OCR\tessdata"
   ```

## Quick Diagnostic Steps

### Step 1: Check Python Version
```bash
python --version
# Should be 3.11 or higher
```

### Step 2: Check Dependencies
```bash
python -c "import fastapi, uvicorn, sqlalchemy; print('All OK')"
```

### Step 3: Check Database
```bash
# Using Docker
docker-compose ps
# Should show 'db' container as 'Up'

# Or test connection
python -c "from app.db.database import engine; from sqlalchemy import text; engine.connect().execute(text('SELECT 1'))"
```

### Step 4: Run Diagnostic Script
```bash
python run_local.py
```

## Using the Diagnostic Script

The `run_local.py` script will:
- Check all dependencies
- Verify database connection
- Check spaCy model
- Start the server with proper error messages

```bash
python run_local.py
```

## Alternative: Use Docker

If local setup is problematic, use Docker:

```bash
# Start everything
docker-compose up -d

# Check logs
docker-compose logs -f api

# Access API
# http://localhost:8000/docs
```

## Windows-Specific Issues

### PowerShell Execution Policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Path Issues
Ensure Python and pip are in your PATH:
```powershell
python --version
pip --version
```

## Getting Help

1. Check logs in terminal output
2. Check `docker-compose logs` if using Docker
3. Verify `.env` file exists and has correct values
4. Try running `python run_local.py` for diagnostics

## Common Error Messages

### "Could not connect to database"
- Start PostgreSQL: `docker-compose up -d db`
- Check DATABASE_URL in `.env`

### "Address already in use"
- Port 8000 is busy, use different port or kill existing process

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`

### "spaCy model not found"
- Download model: `python -m spacy download en_core_web_sm`



