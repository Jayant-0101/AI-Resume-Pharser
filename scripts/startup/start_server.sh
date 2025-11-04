#!/bin/bash
# Linux/Mac script to start the server

echo "Starting Intelligent Resume Parser..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://resume_user:resume_pass@localhost:5432/resume_parser
ENVIRONMENT=development
EOF
fi

# Start database if not running
docker-compose up -d db

# Wait a moment for database
sleep 5

# Start server
echo
echo "Starting server on http://localhost:8000"
echo "Press CTRL+C to stop"
echo
python run_local.py



