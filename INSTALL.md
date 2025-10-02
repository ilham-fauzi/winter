# Installation Guide - Winter

## 🚀 Quick Installation

### Option 1: Using Makefile (Recommended)
```bash
# Clone the repository
git clone https://github.com/ilham-fauzi/winter.git
cd winter

# Install Winter
make install
```

### Option 2: Using Installation Scripts

#### Linux/macOS
```bash
# Make script executable and run
chmod +x install.sh
./install.sh
```

#### Windows (Command Prompt)
```cmd
install.bat
```

#### Windows (PowerShell)
```powershell
.\install.ps1
```

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512MB RAM
- **Disk Space**: 100MB

### Build Tools (for some dependencies)
- **Linux**: `build-essential`, `cmake`
- **macOS**: Xcode Command Line Tools
- **Windows**: Visual Studio Build Tools (usually included with Python)

## 🔧 Installation Methods

### 1. pipx (Recommended)
Isolated environment, prevents conflicts:
```bash
pipx install .
```

### 2. pip --user
User installation, no system-wide changes:
```bash
pip install --user .
```

### 3. pip (System)
System-wide installation:
```bash
pip install .
```

### 4. Development Mode
For development and testing:
```bash
pip install -e .
```

## 🐧 Linux Installation

### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv build-essential cmake

# Install Winter
make install
```

### CentOS/RHEL/Fedora
```bash
# Install system dependencies
sudo yum install -y python3 python3-pip gcc cmake
# OR for newer versions:
sudo dnf install -y python3 python3-pip gcc cmake

# Install Winter
make install
```

### Arch Linux
```bash
# Install system dependencies
sudo pacman -S python python-pip base-devel cmake

# Install Winter
make install
```

## 🍎 macOS Installation

### Using Homebrew (Recommended)
```bash
# Install Python and dependencies
brew install python

# Install Winter
make install
```

### Using MacPorts
```bash
# Install Python
sudo port install python38

# Install Winter
make install
```

## 🪟 Windows Installation

### Using Python from python.org
1. Download Python from https://python.org
2. Install with "Add Python to PATH" checked
3. Run `install.bat` or `install.ps1`

### Using Chocolatey
```powershell
# Install Python
choco install python

# Install Winter
.\install.ps1
```

### Using Scoop
```powershell
# Install Python
scoop install python

# Install Winter
.\install.ps1
```

## 🧪 Testing Installation

After installation, test that Winter is working:

```bash
# Check version
winter --version

# Show help
winter --help

# Run setup
winter setup
```

## 🔄 Updating Winter

### Using pipx
```bash
pipx upgrade winter
```

### Using pip
```bash
pip install --upgrade winter
```

### Using Makefile
```bash
make uninstall
make install
```

## 🗑️ Uninstalling Winter

### Using pipx
```bash
pipx uninstall winter
```

### Using pip
```bash
pip uninstall winter
```

### Using Makefile
```bash
make uninstall
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "Command not found: winter"
- **Solution**: Restart your terminal or run `source ~/.bashrc`
- **Alternative**: Use full path `~/.local/bin/winter`

#### 2. "externally-managed-environment" (Linux)
- **Solution**: Use `pip install --user` or `pipx install`
- **Alternative**: Create virtual environment

#### 3. Build errors (pyarrow, cryptography)
- **Solution**: Install build tools:
  - Linux: `sudo apt-get install build-essential cmake`
  - macOS: `xcode-select --install`
  - Windows: Install Visual Studio Build Tools

#### 4. Permission errors
- **Solution**: Use `--user` flag or `pipx`
- **Alternative**: Use virtual environment

### Getting Help

If you encounter issues:

1. Check system requirements
2. Try different installation method
3. Check Python version: `python3 --version`
4. Check pip version: `pip3 --version`
5. Create issue on GitHub with:
   - Operating system
   - Python version
   - Error message
   - Installation method used

## 📚 Additional Resources

- [GitHub Repository](https://github.com/ilham-fauzi/winter)
- [Documentation](https://github.com/ilham-fauzi/winter#readme)
- [Issues](https://github.com/ilham-fauzi/winter/issues)
- [Discussions](https://github.com/ilham-fauzi/winter/discussions)
