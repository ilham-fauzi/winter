#!/bin/bash

# Simple Upload Script untuk Winter-Snowflake
echo "❄️  Winter-Snowflake Upload Script"
echo "=================================="

# Set API token (ganti dengan token Anda)
# export PYPI_TOKEN='pypi-your-token-here'

echo "📦 Current version: 0.1.1"
echo "📦 Package name: winter-snowflake"
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/ winter_snowflake.egg-info/

# Build package
echo "🔨 Building package..."
python3 -m build

# Check if build successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📁 Distribution files:"
    ls -la dist/
    echo ""
    
    # Upload to PyPI
    echo "🚀 Uploading to PyPI..."
    echo "Username: __token__"
    echo "Password: [Your API Token]"
    echo ""
    
    # Manual upload command
    echo "📋 Manual upload command:"
    echo "TWINE_USERNAME=__token__ TWINE_PASSWORD='pypi-your-token' twine upload dist/*"
    echo ""
    
    # Or use environment variable
    echo "📋 Or set environment variable:"
    echo "export PYPI_TOKEN='pypi-your-token'"
    echo "TWINE_USERNAME=__token__ TWINE_PASSWORD=\"\$PYPI_TOKEN\" twine upload dist/*"
    
else
    echo "❌ Build failed!"
    exit 1
fi
