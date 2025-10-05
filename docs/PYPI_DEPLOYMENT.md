# Panduan Mendaftarkan Winter ke PyPI

Dokumentasi lengkap untuk mendaftarkan package Winter ke Python Package Index (PyPI) agar bisa diinstall melalui `pip install winter`.

## 📋 Prasyarat

### 1. Akun PyPI
- Buat akun di [https://pypi.org](https://pypi.org)
- Aktifkan **2FA (Two-Factor Authentication)**
- Simpan username dan password/API token

### 2. Akun TestPyPI (Rekomen untuk Testing)
- Buat akun di [https://test.pypi.org](https://test.pypi.org)
- Gunakan untuk testing sebelum upload ke PyPI production

### 3. Tools yang Diperlukan
```bash
# Install twine (untuk upload)
pip install twine

# Install build tools (untuk membuat distribusi)
pip install build

# Update setuptools dan wheel
pip install --upgrade setuptools wheel
```

## 🔧 Konfigurasi Package

### 1. Update setup.py
Pastikan `setup.py` sudah sesuai untuk distribusi:

```python
from setuptools import setup, find_packages

setup(
    name="winter",  # Nama harus unik di PyPI
    version="0.1.0",
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
    author_email="your-email@example.com",
    description="Snowflake Terminal Client with Table Scrolling and Prefix Support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/winter",
    project_urls={
        "Bug Reports": "https://github.com/your-org/winter/issues",
        "Source": "https://github.com/your-org/winter",
        "Documentation": "https://github.com/your-org/winter/wiki",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
    ],
    keywords="snowflake database terminal client cli sql",
    include_package_data=True,
    zip_safe=False,
)
```

### 2. Update pyproject.toml
Tambahkan informasi tambahan di `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "sphinx>=5.0.0",
]

test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["winter*"]
exclude = ["tests*"]

[tool.setuptools.package-data]
"winter" = ["*.txt", "*.md", "*.yaml", "*.yml"]
```

### 3. Buat MANIFEST.in
Buat file `MANIFEST.in` untuk memasukkan file tambahan:

```ini
include README.md
include LICENSE
include requirements.txt
include requirements-dev.txt
recursive-include docs *.md
recursive-include examples *.yaml
recursive-include winter *.py
global-exclude __pycache__
global-exclude *.py[co]
```

### 4. Prepare LICENSE File
Buat file `LICENSE` dengan konten MIT License:

```text
MIT License

Copyright (c) 2024 Winter Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🏗️ Build dan Upload Process

### Langkah 1: Bersihkan Folder Build
```bash
# Hapus folder build lama
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
```

### Langkah 2: Build Distribution
```bash
# Build source distribution dan wheel
python -m build

# Cek file yang dibuat
ls dist/
# Output yang diharapkan:
# winter-0.1.0-py3-none-any.whl
# winter-0.1.0.tar.gz
```

### Langkah 3: Validasi Distribution
```bash
# Cek apakah package bisa diinstall
twine check dist/*
```

### Langkah 4: Upload ke TestPyPI (Recommended)
```bash
# Upload ke TestPyPI untuk testing
twine upload --repository testpypi dist/*

# Username: __token__
# Password: API token dari TestPyPI
```

### Langkah 5: Test Install dari TestPyPI
```bash
# Install dari TestPyPI untuk testing
pip install --index-url https://test.pypi.org/simple/ winter

# Test apakah berfungsi
winter --version
winter --help
```

### Langkah 6: Upload ke PyPI Production
Jika testing berhasil, upload ke PyPI:

```bash
# Upload ke PyPI production
twine upload dist/*

# Username: __token__
# Password: API token dari PyPI
```

## 🚀 Automasi dengan Script

### Buat Script Upload
Buat file `upload_to_pypi.sh`:

```bash
#!/bin/bash

echo "🔧 Building Winter package..."

# Clean previous builds
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Build
python -m build

echo "✅ Build completed"
echo "📦 Distribution files:"
ls -la dist/

# Check distribution
echo "🔍 Checking distribution..."
twine check dist/*

echo "🚀 Ready to upload!"
echo "Choose upload target:"
echo "1) Test PyPI"
echo "2) Production PyPI"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "📤 Uploading to Test PyPI..."
    twine upload --repository testpypi dist/*
elif [ "$choice" = "2" ]; then
    echo "📤 Uploading to Production PyPI..."
    twine upload dist/*
else
    echo "❌ Invalid choice"
    exit 1
fi

echo "✅ Upload completed!"
```

```bash
# Buat script executable
chmod +x upload_to_pypi.sh
```

## 📋 Checklist Post-Upload

### 1. Verifikasi Upload
- [ ] Package muncul di PyPI: https://pypi.org/project/winter/
-[ ] Description dan README terlihat dengan benar
-[ ] Download links berfungsi
-[ ] Project URLs mengarah ke repository yang benar

### 2. Test Installation
```bash
# Install dari PyPI
pip install winter

# Test command line
winter --version
winter --help
winter setup
```

### 3. Update Documentation
- [ ] Update README dengan installation command
- [ ] Update repository links menuju PyPI package
- [ ] Update CI/CD untuk menggunakan versi PyPI

## 🔄 Update Versi

### Mengganti Versi
1. Update version di `setup.py` dan `pyproject.toml`
2. Update version di `winter/__init__.py`
3. Update changelog/RELEASE_NOTES.md
4. Build dan upload ulang

```bash
# Update version (contoh: 0.1.0 -> 0.1.1)
sed -i 's/version="0.1.0"/version="0.1.1"/g' setup.py
sed -i 's/version = "0.1.0"/version = "0.1.1"/g' pyproject.toml

# Build dan upload
python -m build
twine upload dist/*
```

## 🐛 Troubleshooting

### Common Issues

**1. Nama Package Sudah Ada**
```bash
# Error: Package 'winter' already exists
# Solusi: Ganti nama atau gunakan nama yang berbeda
```

**2. Dependencies Not Found**
```bash
# Pastikan semua dependencies ada di install_requires
# Dan sudah diinstall di environment build
```

**3. Upload Permission Denied**
```bash
# Pastikan menggunakan API token yang benar
# Username: __token__
# Password: pypi-<your-api-token>
```

**4. Version Already Exists**
```bash
# Error: version 0.1.0 already exists
# Solusi: Update version dan upload ulang
```

## 📚 Resources

- [PyPI Documentation](https://packaging.python.org/tutorials/packaging-projects/)
- [Setuptools Documentation](https://setuptools.readthedocs.io/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PyPI Account Management](https://pypi.org/account/)

## 🎯 Best Practices

1. **Always Test First**: Gunakan TestPyPI sebelum production
2. **Version Management**: Gunakan semantic versioning (semver)
3. **Documentation**: Pastikan README.md lengkap dan akurat
4. **Dependencies**: Minimalkan dependencies dan gunakan version ranges
5. **Security**: Gunakan API token, bukan password
6. **Automation**: Buat script untuk automate build dan upload process

---

Setelah mengikuti panduan ini, package Winter akan bisa diinstall oleh siapa dari mana saja menggunakan:

```bash
pip install winter
```
