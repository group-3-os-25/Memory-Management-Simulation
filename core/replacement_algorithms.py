# core/replacement_algorithms.py

from abc import ABC, abstractmethod
from collections import deque

class ReplacementAlgorithm(ABC):
    """Kelas dasar abstrak untuk semua algoritma penggantian halaman."""
    def __init__(self, frames_limit):
        self.frames_limit = frames_limit
        self.resident_pages = set()

    def page_accessed(self, page_number):
        """Dipanggil saat terjadi page hit."""
        pass

    @abstractmethod
    def page_loaded(self, page_number):
        """Dipanggil saat halaman berhasil dimuat ke memori."""
        pass

    @abstractmethod
    def select_victim(self, future_references=None):
        """Pilih halaman korban untuk diganti."""
        pass
    
    @abstractmethod
    def reset(self):
        """Mereset state internal algoritma."""
        self.resident_pages.clear()

class FIFO(ReplacementAlgorithm):
    """Implementasi algoritma First-In, First-Out (FIFO)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.queue = deque()

    def page_loaded(self, page_number):
        # Jika halaman sudah ada di antrian (kasus jarang), jangan lakukan apa-apa
        if page_number in self.queue:
            return
        self.queue.append(page_number)
        self.resident_pages.add(page_number)

    def select_victim(self, future_references=None):
        victim = self.queue.popleft()
        self.resident_pages.remove(victim)
        return victim

    def reset(self):
        super().reset()
        self.queue.clear()

class LRU(ReplacementAlgorithm):
    """Implementasi algoritma Least Recently Used (LRU)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.stack = [] # Paling lama di index 0, paling baru di index -1

    def page_accessed(self, page_number):
        if page_number in self.stack:
            self.stack.remove(page_number)
            self.stack.append(page_number)

    def page_loaded(self, page_number):
        if page_number not in self.stack:
            self.stack.append(page_number)
            self.resident_pages.add(page_number)
        else: # Jika sudah ada, pindahkan ke paling belakang (paling baru)
            self.page_accessed(page_number)

    def select_victim(self, future_references=None):
        victim = self.stack.pop(0)
        self.resident_pages.remove(victim)
        return victim
        
    def reset(self):
        super().reset()
        self.stack.clear()

class Optimal(ReplacementAlgorithm):
    """Implementasi algoritma Optimal (OPT)."""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)

    def page_accessed(self, page_number):
        # Optimal tidak peduli dengan akses masa lalu, hanya masa depan
        pass

    def page_loaded(self, page_number):
        self.resident_pages.add(page_number)

    def select_victim(self, future_references):
        """Menemukan halaman yang akan digunakan paling jauh di masa depan."""
        farthest_use = -1
        victim_page = -1

        for page in self.resident_pages:
            try:
                # Cari penggunaan berikutnya dari halaman ini
                next_use_index = future_references.index(page)
                if next_use_index > farthest_use:
                    farthest_use = next_use_index
                    victim_page = page
            except ValueError:
                # Jika halaman tidak akan digunakan lagi, itu adalah korban ideal
                self.resident_pages.remove(page)
                return page
        
        # Jika semua halaman akan digunakan lagi, pilih yang paling jauh
        if victim_page != -1:
            self.resident_pages.remove(victim_page)
            return victim_page
        
        # Fallback jika terjadi sesuatu yang aneh (misal, semua halaman sama)
        fallback_victim = list(self.resident_pages)[0]
        self.resident_pages.remove(fallback_victim)
        return fallback_victim
    
    def reset(self):
        super().reset()