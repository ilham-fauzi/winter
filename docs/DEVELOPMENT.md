# Winter Development Guide

## 🚀 **Menjalankan Winter dari Local Project**

### **Metode 1: Development Mode (Recommended)**

```bash
# Install dalam development mode
cd /Users/ilham/Public/Workspace/RND/winter
python3 -m pip install -e .

# Sekarang bisa menggunakan winter command
winter --help
winter hello
winter status
winter setup
```

**Keuntungan:**
- ✅ Bisa menggunakan `winter` command langsung
- ✅ Perubahan code langsung ter-reflect
- ✅ Tidak perlu reinstall setiap kali ada perubahan

### **Metode 2: Python Module**

```bash
# Run sebagai Python module
cd /Users/ilham/Public/Workspace/RND/winter
python3 -m winter --help
python3 -m winter hello
python3 -m winter status
python3 -m winter setup
```

**Keuntungan:**
- ✅ Tidak perlu install ke system
- ✅ Langsung dari source code
- ✅ Mudah untuk development

### **Metode 3: Local Script**

```bash
# Run dengan local script
cd /Users/ilham/Public/Workspace/RND/winter
python3 run_winter.py --help
python3 run_winter.py hello
python3 run_winter.py status
python3 run_winter.py setup
```

**Keuntungan:**
- ✅ Paling mudah untuk development
- ✅ Tidak perlu install apapun
- ✅ Langsung dari project directory

### **Metode 4: Direct Import**

```python
# Dalam Python script atau Jupyter notebook
import sys
sys.path.append('/Users/ilham/Public/Workspace/RND/winter')

from winter.main import main
from winter.setup import run_setup_wizard

# Run setup wizard
run_setup_wizard()

# Atau run main CLI
main()
```

## 🛠️ **Development Workflow**

### **1. Setup Development Environment**

```bash
# Clone atau navigate ke project
cd /Users/ilham/Public/Workspace/RND/winter

# Install dependencies
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt

# Install dalam development mode
python3 -m pip install -e .
```

### **2. Development Commands**

```bash
# Test dengan local script
python3 run_winter.py --help

# Test dengan module
python3 -m winter --help

# Run tests
python3 -m pytest tests/ -v

# Run comprehensive test
python3 test_winter.py
```

### **3. Code Changes**

```bash
# Edit code di editor
# Perubahan langsung ter-reflect jika menggunakan development mode

# Test perubahan
python3 run_winter.py hello
python3 run_winter.py status
```

### **4. Testing Changes**

```bash
# Run unit tests
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_cli.py::test_hello_command -v

# Run comprehensive test
python3 test_winter.py
```

## 🔧 **Development Tools**

### **1. Code Formatting**

```bash
# Install black untuk code formatting
python3 -m pip install black

# Format code
black winter/
black tests/
```

### **2. Linting**

```bash
# Install flake8 untuk linting
python3 -m pip install flake8

# Check code quality
flake8 winter/
flake8 tests/
```

### **3. Type Checking**

```bash
# Install mypy untuk type checking
python3 -m pip install mypy

# Check types
mypy winter/
```

### **4. Testing dengan Coverage**

```bash
# Install pytest-cov
python3 -m pip install pytest-cov

# Run tests dengan coverage
python3 -m pytest tests/ --cov=winter --cov-report=html
```

## 📁 **Project Structure untuk Development**

```
winter/
├── winter/                 # Main package
│   ├── __init__.py
│   ├── __main__.py        # Module entry point
│   ├── main.py            # CLI entry point
│   ├── cli/               # CLI commands
│   ├── snowflake/         # Snowflake connection
│   ├── query/             # Query processing
│   ├── security/          # Security controls
│   ├── ui/                # Table display
│   ├── utils/             # Utilities
│   └── setup/             # Setup wizard
├── tests/                 # Test files
├── docs/                  # Documentation
├── run_winter.py          # Local development script
├── test_winter.py         # Comprehensive test script
├── setup.py               # Package setup
├── pyproject.toml         # Modern Python config
├── requirements.txt       # Dependencies
└── requirements-dev.txt   # Dev dependencies
```

## 🚀 **Quick Start untuk Development**

### **1. Clone/Navigate ke Project**
```bash
cd /Users/ilham/Public/Workspace/RND/winter
```

### **2. Install Dependencies**
```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
```

### **3. Install dalam Development Mode**
```bash
python3 -m pip install -e .
```

### **4. Test Installation**
```bash
# Test dengan local script
python3 run_winter.py --help

# Test dengan module
python3 -m winter --help

# Test dengan installed command
winter --help
```

### **5. Run Tests**
```bash
# Unit tests
python3 -m pytest tests/ -v

# Comprehensive test
python3 test_winter.py
```

## 🐛 **Debugging**

### **1. Debug Mode**
```bash
# Run dengan debug output
PYTHONPATH=/Users/ilham/Public/Workspace/RND/winter python3 run_winter.py --help
```

### **2. Verbose Output**
```bash
# Run dengan verbose output
python3 -m winter --help --verbose
```

### **3. Logging**
```python
# Dalam code, tambahkan logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

## 📊 **Performance Monitoring**

### **1. Memory Usage**
```bash
# Monitor memory usage
python3 -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

### **2. Response Time**
```bash
# Measure response time
time python3 run_winter.py --help
time python3 run_winter.py status
```

## 🔄 **Development Cycle**

### **1. Make Changes**
```bash
# Edit code di editor
vim winter/main.py
# atau
code winter/main.py
```

### **2. Test Changes**
```bash
# Test perubahan
python3 run_winter.py hello
python3 run_winter.py status
```

### **3. Run Tests**
```bash
# Run tests
python3 -m pytest tests/ -v
```

### **4. Commit Changes**
```bash
# Git workflow
git add .
git commit -m "Add new feature"
git push
```

## 🎯 **Best Practices**

### **1. Development Mode**
- ✅ Selalu gunakan `pip install -e .` untuk development
- ✅ Test dengan multiple methods (local script, module, installed command)
- ✅ Run tests setelah setiap perubahan

### **2. Code Quality**
- ✅ Format code dengan black
- ✅ Check linting dengan flake8
- ✅ Check types dengan mypy
- ✅ Maintain test coverage > 80%

### **3. Testing**
- ✅ Run unit tests sebelum commit
- ✅ Test dengan real scenarios
- ✅ Test error handling
- ✅ Test cross-platform compatibility

---

**Dengan setup ini, Anda bisa develop Winter dengan mudah dan efisien!**
