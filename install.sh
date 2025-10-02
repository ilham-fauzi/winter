#!/bin/bash
# Winter - Snowflake Terminal Client
# Cross-platform installation script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Detect operating system
OS=$(uname -s)
ARCH=$(uname -m)

echo -e "${CYAN}❄️  Winter - Snowflake Terminal Client${NC}"
echo -e "${BLUE}Installer for ${OS} (${ARCH})${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    echo -e "${YELLOW}🐍 Checking Python installation...${NC}"
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2)
        echo -e "${GREEN}✅ Python3 is installed: ${PYTHON_VERSION}${NC}"
        
        # Check if version is >= 3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            echo -e "${GREEN}✅ Python version is compatible (>= 3.8)${NC}"
            return 0
        else
            echo -e "${RED}❌ Python version is too old. Please install Python 3.8 or higher${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Python3 is not installed${NC}"
        return 1
    fi
}

# Function to install Python (OS-specific)
install_python() {
    echo -e "${YELLOW}🐍 Installing Python...${NC}"
    
    case "$OS" in
        Linux*)
            if command_exists apt-get; then
                echo -e "${BLUE}Installing Python via apt-get...${NC}"
                sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
            elif command_exists yum; then
                echo -e "${BLUE}Installing Python via yum...${NC}"
                sudo yum install -y python3 python3-pip
            elif command_exists dnf; then
                echo -e "${BLUE}Installing Python via dnf...${NC}"
                sudo dnf install -y python3 python3-pip
            elif command_exists pacman; then
                echo -e "${BLUE}Installing Python via pacman...${NC}"
                sudo pacman -S python python-pip
            else
                echo -e "${RED}❌ Package manager not found. Please install Python manually${NC}"
                exit 1
            fi
            ;;
        Darwin*)
            if command_exists brew; then
                echo -e "${BLUE}Installing Python via Homebrew...${NC}"
                brew install python
            else
                echo -e "${RED}❌ Homebrew not found. Please install Python manually or install Homebrew first${NC}"
                echo -e "${YELLOW}Visit: https://brew.sh${NC}"
                exit 1
            fi
            ;;
        MINGW*|CYGWIN*|MSYS*)
            echo -e "${RED}❌ Please install Python from https://python.org${NC}"
            exit 1
            ;;
    esac
}

# Function to install build tools
install_build_tools() {
    echo -e "${YELLOW}🔧 Checking build tools...${NC}"
    
    case "$OS" in
        Linux*)
            if ! command_exists gcc; then
                echo -e "${YELLOW}⚠️  GCC not found, installing build tools...${NC}"
                if command_exists apt-get; then
                    sudo apt-get update && sudo apt-get install -y build-essential
                elif command_exists yum; then
                    sudo yum groupinstall -y "Development Tools"
                elif command_exists dnf; then
                    sudo dnf groupinstall -y "Development Tools"
                elif command_exists pacman; then
                    sudo pacman -S base-devel
                fi
            else
                echo -e "${GREEN}✅ GCC is available${NC}"
            fi
            
            if ! command_exists cmake; then
                echo -e "${YELLOW}⚠️  CMake not found, installing...${NC}"
                if command_exists apt-get; then
                    sudo apt-get install -y cmake
                elif command_exists yum; then
                    sudo yum install -y cmake
                elif command_exists dnf; then
                    sudo dnf install -y cmake
                elif command_exists pacman; then
                    sudo pacman -S cmake
                fi
            else
                echo -e "${GREEN}✅ CMake is available${NC}"
            fi
            ;;
        Darwin*)
            if ! command_exists xcode-select; then
                echo -e "${YELLOW}⚠️  Xcode Command Line Tools not found${NC}"
                xcode-select --install
            else
                echo -e "${GREEN}✅ Xcode Command Line Tools are available${NC}"
            fi
            ;;
        MINGW*|CYGWIN*|MSYS*)
            echo -e "${GREEN}✅ Windows build tools should be available${NC}"
            ;;
    esac
}

# Function to install pipx
install_pipx() {
    echo -e "${YELLOW}📦 Installing pipx...${NC}"
    
    if command_exists pipx; then
        echo -e "${GREEN}✅ pipx is already installed${NC}"
    else
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
        echo -e "${GREEN}✅ pipx installed successfully${NC}"
        echo -e "${YELLOW}⚠️  Please restart your terminal or run: source ~/.bashrc${NC}"
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    
    python3 -m pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        python3 -m pip install --user -r requirements.txt
    else
        python3 -m pip install --user snowflake-connector-python>=3.0.0 cryptography>=3.4.8 pyyaml>=6.0 rich>=13.0.0 click>=8.0.0 inquirer>=3.0.0 openpyxl>=3.0.0 pyperclip>=1.8.0 pynput>=1.7.0
    fi
    
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
}

# Function to install Winter
install_winter() {
    echo -e "${CYAN}❄️  Installing Winter...${NC}"
    
    echo -e "${BLUE}Choose installation method:${NC}"
    echo -e "${WHITE}1. pipx (recommended - isolated environment)${NC}"
    echo -e "${WHITE}2. pip --user (user installation)${NC}"
    echo -e "${WHITE}3. pip (system installation)${NC}"
    echo -e "${WHITE}4. Development mode${NC}"
    echo -e "${YELLOW}Enter choice (1-4):${NC}"
    read -r choice
    
    case $choice in
        1)
            install_pipx
            pipx install .
            echo -e "${GREEN}✅ Winter installed via pipx successfully!${NC}"
            echo -e "${CYAN}Run: winter --help${NC}"
            ;;
        2)
            python3 -m pip install --user .
            echo -e "${GREEN}✅ Winter installed via pip --user successfully!${NC}"
            echo -e "${CYAN}Run: winter --help${NC}"
            ;;
        3)
            case "$OS" in
                Linux*)
                    echo -e "${YELLOW}⚠️  System installation on Linux may require sudo${NC}"
                    sudo python3 -m pip install .
                    ;;
                *)
                    python3 -m pip install .
                    ;;
            esac
            echo -e "${GREEN}✅ Winter installed via pip successfully!${NC}"
            echo -e "${CYAN}Run: winter --help${NC}"
            ;;
        4)
            python3 -m pip install --user -e .
            echo -e "${GREEN}✅ Winter installed in development mode!${NC}"
            echo -e "${CYAN}Run: winter --help${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
}

# Function to test installation
test_installation() {
    echo -e "${CYAN}🧪 Testing Winter installation...${NC}"
    
    if command_exists winter; then
        winter --version
        echo -e "${GREEN}✅ Winter is working correctly!${NC}"
    else
        echo -e "${RED}❌ Winter command not found${NC}"
        echo -e "${YELLOW}Try running: source ~/.bashrc or restart your terminal${NC}"
    fi
}

# Main installation process
main() {
    echo -e "${CYAN}🔍 Checking system requirements...${NC}"
    
    # Check Python
    if ! check_python; then
        install_python
        if ! check_python; then
            echo -e "${RED}❌ Python installation failed${NC}"
            exit 1
        fi
    fi
    
    # Install build tools
    install_build_tools
    
    # Install dependencies
    install_dependencies
    
    # Install Winter
    install_winter
    
    # Test installation
    test_installation
    
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo -e "${CYAN}Run 'winter --help' to get started${NC}"
}

# Run main function
main "$@"
