@echo off
echo ==========================================
echo       API GENERATOR - STARTUP SCRIPT
echo ==========================================

cd /d "%~dp0backend"

:: Check for VENV
if exist venv (
    echo [INFO] Using existing virtual environment.
    set "PYTHON_CMD=venv\Scripts\python.exe"
    set "PIP_CMD=venv\Scripts\pip.exe"
) else (
    echo [INFO] Creating new virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        echo Please ensure Python is installed and accessible.
        pause
        exit /b
    )
    set "PYTHON_CMD=venv\Scripts\python.exe"
    set "PIP_CMD=venv\Scripts\pip.exe"
)

echo [1/3] Installing dependencies...
"%PIP_CMD%" install fastapi uvicorn python-multipart pandas openpyxl jinja2 requests xlsxwriter
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo Try running 'cd backend && venv\Scripts\pip install -r requirements.txt' manually.
    pause
    exit /b
)

echo [2/3] Starting Backend Server (Port 8000)...
start "Backend API" cmd /k "%PYTHON_CMD% -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo [3/3] Starting Frontend Server...
cd ../frontend
start "Frontend UI" cmd /k "npm run dev"

echo ==========================================
echo Servers are launching...
echo Backend: http://localhost:8000/api/template
echo Frontend: http://localhost:5173
echo ==========================================
pause
