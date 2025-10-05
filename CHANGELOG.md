# Changelog

All notable changes to Winter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Command `winter update` untuk update package ke versi terbaru
- Command `winter check-update` untuk mengecek update tersedia
- Command `winter package-info` untuk menampilkan informasi package
- Support untuk update dependencies dengan opsi `--include-deps`
- Dynamic version detection dari package yang terinstall
- PyPI integration untuk mengecek versi terbaru
- Rich UI untuk tampilan update yang menarik

### Changed
- Improved error handling untuk command update
- Better version comparison menggunakan packaging library

### Fixed
- Import error untuk tomli di Python < 3.11

## [0.1.0] - 2024-01-XX

### Added
- Initial release of Winter
- Snowflake terminal client dengan table scrolling
- Prefix support untuk semua table references
- Dual authentication (password dan RSA keypair)
- Interactive file browser untuk private key selection
- Security controls dengan SELECT-only enforcement
- Connection timeout dan password caching
- Interactive table viewer dengan Rich tables
- Export capabilities (CSV, JSON, Excel)
- Query history dan favorites system
- Search functionality untuk history dan favorites
- Multi-environment support
- Comprehensive CLI commands
- Setup wizard untuk konfigurasi awal
- Audit logging dan security management
- Background counting untuk large datasets
- Smart column formatting dan data type detection

### Features
- 🔐 Dual Authentication Support (Password & RSA Keypair)
- 🔍 Interactive File Browser untuk .p8 file selection
- 🏷️ Automatic Table Prefix System
- 🔒 Security Controls dengan SELECT-only enforcement
- ⏰ Connection Timeout (5 menit default)
- 📊 Interactive Table Display dengan Rich tables
- 🎮 Advanced Scrolling (Arrow keys & WASD)
- 📈 Data Analysis dengan intelligent formatting
- 📁 Export ke CSV, JSON, dan Excel (XLSX)
- 📝 Query History dengan searchable content
- ⭐ Favorites System dengan tags
- 🔍 Search Functionality
- 🌍 Multi-Environment Support
- ⚡ High Performance optimization

### Technical Details
- Python 3.8+ support
- Dependencies: snowflake-connector-python, cryptography, rich, click, dll
- Cross-platform compatibility
- MIT License
- Comprehensive error handling
- Rich console output dengan colors dan formatting
- Modular architecture dengan clean separation of concerns

---

## Version History

- **0.1.0**: Initial release dengan semua core features
- **Future versions**: Akan mengikuti semantic versioning (MAJOR.MINOR.PATCH)

## Migration Guide

### From Development to Production
Jika Anda menggunakan Winter dari source code, migrasi ke PyPI:

```bash
# Uninstall development version
pip uninstall winter

# Install from PyPI
pip install winter

# Run setup wizard
winter setup
```

### Configuration Migration
Konfigurasi tetap kompatibel antara versi. File config di `~/.winter/config.yaml` akan tetap digunakan.

## Support

Untuk pertanyaan atau masalah:
- GitHub Issues: https://github.com/ilham-fauzi/winter/issues
- Documentation: https://github.com/ilham-fauzi/winter/wiki
- Discussions: https://github.com/ilham-fauzi/winter/discussions
