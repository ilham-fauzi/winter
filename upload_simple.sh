#!/bin/bash

# Winter PyPI Upload Script - Simplified Version
# Script untuk upload package Winter ke PyPI dengan environment variable

set -e  # Exit on any error

echo "❄️  Winter - PyPI Upload Script (Simplified)"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if API token is provided
check_api_token() {
    if [ -z "$TESTPYPI_TOKEN" ] && [ -z "$PYPI_TOKEN" ]; then
        print_error "API token tidak ditemukan!"
        echo ""
        echo "Gunakan salah satu cara berikut:"
        echo ""
        echo "1. Set environment variable:"
        echo "   export TESTPYPI_TOKEN='pypi-your-testpypi-token'"
        echo "   export PYPI_TOKEN='pypi-your-pypi-token'"
        echo ""
        echo "2. Atau masukkan token secara manual:"
        echo "   TESTPYPI_TOKEN='pypi-your-token' ./upload_simple.sh"
        echo ""
        echo "3. Atau edit script ini dan masukkan token langsung"
        echo ""
        exit 1
    fi
}

# Clean previous builds
clean_builds() {
    print_status "Cleaning previous builds..."
    
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf winter.egg-info/
    
    print_success "Build artifacts cleaned"
}

# Build distribution
build_distribution() {
    print_status "Building distribution..."
    
    # Build source distribution and wheel
    python3 -m build
    
    if [ $? -eq 0 ]; then
        print_success "Distribution built successfully"
    else
        print_error "Build failed"
        exit 1
    fi
    
    # Show what was created
    print_status "Distribution files created:"
    ls -la dist/
    
    # Calculate file sizes
    print_status "File sizes:"
    du -h dist/*
}

# Validate distribution
validate_distribution() {
    print_status "Validating distribution..."
    
    # Check distribution files
    twine check dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Distribution validation passed"
    else
        print_error "Distribution validation failed"
        exit 1
    fi
}

# Upload to TestPyPI
upload_testpypi() {
    if [ -z "$TESTPYPI_TOKEN" ]; then
        print_error "TESTPYPI_TOKEN tidak ditemukan!"
        echo "Set environment variable: export TESTPYPI_TOKEN='pypi-your-token'"
        exit 1
    fi
    
    print_status "Uploading to TestPyPI..."
    
    # Upload using environment variable
    TWINE_USERNAME=__token__ TWINE_PASSWORD="$TESTPYPI_TOKEN" twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Upload to TestPyPI successful!"
        echo ""
        echo -e "${BLUE}📦 TestPyPI URL:${NC} https://test.pypi.org/project/winter/"
        echo -e "${BLUE}🔧 Test install command:${NC}"
        echo "pip install --index-url https://test.pypi.org/simple/ winter"
    else
        print_error "Upload to TestPyPI failed"
        exit 1
    fi
}

# Upload to Production PyPI
upload_pypi() {
    if [ -z "$PYPI_TOKEN" ]; then
        print_error "PYPI_TOKEN tidak ditemukan!"
        echo "Set environment variable: export PYPI_TOKEN='pypi-your-token'"
        exit 1
    fi
    
    print_status "Uploading to Production PyPI..."
    
    print_warning "This will upload to PRODUCTION PyPI!"
    read -p "Are you sure you want to continue? (y/N): " confirm
    
    if [[ $confirm != [yY] ]]; then
        print_status "Upload cancelled"
        exit 0
    fi
    
    # Upload using environment variable
    TWINE_USERNAME=__token__ TWINE_PASSWORD="$PYPI_TOKEN" twine upload dist/*
    
    if [ $? -eq 0 ]; then
        print_success "Upload to production PyPI successful!"
        echo ""
        echo -e "${GREEN}🎉 Congratulations! Winter is now available on PyPI!${NC}"
        echo -e "${BLUE}📦 PyPI URL:${NC} https://pypi.org/project/winter/"
        echo -e "${BLUE}🔧 Install command:${NC}"
        echo "pip install winter"
    else
        print_error "Upload to production PyPI failed"
        exit 1
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation from PyPI..."
    
    # Install package
    pip3 install "${1:-winter}"
    
    if [ $? -eq 0 ]; then
        print_success "Installation successful"
        
        # Test winter command
        winter --version
        winter --help | head -20
        
        print_success "Package working correctly!"
        
        # Uninstall for cleanup
        pip3 uninstall winter -y
    else
        print_error "Installation test failed"
        exit 1
    fi
}

# Show version info
show_version_info() {
    print_status "Current package version:"
    
    if [ -f "setup.py" ]; then
        grep 'version=' setup.py | head -1
    fi
    if [ -f "pyproject.toml" ]; then
        grep 'version' pyproject.toml | head -1
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "Select upload target:"
    echo "1) Build and validate only (no upload)"
    echo "2) Upload to TestPyPI"
    echo "3) Upload to Production PyPI"
    echo "4) Build + Upload to TestPyPI + Test"
    echo "5) Build + Upload to Production PyPI + Test"
    echo "6) Show version info"
    echo "0) Exit"
    echo ""
}

# Main execution
main() {
    show_version_info
    
    while true; do
        show_menu
        read -p "Enter choice (0-6): " choice
        
        case $choice in
            1)
                clean_builds
                build_distribution
                validate_distribution
                print_success "Build completed! Ready for upload."
                ;;
            2)
                check_api_token
                clean_builds
                build_distribution
                validate_distribution
                upload_testpypi
                ;;
            3)
                check_api_token
                clean_builds
                build_distribution
                validate_distribution
                upload_pypi
                ;;
            4)
                check_api_token
                clean_builds
                build_distribution
                validate_distribution
                upload_testpypi
                echo ""
                echo "Testing installation from TestPyPI..."
                test_installation "--index-url https://test.pypi.org/simple/ winter"
                ;;
            5)
                check_api_token
                clean_builds
                build_distribution
                validate_distribution
                upload_pypi
                echo ""
                test_installation "winter"
                ;;
            6)
                show_version_info
                ;;
            0)
                print_status "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
        echo ""
    done
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
