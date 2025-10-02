@echo off
REM Winter - Snowflake Terminal Client
REM Windows installation script

setlocal enabledelayedexpansion

echo ❄️  Winter - Snowflake Terminal Client
echo Windows Installer
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python version is too old. Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo ✅ Python version is compatible (>= 3.8)

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --user snowflake-connector-python>=3.0.0 cryptography>=3.4.8 pyyaml>=6.0 rich>=13.0.0 click>=8.0.0 inquirer>=3.0.0 openpyxl>=3.0.0 pyperclip>=1.8.0 pynput>=1.7.0

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Choose installation method
echo.
echo Choose installation method:
echo 1. pip --user (recommended for Windows)
echo 2. pip (system installation)
echo 3. Development mode
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo 📦 Installing Winter via pip --user...
    python -m pip install --user .
    if %errorlevel% neq 0 (
        echo ❌ Installation failed
        pause
        exit /b 1
    )
    echo ✅ Winter installed via pip --user successfully!
) else if "%choice%"=="2" (
    echo 📦 Installing Winter via pip (system)...
    python -m pip install .
    if %errorlevel% neq 0 (
        echo ❌ Installation failed
        pause
        exit /b 1
    )
    echo ✅ Winter installed via pip successfully!
) else if "%choice%"=="3" (
    echo 📦 Installing Winter in development mode...
    python -m pip install --user -e .
    if %errorlevel% neq 0 (
        echo ❌ Installation failed
        pause
        exit /b 1
    )
    echo ✅ Winter installed in development mode!
) else (
    echo ❌ Invalid choice
    pause
    exit /b 1
)

REM Test installation
echo.
echo 🧪 Testing Winter installation...
winter --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Winter command not found in PATH
    echo Try restarting your command prompt or PowerShell
) else (
    winter --version
    echo ✅ Winter is working correctly!
)

echo.
echo 🎉 Installation completed successfully!
echo Run 'winter --help' to get started
pause
