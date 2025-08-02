# gui/app.py (Updated to remove limits - minimum 1 frame and 1 page)

import customtkinter as ctk
from tkinter import messagebox
from .theme import COLORS, FONTS
from core.memory_manager import PhysicalMemory, MemoryManagementUnit
from core.replacement_algorithms import FIFO, LRU, Optimal

class VirtualMemorySimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Window Configuration ---
        self.title("Virtual Memory Simulator Kelompok 3 Sistem Operasi")
        self.geometry("1600x900")
        ctk.set_appearance_mode("Dark")
        
        # --- Core Components ---
        self.mmu = None
        self.physical_memory = None
        self.active_pid = -1
        
        # --- Configuration Variables (Updated minimum values) ---
        self.phys_frames_var = ctk.IntVar(value=4)  # Keep default at 4 but allow minimum 1
        self.proc_pages_var = ctk.IntVar(value=8)   # Keep default at 8 but allow minimum 1
        
        # --- Layout Configuration ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- Create UI Components ---
        self.create_control_panel()
        self.create_visualization_panel()
        self.create_log_panel()

    def create_control_panel(self):
        """Create left control panel with enhanced features"""
        panel = ctk.CTkFrame(self, corner_radius=10, fg_color=COLORS["foreground"])
        panel.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nswe")
        panel.grid_columnconfigure(0, weight=1)

        # --- System Configuration ---
        ctk.CTkLabel(panel, text="Konfigurasi Sistem", font=FONTS["heading"]).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Page Size - Allow any positive value
        ctk.CTkLabel(panel, text="Ukuran Halaman (KB):", font=FONTS["body"]).grid(
            row=1, column=0, padx=20, sticky="w")
        self.page_size_entry = ctk.CTkEntry(panel, placeholder_text="Minimal: 1, Contoh: 4")
        self.page_size_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Physical Frames - Updated to allow minimum 1 frame
        ctk.CTkLabel(panel, text="Frame Fisik:", font=FONTS["body"]).grid(
            row=3, column=0, padx=20, sticky="w")
        self.phys_frames_slider = ctk.CTkSlider(
            panel, from_=1, to=64, number_of_steps=63,  # Changed from 4 to 1, adjusted steps
            variable=self.phys_frames_var, 
            command=lambda v: self.phys_frames_label.configure(text=f"{int(v)}")
        )
        self.phys_frames_slider.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.phys_frames_label = ctk.CTkLabel(
            panel, text=f"{self.phys_frames_var.get()}", 
            font=FONTS["body_bold"], text_color=COLORS["primary"]
        )
        self.phys_frames_label.grid(row=3, column=0, padx=20, sticky="e")

        # Replacement Algorithm
        ctk.CTkLabel(panel, text="Algoritma Penggantian:", font=FONTS["body_bold"]).grid(
            row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        algo_frame = ctk.CTkFrame(panel, fg_color="transparent")
        algo_frame.grid(row=6, column=0, padx=20, sticky="w")
        self.algo_var = ctk.StringVar(value="FIFO")
        ctk.CTkRadioButton(algo_frame, text="FIFO", variable=self.algo_var, value="FIFO").pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(algo_frame, text="LRU", variable=self.algo_var, value="LRU").pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(algo_frame, text="Optimal", variable=self.algo_var, value="Optimal").pack(side="left")
        
        # Start Button
        self.start_button = ctk.CTkButton(
            panel, text="Mulai / Reset Simulasi", font=FONTS["body_bold"], 
            fg_color=COLORS["primary"], hover_color=COLORS["secondary"], 
            command=self.start_simulation
        )
        self.start_button.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        
        # --- Interactive Controls ---
        ctk.CTkLabel(panel, text="Kontrol Interaktif", font=FONTS["heading"]).grid(
            row=8, column=0, padx=20, pady=(20, 10), sticky="w")

        # Process Virtual Pages - Updated to allow minimum 1 page
        ctk.CTkLabel(panel, text="Page Virtual Proses:", font=FONTS["body"]).grid(
            row=9, column=0, padx=20, sticky="w")
        self.proc_pages_slider = ctk.CTkSlider(
            panel, from_=1, to=128, number_of_steps=127,  # Changed from 8 to 1, adjusted steps
            variable=self.proc_pages_var, 
            command=lambda v: self.proc_pages_label.configure(text=f"{int(v)}")
        )
        self.proc_pages_slider.grid(row=10, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.proc_pages_label = ctk.CTkLabel(
            panel, text=f"{self.proc_pages_var.get()}", 
            font=FONTS["body_bold"], text_color=COLORS["primary"]
        )
        self.proc_pages_label.grid(row=9, column=0, padx=20, sticky="e")

        self.create_proc_button = ctk.CTkButton(
            panel, text="Buat Proses", command=self.create_process, state="disabled"
        )
        self.create_proc_button.grid(row=11, column=0, padx=20, pady=10, sticky="ew")
        
        # Virtual Address Access
        ctk.CTkLabel(panel, text="Alamat Virtual (byte):", font=FONTS["body"]).grid(
            row=12, column=0, padx=20, pady=(10, 0), sticky="w")
        self.addr_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 8192")
        self.addr_entry.grid(row=13, column=0, padx=20, sticky="ew")
        self.access_button = ctk.CTkButton(
            panel, text="Akses Alamat", command=self.access_memory, state="disabled"
        )
        self.access_button.grid(row=14, column=0, padx=20, pady=5, sticky="ew")

        # Reference String
        ctk.CTkLabel(panel, text="String Referensi Halaman:", font=FONTS["body"]).grid(
            row=15, column=0, padx=20, pady=(10, 0), sticky="w")
        self.ref_string_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 0,1,2,3,0,1,4...")
        self.ref_string_entry.grid(row=16, column=0, padx=20, sticky="ew")
        self.run_ref_button = ctk.CTkButton(
            panel, text="Jalankan String Referensi", command=self.run_reference_string, state="disabled"
        )
        self.run_ref_button.grid(row=17, column=0, padx=20, pady=5, sticky="ew")

        # --- Debug Controls ---
        ctk.CTkLabel(panel, text="Debug Tools", font=FONTS["heading"]).grid(
            row=18, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.debug_button = ctk.CTkButton(
            panel, text="Debug State", command=self.debug_memory_state, 
            state="disabled", fg_color=COLORS["highlight"], text_color="black"
        )
        self.debug_button.grid(row=19, column=0, padx=20, pady=5, sticky="ew")

    def create_visualization_panel(self):
        """Create visualization panel with enhanced displays"""
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        
        # Headers
        ctk.CTkLabel(panel, text="Ruang Alamat Virtual (Proses Aktif)", font=FONTS["heading"]).grid(
            row=0, column=0, pady=(0,10))
        ctk.CTkLabel(panel, text="Memori Fisik (RAM)", font=FONTS["heading"]).grid(
            row=0, column=1, pady=(0,10))
        
        # Virtual Address Space Frame
        self.vas_frame = ctk.CTkScrollableFrame(
            panel, label_text="Pilih Proses untuk Dilihat", 
            label_font=FONTS["body_bold"], corner_radius=10, fg_color=COLORS["foreground"]
        )
        self.vas_frame.grid(row=1, column=0, padx=(0,5), sticky="nswe")
        
        # Physical Memory Frame
        self.phys_mem_frame = ctk.CTkScrollableFrame(
            panel, label_text="Frames", 
            label_font=FONTS["body_bold"], corner_radius=10, fg_color=COLORS["foreground"]
        )
        self.phys_mem_frame.grid(row=1, column=1, padx=(5,0), sticky="nswe")
        
    def create_log_panel(self):
        """Create log panel with statistics"""
        panel = ctk.CTkFrame(self, corner_radius=10, fg_color=COLORS["foreground"], height=200)
        panel.grid(row=1, column=1, padx=10, pady=(0,10), sticky="nswe")
        self.grid_rowconfigure(1, weight=0)
        
        panel.grid_columnconfigure(0, weight=3)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        
        # Log textbox
        self.log_textbox = ctk.CTkTextbox(
            panel, font=FONTS["small"], state="disabled", 
            wrap="word", border_width=0
        )
        self.log_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(panel, fg_color="transparent")
        stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        
        ctk.CTkLabel(stats_frame, text="Statistik Kinerja", font=FONTS["body_bold"]).pack(anchor="w")
        
        self.hits_label = ctk.CTkLabel(stats_frame, text="Hits: 0", font=FONTS["body"])
        self.hits_label.pack(anchor="w", pady=2)
        
        self.faults_label = ctk.CTkLabel(stats_frame, text="Page Faults: 0", font=FONTS["body"])
        self.faults_label.pack(anchor="w", pady=2)
        
        self.hit_ratio_label = ctk.CTkLabel(stats_frame, text="Hit Ratio: 0.00%", font=FONTS["body"])
        self.hit_ratio_label.pack(anchor="w", pady=2)
        
        self.total_accesses_label = ctk.CTkLabel(stats_frame, text="Total Akses: 0", font=FONTS["body"])
        self.total_accesses_label.pack(anchor="w", pady=2)
        
        # Algorithm state display
        self.algo_state_label = ctk.CTkLabel(stats_frame, text="Algorithm State:", font=FONTS["body_bold"])
        self.algo_state_label.pack(anchor="w", pady=(10, 2))
        
        self.algo_info_label = ctk.CTkLabel(stats_frame, text="", font=FONTS["small"], justify="left")
        self.algo_info_label.pack(anchor="w", pady=2)

    def _log(self, message, status=None):
        """Add message to log with optional status coloring"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n", status if status else "normal")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def setup_log_tags(self):
        """Setup color tags for log messages"""
        self.log_textbox.tag_config("hit", foreground=COLORS["page_hit"])
        self.log_textbox.tag_config("fault_free", foreground=COLORS["page_fault"])
        self.log_textbox.tag_config("fault_replace", foreground=COLORS["page_victim"])
        self.log_textbox.tag_config("info", foreground=COLORS["text_secondary"])
        self.log_textbox.tag_config("error", foreground=COLORS["page_victim"])
        
    def start_simulation(self):
        """Initialize simulation with error handling and updated validation"""
        try:
            num_frames = self.phys_frames_var.get()
            page_size_text = self.page_size_entry.get()
            
            if not page_size_text:
                messagebox.showerror("Input Error", "Ukuran Halaman harus diisi.")
                return
                
            page_size_kb = int(page_size_text)
            # Updated validation: minimum 1 KB instead of requiring positive
            if page_size_kb < 1:
                messagebox.showerror("Error", "Ukuran Halaman minimal 1 KB.")
                return
                
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Ukuran Halaman harus berupa angka positif (minimal 1).")
            return

        # Validate minimum frames (should be at least 1)
        if num_frames < 1:
            messagebox.showerror("Error", "Jumlah frame minimal 1.")
            return

        # Initialize physical memory
        self.physical_memory = PhysicalMemory(num_frames, page_size_kb * 1024)
        
        # Initialize replacement algorithm
        algo_map = {"FIFO": FIFO, "LRU": LRU, "Optimal": Optimal}
        algorithm = algo_map[self.algo_var.get()](num_frames)
        
        # Initialize MMU
        self.mmu = MemoryManagementUnit(self.physical_memory, algorithm)
        
        # Reset active process
        self.active_pid = -1
        
        # Update UI state
        self.create_proc_button.configure(state="normal")
        self.access_button.configure(state="disabled")
        self.run_ref_button.configure(state="disabled")
        self.debug_button.configure(state="normal")
        
        # Clear and setup log
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.setup_log_tags()
        
        # Log initialization
        self._log("--- Simulasi Dimulai ---", "info")
        self._log(f"Memori: {num_frames} frames, Ukuran Halaman: {page_size_kb}KB", "info")
        self._log(f"Algoritma: {self.algo_var.get()}", "info")
        
        self.update_all_visuals()

    def create_process(self):
        """Create new process with updated validation"""
        if not self.mmu:
            return
            
        try:
            num_pages = self.proc_pages_var.get()
            page_size_bytes = int(self.page_size_entry.get()) * 1024
            proc_size_bytes = num_pages * page_size_bytes
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Ukuran Halaman harus diisi dengan angka.")
            return

        # Validate minimum pages (should be at least 1)
        if num_pages < 1:
            messagebox.showerror("Error", "Jumlah halaman virtual minimal 1.")
            return

        pid = self.mmu.create_process(proc_size_bytes, page_size_bytes)
        self.active_pid = pid
        
        self._log(f"Proses P{pid} dibuat dengan {num_pages} halaman virtual.", "info")
        
        self.access_button.configure(state="normal")
        self.run_ref_button.configure(state="normal")
        
        self.update_all_visuals()

    def access_memory(self):
        """Access memory address with enhanced logging"""
        if not self.mmu or self.active_pid == -1:
            return
            
        try:
            addr_text = self.addr_entry.get()
            if not addr_text:
                messagebox.showerror("Input Error", "Alamat Virtual harus diisi.")
                return
            v_addr = int(addr_text)
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Alamat Virtual harus diisi dengan angka.")
            return
            
        page_size = self.physical_memory.page_size
        page_num = v_addr // page_size
        
        self._log(f"--> P{self.active_pid} akses VA: {v_addr} (Halaman {page_num})")
        message, status = self.mmu.access_virtual_address(self.active_pid, v_addr)
        
        if "Error" in message:
            self._log(message, "error")
        else:
            self._log(message, status)
        
        self.update_all_visuals()
        
    def run_reference_string(self):
        """Run reference string with step-by-step visualization"""
        if not self.mmu or self.active_pid == -1:
            return
            
        ref_string_text = self.ref_string_entry.get()
        if not ref_string_text:
            messagebox.showerror("Input Error", "String Referensi harus diisi.")
            return
            
        try:
            ref_string = [int(p.strip()) for p in ref_string_text.replace(" ", "").split(',') if p.strip()]
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Format String Referensi tidak valid.")
            return

        self._log("\n--- Menjalankan String Referensi ---", "info")
        page_size_bytes = self.physical_memory.page_size
        
        for i, page_num in enumerate(ref_string):
            v_addr = page_num * page_size_bytes
            future_refs = None
            
            # For Optimal algorithm, provide future references as page numbers
            if self.algo_var.get() == "Optimal" and i < len(ref_string) - 1:
                future_refs = ref_string[i+1:]
            
            self._log(f"--> [Langkah {i+1}] Akses Halaman {page_num} (VA: {v_addr})")
            message, status = self.mmu.access_virtual_address(self.active_pid, v_addr, future_references=future_refs)
            
            if "Error" in message:
                self._log(message, "error")
                break
            else:
                self._log(message, status)
            
            # Update visualization after each step
            self.update_all_visuals()
            self.update()
            self.after(300)  # Pause for visualization
        
        self.update_all_visuals()
        self._log("--- Eksekusi String Referensi Selesai ---", "info")

    def debug_memory_state(self):
        """Debug function to show detailed memory state"""
        if not self.mmu:
            return
            
        self._log("\n--- DEBUG: Memory State ---", "info")
        
        # Show physical memory state
        free_frames = len(self.physical_memory.free_frames)
        total_frames = self.physical_memory.num_frames
        self._log(f"Physical Memory: {free_frames}/{total_frames} frames free", "info")
        
        # Show process information
        for pid, process in self.mmu.processes.items():
            valid_pages = sum(1 for entry in process.page_table if entry.valid)
            self._log(f"Process P{pid}: {valid_pages}/{process.num_pages} pages loaded", "info")
        
        # Show algorithm state
        algo_state = self.mmu.get_algorithm_state()
        if algo_state:
            if 'queue_order' in algo_state:
                queue_str = " -> ".join(map(str, algo_state['queue_order'])) if algo_state['queue_order'] else "Empty"
                self._log(f"FIFO Queue: {queue_str}", "info")
            elif 'usage_order' in algo_state:
                usage_str = " -> ".join(map(str, algo_state['usage_order'])) if algo_state['usage_order'] else "Empty"
                self._log(f"LRU Order: {usage_str}", "info")
            else:
                frame_info = ", ".join([f"F{k}:P{v}" for k, v in algo_state.get('frame_to_page', {}).items()])
                self._log(f"Frame->Page: {frame_info}", "info")
        
        # Show statistics
        stats = self.mmu.get_stats()
        self._log(f"Stats: {stats['hits']} hits, {stats['faults']} faults, {stats['hit_ratio']:.2f}% hit ratio", "info")

    def update_all_visuals(self):
        """Update all visual components with current memory state"""
        # Clear existing widgets
        for widget in self.vas_frame.winfo_children():
            widget.destroy()
        for widget in self.phys_mem_frame.winfo_children():
            widget.destroy()
        
        if not self.mmu:
            return
        
        # Update Virtual Address Space visualization
        if self.active_pid in self.mmu.processes:
            process_info = self.mmu.get_process_info(self.active_pid)
            self.vas_frame.configure(label_text=f"Ruang Alamat Virtual P{self.active_pid}")
            
            for page_info in process_info['pages']:
                page_num = page_info['page_number']
                is_valid = page_info['valid']
                frame_num = page_info['frame_number']
                
                # Color coding based on page state
                if is_valid:
                    color = COLORS["primary"]
                    text = f"Halaman {page_num}\n(Frame {frame_num})"
                else:
                    color = COLORS["frame_empty"]
                    text = f"Halaman {page_num}\n(Di Disk)"
                
                # Create page entry widget
                page_frame = ctk.CTkFrame(self.vas_frame, fg_color=color, corner_radius=6)
                label = ctk.CTkLabel(page_frame, text=text, font=FONTS["small"])
                label.pack(expand=True, pady=5)
                page_frame.pack(pady=3, padx=5, fill="x", ipady=10)
        
        # Update Physical Memory visualization
        if self.physical_memory:
            free_count = len(self.physical_memory.free_frames)
            total_count = self.physical_memory.num_frames
            self.phys_mem_frame.configure(label_text=f"{free_count}/{total_count} Frames Kosong")
            
            for i, content in enumerate(self.physical_memory.frames):
                if content:
                    pid, page_num = content
                    color = COLORS["frame_occupied"]
                    text = f"Frame {i}\n(P{pid}, Halaman {page_num})"
                else:
                    color = COLORS["frame_empty"]
                    text = f"Frame {i}\n(Kosong)"
                
                # Create frame entry widget
                frame_widget = ctk.CTkFrame(self.phys_mem_frame, fg_color=color, corner_radius=6)
                label = ctk.CTkLabel(frame_widget, text=text, font=FONTS["small"])
                label.pack(expand=True, pady=5)
                frame_widget.pack(pady=3, padx=5, fill="x", ipady=10)
        
        # Update statistics
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        if not self.mmu:
            return
            
        stats = self.mmu.get_stats()
        self.hits_label.configure(text=f"Hits: {stats['hits']}")
        self.faults_label.configure(text=f"Page Faults: {stats['faults']}")
        self.hit_ratio_label.configure(text=f"Hit Ratio: {stats['hit_ratio']:.2f}%")
        self.total_accesses_label.configure(text=f"Total Akses: {stats['total_accesses']}")
        
        # Update algorithm state display
        algo_state = self.mmu.get_algorithm_state()
        if algo_state:
            if 'queue_order' in algo_state:
                # FIFO algorithm
                queue_str = " -> ".join(map(str, algo_state['queue_order'])) if algo_state['queue_order'] else "Empty"
                self.algo_info_label.configure(text=f"FIFO Queue:\n{queue_str}")
            elif 'usage_order' in algo_state:
                # LRU algorithm
                usage_str = " -> ".join(map(str, algo_state['usage_order'])) if algo_state['usage_order'] else "Empty"
                self.algo_info_label.configure(text=f"LRU Order:\n{usage_str}")
            else:
                # Optimal or other algorithms
                frame_info = ", ".join([f"F{k}:P{v}" for k, v in algo_state.get('frame_to_page', {}).items()])
                self.algo_info_label.configure(text=f"Frame->Page:\n{frame_info}")

if __name__ == "__main__":
    app = VirtualMemorySimulatorApp()
    app.mainloop()