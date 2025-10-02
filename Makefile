# Winter - Snowflake Terminal Client
# Cross-platform Makefile for installation and setup

# Detect operating system
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

# Python version check
PYTHON_VERSION := $(shell python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
PYTHON_MIN_VERSION := 3.8

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[1;37m
NC := \033[0m # No Color

# Default target
.PHONY: all
all: check-system install-deps install-winter

# Check system requirements
.PHONY: check-system
check-system:
	@echo "$(CYAN)🔍 Checking system requirements...$(NC)"
	@echo "$(BLUE)Operating System: $(UNAME_S)$(NC)"
	@echo "$(BLUE)Architecture: $(UNAME_M)$(NC)"
	@echo "$(BLUE)Python Version: $(PYTHON_VERSION)$(NC)"
	@$(MAKE) check-python
	@$(MAKE) check-build-tools

# Check Python installation
.PHONY: check-python
check-python:
	@echo "$(YELLOW)🐍 Checking Python installation...$(NC)"
	@if command -v python3 >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Python3 is installed$(NC)"; \
		PYTHON_VERSION_CHECK=$$(python3 -c "import sys; print('OK' if sys.version_info >= (3, 8) else 'FAIL')" 2>/dev/null); \
		if [ "$$PYTHON_VERSION_CHECK" = "OK" ]; then \
			echo "$(GREEN)✅ Python version is compatible (>= 3.8)$(NC)"; \
		else \
			echo "$(RED)❌ Python version is too old. Please install Python 3.8 or higher$(NC)"; \
			exit 1; \
		fi; \
	else \
		echo "$(RED)❌ Python3 is not installed$(NC)"; \
		$(MAKE) install-python; \
	fi

# Check build tools
.PHONY: check-build-tools
check-build-tools:
	@echo "$(YELLOW)🔧 Checking build tools...$(NC)"
	@case "$(UNAME_S)" in \
		Linux*) \
			if ! command -v gcc >/dev/null 2>&1; then \
				echo "$(YELLOW)⚠️  GCC not found, installing build tools...$(NC)"; \
				$(MAKE) install-build-tools-linux; \
			else \
				echo "$(GREEN)✅ GCC is available$(NC)"; \
			fi; \
			if ! command -v cmake >/dev/null 2>&1; then \
				echo "$(YELLOW)⚠️  CMake not found, installing...$(NC)"; \
				$(MAKE) install-cmake-linux; \
			else \
				echo "$(GREEN)✅ CMake is available$(NC)"; \
			fi; \
			;; \
		Darwin*) \
			if ! command -v xcode-select >/dev/null 2>&1; then \
				echo "$(YELLOW)⚠️  Xcode Command Line Tools not found$(NC)"; \
				$(MAKE) install-build-tools-macos; \
			else \
				echo "$(GREEN)✅ Xcode Command Line Tools are available$(NC)"; \
			fi; \
			;; \
		MINGW*|CYGWIN*|MSYS*) \
			echo "$(GREEN)✅ Windows build tools should be available$(NC)"; \
			;; \
	esac

# Install Python (OS-specific)
.PHONY: install-python
install-python:
	@echo "$(YELLOW)🐍 Installing Python...$(NC)"
	@case "$(UNAME_S)" in \
		Linux*) \
			if command -v apt-get >/dev/null 2>&1; then \
				echo "$(BLUE)Installing Python via apt-get...$(NC)"; \
				sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv; \
			elif command -v yum >/dev/null 2>&1; then \
				echo "$(BLUE)Installing Python via yum...$(NC)"; \
				sudo yum install -y python3 python3-pip; \
			elif command -v dnf >/dev/null 2>&1; then \
				echo "$(BLUE)Installing Python via dnf...$(NC)"; \
				sudo dnf install -y python3 python3-pip; \
			elif command -v pacman >/dev/null 2>&1; then \
				echo "$(BLUE)Installing Python via pacman...$(NC)"; \
				sudo pacman -S python python-pip; \
			else \
				echo "$(RED)❌ Package manager not found. Please install Python manually$(NC)"; \
				exit 1; \
			fi; \
			;; \
		Darwin*) \
			if command -v brew >/dev/null 2>&1; then \
				echo "$(BLUE)Installing Python via Homebrew...$(NC)"; \
				brew install python; \
			else \
				echo "$(RED)❌ Homebrew not found. Please install Python manually or install Homebrew first$(NC)"; \
				echo "$(YELLOW)Visit: https://brew.sh$(NC)"; \
				exit 1; \
			fi; \
			;; \
		MINGW*|CYGWIN*|MSYS*) \
			echo "$(RED)❌ Please install Python from https://python.org$(NC)"; \
			exit 1; \
			;; \
	esac

# Install build tools for Linux
.PHONY: install-build-tools-linux
install-build-tools-linux:
	@echo "$(YELLOW)🔧 Installing build tools for Linux...$(NC)"
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update && sudo apt-get install -y build-essential; \
	elif command -v yum >/dev/null 2>&1; then \
		sudo yum groupinstall -y "Development Tools"; \
	elif command -v dnf >/dev/null 2>&1; then \
		sudo dnf groupinstall -y "Development Tools"; \
	elif command -v pacman >/dev/null 2>&1; then \
		sudo pacman -S base-devel; \
	fi

# Install CMake for Linux
.PHONY: install-cmake-linux
install-cmake-linux:
	@echo "$(YELLOW)🔧 Installing CMake for Linux...$(NC)"
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get install -y cmake; \
	elif command -v yum >/dev/null 2>&1; then \
		sudo yum install -y cmake; \
	elif command -v dnf >/dev/null 2>&1; then \
		sudo dnf install -y cmake; \
	elif command -v pacman >/dev/null 2>&1; then \
		sudo pacman -S cmake; \
	fi

# Install build tools for macOS
.PHONY: install-build-tools-macos
install-build-tools-macos:
	@echo "$(YELLOW)🔧 Installing Xcode Command Line Tools...$(NC)"
	@xcode-select --install

# Install dependencies
.PHONY: install-deps
install-deps: check-system
	@echo "$(CYAN)📦 Installing Python dependencies...$(NC)"
	@$(MAKE) install-pipx
	@$(MAKE) install-python-deps

# Install pipx (recommended for Python applications)
.PHONY: install-pipx
install-pipx:
	@echo "$(YELLOW)📦 Installing pipx...$(NC)"
	@if command -v pipx >/dev/null 2>&1; then \
		echo "$(GREEN)✅ pipx is already installed$(NC)"; \
	else \
		python3 -m pip install --user pipx; \
		python3 -m pipx ensurepath; \
		echo "$(GREEN)✅ pipx installed successfully$(NC)"; \
		echo "$(YELLOW)⚠️  Please restart your terminal or run: source ~/.bashrc$(NC)"; \
	fi

# Install Python dependencies
.PHONY: install-python-deps
install-python-deps:
	@echo "$(YELLOW)📦 Installing Python dependencies...$(NC)"
	@python3 -m pip install --upgrade pip
	@python3 -m pip install --user -r requirements.txt 2>/dev/null || \
		python3 -m pip install --user snowflake-connector-python>=3.0.0 cryptography>=3.4.8 pyyaml>=6.0 rich>=13.0.0 click>=8.0.0 inquirer>=3.0.0 openpyxl>=3.0.0 pyperclip>=1.8.0 pynput>=1.7.0

# Install Winter
.PHONY: install-winter
install-winter: install-deps
	@echo "$(CYAN)❄️  Installing Winter...$(NC)"
	@$(MAKE) install-method

# Choose installation method
.PHONY: install-method
install-method:
	@echo "$(BLUE)Choose installation method:$(NC)"
	@echo "$(WHITE)1. pipx (recommended - isolated environment)$(NC)"
	@echo "$(WHITE)2. pip --user (user installation)$(NC)"
	@echo "$(WHITE)3. pip (system installation)$(NC)"
	@echo "$(WHITE)4. Development mode$(NC)"
	@echo "$(YELLOW)Enter choice (1-4):$(NC)"
	@read choice; \
	case $$choice in \
		1) $(MAKE) install-pipx-method ;; \
		2) $(MAKE) install-user-method ;; \
		3) $(MAKE) install-system-method ;; \
		4) $(MAKE) install-dev-method ;; \
		*) echo "$(RED)Invalid choice$(NC)"; exit 1 ;; \
	esac

# Install via pipx
.PHONY: install-pipx-method
install-pipx-method:
	@echo "$(BLUE)Installing via pipx...$(NC)"
	@pipx install .
	@echo "$(GREEN)✅ Winter installed via pipx successfully!$(NC)"
	@echo "$(CYAN)Run: winter --help$(NC)"

# Install via pip --user
.PHONY: install-user-method
install-user-method:
	@echo "$(BLUE)Installing via pip --user...$(NC)"
	@python3 -m pip install --user .
	@echo "$(GREEN)✅ Winter installed via pip --user successfully!$(NC)"
	@echo "$(CYAN)Run: winter --help$(NC)"

# Install via pip (system)
.PHONY: install-system-method
install-system-method:
	@echo "$(BLUE)Installing via pip (system)...$(NC)"
	@case "$(UNAME_S)" in \
		Linux*) \
			echo "$(YELLOW)⚠️  System installation on Linux may require sudo$(NC)"; \
			sudo python3 -m pip install .; \
			;; \
		*) \
			python3 -m pip install .; \
			;; \
	esac
	@echo "$(GREEN)✅ Winter installed via pip successfully!$(NC)"
	@echo "$(CYAN)Run: winter --help$(NC)"

# Install in development mode
.PHONY: install-dev-method
install-dev-method:
	@echo "$(BLUE)Installing in development mode...$(NC)"
	@python3 -m pip install --user -e .
	@echo "$(GREEN)✅ Winter installed in development mode!$(NC)"
	@echo "$(CYAN)Run: winter --help$(NC)"

# Uninstall Winter
.PHONY: uninstall
uninstall:
	@echo "$(CYAN)🗑️  Uninstalling Winter...$(NC)"
	@if command -v pipx >/dev/null 2>&1 && pipx list | grep -q winter; then \
		pipx uninstall winter; \
		echo "$(GREEN)✅ Winter uninstalled via pipx$(NC)"; \
	elif python3 -m pip show winter >/dev/null 2>&1; then \
		python3 -m pip uninstall winter; \
		echo "$(GREEN)✅ Winter uninstalled via pip$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Winter not found in pip/pipx$(NC)"; \
	fi

# Clean up
.PHONY: clean
clean:
	@echo "$(CYAN)🧹 Cleaning up...$(NC)"
	@rm -rf build/ dist/ *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

# Test installation
.PHONY: test
test:
	@echo "$(CYAN)🧪 Testing Winter installation...$(NC)"
	@if command -v winter >/dev/null 2>&1; then \
		winter --version; \
		echo "$(GREEN)✅ Winter is working correctly!$(NC)"; \
	else \
		echo "$(RED)❌ Winter command not found$(NC)"; \
		echo "$(YELLOW)Try running: source ~/.bashrc or restart your terminal$(NC)"; \
	fi

# Show system info
.PHONY: info
info:
	@echo "$(CYAN)ℹ️  System Information:$(NC)"
	@echo "$(BLUE)OS: $(UNAME_S)$(NC)"
	@echo "$(BLUE)Architecture: $(UNAME_M)$(NC)"
	@echo "$(BLUE)Python: $(PYTHON_VERSION)$(NC)"
	@echo "$(BLUE)Python Path: $(shell which python3)$(NC)"
	@echo "$(BLUE)Pip Path: $(shell which pip3)$(NC)"
	@if command -v pipx >/dev/null 2>&1; then \
		echo "$(BLUE)Pipx Path: $(shell which pipx)$(NC)"; \
	fi
	@if command -v winter >/dev/null 2>&1; then \
		echo "$(BLUE)Winter Path: $(shell which winter)$(NC)"; \
		winter --version; \
	else \
		echo "$(YELLOW)Winter: Not installed$(NC)"; \
	fi

# Help
.PHONY: help
help:
	@echo "$(CYAN)❄️  Winter - Snowflake Terminal Client$(NC)"
	@echo "$(WHITE)Available targets:$(NC)"
	@echo "$(GREEN)  all$(NC)           - Complete installation (check + deps + install)"
	@echo "$(GREEN)  install$(NC)      - Install Winter (alias for all)"
	@echo "$(GREEN)  check-system$(NC) - Check system requirements"
	@echo "$(GREEN)  install-deps$(NC)  - Install dependencies only"
	@echo "$(GREEN)  install-winter$(NC)- Install Winter only"
	@echo "$(GREEN)  uninstall$(NC)    - Uninstall Winter"
	@echo "$(GREEN)  clean$(NC)        - Clean build artifacts"
	@echo "$(GREEN)  test$(NC)         - Test installation"
	@echo "$(GREEN)  info$(NC)         - Show system information"
	@echo "$(GREEN)  help$(NC)         - Show this help"
	@echo ""
	@echo "$(YELLOW)Quick start:$(NC)"
	@echo "$(WHITE)  make install$(NC) - Complete installation"
	@echo "$(WHITE)  make test$(NC)    - Test installation"

# Alias for install
.PHONY: install
install: all
