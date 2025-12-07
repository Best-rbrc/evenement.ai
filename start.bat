@echo off
REM AI Event Planner - One-Command Startup Script (Windows)
REM This script validates environment configuration and launches both frontend and backend

setlocal enabledelayedexpansion

REM Load environment variables from .env file
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" (
            if not "%%a:~0,1%"=="#" (
                set "%%a=%%b"
            )
        )
    )
)

REM Colors (Windows 10+)
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   AI Event Planner - Startup Script (Windows)             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ========================================================================
REM 1. CHECK REQUIRED ENVIRONMENT VARIABLES
REM ========================================================================
echo [1/5] Checking environment variables...
echo.

set MISSING_VARS=
if "%OPENAI_API_KEY%"=="" (
    echo X OPENAI_API_KEY - Not set
    set MISSING_VARS=1
) else (
    set "KEY_PREVIEW=!OPENAI_API_KEY:~0,4!...!OPENAI_API_KEY:~-4!"
    echo ✓ OPENAI_API_KEY - !KEY_PREVIEW!
)

if "%TALLY_API_KEY%"=="" (
    echo ⚠ TALLY_API_KEY - Not set (Optional, form creation will not work)
) else (
    set "KEY_PREVIEW=!TALLY_API_KEY:~0,4!...!TALLY_API_KEY:~-4!"
    echo ✓ TALLY_API_KEY - !KEY_PREVIEW!
)

echo.

if not "!MISSING_VARS!"=="" (
    echo ERROR: Missing required environment variables!
    echo.
    echo Please set:
    echo   set OPENAI_API_KEY=your-key-here
    echo.
    pause
    exit /b 1
)

REM ========================================================================
REM 2. CHECK PYTHON ENVIRONMENT
REM ========================================================================
echo [2/5] Checking Python environment...
echo.

if not exist "%SCRIPT_DIR%.venv" (
    echo Creating Python virtual environment...
    python -m venv "%SCRIPT_DIR%.venv"
)

call "%SCRIPT_DIR%.venv\Scripts\activate.bat"
echo ✓ Python venv activated
echo.

REM ========================================================================
REM 3. CHECK NODE/NPM ENVIRONMENT
REM ========================================================================
echo [3/5] Checking Node.js environment...
echo.

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Node.js not found. Please install Node.js v16 or higher
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo ✓ Node.js - %NODE_VERSION%

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X npm not found.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i
echo ✓ npm - %NPM_VERSION%

if not exist "%SCRIPT_DIR%frontend\node_modules" (
    echo Installing frontend dependencies...
    cd "%SCRIPT_DIR%frontend"
    call npm install
    cd "%SCRIPT_DIR%"
    echo ✓ Frontend dependencies installed
) else (
    echo ✓ Frontend dependencies - Already installed
)

echo.

REM ========================================================================
REM 4. CHECK FRONTEND CONFIGURATION
REM ========================================================================
echo [4/5] Checking frontend configuration...
echo.

if not exist "%SCRIPT_DIR%frontend\.env" (
    echo Creating frontend .env file...
    (
        echo VITE_API_BASE_URL=http://localhost:8000
    ) > "%SCRIPT_DIR%frontend\.env"
    echo ✓ Frontend .env created
) else (
    echo ✓ Frontend .env exists
)

echo.

REM ========================================================================
REM 5. FINAL VALIDATION
REM ========================================================================
echo [5/5] Final validation...
echo.
echo ✓ All checks passed!
echo.

REM ========================================================================
REM START SERVICES
REM ========================================================================
echo ╔════════════════════════════════════════════════════════════╗
echo ║   Starting services...                                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Start Backend in new window
echo Starting Backend (port 8000)...
start "AI Event Planner - Backend" cmd /k "cd /d "%SCRIPT_DIR%" && call .venv\Scripts\activate.bat && uvicorn server:app --reload --port 8000"
timeout /t 2 /nobreak

REM Start Frontend in new window
echo Starting Frontend (port 8081)...
start "AI Event Planner - Frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && call npm run dev"
timeout /t 3 /nobreak

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   All services running!                                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:8081
echo.
echo Close the windows above to stop the services.
echo.
pause
