@echo off
REM Windows batch script to start the server

echo Starting Intelligent Resume Parser...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
) else (
    call venv\Scripts\activate.bat
)

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    echo DATABASE_URL=postgresql://resume_user:resume_pass@localhost:5432/resume_parser > .env
    echo ENVIRONMENT=development >> .env
)

REM Start database if not running
docker-compose up -d db

REM Wait a moment for database
timeout /t 5 /nobreak >nul

REM Start server
echo.
echo Starting server on http://localhost:8000
echo Press CTRL+C to stop
echo.
python run_local.py



