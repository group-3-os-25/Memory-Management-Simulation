# core/replacement_algorithms.py
"""
Implementasi Algoritma Penggantian Halaman
Menyediakan tiga algoritma utama: FIFO, LRU, dan Optimal
"""
from abc import ABC, abstractmethod
from collections import deque

class ReplacementAlgorithm(ABC):
    """Kelas abstrak untuk semua algoritma penggantian halaman."""
    def __init__(self, frames_limit):
        self.frames_limit = frames_limit
        self.frame_to_page = {}
        self.loaded_frames = set()

    def page_accessed(self, frame_number, page_number):
        """Dipanggil ketika terjadi page hit."""
        pass

    @abstractmethod
    def page_loaded(self, frame_number, page_number):
        """Dipanggil ketika halaman baru dimuat."""
        pass

    @abstractmethod
    def select_victim(self, future_references=None):
        """Memilih frame korban untuk diganti."""
        pass
    
    def page_removed(self, frame_number):
        """Dipanggil ketika halaman dihapus dari frame."""
        if frame_number in self.frame_to_page:
            del self.frame_to_page[frame_number]
        self.loaded_frames.discard(frame_number)
    
    @abstractmethod
    def reset(self):
        """Reset state internal algoritma."""
        self.frame_to_page.clear()
        self.loaded_frames.clear()

class FIFO(ReplacementAlgorithm):
    """Algoritma First-In, First-Out (FIFO)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.queue = deque()

    def page_loaded(self, frame_number, page_number):
        if frame_number not in self.queue:
            self.queue.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        if not self.queue: return -1
        victim_frame = self.queue.popleft()
        return victim_frame
    
    def page_removed(self, frame_number):
        super().page_removed(frame_number)
        if frame_number in self.queue:
            self.queue.remove(frame_number)

    def reset(self):
        super().reset()
        self.queue.clear()

class LRU(ReplacementAlgorithm):
    """Algoritma Least Recently Used (LRU)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.usage_order = []

    def page_accessed(self, frame_number, page_number):
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
        self.usage_order.append(frame_number)

    def page_loaded(self, frame_number, page_number):
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
        self.usage_order.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        if not self.usage_order: return -1
        victim_frame = self.usage_order.pop(0)
        return victim_frame
        
    def page_removed(self, frame_number):
        super().page_removed(frame_number)
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)

    def reset(self):
        super().reset()
        self.usage_order.clear()

class Optimal(ReplacementAlgorithm):
    """Algoritma Optimal (OPT)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)

    def page_loaded(self, frame_number, page_number):
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        if not self.loaded_frames: return -1
        
        victim_frame = -1
        
        if not future_references:
            victim_frame = next(iter(self.loaded_frames))
        else:
            pages_in_ram = {self.frame_to_page.get(f) for f in self.loaded_frames if self.frame_to_page.get(f) is not None}
            pages_not_in_future = pages_in_ram - set(future_references)

            if pages_not_in_future:
                #victim_page = pages_not_in_future.pop()
                victim_page = min(pages_not_in_future)
            else:
                farthest_distance = -1
                victim_page = -1
                for page_num in pages_in_ram:
                    try:
                        distance = future_references.index(page_num)
                        if distance > farthest_distance:
                            farthest_distance = distance
                            victim_page = page_num
                    except ValueError:
                        continue
                if victim_page == -1: # Fallback
                     victim_page = next(iter(pages_in_ram))

            for f_num, p_num in self.frame_to_page.items():
                if p_num == victim_page:
                    victim_frame = f_num
                    break
        
        return victim_frame

    def reset(self):
        super().reset()


# Fungsi pengetesan dan validasi algoritma
def test_algorithms():
    """
    Fungsi untuk menguji dan membandingkan performa ketiga algoritma
    Menggunakan reference string yang sudah diketahui hasilnya untuk validasi
    """
    print("=== Pengetesan Algoritma Penggantian Halaman ===")
    
    # Parameter pengetesan
    num_frames = 3
    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    
    algorithms = {
        'FIFO': FIFO(num_frames),
        'LRU': LRU(num_frames),
        'Optimal': Optimal(num_frames)
    }
    
    print(f"Reference String: {reference_string}")
    print(f"Jumlah Frame: {num_frames}")
    print("-" * 60)
    
    for algo_name, algorithm in algorithms.items():
        print(f"\n{algo_name} Algorithm:")
        page_faults = 0
        loaded_pages = set()
        
        for i, page in enumerate(reference_string):
            # Simulasi akses halaman
            if page in loaded_pages:
                # Page hit
                algorithm.page_accessed(None, page)  # Frame number tidak relevan untuk testing
                status = "HIT"
            else:
                # Page fault
                page_faults += 1
                if len(loaded_pages) < num_frames:
                    # Ada frame kosong
                    frame_num = len(loaded_pages)
                    algorithm.page_loaded(frame_num, page)
                    loaded_pages.add(page)
                    status = "FAULT (load)"
                else:
                    # Perlu penggantian
                    future_refs = reference_string[i+1:] if algo_name == 'Optimal' else None
                    victim_frame = algorithm.select_victim(future_refs)
                    
                    # Hapus halaman lama dan tambah halaman baru
                    old_page = None
                    for p in loaded_pages:
                        if algorithm.frame_to_page.get(victim_frame) == p:
                            old_page = p
                            break
                    
                    if old_page:
                        loaded_pages.remove(old_page)
                    loaded_pages.add(page)
                    algorithm.page_loaded(victim_frame, page)
                    status = f"FAULT (replace {old_page})" if old_page else "FAULT (replace)"
            
            print(f"  Step {i+1:2d}: Page {page} -> {status}")
        
        hit_ratio = ((len(reference_string) - page_faults) / len(reference_string)) * 100
        print(f"  Total Page Faults: {page_faults}")
        print(f"  Hit Ratio: {hit_ratio:.1f}%")
        
        # Reset algoritma untuk pengetesan berikutnya
        algorithm.reset()
        
    print("\n" + "=" * 60)


if __name__ == "__main__":
    """
    Menjalankan pengetesan ketika file dieksekusi langsung
    Berguna untuk validasi implementasi algoritma
    """
    test_algorithms()