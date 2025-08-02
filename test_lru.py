def lru_page_replacement(pages, frame_size):
    """
    Implementasi algoritma LRU (Least Recently Used) untuk penggantian halaman.
    
    Args:
        pages: List referensi halaman.
        frame_size: Jumlah frame fisik yang tersedia.
    
    Returns:
        Dictionary berisi hasil simulasi.
    """
    frames = []  # Menyimpan halaman dalam frame
    usage_order = [] # Melacak urutan penggunaan (paling lama di index 0)
    page_faults = 0
    hits = 0
    results = []
    
    print(f"=== SIMULASI ALGORITMA LRU ===")
    print(f"Frame Size: {frame_size}")
    print(f"Page References: {pages}")
    print(f"Total References: {len(pages)}")
    print("\n" + "="*80)
    
    header = f"{'Ref':<4} {'Page':<5} "
    for i in range(frame_size):
        header += f"{'Frame'+str(i+1):<8} "
    header += f"{'Result':<8} {'Action':<25}"
    print(header)
    print("-" * len(header))
    
    for ref_num, page in enumerate(pages, 1):
        action = ""
        
        if page in frames:
            # Page Hit
            hits += 1
            result_type = "HIT"
            action = f"Page {page} found"
            
            # Update urutan penggunaan: pindahkan halaman yang diakses ke paling belakang (paling baru)
            usage_order.remove(page)
            usage_order.append(page)
        else:
            # Page Fault
            page_faults += 1
            result_type = "FAULT"
            
            if len(frames) < frame_size:
                # Frame masih kosong
                frames.append(page)
                usage_order.append(page)
                action = f"Load page {page}"
            else:
                # Frame penuh, ganti halaman yang paling lama tidak digunakan (LRU)
                victim_page = usage_order.pop(0) # Ambil korban dari awal list
                victim_index = frames.index(victim_page)
                frames[victim_index] = page # Ganti di posisi yang sama
                
                usage_order.append(page) # Tambahkan halaman baru sebagai yang paling baru
                action = f"Replace {victim_page} with {page}"
        
        # Tampilkan hasil langkah ini
        row = f"{ref_num:<4} {page:<5} "
        # Buat salinan frame yang urutannya sesuai untuk ditampilkan
        display_frames = frames[:] + ['-'] * (frame_size - len(frames))
        for item in display_frames:
            row += f"{item:<8} "
        row += f"{result_type:<8} {action:<25}"
        print(row)

        results.append({
            'reference': ref_num, 'page': page, 'frames': frames.copy(),
            'result': result_type, 'action': action
        })
    
    total_references = len(pages)
    hit_rate = (hits / total_references) * 100 if total_references > 0 else 0
    
    print("\n" + "="*80)
    print(f"=== HASIL SIMULASI LRU ===")
    print(f"Total Page Faults: {page_faults}")
    print(f"Total Hits: {hits}")
    print(f"Hit Rate: {hit_rate:.2f}%")
    
    return {
        'algorithm': 'LRU', 'page_faults': page_faults, 'hits': hits,
        'hit_rate': hit_rate, 'details': results
    }


def analyze_lru_behavior(pages, frame_size):
    """Analisis perilaku algoritma LRU dengan visualisasi yang lebih detail."""
    print(f"\n=== ANALISIS PERILAKU LRU ===")
    
    frames = []
    usage_order = []
    for i, page in enumerate(pages):
        print(f"\nStep {i+1}: Processing page {page}")
        print(f"Current frames: {frames}")
        print(f"Usage order (Oldest -> Newest): {usage_order}")
        
        if page in frames:
            # --- BLOK INI YANG DIPERBAIKI ---
            print(f"✓ HIT: Page {page} found in frames")
            usage_order.remove(page)
            usage_order.append(page)
            print(f"→ Updated usage order")
        else:
            # --- DAN BLOK INI ---
            print(f"✗ FAULT: Page {page} not in frames")
            if len(frames) < frame_size:
                frames.append(page)
                usage_order.append(page)
                print(f"→ Added page {page} to frame (frame not full)")
            else:
                victim = usage_order.pop(0)
                victim_idx = frames.index(victim)
                frames[victim_idx] = page
                usage_order.append(page)
                print(f"→ Replaced oldest page {victim} with {page}")
        
        print(f"Frames after: {frames}")
        print(f"Usage order after: {usage_order}")


def main():
    """Fungsi utama untuk menjalankan simulasi LRU."""
    page_references = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 5, 7, 8, 3, 5]
    frame_size = 4
    
    # Jalankan simulasi LRU
    result = lru_page_replacement(page_references, frame_size)
    
    # Contoh mengakses hasil
    print(f"\nRingkasan:")
    print(f"Algoritma: {result['algorithm']}")
    print(f"Page Faults: {result['page_faults']}")
    print(f"Hits: {result['hits']}")
    
    # Jalankan analisis tambahan yang lebih detail
    analyze_lru_behavior(page_references, frame_size)


if __name__ == "__main__":
    main()