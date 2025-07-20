# core/memory_manager.py

import math
from core.replacement_algorithms import FIFO, LRU, Optimal

class PageTableEntry:
    """Mewakili satu entri dalam tabel halaman."""
    def __init__(self):
        self.frame_number = -1
        self.valid = False
        self.dirty = False # Tidak digunakan di sim ini, tapi penting secara konsep

class Process:
    """Mewakili sebuah proses dengan ruang alamat virtualnya sendiri."""
    def __init__(self, pid, virtual_address_space_size, page_size):
        self.pid = pid
        self.num_pages = math.ceil(virtual_address_space_size / page_size)
        self.page_table = [PageTableEntry() for _ in range(self.num_pages)]

    def get_page_entry(self, page_number):
        if 0 <= page_number < self.num_pages:
            return self.page_table[page_number]
        return None

class PhysicalMemory:
    """Mewakili memori fisik (RAM) yang terdiri dari frame."""
    def __init__(self, num_frames, page_size):
        self.num_frames = num_frames
        self.page_size = page_size
        # Setiap frame menyimpan tuple (pid, page_number) atau None jika kosong
        self.frames = [None] * num_frames
        self.free_frames = list(range(num_frames))

    def allocate_frame(self, pid, page_number):
        if not self.free_frames:
            return -1 # Tidak ada frame kosong
        frame_number = self.free_frames.pop(0) # Ambil frame kosong pertama
        self.frames[frame_number] = (pid, page_number)
        return frame_number

    def free_frame(self, frame_number):
        if 0 <= frame_number < self.num_frames and self.frames[frame_number] is not None:
            self.frames[frame_number] = None
            # Tambahkan kembali ke daftar frame kosong dan jaga agar tetap terurut
            self.free_frames.append(frame_number)
            self.free_frames.sort()

    def find_frame_of_page(self, target_pid, target_page_number):
        """Mencari nomor frame yang berisi halaman tertentu dari proses tertentu."""
        for i, content in enumerate(self.frames):
            if content == (target_pid, target_page_number):
                return i
        return -1


class MemoryManagementUnit:
    """MMU menangani terjemahan alamat, page faults, dan alokasi."""
    def __init__(self, physical_memory, replacement_algorithm):
        self.physical_memory = physical_memory
        self.replacement_algorithm = replacement_algorithm
        self.processes = {}
        self.next_pid = 0
        self.stats = {"hits": 0, "faults": 0}

    def create_process(self, virtual_size, page_size):
        pid = self.next_pid
        process = Process(pid, virtual_size, page_size)
        self.processes[pid] = process
        self.next_pid += 1
        return pid

    def terminate_process(self, pid):
        if pid in self.processes:
            process = self.processes[pid]
            # Bebaskan semua frame yang dialokasikan untuk proses ini
            for page_entry in process.page_table:
                if page_entry.valid:
                    self.physical_memory.free_frame(page_entry.frame_number)
            del self.processes[pid]
            return True
        return False

    def access_virtual_address(self, pid, virtual_address, future_references=None):
        """Fungsi utama untuk simulasi akses memori dengan logika yang diperbaiki."""
        if pid not in self.processes:
            return "Error: Process ID tidak ditemukan.", None

        process = self.processes[pid]
        page_size = self.physical_memory.page_size
        page_number = virtual_address // page_size
        offset = virtual_address % page_size

        if page_number >= process.num_pages:
            return f"Error: Alamat virtual {virtual_address} di luar batas untuk Proses {pid}.", None

        page_entry = process.get_page_entry(page_number)

        # --- Kasus 1: Page Hit ---
        if page_entry.valid:
            self.stats["hits"] += 1
            # Beri tahu algoritma (terutama LRU) bahwa halaman ini baru saja diakses
            self.replacement_algorithm.page_accessed(page_number)
            
            physical_address = page_entry.frame_number * page_size + offset
            return f"Hit! Alamat Fisik: {physical_address} (Frame: {page_entry.frame_number})", "hit"

        # --- Kasus 2: Page Fault ---
        self.stats["faults"] += 1
        
        # Coba alokasi frame kosong terlebih dahulu
        free_frame_num = self.physical_memory.allocate_frame(pid, page_number)
        
        # --- Kasus 2a: Page Fault dengan Frame Kosong Tersedia ---
        if free_frame_num != -1:
            page_entry.frame_number = free_frame_num
            page_entry.valid = True
            # Beri tahu algoritma bahwa halaman baru telah dimuat
            self.replacement_algorithm.page_loaded(page_number)
            
            physical_address = free_frame_num * page_size + offset
            return f"Page Fault! Frame kosong {free_frame_num} dialokasikan. Alamat Fisik: {physical_address}", "fault_free"

        # --- Kasus 2b: Page Fault, Tidak Ada Frame Kosong (Perlu Penggantian) ---
        else:
            # Minta algoritma untuk memilih halaman korban
            victim_page_number = self.replacement_algorithm.select_victim(future_references)

            # Temukan di frame mana dan dari proses mana halaman korban berada
            victim_frame_num = -1
            victim_pid = -1
            for i, frame_content in enumerate(self.physical_memory.frames):
                if frame_content and frame_content[1] == victim_page_number:
                    victim_frame_num = i
                    victim_pid = frame_content[0]
                    break
            
            if victim_frame_num == -1:
                # Seharusnya tidak pernah terjadi jika logika algoritma benar
                return "Error: Gagal menemukan halaman korban di memori fisik.", None

            # Invalidate entri tabel halaman korban
            victim_process = self.processes[victim_pid]
            victim_page_entry = victim_process.get_page_entry(victim_page_number)
            victim_page_entry.valid = False
            victim_page_entry.frame_number = -1

            # Bebaskan frame fisik
            self.physical_memory.free_frame(victim_frame_num)
            
            # Sekarang alokasikan frame yang baru kosong ini untuk halaman baru
            new_frame_for_page = self.physical_memory.allocate_frame(pid, page_number)
            page_entry.frame_number = new_frame_for_page
            page_entry.valid = True

            # Beri tahu algoritma bahwa halaman baru telah dimuat (menggantikan yang lama)
            self.replacement_algorithm.page_loaded(page_number)
            
            physical_address = new_frame_for_page * page_size + offset
            return (f"Page Fault! Halaman {victim_page_number} (P{victim_pid}) diganti. "
                    f"Alamat Fisik: {physical_address}"), "fault_replace"


    def get_stats(self):
        total = self.stats["hits"] + self.stats["faults"]
        if total == 0:
            return {"hits": 0, "faults": 0, "hit_ratio": 0}
        return {
            "hits": self.stats["hits"],
            "faults": self.stats["faults"],
            "hit_ratio": (self.stats["hits"] / total) * 100
        }
    
    def reset(self):
        self.stats = {"hits": 0, "faults": 0}
        pids = list(self.processes.keys())
        for pid in pids:
            self.terminate_process(pid)
        self.processes.clear()
        self.next_pid = 0
        if self.replacement_algorithm:
            # Reset state internal algoritma juga
            self.replacement_algorithm.reset()