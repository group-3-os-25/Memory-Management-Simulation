# analisis_grafik.py
# Skrip ini untuk membuat visualisasi data dari hasil simulator memori virtual.
# Data yang digunakan di sini telah disesuaikan dengan tabel-tabel di dokumen
# "Hasil Eksperimen dan Analisis Kinerja (Final)".

import matplotlib.pyplot as plt
import numpy as np

# --- GRAFIK 1: Analisis Anomali Belady & Perbandingan Kinerja ---
# TUJUAN: Menunjukkan bagaimana jumlah page fault berubah saat jumlah frame ditambah.
# DATA DARI: Tabel hasil untuk "Test Case 5: Anomali Belady & Pola Siklis".

# Data yang dikumpulkan dari simulator Anda
frames = [3, 4]      # Jumlah frame yang diuji
faults_fifo = [9, 10] # Hasil Page Faults untuk FIFO (menunjukkan anomali)
faults_lru = [10, 8]  # Hasil Page Faults untuk LRU (kinerja membaik)

# Membuat plot
plt.figure(figsize=(10, 6)) # Mengatur ukuran gambar
plt.plot(frames, faults_fifo, marker='o', linestyle='-', color='#E76F51', label='FIFO', linewidth=2, markersize=8)
plt.plot(frames, faults_lru, marker='s', linestyle='--', color='#2A9D8F', label='LRU', linewidth=2, markersize=8)

# Memberi judul dan label
plt.title('Perbandingan Page Faults vs. Jumlah Frame\n(Test Case 5: Anomali Belady & Pola Siklis)', fontsize=16)
plt.xlabel('Jumlah Frame Fisik', fontsize=12)
plt.ylabel('Total Page Faults', fontsize=12)
plt.xticks(frames) # Memastikan sumbu-x hanya menampilkan frame yang diuji
plt.grid(True, which='both', linestyle=':', linewidth=0.7)
plt.legend(fontsize=12) # Menampilkan legenda

# Menyimpan grafik sebagai file gambar berkualitas tinggi
plt.savefig('grafik_anomali_belady.png', dpi=300, bbox_inches='tight')
print("Grafik 'grafik_anomali_belady.png' berhasil disimpan.")


# --- GRAFIK 2: Perbandingan Hit Ratio pada Beban Kerja Lokalitas ---
# TUJUAN: Menunjukkan algoritma mana yang lebih baik untuk program dengan lokalitas.
# DATA DARI: Tabel hasil untuk "Test Case 2: Pola Lokalitas Tinggi (Revisi)" dengan 4 Frame.

# Data yang dikumpulkan dari simulator Anda
algorithms = ['FIFO', 'LRU']
# Total akses untuk Test Case 2 adalah 14
total_akses = 14

# Hasil page faults untuk FIFO dan LRU dari tabel Test Case 2
page_faults_locality = [8, 6]

# Hitung hit ratio secara otomatis dari data faults
hit_ratio = [((total_akses - pf) / total_akses) * 100 for pf in page_faults_locality]

# Membuat plot batang
plt.figure(figsize=(8, 6))
bars = plt.bar(algorithms, hit_ratio, color=['#3A7EBF', '#F4A261'])

# Memberi judul dan label
plt.title('Perbandingan Hit Ratio pada Beban Kerja Lokalitas Tinggi\n(Test Case 2, Konfigurasi 4 Frame)', fontsize=16)
plt.xlabel('Algoritma Penggantian Halaman', fontsize=12)
plt.ylabel('Hit Ratio (%)', fontsize=12)
plt.ylim(0, 100) # Mengatur batas sumbu-y dari 0 hingga 100

# Menambahkan label nilai di atas setiap bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f'{yval:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Menyimpan grafik sebagai file gambar berkualitas tinggi
plt.savefig('grafik_lokalitas.png', dpi=300, bbox_inches='tight')
print("Grafik 'grafik_lokalitas.png' berhasil disimpan.")

# Untuk menampilkan kedua grafik di layar setelah dijalankan (opsional, hapus tanda #)
# plt.show()
