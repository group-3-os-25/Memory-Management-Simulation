# core/replacement_algorithms.py
"""
Implementasi Algoritma Penggantian Halaman
Menyediakan dua algoritma utama: FIFO dan LRU
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
    def select_victim(self):
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

    def select_victim(self):
        if not self.queue:
            return -1
        victim_frame = self.queue.popleft()
        return victim_frame
    
    def page_removed(self, frame_number):
        super().page_removed(frame_number)
        # Hapus frame dari antrian jika ada, untuk kasus terminate process
        if frame_number in self.queue:
            # Membuat kembali deque tanpa elemen yang dihapus untuk menjaga integritas
            self.queue = deque([f for f in self.queue if f != frame_number])

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

    def select_victim(self):
        if not self.usage_order:
            return -1
        victim_frame = self.usage_order.pop(0)
        return victim_frame
        
    def page_removed(self, frame_number):
        super().page_removed(frame_number)
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)

    def reset(self):
        super().reset()
        self.usage_order.clear()