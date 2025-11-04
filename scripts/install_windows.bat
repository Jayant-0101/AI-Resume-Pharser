@echo off
REM Windows installation script that skips problematic packages

echo Installing Resume Parser dependencies...
echo.

REM Install core packages first (without psycopg2)
echo Step 1: Installing core packages...
pip install fastapi==0.109.0 uvicorn[standard]==0.27.0 python-multipart==0.0.6
pip install sqlalchemy==2.0.25 alembic==1.13.1
pip install pydantic==2.5.3 pydantic-settings==2.1.0 python-dotenv==1.0.1 httpx==0.26.0

echo Step 2: Installing document processing packages...
pip install PyPDF2==3.0.1 pdfplumber==0.10.3 python-docx==1.1.0
pip install pytesseract==0.3.10 Pillow==10.2.0 pdf2image==1.16.3

echo Step 3: Installing AI/ML packages (this may take a while)...
pip install transformers==4.37.2 torch==2.1.2 sentencepiece==0.1.99 spacy==3.7.2

echo Step 4: Downloading spaCy model...
python -m spacy download en_core_web_sm

echo.
echo Installation complete!
echo.
echo Note: Using SQLite database (no PostgreSQL needed for local development)
echo To use PostgreSQL later, install: pip install psycopg2-binary
echo.
echo To start the server, run: python start_server.py

pause



