from setuptools import setup, find_packages
import subprocess
import sys

def post_install():
    """Run setup wizard after installation"""
    try:
        subprocess.run([sys.executable, "-c", "from winter.setup import run_setup_wizard; run_setup_wizard()"])
    except Exception as e:
        print(f"Setup wizard failed: {e}")

setup(
    name="winter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "snowflake-connector-python>=3.0.0",
        "cryptography>=3.4.8",
        "pyyaml>=6.0",
        "rich>=13.0.0",
        "click>=8.0.0",
        "inquirer>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "winter=winter.main:main",
        ],
    },
    python_requires=">=3.8",
    author="Winter Team",
    description="Snowflake Terminal Client with Table Scrolling and Prefix Support",
    long_description=open("README.md").read() if open("README.md").readable() else "",
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/winter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)