# core/replacement_algorithms.py
"""
Implementasi Algoritma Penggantian Halaman
Menyediakan tiga algoritma utama: FIFO, LRU, dan Optimal
"""

from abc import ABC, abstractmethod
from collections import deque


class ReplacementAlgorithm(ABC):
    """
    Kelas abstrak untuk semua algoritma penggantian halaman
    Menyediakan interface standar untuk semua implementasi algoritma
    """
    def __init__(self, frames_limit):
        self.frames_limit = frames_limit
        self.frame_to_page = {}     # Pemetaan nomor frame ke nomor halaman
        self.loaded_frames = set()  # Set frame yang sedang digunakan

    def page_accessed(self, frame_number, page_number):
        """Dipanggil ketika terjadi page hit (halaman diakses dari memori)"""
        pass

    @abstractmethod
    def page_loaded(self, frame_number, page_number):
        """Dipanggil ketika halaman baru dimuat ke frame tertentu"""
        pass

    @abstractmethod
    def select_victim(self, future_references=None):
        """Memilih frame korban untuk diganti. Return: nomor frame"""
        pass
    
    def page_removed(self, frame_number):
        """Dipanggil ketika halaman dihapus dari frame (saat proses dihentikan)"""
        if frame_number in self.frame_to_page:
            del self.frame_to_page[frame_number]
        self.loaded_frames.discard(frame_number)
    
    @abstractmethod
    def reset(self):
        """Reset state internal algoritma ke kondisi awal"""
        self.frame_to_page.clear()
        self.loaded_frames.clear()


class FIFO(ReplacementAlgorithm):
    """
    Algoritma First-In, First-Out (FIFO)
    Mengganti halaman yang paling lama berada di memori (first in, first out)
    """
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.queue = deque()  # Antrian frame berdasarkan urutan kedatangan

    def page_accessed(self, frame_number, page_number):
        """Pada FIFO, page hit tidak mengubah urutan antrian"""
        pass

    def page_loaded(self, frame_number, page_number):
        """Menambahkan frame baru ke akhir antrian"""
        # Jika frame sudah ada, hapus dari posisi lama
        if frame_number in self.queue:
            self.queue.remove(frame_number)
        
        self.queue.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        """Memilih frame yang pertama kali masuk (paling depan antrian)"""
        if not self.queue:
            return -1
            
        victim_frame = self.queue.popleft()
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        return victim_frame

    def reset(self):
        """Reset antrian dan data internal"""
        super().reset()
        self.queue.clear()


class LRU(ReplacementAlgorithm):
    """
    Algoritma Least Recently Used (LRU)
    Mengganti halaman yang paling lama tidak digunakan
    """
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.usage_order = []  # Daftar frame berdasarkan urutan penggunaan (terlama di index 0)

    def page_accessed(self, frame_number, page_number):
        """Memindahkan frame yang diakses ke posisi paling baru (akhir list)"""
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
            self.usage_order.append(frame_number)

    def page_loaded(self, frame_number, page_number):
        """Menambahkan frame baru ke posisi paling baru"""
        # Hapus dari posisi lama jika sudah ada
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
        
        # Tambahkan ke posisi paling baru (akhir list)
        self.usage_order.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        """Memilih frame yang paling lama tidak digunakan (awal list)"""
        if not self.usage_order:
            return -1
            
        victim_frame = self.usage_order.pop(0)
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        return victim_frame
        
    def reset(self):
        """Reset daftar urutan penggunaan"""
        super().reset()
        self.usage_order.clear()


class Optimal(ReplacementAlgorithm):
    """
    Algoritma Optimal (OPT)
    Mengganti halaman yang akan digunakan paling jauh di masa depan
    Membutuhkan informasi referensi masa depan (hanya untuk simulasi)
    """
    def __init__(self, frames_limit):
        super().__init__(frames_limit)

    def page_accessed(self, frame_number, page_number):
        """Algoritma optimal hanya peduli dengan referensi masa depan"""
        pass

    def page_loaded(self, frame_number, page_number):
        """Menambahkan pemetaan frame ke halaman"""
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        """
        Memilih frame korban berdasarkan penggunaan di masa depan
        Prioritas: halaman yang tidak akan digunakan lagi, atau yang paling jauh digunakan
        """
        if not self.loaded_frames:
            return -1
            
        # Jika tidak ada referensi masa depan, pilih frame mana saja
        if not future_references:
            victim_frame = next(iter(self.loaded_frames))
            self.loaded_frames.discard(victim_frame)
            if victim_frame in self.frame_to_page:
                del self.frame_to_page[victim_frame]
            return victim_frame

        # Cari halaman yang tidak akan digunakan lagi di masa depan
        future_pages = set(future_references)
        current_pages = set(self.frame_to_page.values())
        
        # Halaman yang tidak ada di referensi masa depan
        pages_not_in_future = current_pages - future_pages
        if pages_not_in_future:
            # Pilih salah satu halaman yang tidak akan digunakan lagi
            victim_page = pages_not_in_future.pop()
            # Cari frame yang berisi halaman tersebut
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
                # Halaman tidak ditemukan di future_references
                victim_frame = frame_num
                break
        
        # Bersihkan data dan return frame korban
        if victim_frame != -1:
            self.loaded_frames.discard(victim_frame)
            if victim_frame in self.frame_to_page:
                del self.frame_to_page[victim_frame]
            return victim_frame
        
        # Fallback jika terjadi error
        victim_frame = next(iter(self.loaded_frames))
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        return victim_frame

    def reset(self):
        """Reset data internal algoritma"""
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