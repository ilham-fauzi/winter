# Winter Update Commands

Dokumentasi untuk command update package Winter.

## Command Update

### `winter update`
Update Winter package ke versi terbaru.

**Opsi:**
- `--check-only`: Hanya cek versi terbaru tanpa melakukan update
- `--include-deps`: Update dependencies juga

**Contoh penggunaan:**
```bash
# Cek versi terbaru saja
winter update --check-only

# Update Winter ke versi terbaru
winter update

# Update Winter dan semua dependencies
winter update --include-deps
```

### `winter check-update`
Cek apakah ada update tersedia untuk Winter.

**Contoh penggunaan:**
```bash
winter check-update
```

### `winter package-info`
Tampilkan informasi detail package Winter.

**Contoh penggunaan:**
```bash
winter package-info
```

## Fitur

1. **Pengecekan Versi Otomatis**: Command akan otomatis mengecek versi terbaru dari PyPI
2. **Konfirmasi Update**: Meminta konfirmasi sebelum melakukan update
3. **Update Dependencies**: Opsi untuk update semua dependencies
4. **Informasi Package**: Menampilkan informasi detail package dan dependencies
5. **Error Handling**: Menangani error dengan baik dan memberikan saran perbaikan

## Persyaratan

- Koneksi internet untuk mengecek versi terbaru
- Package `packaging` untuk membandingkan versi
- Package `tomli` untuk Python < 3.11 (otomatis terinstall)

## Catatan

- Command update akan menggunakan pip untuk melakukan update
- Pastikan Anda memiliki permission untuk menginstall package
- Restart terminal setelah update untuk memastikan perubahan diterapkan
