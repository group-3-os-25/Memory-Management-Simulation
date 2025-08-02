# core/memory_manager.py (Updated to properly work with replacement algorithms)

import math
from core.replacement_algorithms import FIFO, LRU, Optimal

class PageTableEntry:
    def __init__(self):
        self.frame_number = -1
        self.valid = False
        self.access_time = 0

class Process:
    def __init__(self, pid, virtual_address_space_size, page_size):
        self.pid = pid
        self.num_pages = math.ceil(virtual_address_space_size / page_size)
        self.page_table = [PageTableEntry() for _ in range(self.num_pages)]
        self.page_size = page_size

    def get_page_entry(self, page_number):
        if 0 <= page_number < self.num_pages:
            return self.page_table[page_number]
        return None

class PhysicalMemory:
    def __init__(self, num_frames, page_size):
        self.num_frames = num_frames
        self.page_size = page_size
        self.frames = [None] * num_frames  # (pid, page_number) tuples
        self.free_frames = list(range(num_frames))

    def allocate_frame(self, pid, page_number):
        """Allocate a free frame for a page"""
        if not self.free_frames:
            return -1
        frame_number = self.free_frames.pop(0)
        self.frames[frame_number] = (pid, page_number)
        return frame_number

    def free_frame(self, frame_number):
        """Free a frame and add it back to free list"""
        if 0 <= frame_number < self.num_frames and self.frames[frame_number] is not None:
            self.frames[frame_number] = None
            self.free_frames.append(frame_number)
            self.free_frames.sort()

    def update_frame(self, frame_number, pid, page_number):
        """Update existing frame with new page"""
        if 0 <= frame_number < self.num_frames:
            self.frames[frame_number] = (pid, page_number)

    def find_frame_by_page(self, pid, page_number):
        """Find frame number by pid and page number"""
        for frame_num, content in enumerate(self.frames):
            if content and content[0] == pid and content[1] == page_number:
                return frame_num
        return -1

    def get_frame_contents(self):
        """Get all frame contents for visualization"""
        return [(i, self.frames[i]) for i in range(self.num_frames)]

class MemoryManagementUnit:
    def __init__(self, physical_memory, replacement_algorithm):
        self.physical_memory = physical_memory
        self.replacement_algorithm = replacement_algorithm
        self.processes = {}
        self.next_pid = 0
        self.stats = {"hits": 0, "faults": 0}
        self.access_counter = 0

    def create_process(self, virtual_size, page_size):
        """Create a new process with virtual address space"""
        pid = self.next_pid
        process = Process(pid, virtual_size, page_size)
        self.processes[pid] = process
        self.next_pid += 1
        return pid

    def terminate_process(self, pid):
        """Terminate a process and free all its frames"""
        if pid in self.processes:
            process = self.processes[pid]
            for page_entry in process.page_table:
                if page_entry.valid:
                    self.physical_memory.free_frame(page_entry.frame_number)
                    self.replacement_algorithm.page_removed(page_entry.frame_number)
            del self.processes[pid]
            return True
        return False

    def access_virtual_address(self, pid, virtual_address, future_references=None):
        """Access virtual address - converts to page number and calls access_page"""
        page_size = self.physical_memory.page_size
        page_number = virtual_address // page_size
        return self.access_page(pid, page_number, future_references)

    def access_page(self, pid, page_number, future_references=None):
        """Core page access logic with proper synchronization to replacement algorithms"""
        if pid not in self.processes:
            return "Error: Process ID tidak ditemukan.", None
        
        process = self.processes[pid]
        if page_number >= process.num_pages:
            return f"Error: Halaman {page_number} di luar batas untuk Proses {pid}.", None

        page_entry = process.get_page_entry(page_number)
        self.access_counter += 1

        # Case 1: Page Hit
        if page_entry.valid:
            self.stats["hits"] += 1
            page_entry.access_time = self.access_counter
            
            # Notify replacement algorithm about page access
            self.replacement_algorithm.page_accessed(page_entry.frame_number, page_number)
            
            return f"Hit! Halaman {page_number} ada di Frame {page_entry.frame_number}", "hit"

        # Case 2: Page Fault
        self.stats["faults"] += 1
        
        # Case 2a: Page Fault with free frame available
        free_frame_num = self.physical_memory.allocate_frame(pid, page_number)
        if free_frame_num != -1:
            page_entry.frame_number = free_frame_num
            page_entry.valid = True
            page_entry.access_time = self.access_counter
            
            # Notify replacement algorithm about new page load
            self.replacement_algorithm.page_loaded(free_frame_num, page_number)
            
            return f"Page Fault! Frame kosong {free_frame_num} dialokasikan untuk halaman {page_number}.", "fault_free"

        # Case 2b: Page Fault, need replacement - Convert future references to page numbers
        future_page_refs = None
        if future_references and self.replacement_algorithm.__class__.__name__ == 'Optimal':
            # Convert virtual addresses to page numbers for Optimal algorithm
            page_size = self.physical_memory.page_size
            future_page_refs = [addr // page_size if isinstance(addr, int) and addr >= page_size 
                              else addr for addr in future_references]

        victim_frame_num = self.replacement_algorithm.select_victim(future_page_refs)
        
        if victim_frame_num == -1:
            return "Error: Gagal memilih frame korban.", None

        # Get victim page information
        victim_content = self.physical_memory.frames[victim_frame_num]
        victim_message = ""
        
        if victim_content:
            victim_pid, victim_page_number = victim_content
            victim_message = f"Halaman {victim_page_number} (P{victim_pid})"
            
            # Update victim page's page table entry
            if victim_pid in self.processes:
                victim_process = self.processes[victim_pid]
                victim_page_entry = victim_process.get_page_entry(victim_page_number)
                if victim_page_entry:
                    victim_page_entry.valid = False
                    victim_page_entry.frame_number = -1

        # Load new page into the frame
        self.physical_memory.update_frame(victim_frame_num, pid, page_number)
        page_entry.frame_number = victim_frame_num
        page_entry.valid = True
        page_entry.access_time = self.access_counter
        
        # Notify replacement algorithm about the replacement
        self.replacement_algorithm.page_loaded(victim_frame_num, page_number)
        
        if victim_message:
            return f"Page Fault! {victim_message} di frame {victim_frame_num} diganti dengan halaman {page_number} (P{pid}).", "fault_replace"
        else:
            return f"Page Fault! Frame {victim_frame_num} dialokasikan untuk halaman {page_number} (P{pid}).", "fault_free"
        
    def get_stats(self):
        """Get memory access statistics"""
        total = self.stats["hits"] + self.stats["faults"]
        if total == 0:
            return {"hits": 0, "faults": 0, "hit_ratio": 0, "total_accesses": 0}
        return {
            "hits": self.stats["hits"],
            "faults": self.stats["faults"],
            "hit_ratio": (self.stats["hits"] / total) * 100,
            "total_accesses": total
        }
    
    def get_process_info(self, pid):
        """Get detailed process information for visualization"""
        if pid not in self.processes:
            return None
            
        process = self.processes[pid]
        pages_info = []
        
        for i, page_entry in enumerate(process.page_table):
            pages_info.append({
                'page_number': i,
                'valid': page_entry.valid,
                'frame_number': page_entry.frame_number if page_entry.valid else None,
                'access_time': page_entry.access_time
            })
            
        return {
            'pid': pid,
            'num_pages': process.num_pages,
            'page_size': process.page_size,
            'pages': pages_info
        }
    
    def get_algorithm_state(self):
        """Get current state of replacement algorithm for debugging"""
        if hasattr(self.replacement_algorithm, 'get_queue_status'):
            return self.replacement_algorithm.get_queue_status()
        elif hasattr(self.replacement_algorithm, 'usage_order'):
            return {'usage_order': list(self.replacement_algorithm.usage_order)}
        else:
            return {'frame_to_page': dict(self.replacement_algorithm.frame_to_page)}
    
    def reset(self):
        """Reset MMU to initial state"""
        self.stats = {"hits": 0, "faults": 0}
        self.access_counter = 0
        
        # Terminate all processes
        pids = list(self.processes.keys())
        for pid in pids:
            self.terminate_process(pid)
        
        self.next_pid = 0
        
        # Reset replacement algorithm
        if self.replacement_algorithm:
            self.replacement_algorithm.reset()

    def debug_memory_state(self):
        """Debug function to print current memory state"""
        print("=== MEMORY STATE DEBUG ===")
        print(f"Physical Memory: {self.physical_memory.num_frames} frames")
        print(f"Free frames: {self.physical_memory.free_frames}")
        print(f"Stats: {self.get_stats()}")
        
        for pid, process in self.processes.items():
            print(f"\nProcess {pid}:")
            valid_pages = [i for i, entry in enumerate(process.page_table) if entry.valid]
            print(f"  Valid pages: {valid_pages}")
            for i in valid_pages:
                entry = process.page_table[i]
                print(f"    Page {i} -> Frame {entry.frame_number} (access_time: {entry.access_time})")
        
        print(f"\nReplacement Algorithm State: {self.get_algorithm_state()}")
        print("==========================")