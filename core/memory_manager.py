# core/memory_manager.py
"""
Modul Pengelola Memori Virtual
Mengimplementasikan simulasi sistem manajemen memori virtual dengan paging
"""

import math
from core.replacement_algorithms import FIFO, LRU

class PageTableEntry:
    """
    Entri dalam tabel halaman untuk setiap halaman virtual
    Menyimpan informasi apakah halaman ada di memori fisik dan nomor frame-nya
    """
    def __init__(self):
        self.frame_number = -1  # Nomor frame di memori fisik (-1 jika tidak valid)
        self.valid = False      # Status apakah halaman ada di memori fisik

class Process:
    """
    Representasi proses dengan ruang alamat virtual
    Setiap proses memiliki tabel halaman sendiri
    """
    def __init__(self, pid, virtual_address_space_size, page_size):
        self.pid = pid
        self.num_pages = math.ceil(virtual_address_space_size / page_size)
        self.page_table = [PageTableEntry() for _ in range(self.num_pages)]

    def get_page_entry(self, page_number):
        """Mengambil entri tabel halaman untuk nomor halaman tertentu"""
        if 0 <= page_number < self.num_pages:
            return self.page_table[page_number]
        return None

class PhysicalMemory:
    """
    Representasi memori fisik (RAM) yang terdiri dari frame-frame
    Mengelola alokasi dan dealokasi frame untuk halaman-halaman proses
    """
    def __init__(self, num_frames, page_size):
        self.num_frames = num_frames
        self.page_size = page_size
        self.frames = [None] * num_frames        # Isi setiap frame: (pid, page_number) atau None
        self.free_frames = list(range(num_frames))  # Daftar frame yang masih kosong

    def allocate_frame(self, pid, page_number):
        """
        Alokasi frame kosong untuk halaman tertentu dari proses
        Return: nomor frame yang dialokasikan, atau -1 jika tidak ada frame kosong
        """
        if not self.free_frames:
            return -1
        frame_number = self.free_frames.pop(0)
        self.frames[frame_number] = (pid, page_number)
        return frame_number

    def free_frame(self, frame_number):
        """Membebaskan frame dan mengembalikannya ke daftar frame kosong"""
        if 0 <= frame_number < self.num_frames and self.frames[frame_number] is not None:
            self.frames[frame_number] = None
            self.free_frames.append(frame_number)
            self.free_frames.sort()

    def find_frame_by_page(self, pid, page_number):
        """Mencari nomor frame berdasarkan PID dan nomor halaman"""
        for frame_num, content in enumerate(self.frames):
            if content and content[0] == pid and content[1] == page_number:
                return frame_num
        return -1


class MemoryManagementUnit:
    """
    Unit Pengelola Memori (MMU) - komponen utama yang menangani:
    - Translasi alamat virtual ke alamat fisik
    - Penanganan page fault
    - Pengelolaan algoritma penggantian halaman
    """
    def __init__(self, physical_memory, replacement_algorithm):
        self.physical_memory = physical_memory
        self.replacement_algorithm = replacement_algorithm
        self.processes = {}                      # Daftar semua proses aktif
        self.next_pid = 0                        # Counter untuk PID berikutnya
        self.stats = {"hits": 0, "faults": 0}    # Statistik performa sistem

    def create_process(self, virtual_size, page_size):
        """
        Membuat proses baru dengan ruang alamat virtual tertentu
        Return: PID proses yang baru dibuat
        """
        pid = self.next_pid
        process = Process(pid, virtual_size, page_size)
        self.processes[pid] = process
        self.next_pid += 1
        return pid

    def terminate_process(self, pid):
        """
        Menghentikan proses dan membebaskan semua frame yang dialokasikan
        Return: True jika berhasil, False jika proses tidak ditemukan
        """
        if pid in self.processes:
            process = self.processes[pid]
            # Bebaskan semua frame yang dialokasikan untuk proses ini
            for page_entry in process.page_table:
                if page_entry.valid:
                    # Penting: panggil page_removed di algoritma untuk update state internalnya
                    self.replacement_algorithm.page_removed(page_entry.frame_number)
                    self.physical_memory.free_frame(page_entry.frame_number)
            del self.processes[pid]
            return True
        return False

    def access_virtual_address(self, pid, virtual_address):
        """
        Mengakses alamat virtual - mengkonversi ke nomor halaman dan memanggil access_page
        """
        page_size = self.physical_memory.page_size
        page_number = virtual_address // page_size
        return self.access_page(pid, page_number)

    def access_page(self, pid, page_number):
        """
        Logika inti akses halaman - menangani page hit dan page fault
        """
        # Validasi proses dan halaman
        if pid not in self.processes:
            return "Error: Process ID tidak ditemukan.", None
        
        process = self.processes[pid]
        if page_number >= process.num_pages:
            return f"Error: Halaman {page_number} di luar batas untuk Proses {pid}.", None

        page_entry = process.get_page_entry(page_number)

        # Kasus 1: Page Hit - halaman sudah ada di memori fisik
        if page_entry.valid:
            self.stats["hits"] += 1
            self.replacement_algorithm.page_accessed(page_entry.frame_number, page_number)
            return f"Hit! Halaman {page_number} ada di Frame {page_entry.frame_number}", "hit"

        # Kasus 2: Page Fault - halaman tidak ada di memori fisik
        self.stats["faults"] += 1
        
        # Kasus 2a: Ada frame kosong tersedia
        free_frame_num = self.physical_memory.allocate_frame(pid, page_number)
        if free_frame_num != -1:
            page_entry.frame_number = free_frame_num
            page_entry.valid = True
            self.replacement_algorithm.page_loaded(free_frame_num, page_number)
            return f"Page Fault! Frame kosong {free_frame_num} dialokasikan untuk halaman {page_number}.", "fault_free"

        # Kasus 2b: Tidak ada frame kosong - perlu penggantian halaman
        victim_frame_num = self.replacement_algorithm.select_victim()
        
        if victim_frame_num == -1:
            return "Error: Gagal memilih frame korban.", None

        # Ambil informasi halaman korban yang akan diganti
        victim_content = self.physical_memory.frames[victim_frame_num]
        if not victim_content:
            return "Error: Frame korban kosong secara tidak terduga.", None
            
        victim_pid, victim_page_number = victim_content

        # Update tabel halaman proses korban - tandai sebagai tidak valid
        if victim_pid in self.processes:
            victim_process = self.processes[victim_pid]
            victim_page_entry = victim_process.get_page_entry(victim_page_number)
            if victim_page_entry:
                victim_page_entry.valid = False
                victim_page_entry.frame_number = -1

        # Load halaman baru ke frame korban
        self.physical_memory.frames[victim_frame_num] = (pid, page_number)
        page_entry.frame_number = victim_frame_num
        page_entry.valid = True
        
        # Update algoritma penggantian
        self.replacement_algorithm.page_loaded(victim_frame_num, page_number)
        
        return f"Page Fault! Halaman {victim_page_number} (P{victim_pid}) di frame {victim_frame_num} diganti oleh halaman {page_number} (P{pid}).", "fault_replace"
    
    def get_stats(self):
        """Mengambil statistik performa sistem (hit ratio, jumlah hit/fault)"""
        total = self.stats["hits"] + self.stats["faults"]
        if total == 0:
            return {"hits": 0, "faults": 0, "hit_ratio": 0}
        return {
            "hits": self.stats["hits"],
            "faults": self.stats["faults"],
            "hit_ratio": (self.stats["hits"] / total) * 100
        }
    
    def reset(self):
        """Reset sistem ke kondisi awal - hapus semua proses dan statistik"""
        self.stats = {"hits": 0, "faults": 0}
        
        # Reset algoritma penggantian terlebih dahulu
        if self.replacement_algorithm:
            self.replacement_algorithm.reset()

        # Kemudian kosongkan memori fisik dan hapus proses
        pids = list(self.processes.keys())
        for pid in pids:
            process = self.processes[pid]
            for page_entry in process.page_table:
                if page_entry.valid:
                    self.physical_memory.free_frame(page_entry.frame_number)
            del self.processes[pid]
        self.next_pid = 0