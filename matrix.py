import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any

# =========================================================
# KONSTANTA & STYLING
# =========================================================
PRIMARY_COLOR = "#0047AB"  # Biru gelap (Cobalt Blue)
ACCENT_COLOR = "#00BFFF"   # Biru cerah (Deep Sky Blue)
BACKGROUND_COLOR = "#F0F0F0" # Abu-abu terang
TEXT_COLOR = "#333333"

class Mahasiswa:
    """Kelas untuk merepresentasikan data seorang Mahasiswa, kini dengan kamus nilai mata kuliah."""
    def __init__(self, nama: str, nim: str):
        self.nama = nama
        self.nim = nim
        self.matkul_nilai: Dict[str, int] = {}

    def tambah_nilai_matkul(self, matkul: str, nilai: int):
        """Menambahkan atau memperbarui Nilai Akhir (0-100) untuk mata kuliah tertentu."""
        self.matkul_nilai[matkul] = nilai

    def konversi_nilai_ke_huruf_dan_bobot(self, nilai: int) -> tuple[str, float]:
        """Mengkonversi nilai (0-100) ke Nilai Huruf dan Bobot Skala 4.00."""
        if nilai >= 85:
            return "A", 4.0
        elif nilai >= 75:
            return "B", 3.0
        elif nilai >= 65:
            return "C", 2.0
        elif nilai >= 50:
            return "D", 1.0
        else:
            return "E", 0.0

    def hitung_rata_rata(self) -> float:
        """Menghitung rata-rata nilai (0-100) dari semua mata kuliah."""
        if not self.matkul_nilai:
            return 0.0
        total_nilai = sum(self.matkul_nilai.values())
        return total_nilai / len(self.matkul_nilai)

    def hitung_ipk(self) -> float:
        """Menghitung IPK (Indeks Prestasi Kumulatif) berdasarkan skala 4.00."""
        if not self.matkul_nilai:
            return 0.0
            
        total_bobot = 0.0
        jumlah_matkul = len(self.matkul_nilai)
        
        for nilai_akhir in self.matkul_nilai.values():
            _, bobot = self.konversi_nilai_ke_huruf_dan_bobot(nilai_akhir)
            total_bobot += bobot
            
        return total_bobot / jumlah_matkul

    def get_predikat_rata_rata(self) -> str:
        """Dipertahankan di kelas untuk konsistensi, tapi tidak ditampilkan di UI."""
        rata_rata = self.hitung_rata_rata()
        if rata_rata >= 85: return "A"
        elif rata_rata >= 75: return "B"
        elif rata_rata >= 65: return "C"
        else: return "D"

# =========================================================
# APLIKASI GUI
# =========================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Informasi Akademik Sederhana")
        # Menjaga ukuran UI agar semua elemen terlihat
        self.root.geometry("1050x650") 
        self.root.resizable(False, False)
        self.root.config(bg=BACKGROUND_COLOR)

        self.data_mahasiswa: list[Mahasiswa] = []
        self.mahasiswa_terpilih: Mahasiswa | None = None

        self.apply_styles()
        self.create_widgets()
        self.update_mahasiswa_table()

    def apply_styles(self):
        """Menerapkan tema dan gaya modern pada widget Tkinter/ttk."""
        style = ttk.Style()
        style.theme_use("clam") # Tema dasar yang bersih

        # Gaya Judul Utama
        tk.Label(self.root, text="SISTEM PENGELOLAAN DATA AKADEMIK", 
                 fg=PRIMARY_COLOR, bg=BACKGROUND_COLOR, font=("Helvetica", 18, "bold")).pack(pady=15)

        # Gaya Treeview (Tabel)
        style.configure("Treeview", 
                        background="white", 
                        foreground=TEXT_COLOR, 
                        rowheight=28, 
                        font=('Arial', 10),
                        fieldbackground="white")
        style.map("Treeview", 
                  background=[("selected", ACCENT_COLOR)])
        style.configure("Treeview.Heading", 
                        background=PRIMARY_COLOR, 
                        foreground="white", 
                        font=('Arial', 10, 'bold'), 
                        padding=[10, 8])

        # Gaya Tombol
        style.configure('Custom.TButton', 
                        foreground='white', 
                        background=PRIMARY_COLOR, 
                        font=('Arial', 10, 'bold'),
                        borderless=1)
        style.map('Custom.TButton', 
                  background=[('active', ACCENT_COLOR)],
                  foreground=[('active', 'white')])

        # Gaya Frame (Card-like)
        self.card_style = {"bg": "white", "padx": 15, "pady": 15, "bd": 1, "relief": "groove"}

    def create_widgets(self):
        """Membuat dan menata semua widget UI."""
        
        # CONTAINER UTAMA: Menggunakan Frame yang lebih besar (PACK)
        main_container = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        main_container.pack(pady=10, padx=20, fill="x")
        
        # -----------------------------------------------------
        # FRAME KIRI: INPUT & KARTU DATA (PACK di dalam main_container)
        # -----------------------------------------------------
        frame_kiri = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        frame_kiri.pack(side="left", padx=20, anchor="n")
        
        # --- CARD 1: INPUT MAHASISWA (PACK di dalam frame_kiri) ---
        card_mhs = tk.Frame(frame_kiri, **self.card_style)
        card_mhs.pack(pady=10, fill="x")

        # Panggil fungsi dengan label yang diperlukan
        self.create_input_section(card_mhs, "DATA MAHASISWA", 
                                  ["Nama", "NIM"], 
                                  self.create_mhs_buttons)

        # --- CARD 2: INPUT NILAI MATA KULIAH (PACK di dalam frame_kiri) ---
        card_matkul = tk.Frame(frame_kiri, **self.card_style)
        card_matkul.pack(pady=10, fill="x")

        # Panggil fungsi dengan label yang diperlukan
        self.create_input_section(card_matkul, "INPUT NILAI MATA KULIAH (0-100)", 
                                  ["Matkul", "Nilai"], 
                                  self.create_matkul_buttons)

        # -----------------------------------------------------
        # FRAME KANAN: TABEL DATA (PACK di dalam main_container)
        # -----------------------------------------------------
        frame_kanan = tk.Frame(main_container, bg=BACKGROUND_COLOR)
        frame_kanan.pack(side="right", padx=10, anchor="n")
        
        # --- TABEL 1: DATA MAHASISWA (PACK di dalam frame_kanan) ---
        tk.Label(frame_kanan, text="DAFTAR MAHASISWA (Rata-Rata & IPK)", bg=BACKGROUND_COLOR, fg=PRIMARY_COLOR, 
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        self.setup_mahasiswa_table(frame_kanan)

        # --- TABEL 2: DATA NILAI MATA KULIAH (PACK di dalam frame_kanan) ---
        tk.Label(frame_kanan, text="DETAIL NILAI MATA KULIAH", bg=BACKGROUND_COLOR, fg=PRIMARY_COLOR, 
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(15, 5))
        self.setup_matkul_table(frame_kanan)
        
    def create_input_section(self, parent: tk.Frame, title: str, labels: list[str], button_creator: Any):
        """Fungsi pembantu untuk membuat bagian input yang seragam (Mahasiswa/Nilai)."""
        
        # Row 0: Title
        tk.Label(parent, text=title, bg="white", fg=PRIMARY_COLOR, 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
                 
        for i, label_text in enumerate(labels):
            # Baris input dimulai dari Row 1
            tk.Label(parent, text=f"{label_text}:", bg="white", fg=TEXT_COLOR, 
                     font=("Arial", 10)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=5)
            
            entry = tk.Entry(parent, width=30, bd=1, relief="solid", font=("Arial", 10))
            entry.grid(row=i + 1, column=1, pady=5, padx=5, ipady=3)
            
            # Menyimpan referensi ke entry widget
            if label_text == "Nama": self.entry_nama = entry
            elif label_text == "NIM": self.entry_nim = entry
            elif label_text == "Matkul": self.entry_matkul = entry
            elif label_text == "Nilai": self.entry_nilai = entry

        # Baris untuk tombol adalah setelah baris input terakhir
        button_start_row = len(labels) + 1 
        button_creator(parent, button_start_row) 

    def create_mhs_buttons(self, parent_card: tk.Frame, start_row: int):
        """Membuat dan menempatkan tombol CRUD Mahasiswa."""
        btn_frame_mhs = tk.Frame(parent_card, bg="white") 
        # Grid tombol di dalam parent_card (card_mhs)
        btn_frame_mhs.grid(row=start_row, column=0, columnspan=2, pady=(15, 0), sticky="w")
        
        # Tombol Mahasiswa dengan lebar 10
        self.make_button(btn_frame_mhs, "➕ Tambah", self.tambah_mahasiswa, 0, width=10)
        self.make_button(btn_frame_mhs, "✏️ Edit", self.edit_mahasiswa, 1, width=10)
        self.make_button(btn_frame_mhs, "❌ Hapus", self.hapus_mahasiswa, 2, width=10)

    def create_matkul_buttons(self, parent_card: tk.Frame, start_row: int):
        """Membuat dan menempatkan tombol CRUD Mata Kuliah."""
        btn_frame_matkul = tk.Frame(parent_card, bg="white")
        # Grid tombol di dalam parent_card (card_matkul)
        btn_frame_matkul.grid(row=start_row, column=0, columnspan=2, pady=(15, 0), sticky="w")

        # Tombol Mata Kuliah
        self.make_button(btn_frame_matkul, "✅ Tambah/Edit", self.tambah_edit_nilai, 0, width=15)
        # FIX: Melebarkan tombol Hapus Nilai menjadi 17 agar teks tidak terpotong
        self.make_button(btn_frame_matkul, "🗑️ Hapus Nilai", self.hapus_nilai, 1, width=17)

    # ---------------------------------------------------------
    # SETUP TABEL
    # ---------------------------------------------------------
    def setup_mahasiswa_table(self, parent):
        """Mengatur Treeview untuk daftar Mahasiswa (tanpa Predikat)."""
        frame_mhs_tabel = tk.Frame(parent, bg=BACKGROUND_COLOR)
        frame_mhs_tabel.pack(fill="x")

        # Kolom yang ditampilkan: Nama, NIM, Rata-Rata, IPK
        self.tree_mhs = ttk.Treeview(frame_mhs_tabel, columns=("nama", "nim", "rata", "ipk"),
                                     show="headings", height=10)

        for col, text, width, anchor in [("nama", "Nama Mahasiswa", 200, "w"), 
                                         ("nim", "NIM", 100, "center"),
                                         ("rata", "Rata-Rata (0-100)", 130, "center"), 
                                         ("ipk", "IPK (4.00)", 100, "center")]: 
            self.tree_mhs.heading(col, text=text)
            self.tree_mhs.column(col, width=width, anchor=anchor)

        self.tree_mhs.bind("<ButtonRelease-1>", self.pilih_mahasiswa)
        self.tree_mhs.pack(side='left', fill="x", expand=True) # Menggunakan pack

        # Scrollbar (Opsional, tapi praktik yang baik)
        vsb_mhs = ttk.Scrollbar(frame_mhs_tabel, orient="vertical", command=self.tree_mhs.yview)
        self.tree_mhs.configure(yscrollcommand=vsb_mhs.set)
        vsb_mhs.pack(side='right', fill='y')


    def setup_matkul_table(self, parent):
        """Mengatur Treeview untuk daftar Nilai Mata Kuliah."""
        frame_matkul_tabel = tk.Frame(parent, bg=BACKGROUND_COLOR)
        frame_matkul_tabel.pack(fill="x")

        # Kolom yang ditampilkan: Mata Kuliah, Nilai, Nilai Huruf
        self.tree_matkul = ttk.Treeview(frame_matkul_tabel, columns=("matkul", "nilai", "huruf"),
                                        show="headings", height=8)

        for col, text, width, anchor in [("matkul", "Mata Kuliah", 200, "w"), 
                                         ("nilai", "Nilai", 100, "center"),
                                         ("huruf", "Nilai Huruf", 130, "center")]:
            self.tree_matkul.heading(col, text=text)
            self.tree_matkul.column(col, width=width, anchor=anchor)
        
        self.tree_matkul.bind("<ButtonRelease-1>", self.pilih_nilai)
        self.tree_matkul.pack(side='left', fill="x", expand=True) # Menggunakan pack
        
        # Scrollbar (Opsional, tapi praktik yang baik)
        vsb_matkul = ttk.Scrollbar(frame_matkul_tabel, orient="vertical", command=self.tree_matkul.yview)
        self.tree_matkul.configure(yscrollcommand=vsb_matkul.set)
        vsb_matkul.pack(side='right', fill='y')


    # ---------------------------------------------------------
    # BUTTON FACTORY
    # ---------------------------------------------------------
    def make_button(self, parent: tk.Frame, text: str, cmd: Any, col: int, width: int = 12):
        """Membuat dan menempatkan tombol dengan gaya kustom ttk."""
        button = ttk.Button(parent, text=text, command=cmd, style='Custom.TButton',
                           width=width)
        # Tombol di dalam btn_frame_mhs/btn_frame_matkul menggunakan GRID
        button.grid(row=0, column=col, pady=5, padx=5, ipady=5)

    # ---------------------------------------------------------
    # VALIDASI & LOGIKA 
    # ---------------------------------------------------------
    def validasi_input(self, nama: str, nim: str, matkul: str | None = None, nilai: str | None = None) -> bool:
        """Melakukan validasi input Mahasiswa dan Nilai Matkul."""
        # Validasi Mahasiswa
        if nama and not all(c.isalpha() or c.isspace() or c == '.' for c in nama):
            messagebox.showerror("Error", "Nama hanya boleh huruf, spasi, atau titik!")
            return False
        if nim and not nim.isdigit():
            messagebox.showerror("Error", "NIM harus berisi angka!")
            return False

        # Validasi Mata Kuliah & Nilai
        if matkul or nilai:
            if not matkul:
                 messagebox.showerror("Error", "Nama Mata Kuliah tidak boleh kosong!")
                 return False
            if not nilai or not nilai.isdigit():
                messagebox.showerror("Error", "Nilai harus berupa angka (0 - 100)!")
                return False
            
            nilai_int = int(nilai)
            if not (0 <= nilai_int <= 100):
                messagebox.showerror("Error", "Nilai harus berada dalam rentang 0 - 100!")
                return False
        return True

    # =========================================================
    # CRUD MAHASISWA
    # =========================================================
    def tambah_mahasiswa(self):
        """Menambahkan Mahasiswa baru."""
        nama = self.entry_nama.get().strip()
        nim = self.entry_nim.get().strip()
        
        if not self.validasi_input(nama, nim): return
        if not nama or not nim:
            messagebox.showerror("Error", "Nama dan NIM harus diisi!")
            return

        if any(mhs.nim == nim for mhs in self.data_mahasiswa):
            messagebox.showerror("Error", f"NIM {nim} sudah terdaftar!")
            return

        self.data_mahasiswa.append(Mahasiswa(nama, nim))
        self.update_mahasiswa_table()
        self.clear_input_mhs()
        messagebox.showinfo("Sukses", "Mahasiswa berhasil ditambahkan!")

    def edit_mahasiswa(self):
        """Mengedit data Mahasiswa yang dipilih."""
        selected = self.tree_mhs.selection()
        if not selected or not self.mahasiswa_terpilih:
            messagebox.showwarning("Peringatan", "Pilih Mahasiswa yang ingin diedit terlebih dahulu!")
            return
        
        nama = self.entry_nama.get().strip()
        nim = self.entry_nim.get().strip()
        
        if not self.validasi_input(nama, nim): return

        index = self.tree_mhs.index(selected)
        
        for i, mhs in enumerate(self.data_mahasiswa):
            if i != index and mhs.nim == nim:
                messagebox.showerror("Error", f"NIM {nim} sudah terdaftar pada data lain!")
                return

        mhs = self.data_mahasiswa[index]
        mhs.nama = nama
        mhs.nim = nim

        self.update_mahasiswa_table()
        self.clear_input_mhs()
        self.mahasiswa_terpilih = None
        messagebox.showinfo("Sukses", "Data Mahasiswa berhasil diedit!")

    def hapus_mahasiswa(self):
        """Menghapus data Mahasiswa yang dipilih."""
        selected = self.tree_mhs.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih Mahasiswa yang ingin dihapus terlebih dahulu!")
            return

        if messagebox.askyesno("Konfirmasi Hapus", "Apakah Anda yakin ingin menghapus Mahasiswa ini dan semua nilainya?"):
            # Cari objek Mahasiswa yang benar untuk dihapus
            index = self.tree_mhs.index(selected)
            if index < len(self.data_mahasiswa):
                mhs_dihapus = self.data_mahasiswa[index]
                if mhs_dihapus == self.mahasiswa_terpilih:
                    self.mahasiswa_terpilih = None # Hapus referensi jika yang dihapus adalah yang aktif
                del self.data_mahasiswa[index]
                
            self.update_mahasiswa_table()
            self.clear_input_mhs()
            self.update_matkul_table() # Kosongkan tabel nilai
            messagebox.showinfo("Sukses", "Mahasiswa berhasil dihapus!")
            
    # =========================================================
    # CRUD NILAI MATA KULIAH
    # =========================================================
    def tambah_edit_nilai(self):
        """Menambahkan atau mengedit nilai mata kuliah untuk Mahasiswa yang dipilih."""
        if not self.mahasiswa_terpilih:
            messagebox.showwarning("Peringatan", "Pilih Mahasiswa dari daftar di kanan terlebih dahulu!")
            return
            
        matkul = self.entry_matkul.get().strip()
        nilai = self.entry_nilai.get().strip()
        
        if not self.validasi_input("", "", matkul, nilai): return
        
        nilai_int = int(nilai)
        self.mahasiswa_terpilih.tambah_nilai_matkul(matkul, nilai_int)
        
        # Perbarui kedua tabel
        self.update_mahasiswa_table() 
        self.update_matkul_table(self.mahasiswa_terpilih)
        self.clear_input_matkul()
        messagebox.showinfo("Sukses", f"Nilai {matkul} berhasil ditambahkan/diperbarui untuk {self.mahasiswa_terpilih.nama}!")

    def hapus_nilai(self):
        """Menghapus nilai mata kuliah yang dipilih dari Mahasiswa yang aktif."""
        if not self.mahasiswa_terpilih:
            messagebox.showwarning("Peringatan", "Pilih Mahasiswa dari daftar di kanan terlebih dahulu!")
            return

        selected_matkul = self.tree_matkul.selection()
        if not selected_matkul:
            messagebox.showwarning("Peringatan", "Pilih baris Mata Kuliah yang ingin dihapus!")
            return
            
        # Mengambil nama mata kuliah dari baris yang dipilih
        matkul_nama = self.tree_matkul.item(selected_matkul, 'values')[0]
        
        if messagebox.askyesno("Konfirmasi Hapus", f"Hapus nilai {matkul_nama} dari {self.mahasiswa_terpilih.nama}?"):
            if matkul_nama in self.mahasiswa_terpilih.matkul_nilai:
                del self.mahasiswa_terpilih.matkul_nilai[matkul_nama]
                
                # Perbarui kedua tabel
                self.update_mahasiswa_table() 
                self.update_matkul_table(self.mahasiswa_terpilih)
                self.clear_input_matkul()
                messagebox.showinfo("Sukses", "Nilai berhasil dihapus!")

    # =========================================================
    # TABLE & INPUT MANAGEMENT 
    # =========================================================
    def update_mahasiswa_table(self):
        """Memperbarui tampilan tabel Mahasiswa."""
        for item in self.tree_mhs.get_children(): 
            self.tree_mhs.delete(item)
        for m in self.data_mahasiswa:
            rata = m.hitung_rata_rata()
            ipk = m.hitung_ipk() 
            self.tree_mhs.insert("", tk.END, values=(m.nama, m.nim, f"{rata:.2f}", f"{ipk:.2f}"))

    def update_matkul_table(self, mhs: Mahasiswa | None = None):
        """Memperbarui tampilan tabel Nilai Mata Kuliah."""
        for item in self.tree_matkul.get_children(): 
            self.tree_matkul.delete(item)

        if mhs and mhs.matkul_nilai:
            for matkul, nilai in mhs.matkul_nilai.items():
                nilai_huruf, _ = mhs.konversi_nilai_ke_huruf_dan_bobot(nilai) 
                self.tree_matkul.insert("", tk.END, values=(matkul, nilai, nilai_huruf))

    def pilih_mahasiswa(self, event: tk.Event):
        """Mengaktifkan Mahasiswa yang dipilih dan memuat datanya ke input."""
        selected = self.tree_mhs.selection()
        if not selected: return
        
        try:
            index = self.tree_mhs.index(selected)
            self.mahasiswa_terpilih = self.data_mahasiswa[index]

            # Muat data Mahasiswa ke input
            self.clear_input_mhs()
            self.entry_nama.insert(0, self.mahasiswa_terpilih.nama)
            self.entry_nim.insert(0, self.mahasiswa_terpilih.nim)
            
            # Muat Nilai Matkul Mahasiswa yang dipilih ke tabel Nilai
            self.update_matkul_table(self.mahasiswa_terpilih)
            self.clear_input_matkul()
            
        except IndexError: 
            self.clear_input_mhs()
            self.mahasiswa_terpilih = None

    def pilih_nilai(self, event: tk.Event):
        """Memuat data Mata Kuliah yang dipilih ke input Matkul."""
        selected = self.tree_matkul.selection()
        if not selected: return
        
        try:
            matkul_nama, nilai_akhir_str, _ = self.tree_matkul.item(selected, 'values')
            self.clear_input_matkul()
            self.entry_matkul.insert(0, matkul_nama)
            self.entry_nilai.insert(0, nilai_akhir_str)
        except Exception:
            self.clear_input_matkul()

    def clear_input_mhs(self):
        """Mengosongkan input Nama dan NIM."""
        self.entry_nama.delete(0, tk.END)
        self.entry_nim.delete(0, tk.END)
        
    def clear_input_matkul(self):
        """Mengosongkan input Mata Kuliah dan Nilai."""
        self.entry_matkul.delete(0, tk.END)
        self.entry_nilai.delete(0, tk.END)

# MAIN PROGRAM
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()