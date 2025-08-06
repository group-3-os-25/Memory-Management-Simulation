# gui/app.py
"""
Aplikasi GUI untuk Simulator Memori Virtual
Menyediakan interface pengguna untuk berinteraksi dengan sistem manajemen memori
"""
import customtkinter as ctk
from tkinter import ttk, messagebox
from .theme import COLORS, FONTS
from core.memory_manager import PhysicalMemory, MemoryManagementUnit
from core.replacement_algorithms import FIFO, LRU

class VirtualMemorySimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Virtual Memory Simulator")
        self.geometry("1600x900")
        ctk.set_appearance_mode("Dark")
        
        self.mmu = None
        self.physical_memory = None
        self.active_pid = -1
        
        self.phys_frames_var = ctk.IntVar(value=16)
        self.proc_pages_var = ctk.IntVar(value=32)
        
        self.grid_columnconfigure(0, weight=1, minsize=350)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.create_control_panel()
        self.create_visualization_panel()
        self.create_log_panel()

    def create_control_panel(self):
        # ... (Tidak ada perubahan di fungsi ini, gunakan kode dari jawaban sebelumnya)
        panel = ctk.CTkFrame(self, corner_radius=10, fg_color=COLORS["foreground"])
        panel.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nswe")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(10, weight=1)
        ctk.CTkLabel(panel, text="Konfigurasi Sistem", font=FONTS["heading"]).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        ctk.CTkLabel(panel, text="Ukuran Halaman (KB):", font=FONTS["body"]).grid(row=1, column=0, padx=20, sticky="w")
        self.page_size_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 4")
        self.page_size_entry.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(panel, text="Frame Fisik:", font=FONTS["body"]).grid(row=3, column=0, padx=20, sticky="w")
        self.phys_frames_slider = ctk.CTkSlider(panel, from_=4, to=64, number_of_steps=60, variable=self.phys_frames_var, command=lambda v: self.phys_frames_label.configure(text=f"{int(v)}"))
        self.phys_frames_slider.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="ew")
        self.phys_frames_label = ctk.CTkLabel(panel, text=f"{self.phys_frames_var.get()}", font=FONTS["body_bold"], text_color=COLORS["primary"])
        self.phys_frames_label.grid(row=3, column=0, padx=20, sticky="e")
        ctk.CTkLabel(panel, text="Algoritma Penggantian:", font=FONTS["body_bold"]).grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        algo_frame = ctk.CTkFrame(panel, fg_color="transparent")
        algo_frame.grid(row=6, column=0, padx=20, sticky="w")
        self.algo_var = ctk.StringVar(value="FIFO")
        ctk.CTkRadioButton(algo_frame, text="FIFO", variable=self.algo_var, value="FIFO").pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(algo_frame, text="LRU", variable=self.algo_var, value="LRU").pack(side="left", padx=(0, 10))
        self.start_button = ctk.CTkButton(panel, text="Mulai / Reset Simulasi", font=FONTS["body_bold"], fg_color=COLORS["primary"], hover_color=COLORS["secondary"], command=self.start_simulation)
        self.start_button.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(panel, text="Manajemen Proses", font=FONTS["heading"]).grid(row=8, column=0, padx=20, pady=10, sticky="w")
        proc_creation_frame = ctk.CTkFrame(panel, fg_color="transparent")
        proc_creation_frame.grid(row=9, column=0, padx=20, pady=(0,10), sticky="ew")
        proc_creation_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(proc_creation_frame, text="Page Virtual:", font=FONTS["body"]).grid(row=0, column=0, sticky="w")
        self.proc_pages_slider = ctk.CTkSlider(proc_creation_frame, from_=8, to=128, number_of_steps=120, variable=self.proc_pages_var, command=lambda v: self.proc_pages_label.configure(text=f"{int(v)}"))
        self.proc_pages_slider.grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="ew")
        self.proc_pages_label = ctk.CTkLabel(proc_creation_frame, text=f"{self.proc_pages_var.get()}", font=FONTS["body_bold"], text_color=COLORS["primary"])
        self.proc_pages_label.grid(row=0, column=1, sticky="e")
        self.create_proc_button = ctk.CTkButton(proc_creation_frame, text="Buat Proses", command=self.create_process, state="disabled")
        self.create_proc_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        self.process_list_frame = ctk.CTkScrollableFrame(panel, label_text="Daftar Proses", label_font=FONTS["body_bold"])
        self.process_list_frame.grid(row=10, column=0, padx=20, pady=10, sticky="nsew")
        ctk.CTkLabel(panel, text="Kontrol Proses Aktif", font=FONTS["heading"]).grid(row=11, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(panel, text="Alamat Virtual (byte):", font=FONTS["body"]).grid(row=12, column=0, padx=20, pady=(10, 0), sticky="w")
        self.addr_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 8192")
        self.addr_entry.grid(row=13, column=0, padx=20, sticky="ew")
        self.access_button = ctk.CTkButton(panel, text="Akses Alamat", command=self.access_memory, state="disabled")
        self.access_button.grid(row=14, column=0, padx=20, pady=5, sticky="ew")
        ctk.CTkLabel(panel, text="String Referensi Halaman:", font=FONTS["body"]).grid(row=15, column=0, padx=20, pady=(10, 0), sticky="w")
        self.ref_string_entry = ctk.CTkEntry(panel, placeholder_text="Contoh: 0,1,2,3,0,1,4...")
        self.ref_string_entry.grid(row=16, column=0, padx=20, sticky="ew")
        self.run_ref_button = ctk.CTkButton(panel, text="Jalankan String Referensi", command=self.run_reference_string, state="disabled")
        self.run_ref_button.grid(row=17, column=0, padx=20, pady=5, sticky="ew")

    def create_visualization_panel(self):
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        
        # --- PERUBAHAN TATA LETAK ---
        panel.grid_columnconfigure(0, weight=2) # Kolom kiri untuk tabel dan VAS
        panel.grid_columnconfigure(1, weight=1) # Kolom kanan untuk RAM
        panel.grid_rowconfigure(0, weight=1) # Baris atas untuk Tabel
        panel.grid_rowconfigure(1, weight=1) # Baris bawah untuk VAS

        # --- Panel Kiri Atas: Page Table ---
        ctk.CTkLabel(panel, text="Page Table (Proses Aktif)", font=FONTS["heading"]).grid(row=0, column=0, pady=(0,5), sticky="s")
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background=COLORS["foreground"], foreground=COLORS["text"], fieldbackground=COLORS["foreground"], borderwidth=0, rowheight=25)
        style.configure("Treeview.Heading", background=COLORS["primary"], foreground="white", font=FONTS["body_bold"], relief="flat")
        style.map("Treeview.Heading", background=[('active', COLORS["secondary"])])
        
        page_table_container = ctk.CTkFrame(panel, fg_color="transparent")
        page_table_container.grid(row=0, column=0, padx=(0,5), sticky="nswe")
        page_table_container.grid_rowconfigure(0, weight=1)
        page_table_container.grid_columnconfigure(0, weight=1)
        
        self.page_table_view = ttk.Treeview(page_table_container, columns=("Page", "Frame", "Valid"), show="headings")
        self.page_table_view.heading("Page", text="Nomor Page")
        self.page_table_view.heading("Frame", text="Nomor Frame")
        self.page_table_view.heading("Valid", text="Status")
        self.page_table_view.grid(row=0, column=0, sticky="nswe")

        # --- Panel Kiri Bawah: Ruang Alamat Virtual (Blok) ---
        self.vas_frame = ctk.CTkScrollableFrame(panel, label_text="Ruang Alamat Virtual", label_font=FONTS["body_bold"], corner_radius=10, fg_color=COLORS["foreground"])
        self.vas_frame.grid(row=1, column=0, padx=(0,5), pady=(10,0), sticky="nswe")

        # --- Panel Kanan: Memori Fisik ---
        ctk.CTkLabel(panel, text="Memori Fisik (RAM)", font=FONTS["heading"]).grid(row=0, column=1, pady=(0,10))
        self.phys_mem_frame = ctk.CTkScrollableFrame(panel, label_text="Frames", label_font=FONTS["body_bold"], corner_radius=10, fg_color=COLORS["foreground"])
        self.phys_mem_frame.grid(row=0, column=1, rowspan=2, padx=(5,0), sticky="nswe")

    def update_all_visuals(self):
        # --- PERUBAHAN: Mengisi data ke TIGA panel ---
        # Clear old views
        for item in self.page_table_view.get_children():
            self.page_table_view.delete(item)
        for widget in self.vas_frame.winfo_children(): # Clear VAS Frame
            widget.destroy()
        for widget in self.phys_mem_frame.winfo_children():
            widget.destroy()
            
        if not self.mmu: return
        
        # Update Page Table View & Virtual Address Space (VAS) View
        if self.active_pid in self.mmu.processes:
            process = self.mmu.processes[self.active_pid]
            self.vas_frame.configure(label_text=f"Ruang Alamat Virtual P{self.active_pid}")
            
            for i, entry in enumerate(process.page_table):
                # Data untuk Tabel
                frame_display = entry.frame_number if entry.valid else "-"
                valid_display = "Valid" if entry.valid else "Invalid"
                tags = ("valid",) if entry.valid else ("invalid",)
                self.page_table_view.insert("", "end", values=(i, frame_display, valid_display), tags=tags)
                
                # Data untuk VAS Blok
                color = COLORS["primary"] if entry.valid else COLORS["frame_empty"]
                text = f"Halaman {i}\n(Ke Frame {entry.frame_number})" if entry.valid else f"Halaman {i}\n(Di Disk)"
                page_frame = ctk.CTkFrame(self.vas_frame, fg_color=color, corner_radius=6)
                label = ctk.CTkLabel(page_frame, text=text, font=FONTS["small"])
                label.pack(expand=True, ipady=5)
                page_frame.pack(pady=3, padx=5, fill="x")

        else: # Jika tidak ada proses aktif terpilih
             self.vas_frame.configure(label_text="Ruang Alamat Virtual")

        self.page_table_view.tag_configure("valid", foreground=COLORS["page_hit"])
        self.page_table_view.tag_configure("invalid", foreground=COLORS["text_secondary"])

        # Update Physical Memory View
        if self.physical_memory:
            free_frames = len(self.physical_memory.free_frames)
            total_frames = self.physical_memory.num_frames
            self.phys_mem_frame.configure(label_text=f"{total_frames - free_frames}/{total_frames} Frames Terisi")
            
            for i, content in enumerate(self.physical_memory.frames):
                if content:
                    pid, page_num = content
                    color_index = pid % len(COLORS["PROCESS_COLORS"])
                    color = COLORS["PROCESS_COLORS"][color_index]
                    text = f"Frame {i}\n(P{pid}, Halaman {page_num})"
                else:
                    color = COLORS["frame_empty"]
                    text = f"Frame {i}\n(Kosong)"
                
                frame_widget = ctk.CTkFrame(self.phys_mem_frame, fg_color=color, corner_radius=6)
                label = ctk.CTkLabel(frame_widget, text=text, font=FONTS["small"])
                label.pack(expand=True, ipady=10)
                frame_widget.pack(pady=3, padx=5, fill="x")
                
        # Update Stats
        stats = self.mmu.get_stats()
        self.hits_label.configure(text=f"Hits: {stats['hits']}")
        self.faults_label.configure(text=f"Page Faults: {stats['faults']}")
        self.hit_ratio_label.configure(text=f"Hit Ratio: {stats['hit_ratio']:.2f}%")
        self.total_time_label.configure(text=f"Total Time: {stats['total_time']:.2f} ms")
        self.last_time_label.configure(text=f"Last Op Time: {stats['last_time']:.2f} ms")

    # Sisa fungsi lainnya (create_log_panel, _log, start_simulation, create_process, dll.)
    # tidak perlu diubah. Salin semua fungsi tersebut dari jawaban sebelumnya.
    # ... (Salin semua fungsi lainnya dari create_log_panel sampai akhir kelas)
    def create_log_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=10, fg_color=COLORS["foreground"], height=250)
        panel.grid(row=1, column=1, padx=10, pady=(0,10), sticky="nswe")
        self.grid_rowconfigure(1, weight=0)
        panel.grid_columnconfigure(0, weight=3)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(0, weight=1)
        self.log_textbox = ctk.CTkTextbox(panel, font=FONTS["small"], state="disabled", wrap="word", border_width=0, fg_color=COLORS["foreground"])
        self.log_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        stats_frame = ctk.CTkFrame(panel, fg_color="transparent")
        stats_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        ctk.CTkLabel(stats_frame, text="Kinerja", font=FONTS["body_bold"]).pack(anchor="w")
        self.hits_label = ctk.CTkLabel(stats_frame, text="Hits: 0", font=FONTS["body"])
        self.hits_label.pack(anchor="w")
        self.faults_label = ctk.CTkLabel(stats_frame, text="Page Faults: 0", font=FONTS["body"])
        self.faults_label.pack(anchor="w")
        self.hit_ratio_label = ctk.CTkLabel(stats_frame, text="Hit Ratio: 0.00%", font=FONTS["body"])
        self.hit_ratio_label.pack(anchor="w")
        self.total_time_label = ctk.CTkLabel(stats_frame, text="Total Time: 0.00 ms", font=FONTS["body"])
        self.total_time_label.pack(anchor="w")
        self.last_time_label = ctk.CTkLabel(stats_frame, text="Last Op Time: 0.00 ms", font=FONTS["body"])
        self.last_time_label.pack(anchor="w")

    def _log(self, message, status=None):
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        self.log_textbox.configure(state="normal")
        start_index = self.log_textbox.index("end-1c")
        self.log_textbox.insert("end", f"[{current_time}] {message}\n")
        end_index = self.log_textbox.index("end-2c")
        if status:
            self.log_textbox.tag_add(status, start_index, end_index)
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")

    def setup_log_tags(self):
        self.log_textbox.tag_config("hit", foreground=COLORS["page_hit"])
        self.log_textbox.tag_config("fault_free", foreground=COLORS["page_fault"])
        self.log_textbox.tag_config("fault_replace", foreground=COLORS["page_victim"])
        self.log_textbox.tag_config("info", foreground=COLORS["text_secondary"])
        self.log_textbox.tag_config("error", foreground=COLORS["page_victim"])

    def start_simulation(self):
        try:
            num_frames = self.phys_frames_var.get()
            page_size_kb = int(self.page_size_entry.get())
            if page_size_kb <= 0: raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Input Ukuran Halaman dan Frame Fisik harus angka positif.")
            return
        algo_map = {"FIFO": FIFO, "LRU": LRU}
        algorithm = algo_map[self.algo_var.get()](num_frames)
        self.physical_memory = PhysicalMemory(num_frames, page_size_kb * 1024)
        self.mmu = MemoryManagementUnit(self.physical_memory, algorithm)
        self.create_proc_button.configure(state="normal")
        self.active_pid = -1
        self.update_access_controls()
        self.update_process_list()
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.setup_log_tags()
        self._log("--- Simulasi Dimulai ---", "info")
        self._log(f"Memori: {num_frames} frames, Halaman: {page_size_kb}KB, Algoritma: {self.algo_var.get()}", "info")
        self.update_all_visuals()

    def create_process(self):
        if not self.mmu: return
        try:
            num_pages = self.proc_pages_var.get()
            page_size_bytes = int(self.page_size_entry.get()) * 1024
            proc_size_bytes = num_pages * page_size_bytes
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Ukuran Halaman harus diisi.")
            return
        pid = self.mmu.create_process(proc_size_bytes, page_size_bytes)
        self._log(f"Proses P{pid} dibuat dengan {num_pages} halaman.", "info")
        self.update_process_list()
        self.select_process(pid)

    def update_process_list(self):
        for widget in self.process_list_frame.winfo_children():
            widget.destroy()
        if not self.mmu or not self.mmu.processes: return
        sorted_pids = sorted(self.mmu.processes.keys())
        for pid in sorted_pids:
            proc_frame = ctk.CTkFrame(self.process_list_frame, fg_color="transparent")
            proc_frame.pack(fill="x", pady=2, padx=2)
            button_color = COLORS["secondary"] if pid == self.active_pid else "transparent"
            proc_button = ctk.CTkButton(proc_frame, text=f"Proses {pid}", fg_color=button_color, command=lambda p=pid: self.select_process(p))
            proc_button.pack(side="left", fill="x", expand=True)
            del_button = ctk.CTkButton(proc_frame, text="X", width=30, fg_color=COLORS["page_victim"], command=lambda p=pid: self.terminate_process(p))
            del_button.pack(side="right", padx=(5,0))

    def select_process(self, pid):
        if self.mmu and pid in self.mmu.processes:
            self.active_pid = pid
            self._log(f"Proses P{pid} dipilih sebagai proses aktif.", "info")
            self.update_process_list()
            self.update_all_visuals()
        self.update_access_controls()
    
    def terminate_process(self, pid):
        if self.mmu and self.mmu.terminate_process(pid):
            self._log(f"Proses P{pid} dihentikan.", "info")
            if self.active_pid == pid:
                self.active_pid = -1
            self.update_process_list()
            self.update_all_visuals()
            self.update_access_controls()
        else:
            self._log(f"Gagal menghentikan proses P{pid}.", "error")

    def update_access_controls(self):
        state = "normal" if self.active_pid != -1 else "disabled"
        self.access_button.configure(state=state)
        self.run_ref_button.configure(state=state)

    def access_memory(self):
        if self.active_pid == -1: return
        try:
            v_addr = int(self.addr_entry.get())
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Alamat Virtual harus angka.")
            return
        self._log(f"--> P{self.active_pid} akses VA: {v_addr}", "info")
        message, status = self.mmu.access_virtual_address(self.active_pid, v_addr)
        self._log(message, status if status else "error")
        self.update_all_visuals()

    def run_reference_string(self):
        if self.active_pid == -1: return
        try:
            ref_string = [int(p) for p in self.ref_string_entry.get().replace(" ", "").split(',') if p]
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Format String Referensi tidak valid.")
            return
        self._log(f"--- Menjalankan String Referensi untuk P{self.active_pid} ---", "info")
        page_size_bytes = self.physical_memory.page_size
        for i, page_num in enumerate(ref_string):
            v_addr = page_num * page_size_bytes
            self._log(f"--> [Langkah {i+1}] Akses Halaman {page_num}", "info")
            message, status = self.mmu.access_virtual_address(self.active_pid, v_addr)
            self._log(message, status if status else "error")
            if "Error" in message: break
            self.update_all_visuals()
            self.update()
            self.after(200)
        self.update_all_visuals()
        self._log("--- Eksekusi Selesai ---", "info")
