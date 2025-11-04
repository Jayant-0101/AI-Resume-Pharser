#!/bin/bash

################################################################################
# Intelligent Resume Parser - Complete Setup Script
# GEMINI SOLUTION - AI-Powered Resume Analysis & Extraction Platform
#
# This script automates the complete setup of the Resume Parser project
# after cloning from git repository.
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
#
# Requirements:
#   - Python 3.8 or higher
#   - pip (Python package manager)
#   - Internet connection (for downloading packages)
#
# Compatible with: Linux, macOS, Windows (Git Bash / WSL)
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="venv"
PYTHON_MIN_VERSION="3.8"
PROJECT_NAME="Intelligent Resume Parser"

# Print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    print_header "Step 1: Checking Python Installation"
    
    if ! command_exists python3 && ! command_exists python; then
        print_error "Python is not installed!"
        echo ""
        echo "Please install Python 3.8 or higher from:"
        echo "  https://www.python.org/downloads/"
        exit 1
    fi
    
    # Determine python command
    if command_exists python3; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    # Check version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    print_info "Found Python version: $PYTHON_VERSION"
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python version check passed: $PYTHON_VERSION"
}

# Check required files
check_project_files() {
    print_header "Step 2: Verifying Project Files"
    
    REQUIRED_FILES=("requirements.txt" "simple_start.py" "app/main.py")
    MISSING_FILES=()
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            MISSING_FILES+=("$file")
        else
            print_success "Found: $file"
        fi
    done
    
    if [ ${#MISSING_FILES[@]} -ne 0 ]; then
        print_error "Missing required files:"
        for file in "${MISSING_FILES[@]}"; do
            echo "  - $file"
        done
        echo ""
        print_error "Please ensure you're in the project root directory"
        exit 1
    fi
    
    print_success "All required project files found"
}

# Create virtual environment
create_venv() {
    print_header "Step 3: Creating Virtual Environment"
    
    if [ -d "$VENV_NAME" ]; then
        print_warning "Virtual environment '$VENV_NAME' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf "$VENV_NAME"
        else
            print_info "Using existing virtual environment"
            return
        fi
    fi
    
    print_info "Creating virtual environment: $VENV_NAME"
    $PYTHON_CMD -m venv "$VENV_NAME"
    
    if [ ! -d "$VENV_NAME" ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment created successfully"
}

# Activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source "$VENV_NAME/bin/activate"
    
    # Verify activation
    if [ -z "$VIRTUAL_ENV" ]; then
        print_error "Failed to activate virtual environment"
        exit 1
    fi
    
    print_success "Virtual environment activated"
    print_info "Python path: $(which python)"
}

# Upgrade pip
upgrade_pip() {
    print_header "Step 4: Upgrading pip"
    
    print_info "Upgrading pip to latest version..."
    pip install --upgrade pip --quiet
    
    PIP_VERSION=$(pip --version | awk '{print $2}')
    print_success "pip upgraded to version: $PIP_VERSION"
}

# Install dependencies
install_dependencies() {
    print_header "Step 5: Installing Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        exit 1
    fi
    
    print_info "Installing packages from requirements.txt..."
    print_warning "This may take 2-5 minutes depending on your internet connection..."
    
    if pip install -r requirements.txt; then
        print_success "All dependencies installed successfully"
    else
        print_error "Failed to install some dependencies"
        print_warning "You can try installing manually: pip install -r requirements.txt"
        exit 1
    fi
}

# Install spaCy model (optional)
install_spacy_model() {
    print_header "Step 6: Installing spaCy Model (Optional)"
    
    if ! python -c "import spacy" 2>/dev/null; then
        print_warning "spaCy not installed, skipping model download"
        print_info "The application will work without spaCy, but with enhanced accuracy if installed"
        return
    fi
    
    print_info "Downloading spaCy English model (en_core_web_sm)..."
    print_info "This may take a few minutes..."
    
    if python -m spacy download en_core_web_sm --quiet 2>/dev/null; then
        print_success "spaCy model downloaded successfully"
    else
        print_warning "Failed to download spaCy model (this is optional)"
        print_info "You can install it later with: python -m spacy download en_core_web_sm"
    fi
}

# Create .env file
create_env_file() {
    print_header "Step 7: Creating Configuration File"
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing .env file"
            return
        fi
    fi
    
    print_info "Creating .env file with default configuration..."
    
    cat > .env << EOF
# Database Configuration
# Default: SQLite (no setup required)
# For PostgreSQL, uncomment and configure:
# DATABASE_URL=postgresql://user:password@localhost:5432/resume_parser
DATABASE_URL=sqlite:///./resume_parser.db

# Environment
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Model Cache Directory
MODEL_CACHE_DIR=./models

# GPU Support (set to true if you have CUDA installed)
USE_GPU=false
EOF
    
    print_success ".env file created with default settings"
    print_info "You can edit .env to customize configuration"
}

# Verify installation
verify_installation() {
    print_header "Step 8: Verifying Installation"
    
    print_info "Checking installed packages..."
    
    # Check critical packages
    CRITICAL_PACKAGES=("fastapi" "uvicorn" "sqlalchemy" "pydantic")
    MISSING_PACKAGES=()
    
    for package in "${CRITICAL_PACKAGES[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            print_success "$package is installed"
        else
            MISSING_PACKAGES+=("$package")
            print_error "$package is missing"
        fi
    done
    
    if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
        print_error "Some critical packages are missing!"
        print_info "Try reinstalling: pip install -r requirements.txt"
        exit 1
    fi
    
    # Test app import
    print_info "Testing application import..."
    if python -c "from app.main import app" 2>/dev/null; then
        print_success "Application module imports successfully"
    else
        print_error "Failed to import application module"
        exit 1
    fi
    
    print_success "Installation verification complete"
}

# Print next steps
print_next_steps() {
    print_header "Setup Complete!"
    
    echo -e "${GREEN}✓${NC} All setup steps completed successfully!"
    echo ""
    echo "Next steps to run the application:"
    echo ""
    echo "1. Activate virtual environment:"
    echo "   ${BLUE}source $VENV_NAME/bin/activate${NC}"
    echo ""
    echo "2. Start the server:"
    echo "   ${BLUE}python simple_start.py${NC}"
    echo ""
    echo "   Or manually:"
    echo "   ${BLUE}uvicorn app.main:app --host 0.0.0.0 --port 8000${NC}"
    echo ""
    echo "3. Open your browser and visit:"
    echo "   ${BLUE}http://localhost:8000${NC}"
    echo ""
    echo "4. API Documentation:"
    echo "   ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo "5. Run tests (optional):"
    echo "   ${BLUE}python test_api.py${NC}"
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "For more information, see README.md"
    echo ""
    echo -e "${GREEN}Happy coding!${NC}"
    echo ""
}

# Main execution
main() {
    clear
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                                               ║${NC}"
    echo -e "${BLUE}║          ${GREEN}$PROJECT_NAME${BLUE}          ║${NC}"
    echo -e "${BLUE}║                    ${YELLOW}Complete Setup Script${BLUE}                           ║${NC}"
    echo -e "${BLUE}║                                                                               ║${NC}"
    echo -e "${BLUE}║                    ${YELLOW}GEMINI SOLUTION${BLUE}                                ║${NC}"
    echo -e "${BLUE}║                                                                               ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Run setup steps
    check_python_version
    check_project_files
    create_venv
    activate_venv
    upgrade_pip
    install_dependencies
    install_spacy_model
    create_env_file
    verify_installation
    print_next_steps
}

# Run main function
main
