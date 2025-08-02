# Fixed replacement_algorithms.py - Consistent with GUI implementation

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
    """FIFO implementation yang konsisten dengan GUI"""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.queue = deque()  # menyimpan frame_number berdasarkan urutan masuk
        self.load_order = {}  # tracking urutan pemuatan untuk debugging
        self.load_counter = 0  # counter untuk tracking urutan
        
    def page_accessed(self, frame_number, page_number):
        """FIFO tidak mengubah urutan saat page hit"""
        pass

    def page_loaded(self, frame_number, page_number):
        """Menambahkan frame ke queue FIFO"""
        # Jika frame sudah ada, hapus dari posisi lama
        if frame_number in self.queue:
            self.queue.remove(frame_number)
            
        # Tambahkan ke akhir queue sebagai yang terbaru masuk
        self.queue.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)
        
        # Track urutan untuk debugging
        self.load_counter += 1
        self.load_order[frame_number] = self.load_counter

    def select_victim(self, future_references=None):
        """Pilih frame yang paling lama (first-in)"""
        if not self.queue:
            return -1
            
        # Ambil frame yang paling lama dari depan queue
        victim_frame = self.queue.popleft()
        
        # Bersihkan tracking
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        if victim_frame in self.load_order:
            del self.load_order[victim_frame]
            
        return victim_frame
    
    def get_queue_status(self):
        """Utility method untuk debugging"""
        return {
            'queue_order': list(self.queue),
            'frame_to_page': dict(self.frame_to_page),
            'load_order': dict(self.load_order)
        }

    def reset(self):
        """Reset semua state internal"""
        super().reset()
        self.queue.clear()
        self.load_order.clear()
        self.load_counter = 0

class LRU(ReplacementAlgorithm):
    """LRU implementation"""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)
        self.usage_order = []  # frame paling lama di index 0

    def page_accessed(self, frame_number, page_number):
        """Memindahkan frame ke posisi paling baru"""
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
            self.usage_order.append(frame_number)

    def page_loaded(self, frame_number, page_number):
        """Menambahkan frame baru ke posisi paling baru"""
        if frame_number in self.usage_order:
            self.usage_order.remove(frame_number)
        
        self.usage_order.append(frame_number)
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        """Pilih frame yang paling lama tidak digunakan"""
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
    """Optimal implementation"""
    def __init__(self, frames_limit):
        super().__init__(frames_limit)

    def page_accessed(self, frame_number, page_number):
        """Optimal tidak peduli dengan akses masa lalu"""
        pass

    def page_loaded(self, frame_number, page_number):
        """Menambahkan mapping frame ke page"""
        self.frame_to_page[frame_number] = page_number
        self.loaded_frames.add(frame_number)

    def select_victim(self, future_references=None):
        """Pilih frame berdasarkan penggunaan masa depan"""
        if not self.loaded_frames:
            return -1
            
        if not future_references:
            victim_frame = next(iter(self.loaded_frames))
            self.loaded_frames.discard(victim_frame)
            if victim_frame in self.frame_to_page:
                del self.frame_to_page[victim_frame]
            return victim_frame

        # Cari frame yang halaman-nya tidak akan digunakan lagi
        future_pages = set(future_references)
        current_pages = set(self.frame_to_page.values())
        
        pages_not_in_future = current_pages - future_pages
        if pages_not_in_future:
            #victim_page = pages_not_in_future.pop()
            victim_page = min(pages_not_in_future)
            for frame_num, page_num in self.frame_to_page.items():
                if page_num == victim_page:
                    self.loaded_frames.discard(frame_num)
                    del self.frame_to_page[frame_num]
                    return frame_num
        
        # Jika semua halaman akan digunakan, cari yang paling jauh
        farthest_distance = -1
        victim_frame = -1
        
        for frame_num, page_num in self.frame_to_page.items():
            try:
                distance = future_references.index(page_num)
                if distance > farthest_distance:
                    farthest_distance = distance
                    victim_frame = frame_num
            except ValueError:
                victim_frame = frame_num
                break
        
        if victim_frame != -1:
            self.loaded_frames.discard(victim_frame)
            if victim_frame in self.frame_to_page:
                del self.frame_to_page[victim_frame]
            return victim_frame
        
        # Fallback
        victim_frame = next(iter(self.loaded_frames))
        self.loaded_frames.discard(victim_frame)
        if victim_frame in self.frame_to_page:
            del self.frame_to_page[victim_frame]
        return victim_frame

    def reset(self):
        super().reset()


# FIXED SIMULATOR - Konsisten dengan GUI
class FixedPageReplacementSimulator:
    """Simulator yang konsisten dengan GUI implementation"""
    
    def __init__(self, algorithm_class, frames_limit):
        self.algorithm = algorithm_class(frames_limit)
        self.frames_limit = frames_limit
        self.current_frames = {}  # frame_number -> page_number
        
    def simulate(self, page_references, verbose=True):
        """Simulasi dengan implementasi yang konsisten"""
        page_faults = 0
        hits = 0
        results = []
        
        if verbose:
            print(f"=== FIXED SIMULASI ALGORITMA {self.algorithm.__class__.__name__} ===")
            print(f"Frame Size: {self.frames_limit}")
            print(f"Page References: {page_references}")
            print(f"Total References: {len(page_references)}")
            print("\n" + "="*80)
            
            header = f"{'Ref':<4} {'Page':<5} "
            for i in range(self.frames_limit):
                header += f"{'Frame'+str(i):<8} "
            header += f"{'Result':<8} {'Action':<30}"
            print(header)
            print("-" * len(header))
        
        for ref_num, page in enumerate(page_references, 1):
            # Check if page is already in frames
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
                    # FIXED: Use consistent frame allocation like GUI
                    available_frames = set(range(self.frames_limit)) - set(self.current_frames.keys())
                    frame_num = min(available_frames)  # Consistent with GUI
                    
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
                row += f"{result_type:<8} {action:<30}"
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
        """Helper method untuk menemukan frame yang berisi halaman tertentu"""
        for frame_num, page_num in self.current_frames.items():
            if page_num == page:
                return frame_num
        return None
    
    def reset(self):
        """Reset simulator dan algorithm"""
        self.algorithm.reset()
        self.current_frames.clear()


def test_consistency():
    """Test konsistensi antara implementasi lama dan baru"""
    print("="*100)
    print("TESTING CONSISTENCY BETWEEN OLD AND NEW IMPLEMENTATIONS")
    print("="*100)
    
    # Test dengan reference string yang sama
    ref_string = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1, 5, 7, 8, 3, 5]
    frames_limit = 4
    
    # Test dengan fixed simulator
    print("Testing FIXED Simulator:")
    fixed_sim = FixedPageReplacementSimulator(FIFO, frames_limit)
    fixed_result = fixed_sim.simulate(ref_string)
    
    print("\nTesting dengan reference string dari GUI (simulasi):")
    gui_ref_string = [0, 1, 2, 3, 0, 1, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    gui_sim = FixedPageReplacementSimulator(FIFO, 4)
    gui_result = gui_sim.simulate(gui_ref_string)

if __name__ == "__main__":
    test_consistency()