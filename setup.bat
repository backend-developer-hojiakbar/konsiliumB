@echo off
REM Konsilium Backend Setup Script for Windows

echo ================================
echo Konsilium Backend Setup
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo Dependencies installed successfully
) else (
    echo Failed to install dependencies
    exit /b 1
)
echo.

REM Setup environment file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo .env file created
    echo Please edit .env file with your configuration
) else (
    echo .env file already exists
)
echo.

REM Database check
echo Checking database configuration...
echo Make sure PostgreSQL is running and database 'konsilium_db' exists
echo.

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate
if %errorlevel% equ 0 (
    echo Migrations completed successfully
) else (
    echo Migration failed. Please check database configuration
    exit /b 1
)
echo.

REM Create superuser prompt
set /p response="Would you like to create a superuser? (y/n): "
if /i "%response%"=="y" (
    python manage.py createsuperuser
)
echo.

REM Success message
echo ================================
echo Setup completed successfully!
echo ================================
echo.
echo To start the development server:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run server: python manage.py runserver
echo.
echo API will be available at: http://localhost:8000
echo Admin panel: http://localhost:8000/admin
echo API Documentation: http://localhost:8000/swagger/
echo.

pause
