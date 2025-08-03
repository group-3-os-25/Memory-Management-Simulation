# gui/theme.py
"""
Konfigurasi Tema dan Styling untuk Aplikasi Simulator Memori Virtual
Mendefinisikan palet warna dan font yang digunakan di seluruh aplikasi
"""

# Palet Warna dengan Tema Dark Mode
COLORS = {
    # Warna dasar interface
    "background": "#242424",    # Latar belakang utama aplikasi
    "foreground": "#2D2D2D",   # Latar belakang panel dan frame
    "primary": "#3A7EBF",      # Warna aksen utama (biru)
    "secondary": "#326C9E",    # Warna aksen sekunder (biru gelap)
    
    # Warna teks
    "text": "#DCE4EE",         # Teks utama (putih keabuan)
    "text_secondary": "#AAB3BE", # Teks sekunder (abu-abu)
    
    # Warna status memori
    "frame_empty": "#3B3B3B",      # Frame kosong (abu-abu gelap)
    "frame_occupied": "#3A7EBF",   # Frame terisi (biru)
    "page_hit": "#2A9D8F",         # Page hit (hijau-biru/teal)
    "page_fault": "#F4A261",       # Page fault (oranye)
    "page_victim": "#E76F51",      # Halaman korban (merah-oranye)
    "highlight": "#E9C46A",        # Highlight (kuning)
}

# Konfigurasi Font dan Tipografi
FONTS = {
    "title": ("Roboto", 24, "bold"),       # Judul utama aplikasi
    "heading": ("Roboto", 16, "bold"),     # Judul section dan panel
    "body": ("Roboto", 12),                # Teks body normal
    "body_bold": ("Roboto", 12, "bold"),   # Teks body tebal
    "small": ("Roboto", 10),               # Teks kecil untuk detail
}