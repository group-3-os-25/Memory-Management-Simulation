# core/replacement_algorithms.py

from abc import ABC, abstractmethod
from collections import deque

class ReplacementAlgorithm(ABC):
    """Kelas dasar abstrak untuk semua algoritma penggantian halaman."""
    def __init__(self, frames_limit):
        self.frames_limit = frames_limit
        self.frame_to_page = {}  # mapping frame_number -> page_number
        self.loaded_frames = set()  # set of frame numbers yang sedang digunakan

    def page_accessed(self, frame_number, page_number):
        """Dipanggil saat terjadi page hit."""
        pass

    @abstractmethod
    def page_loaded(self, frame_number, page_number):
        """Dipanggil saat halaman berhasil dimuat ke frame tertentu."""
        pass

    @abstractmethod
    def select_victim(self, future_references=None):
        """Pilih frame korban untuk diganti. Return frame_number."""
        pass
    
    def page_removed(self, frame_number):
        """Dipanggil saat halaman dihapus dari frame."""
        if frame_number in self.frame_to_page:
            del self.frame_to_page[frame_number]
        self.loaded_frames.discard(frame_number)
    
    @abstractmethod
    def reset(self):
        """Mereset state internal algoritma."""
        self.frame_to_page.clear()
        self.loaded_frames.clear()

class FIFO(ReplacementAlgorithm):
    """
    Implementasi algoritma First-In, First-Out (FIFO).
    Enhanced version dengan logging dan visualisasi yang lebih baik.
    """
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.queue = deque()  # menyimpan frame_number berdasarkan urutan masuk
        self.load_order = {}  # tracking urutan pemuatan untuk debugging
        self.load_counter = 0  # counter untuk tracking urutan
        
    def page_accessed(self, frame_number, page_number):
        """
        Pada FIFO, page hit tidak mengubah state urutan antrian.
        Ini adalah perbedaan utama dengan LRU dimana akses mempengaruhi urutan.
        """
        # FIFO tidak peduli dengan akses - urutan tetap berdasarkan waktu masuk
        pass

    def page_loaded(self, frame_number, page_number):
        """
        Dipanggil saat page fault untuk menambahkan frame baru ke antrian.
        Frame ditambahkan di akhir antrian (newest).
        """
        # Jika frame sudah ada, hapus dari posisi lama (seharusnya tidak terjadi dalam FIFO normal)
        if frame_number in self.queue:
            self.queue.remove(frame_number)
            
        # Tambahkan ke akhir antrian sebagai yang terbaru masuk
        self.queue.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)
        
        # Track urutan untuk debugging
        self.load_counter += 1
        self.load_order[frame_number] = self.load_counter

    def select_victim(self, future_references=None):
        """
        Pilih dan hapus frame yang pertama kali masuk (oldest).
        Ini mengimplementasikan prinsip FIFO: First-In, First-Out.
        """
        if not self.queue:
            return -1
            
        # Ambil frame yang paling lama (first-in) dari depan antrian
        victim_frame = self.queue.popleft()
        
        # Bersihkan tracking
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        if victim_frame in self.load_order:
            del self.load_order[victim_frame]
            
        return victim_frame
    
    def get_queue_status(self):
        """Utility method untuk debugging - menampilkan status antrian FIFO"""
        return {
            'queue_order': list(self.queue),  # oldest -> newest
            'frame_to_page': dict(self.frame_to_page),
            'load_order': dict(self.load_order)
        }

    def reset(self):
        """Reset semua state internal algoritma FIFO"""
        super().reset()
        self.queue.clear()
        self.load_order.clear()
        self.load_counter = 0

class LRU(ReplacementAlgorithm):
    """Implementasi algoritma Least Recently Used (LRU)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.usage_order = []  # frame paling lama di index 0, paling baru di index -1

    def page_accessed(self, frame_number, page_number):
        """
        Memindahkan frame yang diakses ke posisi paling baru (akhir list).
        Ini adalah perbedaan utama dengan FIFO - LRU memperbarui urutan saat akses.
        """
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
            self.usage_order.append(frame_number)

    def page_loaded(self, frame_number, page_number):
        """Menambahkan frame baru atau memperbarui posisinya jika sudah ada."""
        # Hapus dari posisi lama jika ada
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
        
        # Tambahkan ke posisi paling baru
        self.usage_order.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        """Pilih dan hapus frame yang paling lama tidak digunakan (awal list)."""
        if not self.usage_order:
            return -1
            
        victim_frame = self.usage_order.pop(0)
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        return victim_frame
        
    def reset(self):
        super().reset()
        self.usage_order.clear()

class Optimal(ReplacementAlgorithm):
    """Implementasi algoritma Optimal (OPT)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)

    def page_accessed(self, frame_number, page_number):
        """Optimal tidak peduli dengan akses masa lalu, hanya masa depan."""
        pass

    def page_loaded(self, frame_number, page_number):
        """Menambahkan mapping frame ke page."""
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        """Pilih frame korban berdasarkan penggunaan di masa depan."""
        if not self.loaded_frames:
            return -1
            
        if not future_references:
            # Jika tidak ada referensi masa depan, pilih frame mana saja
            victim_frame = next(iter(self.loaded_frames))
            self.loaded_frames.discard(victim_frame)
            if victim_frame in self.frame_to_page:
                del self.frame_to_page[victim_frame]
            return victim_frame

        # Cari frame yang halaman-nya tidak akan digunakan lagi
        future_pages = set(future_references)
        current_pages = set(self.frame_to_page.values())
        
        # Halaman yang tidak akan digunakan lagi
        pages_not_in_future = current_pages - future_pages
        if pages_not_in_future:
            # Pilih salah satu halaman yang tidak akan digunakan
            victim_page = pages_not_in_future.pop()
            # Cari frame yang berisi halaman ini
            for frame_num, page_num in self.frame_to_page.items():
                if page_num == victim_page:
                    self.loaded_frames.discard(frame_num)
                    del self.frame_to_page[frame_num]
                    return frame_num
        
        # Jika semua halaman akan digunakan, cari yang paling jauh di masa depan
        farthest_distance = -1
        victim_frame = -1
        
        for frame_num, page_num in self.frame_to_page.items():
            try:
                # Cari posisi pertama halaman ini di future_references
                distance = future_references.index(page_num)
                if distance > farthest_distance:
                    farthest_distance = distance
                    victim_frame = frame_num
            except ValueError:
                # Halaman tidak ditemukan di future_references (seharusnya tidak terjadi)
                victim_frame = frame_num
                break
        
        if victim_frame != -1:
            self.loaded_frames.discard(victim_frame)
            if victim_frame in self.frame_to_page:
                del self.frame_to_page[victim_frame]
            return victim_frame
        
        # Fallback jika terjadi kesalahan logika
        victim_frame = next(iter(self.loaded_frames))
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        return victim_frame

    def reset(self):
        super().reset()


# Utility class untuk simulasi yang kompatibel dengan implementasi sebelumnya
class PageReplacementSimulator:
    """
    Simulator yang menggunakan algoritma replacement dengan interface yang familiar.
    Menggabungkan fleksibilitas arsitektur OOP dengan kemudahan penggunaan.
    """
    
    def __init__(self, algorithm_class, frames_limit):
        self.algorithm = algorithm_class(frames_limit)
        self.frames_limit = frames_limit
        self.current_frames = {}  # frame_number -> page_number (untuk display)
        self.next_frame_number = 0
        
    def simulate(self, page_references, verbose=True):
        """
        Menjalankan simulasi dengan interface yang mirip implementasi sebelumnya.
        """
        page_faults = 0
        hits = 0
        results = []
        
        if verbose:
            print(f"=== SIMULASI ALGORITMA {self.algorithm.__class__.__name__} ===")
            print(f"Frame Size: {self.frames_limit}")
            print(f"Page References: {page_references}")
            print(f"Total References: {len(page_references)}")
            print("\n" + "="*80)
            
            # Header tabel
            header = f"{'Ref':<4} {'Page':<5} "
            for i in range(self.frames_limit):
                header += f"{'Frame'+str(i):<8} "
            header += f"{'Result':<8} {'Action':<25}"
            print(header)
            print("-" * len(header))
        
        for ref_num, page in enumerate(page_references, 1):
            # Cek apakah halaman sudah ada di frame
            page_in_frame = page in self.current_frames.values()
            
            if page_in_frame:
                # Page Hit
                hits += 1
                result_type = "HIT"
                action = f"Page {page} found"
                
                # Notify algorithm tentang akses
                frame_num = self._find_frame_with_page(page)
                if frame_num is not None:
                    self.algorithm.page_accessed(frame_num, page)
                    
            else:
                # Page Fault
                page_faults += 1
                result_type = "FAULT"
                
                if len(self.current_frames) < self.frames_limit:
                    # Ada frame kosong
                    frame_num = self.next_frame_number
                    self.next_frame_number += 1
                    
                    self.current_frames[frame_num] = page
                    self.algorithm.page_loaded(frame_num, page)
                    action = f"Load page {page} to frame {frame_num}"
                    
                else:
                    # Frame penuh, perlu replacement
                    future_refs = page_references[ref_num:] if hasattr(self.algorithm, 'select_victim') else None
                    victim_frame = self.algorithm.select_victim(future_refs)
                    
                    if victim_frame in self.current_frames:
                        replaced_page = self.current_frames[victim_frame]
                        action = f"Replace page {replaced_page} with {page} (frame {victim_frame})"
                    else:
                        action = f"Load page {page} to frame {victim_frame}"
                    
                    self.current_frames[victim_frame] = page
                    self.algorithm.page_loaded(victim_frame, page)
            
            if verbose:
                # Tampilkan hasil langkah ini
                row = f"{ref_num:<4} {page:<5} "
                for i in range(self.frames_limit):
                    if i in self.current_frames:
                        row += f"{self.current_frames[i]:<8} "
                    else:
                        row += f"{'-':<8} "
                row += f"{result_type:<8} {action:<25}"
                print(row)
            
            # Simpan hasil
            results.append({
                'reference': ref_num,
                'page': page,
                'frames': dict(self.current_frames),
                'result': result_type,
                'action': action
            })
        
        # Hitung statistik
        total_references = len(page_references)
        hit_rate = (hits / total_references) * 100
        fault_rate = (page_faults / total_references) * 100
        
        if verbose:
            print("\n" + "="*80)
            print(f"=== HASIL SIMULASI {self.algorithm.__class__.__name__} ===")
            print(f"Total Page Faults: {page_faults}")
            print(f"Total Hits: {hits}")
            print(f"Hit Rate: {hit_rate:.2f}%")
            print(f"Fault Rate: {fault_rate:.2f}%")
        
        return {
            'algorithm': self.algorithm.__class__.__name__,
            'page_faults': page_faults,
            'hits': hits,
            'hit_rate': hit_rate,
            'fault_rate': fault_rate,
            'total_references': total_references,
            'details': results
        }
    
    def _find_frame_with_page(self, page):
        """Helper method untuk menemukan frame yang berisi halaman tertentu."""
        for frame_num, page_num in self.current_frames.items():
            if page_num == page:
                return frame_num
        return None
    
    def reset(self):
        """Reset simulator dan algorithm."""
        self.algorithm.reset()
        self.current_frames.clear()
        self.next_frame_number = 0


# Contoh penggunaan yang kompatibel dengan implementasi sebelumnya
def main():
    """Demonstrasi penggunaan dengan data yang sama seperti sebelumnya."""
    page_references = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 5, 7, 8, 3, 5]
    frames_limit = 4
    
    # Test FIFO
    print("Testing Enhanced FIFO Algorithm:")
    fifo_sim = PageReplacementSimulator(FIFO, frames_limit)
    fifo_result = fifo_sim.simulate(page_references)
    
    # Test LRU untuk perbandingan
    print("\n" + "="*80)
    print("Testing LRU Algorithm:")
    lru_sim = PageReplacementSimulator(LRU, frames_limit)
    lru_result = lru_sim.simulate(page_references)
    
    # Test Optimal untuk perbandingan
    print("\n" + "="*80)
    print("Testing Optimal Algorithm:")
    opt_sim = PageReplacementSimulator(Optimal, frames_limit)
    opt_result = opt_sim.simulate(page_references)
    
    # Ringkasan perbandingan
    print("\n" + "="*80)
    print("=== PERBANDINGAN ALGORITMA ===")
    algorithms = [
        ("FIFO", fifo_result),
        ("LRU", lru_result), 
        ("Optimal", opt_result)
    ]
    
    print(f"{'Algorithm':<10} {'Page Faults':<12} {'Hits':<6} {'Hit Rate':<10}")
    print("-" * 45)
    for name, result in algorithms:
        print(f"{name:<10} {result['page_faults']:<12} {result['hits']:<6} {result['hit_rate']:<10.2f}%")


