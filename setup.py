from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="winter-snowflake",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "snowflake-connector-python>=3.0.0",
        "cryptography>=3.4.8",
        "pyyaml>=6.0",
        "rich>=13.0.0",
        "click>=8.0.0",
        "inquirer>=3.0.0",
        "openpyxl>=3.0.0",
        "pyperclip>=1.8.0",
        "packaging>=21.0",
        "tomli>=2.0.0; python_version < '3.11'",
    ],
    entry_points={
        "console_scripts": [
            "winter=winter.main:main",
        ],
    },
    python_requires=">=3.8",
    author="Winter Team",
    author_email="winter-team@example.com",
    description="Snowflake Terminal Client with Table Scrolling and Prefix Support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ilham-fauzi/winter",
    project_urls={
        "Bug Reports": "https://github.com/ilham-fauzi/winter/issues",
        "Source": "https://github.com/ilham-fauzi/winter",
        "Documentation": "https://github.com/ilham-fauzi/winter/wiki",
        "Changelog": "https://github.com/ilham-fauzi/winter/blob/main/CHANGELOG.md",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Terminals :: Terminal Emulators/X Terminals",
        "Topic :: System :: Systems Administration",
        "Operating System :: OS Independent",
    ],
    keywords="snowflake database terminal client cli sql query management",
    include_package_data=True,
    zip_safe=False,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.0.0",
        ],
    },
)