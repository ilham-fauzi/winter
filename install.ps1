# Winter - Snowflake Terminal Client
# Windows PowerShell installation script

Write-Host "❄️  Winter - Snowflake Terminal Client" -ForegroundColor Cyan
Write-Host "Windows PowerShell Installer" -ForegroundColor Blue
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check if Python is installed
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow

if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
    
    # Check Python version
    $versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python version is compatible (>= 3.8)" -ForegroundColor Green
    } else {
        Write-Host "❌ Python version is too old. Please install Python 3.8 or higher" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "❌ Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
$dependencies = @(
    "snowflake-connector-python>=3.0.0",
    "cryptography>=3.4.8",
    "pyyaml>=6.0",
    "rich>=13.0.0",
    "click>=8.0.0",
    "inquirer>=3.0.0",
    "openpyxl>=3.0.0",
    "pyperclip>=1.8.0",
    "pynput>=1.7.0"
)

foreach ($dep in $dependencies) {
    python -m pip install --user $dep
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install $dep" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green

# Choose installation method
Write-Host ""
Write-Host "Choose installation method:" -ForegroundColor Blue
Write-Host "1. pip --user (recommended for Windows)" -ForegroundColor White
Write-Host "2. pip (system installation)" -ForegroundColor White
Write-Host "3. Development mode" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host "📦 Installing Winter via pip --user..." -ForegroundColor Yellow
        python -m pip install --user .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Installation failed" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "✅ Winter installed via pip --user successfully!" -ForegroundColor Green
    }
    "2" {
        Write-Host "📦 Installing Winter via pip (system)..." -ForegroundColor Yellow
        python -m pip install .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Installation failed" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "✅ Winter installed via pip successfully!" -ForegroundColor Green
    }
    "3" {
        Write-Host "📦 Installing Winter in development mode..." -ForegroundColor Yellow
        python -m pip install --user -e .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Installation failed" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "✅ Winter installed in development mode!" -ForegroundColor Green
    }
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Test installation
Write-Host ""
Write-Host "🧪 Testing Winter installation..." -ForegroundColor Cyan

if (Test-Command "winter") {
    winter --version
    Write-Host "✅ Winter is working correctly!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Winter command not found in PATH" -ForegroundColor Yellow
    Write-Host "Try restarting your PowerShell or Command Prompt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
Write-Host "Run 'winter --help' to get started" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
