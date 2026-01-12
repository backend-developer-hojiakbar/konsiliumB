#!/bin/bash

# Konsilium Backend Setup Script

echo "================================"
echo "Konsilium Backend Setup"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $python_version found${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}→ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}→ Please edit .env file with your configuration${NC}"
else
    echo -e "${YELLOW}→ .env file already exists${NC}"
fi
echo ""

# Database check
echo "Checking database configuration..."
echo -e "${YELLOW}→ Make sure PostgreSQL is running and database 'konsilium_db' exists${NC}"
echo ""

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations completed successfully${NC}"
else
    echo -e "${RED}✗ Migration failed. Please check database configuration${NC}"
    exit 1
fi
echo ""

# Create superuser prompt
echo "Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi
echo ""

# Success message
echo "================================"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "================================"
echo ""
echo "To start the development server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run server: python manage.py runserver"
echo ""
echo "API will be available at: http://localhost:8000"
echo "Admin panel: http://localhost:8000/admin"
echo "API Documentation: http://localhost:8000/swagger/"
echo ""
