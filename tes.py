def fifo_page_replacement(pages, frame_size):
    """
    Implementasi algoritma FIFO (First-In, First-Out) untuk penggantian halaman
    
    Args:
        pages: List referensi halaman
        frame_size: Jumlah frame fisik yang tersedia
    
    Returns:
        Dictionary berisi hasil simulasi
    """
    frames = []  # Menyimpan halaman dalam frame
    page_faults = 0
    hits = 0
    results = []  # Menyimpan detail setiap langkah
    
    print(f"=== SIMULASI ALGORITMA FIFO ===")
    print(f"Frame Size: {frame_size}")
    print(f"Page References: {pages}")
    print(f"Total References: {len(pages)}")
    print("\n" + "="*80)
    
    # Header tabel
    header = f"{'Ref':<4} {'Page':<5} "
    for i in range(frame_size):
        header += f"{'Frame'+str(i+1):<8} "
    header += f"{'Result':<8} {'Action':<20}"
    print(header)
    print("-" * len(header))
    
    for ref_num, page in enumerate(pages, 1):
        result_type = ""
        action = ""
        frames_before = frames.copy()
        
        if page in frames:
            # Page Hit - halaman sudah ada di frame
            hits += 1
            result_type = "HIT"
            action = f"Page {page} found"
        else:
            # Page Fault - halaman tidak ada di frame
            page_faults += 1
            result_type = "FAULT"
            
            if len(frames) < frame_size:
                # Frame masih ada yang kosong
                frames.append(page)
                action = f"Load page {page}"
            else:
                # Frame penuh, ganti halaman pertama (FIFO)
                replaced_page = frames.pop(0)  # Hapus yang pertama masuk
                frames.append(page)  # Tambah halaman baru di akhir
                action = f"Replace {replaced_page} with {page}"
        
        # Tampilkan hasil langkah ini
        row = f"{ref_num:<4} {page:<5} "
        for i in range(frame_size):
            if i < len(frames):
                row += f"{frames[i]:<8} "
            else:
                row += f"{'-':<8} "
        row += f"{result_type:<8} {action:<20}"
        print(row)
        
        # Simpan hasil untuk return
        results.append({
            'reference': ref_num,
            'page': page,
            'frames': frames.copy(),
            'result': result_type,
            'action': action
        })
    
    # Hitung statistik
    total_references = len(pages)
    hit_rate = (hits / total_references) * 100
    fault_rate = (page_faults / total_references) * 100
    
    print("\n" + "="*80)
    print(f"=== HASIL SIMULASI FIFO ===")
    print(f"Total Page Faults: {page_faults}")
    print(f"Total Hits: {hits}")
    print(f"Hit Rate: {hit_rate:.2f}%")
    print(f"Fault Rate: {fault_rate:.2f}%")
    
    return {
        'algorithm': 'FIFO',
        'page_faults': page_faults,
        'hits': hits,
        'hit_rate': hit_rate,
        'fault_rate': fault_rate,
        'total_references': total_references,
        'details': results
    }


def main():
    """
    Fungsi utama untuk menjalankan simulasi
    """
    # Data dari dokumen yang Anda berikan
    page_references = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 5, 7, 8, 3, 5]
    frame_size = 4
    
    # Jalankan simulasi FIFO
    result = fifo_page_replacement(page_references, frame_size)
    
    # Contoh mengakses hasil
    print(f"\nRingkasan:")
    print(f"Algoritma: {result['algorithm']}")
    print(f"Page Faults: {result['page_faults']}")
    print(f"Hits: {result['hits']}")
    print(f"Hit Rate: {result['hit_rate']:.2f}%")


# Fungsi tambahan untuk analisis lebih detail
def analyze_fifo_behavior(pages, frame_size):
    """
    Analisis perilaku algoritma FIFO dengan visualisasi yang lebih detail
    """
    print(f"\n=== ANALISIS PERILAKU FIFO ===")
    
    frames = []
    for i, page in enumerate(pages):
        print(f"\nStep {i+1}: Processing page {page}")
        print(f"Current frames: {frames}")
        
        if page in frames:
            print(f"✓ HIT: Page {page} found in frames")
        else:
            print(f"✗ FAULT: Page {page} not in frames")
            if len(frames) < frame_size:
                frames.append(page)
                print(f"→ Added page {page} to frame (frame not full)")
            else:
                oldest = frames.pop(0)
                frames.append(page)
                print(f"→ Replaced oldest page {oldest} with {page}")
        
        print(f"Frames after: {frames}")


if __name__ == "__main__":
    main()
    
    # Jalankan analisis tambahan
    page_references = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 5, 7, 8, 3, 5]
    analyze_fifo_behavior(page_references, 4)