#!/usr/bin/env python3
"""
Local development script for Winter.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run Winter
from winter.main import main

if __name__ == "__main__":
    main()
