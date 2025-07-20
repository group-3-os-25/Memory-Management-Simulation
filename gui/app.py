# gui/app.py

import customtkinter as ctk
from tkinter import messagebox
from .theme import COLORS, FONTS
from core.memory_manager import PhysicalMemory, MemoryManagementUnit
from core.replacement_algorithms import FIFO, LRU, Optimal

class VirtualMemorySimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- Konfigurasi Window Utama ---
        self.title("Virtual Memory Simulator Kelompok 3 Sistem Operasi")
        self.geometry("1500x850")
        ctk.set_appearance_mode("Dark")
        
        self.mmu = None
        self.physical_memory = None
        self.active_pid = -1
        
        self.phys_frames_var = ctk.IntVar(value=16)
        self.proc_pages_var = ctk.IntVar(value=32)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.create_control_panel()
        self.create_visualization_panel()
        self.create_log_panel()

    def create_control_panel(self):
        """
        Membuat panel kontrol di sebelah kiri.
        FUNGSI INI DIROMBAK TOTAL MENGGUNAKAN .grid() UNTUK MENGATASI BUG LAYOUT.
        """
        panel = ctk.CTkFrame(self, corner_radius=10, fg_color=COLORS["foreground"])
        panel.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nswe")
        panel.grid_columnconfigure(0, weight=1)

        # --- Judul Konfigurasi ---
        ctk.CTkLabel(panel, text="Konfigurasi Sistem", font=FONTS["heading"]).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Ukuran Halaman
        ctk.CTkLabel(panel, text="Ukuran Halaman (KB):", font=FONTS["body"]).grid(row=1, column=0, padx=20, sticky="w")
        self.page_size_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 4")
        self.page_size_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        # Frame Fisik
        ctk.CTkLabel(panel, text="Frame Fisik:", font=FONTS["body"]).grid(row=3, column=0, padx=20, sticky="w")
        self.phys_frames_slider = ctk.CTkSlider(panel, from_=4, to=64, number_of_steps=60, variable=self.phys_frames_var, command=lambda v: self.phys_frames_label.configure(text=f"{int(v)}"))
        self.phys_frames_slider.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.phys_frames_label = ctk.CTkLabel(panel, text=f"{self.phys_frames_var.get()}", font=FONTS["body_bold"], text_color=COLORS["primary"])
        self.phys_frames_label.grid(row=3, column=0, padx=20, sticky="e")

        # Algoritma
        ctk.CTkLabel(panel, text="Algoritma Penggantian:", font=FONTS["body_bold"]).grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        algo_frame = ctk.CTkFrame(panel, fg_color="transparent")
        algo_frame.grid(row=6, column=0, padx=20, sticky="w")
        self.algo_var = ctk.StringVar(value="FIFO")
        ctk.CTkRadioButton(algo_frame, text="FIFO", variable=self.algo_var, value="FIFO").pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(algo_frame, text="LRU", variable=self.algo_var, value="LRU").pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(algo_frame, text="Optimal", variable=self.algo_var, value="Optimal").pack(side="left")
        
        # Tombol Mulai
        self.start_button = ctk.CTkButton(panel, text="Mulai / Reset Simulasi", font=FONTS["body_bold"], fg_color=COLORS["primary"], hover_color=COLORS["secondary"], command=self.start_simulation)
        self.start_button.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        
        # Judul Kontrol Interaktif
        ctk.CTkLabel(panel, text="Kontrol Interaktif", font=FONTS["heading"]).grid(row=8, column=0, padx=20, pady=10, sticky="w")

        # Page Virtual Proses
        ctk.CTkLabel(panel, text="Page Virtual Proses:", font=FONTS["body"]).grid(row=9, column=0, padx=20, sticky="w")
        self.proc_pages_slider = ctk.CTkSlider(panel, from_=8, to=128, number_of_steps=120, variable=self.proc_pages_var, command=lambda v: self.proc_pages_label.configure(text=f"{int(v)}"))
        self.proc_pages_slider.grid(row=10, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.proc_pages_label = ctk.CTkLabel(panel, text=f"{self.proc_pages_var.get()}", font=FONTS["body_bold"], text_color=COLORS["primary"])
        self.proc_pages_label.grid(row=9, column=0, padx=20, sticky="e")

        self.create_proc_button = ctk.CTkButton(panel, text="Buat Proses", command=self.create_process, state="disabled")
        self.create_proc_button.grid(row=11, column=0, padx=20, pady=10, sticky="ew")
        
        # Alamat Virtual
        ctk.CTkLabel(panel, text="Alamat Virtual (byte):", font=FONTS["body"]).grid(row=12, column=0, padx=20, pady=(10, 0), sticky="w")
        self.addr_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 8192")
        self.addr_entry.grid(row=13, column=0, padx=20, sticky="ew")
        self.access_button = ctk.CTkButton(panel, text="Akses Alamat", command=self.access_memory, state="disabled")
        self.access_button.grid(row=14, column=0, padx=20, pady=5, sticky="ew")

        # String Referensi
        ctk.CTkLabel(panel, text="String Referensi Halaman:", font=FONTS["body"]).grid(row=15, column=0, padx=20, pady=(10, 0), sticky="w")
        self.ref_string_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 0,1,2,3,0,1,4...")
        self.ref_string_entry.grid(row=16, column=0, padx=20, sticky="ew")
        self.run_ref_button = ctk.CTkButton(panel, text="Jalankan String Referensi", command=self.run_reference_string, state="disabled")
        self.run_ref_button.grid(row=17, column=0, padx=20, pady=5, sticky="ew")

    def create_visualization_panel(self):
        # ... (Tidak ada perubahan di fungsi ini) ...
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        panel.grid_columnconfigure(0, weight=1); panel.grid_columnconfigure(1, weight=1); panel.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(panel, text="Ruang Alamat Virtual (Proses Aktif)", font=FONTS["heading"]).grid(row=0, column=0, pady=(0,10))
        ctk.CTkLabel(panel, text="Memori Fisik (RAM)", font=FONTS["heading"]).grid(row=0, column=1, pady=(0,10))
        self.vas_frame = ctk.CTkScrollableFrame(panel, label_text="Pilih Proses untuk Dilihat", label_font=FONTS["body_bold"], corner_radius=10, fg_color=COLORS["foreground"])
        self.vas_frame.grid(row=1, column=0, padx=(0,5), sticky="nswe")
        self.phys_mem_frame = ctk.CTkScrollableFrame(panel, label_text="Frames", label_font=FONTS["body_bold"], corner_radius=10, fg_color=COLORS["foreground"])
        self.phys_mem_frame.grid(row=1, column=1, padx=(5,0), sticky="nswe")
        
    def create_log_panel(self):
        # ... (Tidak ada perubahan di fungsi ini) ...
        panel = ctk.CTkFrame(self, corner_radius=10, fg_color=COLORS["foreground"], height=200)
        panel.grid(row=1, column=1, padx=10, pady=(0,10), sticky="nswe")
        self.grid_rowconfigure(1, weight=0); panel.grid_columnconfigure(0, weight=3); panel.grid_columnconfigure(1, weight=1); panel.grid_rowconfigure(0, weight=1)
        self.log_textbox = ctk.CTkTextbox(panel, font=FONTS["small"], state="disabled", wrap="word", border_width=0)
        self.log_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        stats_frame = ctk.CTkFrame(panel, fg_color="transparent")
        stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        ctk.CTkLabel(stats_frame, text="Kinerja", font=FONTS["body_bold"]).pack(anchor="w")
        self.hits_label = ctk.CTkLabel(stats_frame, text="Hits: 0", font=FONTS["body"]); self.hits_label.pack(anchor="w")
        self.faults_label = ctk.CTkLabel(stats_frame, text="Page Faults: 0", font=FONTS["body"]); self.faults_label.pack(anchor="w")
        self.hit_ratio_label = ctk.CTkLabel(stats_frame, text="Hit Ratio: 0.00%", font=FONTS["body"]); self.hit_ratio_label.pack(anchor="w")

    def _log(self, message, status=None):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n", status if status else "normal")
        self.log_textbox.configure(state="disabled"); self.log_textbox.see("end")

    def setup_log_tags(self):
        self.log_textbox.tag_config("hit", foreground=COLORS["page_hit"])
        self.log_textbox.tag_config("fault_free", foreground=COLORS["page_fault"])
        self.log_textbox.tag_config("fault_replace", foreground=COLORS["page_victim"])
        self.log_textbox.tag_config("info", foreground=COLORS["text_secondary"])
        self.log_textbox.tag_config("error", foreground=COLORS["page_victim"])
        
    def start_simulation(self):
        try:
            num_frames = self.phys_frames_var.get()
            page_size_text = self.page_size_entry.get()
            if not page_size_text: messagebox.showerror("Input Error", "Ukuran Halaman harus diisi."); return
            page_size_kb = int(page_size_text)
            if page_size_kb <= 0: raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Ukuran Halaman harus berupa angka positif."); return

        self.physical_memory = PhysicalMemory(num_frames, page_size_kb * 1024)
        algo_map = {"FIFO": FIFO, "LRU": LRU, "Optimal": Optimal}
        algorithm = algo_map[self.algo_var.get()](num_frames)
        self.mmu = MemoryManagementUnit(self.physical_memory, algorithm)
        
        self.create_proc_button.configure(state="normal"); self.access_button.configure(state="disabled"); self.run_ref_button.configure(state="disabled")
        self.log_textbox.configure(state="normal"); self.log_textbox.delete("1.0", "end"); self.log_textbox.configure(state="disabled")
        self.setup_log_tags()
        self._log("--- Simulasi Dimulai ---", "info")
        self._log(f"Memori: {num_frames} frames, Ukuran Halaman: {page_size_kb}KB", "info")
        self._log(f"Algoritma: {self.algo_var.get()}", "info")
        self.update_all_visuals()

    def create_process(self):
        if not self.mmu: return
        try:
            num_pages = self.proc_pages_var.get()
            page_size_bytes = int(self.page_size_entry.get()) * 1024
            proc_size_bytes = num_pages * page_size_bytes
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Ukuran Halaman harus diisi dengan angka."); return

        pid = self.mmu.create_process(proc_size_bytes, page_size_bytes)
        self.active_pid = pid
        self._log(f"Proses P{pid} dibuat dengan {num_pages} halaman virtual.", "info")
        self.access_button.configure(state="normal"); self.run_ref_button.configure(state="normal")
        self.update_all_visuals()

    def access_memory(self):
        if not self.mmu: return
        try:
            addr_text = self.addr_entry.get()
            if not addr_text: messagebox.showerror("Input Error", "Alamat Virtual harus diisi."); return
            v_addr = int(addr_text)
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Alamat Virtual harus diisi dengan angka."); return
            
        self._log(f"--> P{self.active_pid} meminta akses ke VA: {v_addr}")
        message, status = self.mmu.access_virtual_address(self.active_pid, v_addr)
        if "Error" in message: self._log(message, "error")
        else: self._log(message, status)
        self.update_all_visuals()
        
    def run_reference_string(self):
        if not self.mmu: return
        ref_string_text = self.ref_string_entry.get()
        if not ref_string_text: messagebox.showerror("Input Error", "String Referensi harus diisi."); return
        try: ref_string = [int(p) for p in ref_string_text.replace(" ", "").split(',') if p]
        except (ValueError, TypeError): messagebox.showerror("Error", "Format String Referensi tidak valid."); return

        self._log("\n--- Menjalankan String Referensi ---", "info")
        page_size_bytes = self.physical_memory.page_size
        
        for i, page_num in enumerate(ref_string):
            v_addr = page_num * page_size_bytes
            future_refs = ref_string[i+1:]
            
            self._log(f"--> [Langkah {i+1}] Mengakses Halaman {page_num} (VA: {v_addr})")
            message, status = self.mmu.access_virtual_address(self.active_pid, v_addr, future_references=future_refs)
            if "Error" in message: self._log(message, "error"); break
            else: self._log(message, status)
            
            self.update(); self.after(200)
        
        self.update_all_visuals()
        self._log("--- Eksekusi String Referensi Selesai ---", "info")

    def update_all_visuals(self):
        for widget in self.vas_frame.winfo_children(): widget.destroy()
        for widget in self.phys_mem_frame.winfo_children(): widget.destroy()
        if not self.mmu: return
        if self.active_pid in self.mmu.processes:
            process = self.mmu.processes[self.active_pid]
            self.vas_frame.configure(label_text=f"Ruang Alamat Virtual P{self.active_pid}")
            for i, entry in enumerate(process.page_table):
                color = COLORS["primary"] if entry.valid else COLORS["frame_empty"]
                text = f"Halaman {i}\n(Ke Frame {entry.frame_number})" if entry.valid else f"Halaman {i}\n(Di Disk)"
                label = ctk.CTkLabel(ctk.CTkFrame(self.vas_frame, fg_color=color, corner_radius=6), text=text, font=FONTS["small"])
                label.pack(expand=True); label.master.pack(pady=3, padx=5, fill="x", ipady=10)
        if self.physical_memory:
            self.phys_mem_frame.configure(label_text=f"{len(self.physical_memory.free_frames)}/{self.physical_memory.num_frames} Frames Kosong")
            for i, content in enumerate(self.physical_memory.frames):
                if content: pid, page_num = content; color = COLORS["frame_occupied"]; text = f"Frame {i}\n(P{pid}, Halaman {page_num})"
                else: color = COLORS["frame_empty"]; text = f"Frame {i}\n(Kosong)"
                label = ctk.CTkLabel(ctk.CTkFrame(self.phys_mem_frame, fg_color=color, corner_radius=6), text=text, font=FONTS["small"])
                label.pack(expand=True); label.master.pack(pady=3, padx=5, fill="x", ipady=10)
            stats = self.mmu.get_stats()
            self.hits_label.configure(text=f"Hits: {stats['hits']}")
            self.faults_label.configure(text=f"Page Faults: {stats['faults']}")
            self.hit_ratio_label.configure(text=f"Hit Ratio: {stats['hit_ratio']:.2f}%")