# PowerShell setup script for resume parser

Write-Host "Setting up Intelligent Resume Parser..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
Write-Host "Downloading spaCy model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your configuration" -ForegroundColor Yellow
}

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "2. Start PostgreSQL: docker-compose up -d db"
Write-Host "3. Run migrations: alembic upgrade head"
Write-Host "4. Start server: uvicorn app.main:app --reload"

