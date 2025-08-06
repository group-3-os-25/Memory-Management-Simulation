# gui/theme.py
"""
Konfigurasi Tema dan Styling untuk Aplikasi Simulator Memori Virtual
Mendefinisikan palet warna dan font yang digunakan di seluruh aplikasi
"""

# Palet Warna dengan Tema Dark Mode
COLORS = {
    # Warna dasar interface
    "background": "#242424",      # Latar belakang utama aplikasi
    "foreground": "#2D2D2D",      # Latar belakang panel dan frame
    "primary": "#3A7EBF",         # Warna aksen utama (biru)
    "secondary": "#326C9E",       # Warna aksen sekunder (biru gelap)
    
    # Warna teks
    "text": "#DCE4EE",            # Teks utama (putih keabuan)
    "text_secondary": "#AAB3BE",   # Teks sekunder (abu-abu)
    
    # Warna status memori
    "frame_empty": "#3B3B3B",      # Frame kosong (abu-abu gelap)
    "page_hit": "#2A9D8F",         # Page hit (hijau-biru/teal)
    "page_fault": "#F4A261",       # Page fault (oranye)
    "page_victim": "#E76F51",      # Halaman korban (merah-oranye)
    
    # Palet warna untuk membedakan proses (P0, P1, P2, dst.)
    "PROCESS_COLORS": [
        "#3A7EBF",  # Biru (P0)
        "#34A853",  # Hijau (P1)
        "#FABB05",  # Kuning (P2)
        "#EA4335",  # Merah (P3)
        "#9C27B0",  # Ungu (P4)
        "#00BCD4",  # Cyan (P5)
        "#FF9800",  # Oranye (P6)
    ]
}

# Konfigurasi Font dan Tipografi
FONTS = {
    "title": ("Roboto", 24, "bold"),        # Judul utama aplikasi
    "heading": ("Roboto", 16, "bold"),      # Judul section dan panel
    "body": ("Roboto", 12),                 # Teks body normal
    "body_bold": ("Roboto", 12, "bold"),    # Teks body tebal
    "small": ("Roboto", 10),                # Teks kecil untuk detail
}