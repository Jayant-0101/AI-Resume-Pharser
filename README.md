DOCKER AND DOCS AND TEST FILE IS MAIN BRANCH IT SELF AND REST THERE IS README FILE IN MASTER BRANCH GO THROUGH IT ONCE FOR COMPLETE SETUP AND SETUP.SH FILE IS ALSO AVILABLE IN MASTER BRANCH ITSLEF
 link for the resumes used in videos-https://drive.google.com/drive/folders/1xkV_OCH2Rpdc24wHHWUqZpTqAvklZtIB?usp=sharing

LINK FOR VIDEO TUTORIAL AND WALKTHROUGH-https://drive.google.com/file/d/1PDv4yp3-LqbtD4w9j57D7HSafXnCVNm2/view?usp=sharing
Link For PPT: https://www.canva.com/design/DAG3xJq7CoM/lO9HHpYPIfuACzki6NP04g/edit?utm_content=DAG3xJq7CoM&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton




# Intelligent Resume Parser - Step-by-Step Setup Guide

**AI-Powered Resume Analysis & Extraction Platform by GEMINI SOLUTION**

This guide will walk you through setting up and running the Resume Parser application on your computer.

---

## 📋 Prerequisites

Before starting, ensure you have:

1. **Python 3.8 or higher** installed
   - Check version: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Internet connection** (for downloading dependencies)

3. **A terminal/command prompt** (PowerShell on Windows, Terminal on Mac/Linux)

---

## 🚀 Step-by-Step Installation

### Step 1: Navigate to Project Directory

Open your terminal/command prompt and navigate to the project folder:

**Windows (PowerShell):**
```powershell
cd "C:\Users\lenovo\Documents\resume parser"
```

**Windows (Command Prompt):**
```cmd
cd "C:\Users\lenovo\Documents\resume parser"
```

**Mac/Linux:**
```bash
cd ~/path/to/resume-parser
```

**Verify:** You should see files like `simple_start.py`, `requirements.txt`, and `app/` folder.

**Quick check (Windows PowerShell):**
```powershell
Test-Path simple_start.py
```
**Expected:** `True`

**Quick check (Mac/Linux):**
```bash
ls simple_start.py
```

---

### Step 2: Check Python Installation

```bash
python --version
```

**Expected output:** `Python 3.8.x` or higher

**If you see an error:**
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

---

### Step 3: Install Required Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

**This will take 2-5 minutes** depending on your internet speed.

**Expected output:** You'll see packages being downloaded and installed.

**If you encounter errors:**
- Try: `python -m pip install -r requirements.txt`
- Or install individually: `pip install fastapi uvicorn sqlalchemy pydantic`

---

### Step 4: Install Optional Dependencies (Recommended)

For enhanced parsing accuracy, install spaCy model:

```bash
python -m spacy download en_core_web_sm
```

**Note:** This is optional. The application works without it, but with better accuracy if installed.

**If spaCy installation fails:**
- The application will still work using basic parsing
- You can skip this step and continue

---

### Step 5: Verify Installation

Check if key packages are installed:

```bash
python -c "import fastapi, uvicorn, sqlalchemy; print('All packages installed successfully!')"
```

**Expected output:** `All packages installed successfully!`

---

## 🏃 Running the Application

### Option A: Simple Start (Recommended)

Use the provided startup script:

```bash
python simple_start.py
```

**Expected output:**
```
============================================================
Starting Resume Parser (Minimal Mode)
============================================================
[OK] Core packages found
[OK] App module loaded
[OK] Created .env file with SQLite

Server starting on http://localhost:8000
API docs: http://localhost:8000/docs
Press CTRL+C to stop
```

---

### Option B: Manual Start

If you prefer to start manually:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## ✅ Verify the Application is Running

### Test 1: Open Web Interface

1. Open your web browser
2. Navigate to: **http://localhost:8000**
3. **Expected:** You should see the "GEMINI SOLUTION" homepage with upload interface

### Test 2: Check API Documentation

1. Navigate to: **http://localhost:8000/docs**
2. **Expected:** You should see Swagger UI with all API endpoints

### Test 3: Health Check

1. Navigate to: **http://localhost:8000/health**
2. **Expected:** You should see: `{"status":"healthy"}`

### Test 4: Test API Endpoint

Open a new terminal and run:

```bash
curl http://localhost:8000/health
```

Or use PowerShell:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

**Expected:** JSON response with `{"status":"healthy"}`

---

## 🧪 Running the Test Suite

To test all API endpoints (Health, Functional, Performance, Security):

```bash
python test_api.py
```

**Expected output:**
```
======================================================================
COMPREHENSIVE API TEST SUITE
======================================================================
Testing API at: http://localhost:8000

======================================================================
1. HEALTH CHECK TESTS
======================================================================
[PASS] Server Availability: Server is accessible (Status: 200)
[PASS] Health Endpoint: Status: 200
[PASS] API Health Check: Status: 200, Service: resume-parser-api

======================================================================
2. FUNCTIONAL TESTS
======================================================================
[PASS] Upload Resume: Resume ID: X, Success: True
[PASS] Get Resume: Status: 200
[PASS] List Resumes: Status: 200
...

======================================================================
[PASS] OVERALL: X/X tests passed (XX.X%)
======================================================================
```

**Test Duration:** Approximately 30-60 seconds

---

## 📤 Testing Resume Upload

### Method 1: Using Web Interface

1. Go to: **http://localhost:8000**
2. Click "Choose a file" or drag and drop a resume file
3. Supported formats: PDF, DOCX, TXT, or images (PNG, JPG)
4. Click "Parse Resume"
5. Wait for processing (usually 2-5 seconds)
6. **Expected:** You'll see parsed information displayed in cards

### Method 2: Using API (cURL)

```bash
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "accept: application/json" \
  -F "file=@path/to/your/resume.pdf"
```

### Method 3: Using Python

Create a file `test_upload.py`:

```python
import requests

with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/resumes/upload',
        files={'file': f}
    )
    print(response.json())
```

Run it:
```bash
python test_upload.py
```

---

## 🔧 Troubleshooting

### Problem 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Problem 2: "Port 8000 is already in use"

**Solution:**
1. Find and stop the process using port 8000:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   
   # Mac/Linux
   lsof -ti:8000 | xargs kill
   ```

2. Or use a different port:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001
   ```

### Problem 3: "Connection refused" or "Cannot connect to server"

**Solution:**
1. Make sure the server is running (check Step 5)
2. Verify you're using the correct URL: `http://localhost:8000`
3. Check if firewall is blocking the connection

### Problem 4: "Database connection error"

**Solution:**
The application uses SQLite by default (no setup needed). If you see database errors:
1. Delete the `.env` file
2. Restart the server (it will create a new SQLite database)

### Problem 5: "spaCy model not found"

**Solution:**
This is optional. The application works without it. To install:
```bash
python -m spacy download en_core_web_sm
```

---

## 📁 Project Structure

```
resume-parser/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   ├── services/           # Business logic
│   ├── db/                # Database models
│   └── main.py           # Application entry point
├── static/                # Web interface files
│   ├── index.html        # Main page
│   ├── dashboard.html    # Dashboard page
│   ├── script.js          # Frontend JavaScript
│   └── styles.css         # Styling
├── requirements.txt       # Python dependencies
├── simple_start.py       # Startup script
├── test_api.py           # API test suite
└── README.md            # This file
```

---

## 🌐 Access Points

Once running, you can access:

- **Main Interface:** http://localhost:8000
- **Dashboard:** http://localhost:8000/dashboard
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **API Health:** http://localhost:8000/api/v1/resumes/health/check

---

## 📊 Features

- ✅ **Multi-Format Support:** PDF, DOCX, TXT, Images (OCR)
- ✅ **AI-Powered Parsing:** Advanced NLP for accurate extraction
- ✅ **Fast Processing:** <5 seconds response time
- ✅ **High Accuracy:** >85% accuracy for core fields
- ✅ **Beautiful UI:** Modern, responsive web interface
- ✅ **Dashboard:** View parsing history
- ✅ **RESTful API:** Complete API for integration

---

## 🛑 Stopping the Server

To stop the server:
1. Go to the terminal where the server is running
2. Press `CTRL + C`
3. Wait for the server to shut down gracefully

---

## 📝 Next Steps

After setup:
1. ✅ Test the web interface
2. ✅ Upload a sample resume
3. ✅ Check the dashboard for history
4. ✅ Review API documentation
5. ✅ Run the test suite

---

## 💡 Tips

- **First run:** May take longer due to model loading
- **Large files:** Processing time increases with file size
- **Multiple uploads:** Each resume is saved in the dashboard
- **Browser cache:** Refresh (F5) if you see old content

---

## 🆘 Need Help?

If you encounter issues:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed
3. Check server logs in the terminal
4. Ensure port 8000 is not in use

---

## 📄 License

This project is part of GEMINI SOLUTION.

**Developer:** JAYANT SHARMA  
**Roll No:** CO24529  
**Email:** co24529@ccet.ac.in

---

**Last Updated:** 2024  
**Version:** 1.0.0




