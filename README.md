# Virtual Memory Simulator

## Deskripsi
Simulator sistem manajemen memori virtual dengan paging yang dikembangkan untuk mata kuliah Sistem Operasi. Aplikasi ini mensimulasikan cara kerja Memory Management Unit (MMU) dalam menangani translasi alamat virtual ke alamat fisik, page fault, dan algoritma penggantian halaman.

## Fitur Utama
- **Simulasi Memori Virtual**: Implementasi lengkap sistem paging dengan page table
- **Algoritma Penggantian Halaman**: 
  - FIFO (First-In, First-Out)
  - LRU (Least Recently Used)
  - Optimal (Belady's Algorithm)
- **Interface Grafis**: GUI interaktif menggunakan CustomTkinter
- **Visualisasi Real-time**: Tampilan visual ruang alamat virtual dan memori fisik
- **Statistik Performa**: Monitoring hit ratio dan page fault
- **Mode Eksekusi**: Akses alamat individual atau batch reference string

## Struktur Proyek
```
virtual-memory-simulator/
├── main.py                     # Entry point aplikasi
├── README.md                   # Dokumentasi proyek
├── core/
│   ├── memory_manager.py       # Implementasi MMU dan manajemen memori
│   └── replacement_algorithms.py # Algoritma penggantian halaman
└── gui/
    ├── app.py                  # Aplikasi GUI utama
    └── theme.py                # Konfigurasi tema dan styling
```

## Requirements
```
customtkinter>=5.0.0
tkinter (built-in dengan Python)
```

## Instalasi
1. Clone repository atau download source code
2. Install dependencies:
   ```bash
   pip install customtkinter
   ```
3. Jalankan aplikasi:
   ```bash
   python main.py
   ```

## Cara Penggunaan

### 1. Konfigurasi Sistem
- **Ukuran Halaman**: Masukkan ukuran halaman dalam KB (contoh: 4)
- **Frame Fisik**: Atur jumlah frame di memori fisik (4-64 frame)
- **Algoritma**: Pilih algoritma penggantian (FIFO/LRU/Optimal)
- Klik **"Mulai / Reset Simulasi"**

### 2. Membuat Proses
- Atur jumlah halaman virtual untuk proses (8-128 halaman)
- Klik **"Buat Proses"** untuk membuat proses baru

### 3. Akses Memori
#### Akses Individual:
- Masukkan alamat virtual dalam byte (contoh: 8192)
- Klik **"Akses Alamat"**

#### Batch Reference String:
- Masukkan string referensi halaman (contoh: 0,1,2,3,0,1,4,2,1,0,3,2)
- Klik **"Jalankan String Referensi"**

### 4. Monitoring
- **Area Log**: Menampilkan aktivitas sistem secara real-time
- **Visualisasi**: Melihat status ruang alamat virtual dan memori fisik
- **Statistik**: Monitoring hits, page faults, dan hit ratio

## Algoritma yang Diimplementasikan

### FIFO (First-In, First-Out)
- Mengganti halaman yang paling lama berada di memori
- Sederhana namun tidak optimal
- Dapat mengalami Belady's Anomaly

### LRU (Least Recently Used)
- Mengganti halaman yang paling lama tidak digunakan
- Performa lebih baik dari FIFO
- Mempertimbangkan pola akses masa lalu

### Optimal (Belady's Algorithm)
- Mengganti halaman yang akan digunakan paling jauh di masa depan
- Performa optimal secara teoritis
- Membutuhkan pengetahuan referensi masa depan (hanya untuk simulasi)

## Contoh Penggunaan

### Skenario Testing:
1. **Konfigurasi**: 4KB page size, 3 frames, algoritma LRU
2. **Proses**: 16 halaman virtual
3. **Reference String**: `7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1`

### Expected Output:
- Sistem akan menampilkan setiap akses memori
- Page hit/fault untuk setiap referensi
- Visualisasi perubahan state memori
- Statistik akhir performa

## Testing dan Validasi

### Testing Algoritma:
```bash
python core/replacement_algorithms.py
```
Menjalankan pengetesan otomatis untuk memvalidasi implementasi algoritma.

### Manual Testing:
- Gunakan reference string yang sudah diketahui hasilnya
- Bandingkan output dengan perhitungan manual
- Verifikasi hit ratio dan jumlah page fault

## Fitur Visualisasi

### Ruang Alamat Virtual:
- Menampilkan semua halaman virtual proses aktif
- Indikator halaman yang ada di memori vs di disk
- Pemetaan ke frame fisik

### Memori Fisik:
- Status setiap frame (kosong/terisi)
- Informasi proses dan halaman yang menempati frame
- Counter frame yang tersedia

### Color Coding:
- 🟢 **Hijau-biru (Teal)**: Page Hit
- 🟠 **Oranye**: Page Fault (frame kosong)
- 🔴 **Merah-oranye**: Page Fault (penggantian)
- 🔵 **Biru**: Frame terisi / halaman valid
- ⚫ **Abu-abu**: Frame kosong / halaman di disk

## Troubleshooting

### Error "Ukuran Halaman harus diisi"
- Pastikan field ukuran halaman terisi dengan angka positif

### Error "Process ID tidak ditemukan"
- Buat proses terlebih dahulu sebelum mengakses memori

### Error "Format String Referensi tidak valid"
- Gunakan format: `1,2,3,4` (dipisah koma, tanpa spasi)
- Pastikan semua nilai adalah angka

### GUI Tidak Responsive
- Tutup dan restart aplikasi
- Pastikan sistem memiliki cukup RAM

## Pengembangan

### Struktur Kelas Utama:
- `MemoryManagementUnit`: Core MMU functionality
- `PhysicalMemory`: Manajemen frame fisik
- `Process`: Representasi proses dengan page table
- `ReplacementAlgorithm`: Base class untuk algoritma

### Menambah Algoritma Baru:
1. Inherit dari `ReplacementAlgorithm`
2. Implement required methods: `page_loaded`, `select_victim`, `reset`
3. Tambahkan ke `algo_map` di `app.py`

## Kontributor
Kelompok 3 - Mata Kuliah Sistem Operasi
- Akhyar Rasyid Asy-syifa (2306241682)
- Fadhlurohman Dzaki (2306202132)
- Hadyan Fachri (2306245030)
- Kevin Yehezkiel Manurung (2206826974)
- Muhammad Ruzbehan Baqli (2306245062)

## Lisensi
Proyek ini dibuat untuk keperluan edukasi mata kuliah Sistem Operasi.

---
**Catatan**: Simulator ini dibuat untuk tujuan pembelajaran dan tidak mencerminkan kompleksitas penuh sistem manajemen memori di sistem operasi nyata.