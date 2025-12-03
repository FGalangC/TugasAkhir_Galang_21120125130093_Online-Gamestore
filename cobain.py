import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from collections import deque
import json
import os

# Modul 1: Variabel, Tipe Data, dan Array

DATA_FILENAME = "gamevault_data.json"      # Variabel string
MAX_RECENT = 10                            # Variabel integer (constant)

# Array (List)
PLATFORM_OPTIONS = ["PC", "PS5", "PS4", "Xbox", "Nintendo Switch", "Mobile", "VR"]
STATUS_OPTIONS = ["Playing", "Completed", "Planned"]

# Modul 5: OOP - class Game

class Game:
    def __init__(self, title: str, genre: str, platform: str, year: int, status: str):
        # tipe data string dan integer
        self.title = title
        self.genre = genre
        self.platform = platform
        self.year = int(year)
        self.status = status

    # Modul 4: Method
    def to_dict(self):
        return {
            "title": self.title,
            "genre": self.genre,
            "platform": self.platform,
            "year": self.year,
            "status": self.status
        }

    # Modul 4 + OOP: staticmethod → contoh function dalam class
    @staticmethod
    def from_dict(d):
        return Game(d["title"], d["genre"], d["platform"], int(d["year"]), d["status"])

    def __str__(self):
        return f"{self.title} | {self.genre} | {self.platform} | {self.year} | {self.status}"

# Modul 5 + Modul 6: CatalogManager (OOP + Stack & Queue)

class CatalogManager:
    def __init__(self, filename=DATA_FILENAME):
        self.filename = filename
        self.games_list = []          # Array → Modul 1
        self.undo_stack = []          # Stack → Modul 6 (LIFO)
        self.recent_queue = deque(maxlen=MAX_RECENT)  # Queue → Modul 6 (FIFO)
        self.load()

    # Modul 4: Method 
    def load(self):
        # Modul 2: Pengkondisian (if/else)
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Modul 3: Perulangan (loop daftar game)
                    self.games_list = [Game.from_dict(d) for d in data]
            except Exception:
                self.games_list = []
        else:
            self.games_list = []

    # Modul 4: Method
    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([g.to_dict() for g in self.games_list], f, indent=2)

    # Modul 4: Method + Modul 2 (Pengkondisian)
    def add_game(self, game: Game):
        if any(g.title.lower() == game.title.lower() for g in self.games_list):   # modul 3 (loop any)
            raise ValueError("Game dengan judul sama sudah ada.")
        self.games_list.append(game)
        self.save()

    # Modul 4: Method (delete) + Stack for undo
    def remove_game(self, title: str):
        removed = [g for g in self.games_list if g.title.lower() == title.lower()]
        if not removed:
            raise ValueError("Game tidak ditemukan.")
        for g in removed:          # Modul 3: Loop
            self.undo_stack.append(("delete", g.to_dict()))
        self.games_list = [g for g in self.games_list if g.title.lower() != title.lower()]
        self.save()

    # Modul 4: Edit Method
    def edit_game(self, title: str, new_game: Game):
        found = False
        # Modul 3: Loop
        for i, g in enumerate(self.games_list):
            if g.title.lower() == title.lower():
                self.undo_stack.append(("edit", g.to_dict()))
                self.games_list[i] = new_game
                found = True
        if not found:
            raise ValueError("Game tidak ditemukan untuk diedit.")
        self.save()

    # Modul 4
    def search_games(self, keyword: str):
        if not keyword: return list(self.games_list)
        keyword = keyword.lower()
        # Modul 3: Loop 
        return [g for g in self.games_list if (
            keyword in g.title.lower() or
            keyword in g.genre.lower() or
            keyword in g.platform.lower() or
            keyword in str(g.year) or
            keyword in g.status.lower())]

    def list_all(self):
        return list(self.games_list)

    # Modul 6: Stack Undo
    def undo(self):
        if not self.undo_stack:
            raise ValueError("Tidak ada operasi untuk di-undo.")
        op, payload = self.undo_stack.pop()   # LIFO mechanism
        if op == "delete":
            g = Game.from_dict(payload)
            self.games_list.append(g)
            self.save()
            return f"Restore: {g.title}"
        elif op == "edit":
            prev = Game.from_dict(payload)
            replaced = False
            for i, g in enumerate(self.games_list):  # Modul 3
                if g.title.lower() == prev.title.lower():
                    self.games_list[i] = prev
                    replaced = True
                    break
            if not replaced:
                self.games_list.append(prev)
            self.save()
            return f"Undo edit: {prev.title}"

    # Modul 6: Queue (Push Recent)
    def push_recent(self, game: Game):
        self.recent_queue.append(game.to_dict())

    def get_recent(self):
        return [Game.from_dict(d) for d in list(self.recent_queue)]


# Modul 4 (Function: Validasi & Normalisasi)

def validate_nonempty(s: str):
    return bool(s and s.strip())

def validate_year(y):
    try:
        yy = int(y)
        return 1970 <= yy <= 2050  # Modul 2 (pengkondisian)
    except:
        return False

def normalize_status(s: str):
        s = s.strip().lower()
        if s in ("playing", "main", "sedang bermain"): return "Playing"     # modul 2
        if s in ("completed", "tamat", "selesai"): return "Completed"
        if s in ("planned", "belum", "to play"): return "Planned"
        return s.title()

# Modul 8: LOGIN UI (GUI)

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("GameVault - Login")
        self.root.geometry("400x260")
        self.root.configure(bg="#0f0f0f")

        tk.Label(root, text="GAMEVAULT LOGIN", font=("Poppins", 18, "bold"), fg="#00d0ff", bg="#0f0f0f").pack(pady=15)

        tk.Label(root, text="Masukkan Username:", font=("Poppins", 10), fg="white", bg="#0f0f0f").pack()

        self.username_entry = tk.Entry(root, font=("Poppins", 11), bg="#1a1a1a", fg="white", relief=tk.FLAT)
        self.username_entry.pack(pady=10)

        tk.Button(root, text="LOGIN", font=("Poppins", 11, "bold"), bg="#00d0ff",
                  fg="#002834", relief=tk.FLAT, width=15, command=self.submit).pack(pady=15)

    # Modul 4: Method + GUI Action
    def submit(self):
        username = self.username_entry.get().strip()
        if not username:   # Modul 2: Pengkondisian
            return messagebox.showerror("Error", "Username tidak boleh kosong")

        self.root.destroy()
        main(username)

# Modul 8: GUI 

class GameVaultGUI:
    def __init__(self, root, username):
        self.username = username
        self.root = root
        self.root.title(f"GameVault - Welcome {username}")
        self.root.geometry("980x620")
        self.root.configure(bg="#0f0f0f")
        self.root.minsize(880, 520)

        self.mgr = CatalogManager()

        self.bg = "#0f0f0f"
        self.card = "#141414"
        self.fg = "#e6e6e6"
        self.accent = "#00d0ff"
        self.button_accent = "#12b3d9"

        tk.Label(root, text=f"GAMEVAULT - {username.upper()}",
                 font=("Poppins", 22, "bold"), fg=self.accent, bg=self.bg).pack(pady=(12, 6))

        container = tk.Frame(root, bg=self.bg)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # LEFT PANEL - FORM ENTRY
        left = tk.Frame(container, bg=self.card)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(8,16), pady=8)

        def label(text):
            return tk.Label(left, text=text, bg=self.card, fg=self.fg, font=("Poppins", 10))

        label("Title").pack(anchor="w", pady=(8,2))
        self.e_title = ttk.Entry(left, width=28)
        self.e_title.pack(pady=4)

        label("Genre").pack(anchor="w", pady=(8,2))
        self.e_genre = ttk.Entry(left, width=28)
        self.e_genre.pack(pady=4)

        # Dropdown 
        label("Platform").pack(anchor="w", pady=(8,2))
        self.platform_var = tk.StringVar(value=PLATFORM_OPTIONS[0])
        self.e_platform = ttk.Combobox(left, textvariable=self.platform_var, values=PLATFORM_OPTIONS, width=26)
        self.e_platform.pack(pady=4)

        label("Year").pack(anchor="w", pady=(8,2))
        self.e_year = ttk.Entry(left, width=28)
        self.e_year.pack(pady=4)

        label("Status").pack(anchor="w", pady=(8,2))
        self.status_var = tk.StringVar(value=STATUS_OPTIONS[2])
        self.e_status = ttk.Combobox(left, textvariable=self.status_var, values=STATUS_OPTIONS, width=26)
        self.e_status.pack(pady=4)

        def btn(text, cmd):
            return tk.Button(left, text=text, font=("Poppins", 10, "bold"), width=20, command=cmd,
                             bg=self.button_accent, fg="#062027", relief=tk.FLAT)

        # BUTTON ACTIONS 
        btn("Tambah Game", self.gui_add).pack(pady=6)
        btn("Edit Selected", self.gui_edit).pack(pady=6)
        btn("Hapus Selected", self.gui_delete).pack(pady=6)
        btn("Undo", self.gui_undo).pack(pady=6)
        tk.Button(left, text="Clear Form", command=self.clear_form, bg="#2a2a2a", fg=self.fg, relief=tk.FLAT).pack(pady=(6,12))

        # RIGHT PANEL - GAME LIST

        right = tk.Frame(container, bg=self.bg)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0,8), pady=8)

        search_frame = tk.Frame(right, bg=self.bg)
        search_frame.pack(fill=tk.X, pady=(4,8))

        tk.Label(search_frame, text="Search", font=("Poppins", 10), fg=self.fg, bg=self.bg).pack(side=tk.LEFT, padx=(4,6))
        self.e_search = ttk.Entry(search_frame)
        self.e_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))

        tk.Button(search_frame, text="Cari", command=self.gui_search, bg=self.button_accent,
                  fg="#062027", relief=tk.FLAT).pack(side=tk.LEFT, padx=6)
        tk.Button(search_frame, text="Tampilkan Semua", command=self.gui_list_all,
                  bg=self.button_accent, fg="#062027", relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

        # List Display Header
        header = tk.Frame(right, bg=self.card)
        header.pack(fill=tk.X, pady=(0,6))

        tk.Label(header, text="Title", bg=self.card, fg=self.fg, width=23, anchor="w", font=("Poppins", 10, "bold")).pack(side=tk.LEFT, padx=8)
        tk.Label(header, text="Genre", bg=self.card, fg=self.fg, width=15, anchor="w", font=("Poppins", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="Platform", bg=self.card, fg=self.fg, width=12, anchor="w", font=("Poppins", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="Year", bg=self.card, fg=self.fg, width=7, anchor="w", font=("Poppins", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="Status", bg=self.card, fg=self.fg, width=10, anchor="w", font=("Poppins", 10, "bold")).pack(side=tk.LEFT)

        # Listbox (GUI) → menampilkan data game
        self.listbox = tk.Listbox(right, font=("Consolas", 10), bg="#0b0b0b", fg=self.accent,
                                  selectbackground="#063a45", selectforeground="#fff", activestyle="none")
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<Double-Button-1>", self.on_double_click)

        tk.Button(right, text="Lihat Recent", command=self.gui_show_recent, bg=self.button_accent,
                  fg="#062027", relief=tk.FLAT).pack(side=tk.LEFT, padx=6, pady=6)
        tk.Button(right, text="Export JSON", command=self.export_json, bg="#2a2a2a",
                  fg=self.fg, relief=tk.FLAT).pack(side=tk.LEFT, padx=6, pady=6)

        self.gui_list_all()

    # Format Row Fixed Width 
    # Modul 4: Method
    def format_row(self, g: Game):
        return (
            f"{g.title[:28].ljust(30)}"
            f"{g.genre[:16].ljust(18)}"
            f"{g.platform[:12].ljust(14)}"
            f"{str(g.year).ljust(8)}"
            f"{g.status[:10].ljust(12)}"
        )

    # GUI FUNCTIONS 
    def clear_form(self):                    # Modul 4
        self.e_title.delete(0, tk.END)
        self.e_genre.delete(0, tk.END)
        self.e_year.delete(0, tk.END)
        self.platform_var.set(PLATFORM_OPTIONS[0])
        self.status_var.set(STATUS_OPTIONS[2])

    def gui_add(self):                       # Modul 4 + GUI Action
        title = self.e_title.get().strip()
        genre = self.e_genre.get().strip()
        platform = self.platform_var.get().strip()
        year = self.e_year.get().strip()
        status = normalize_status(self.status_var.get())

        # Modul 2: Pengkondisian
        if not validate_nonempty(title): return messagebox.showerror("Error", "Title tidak boleh kosong")
        if not validate_nonempty(genre): return messagebox.showerror("Error", "Genre tidak boleh kosong")
        if not validate_nonempty(platform): return messagebox.showerror("Error", "Platform tidak boleh kosong")
        if not validate_year(year): return messagebox.showerror("Error", "Year tidak valid (1970-2050)")

        try:
            self.mgr.add_game(Game(title, genre, platform, int(year), status))
            messagebox.showinfo("Sukses", f"Game '{title}' ditambahkan!")
            self.gui_list_all()
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    # Modul 3: Loop menampilkan list
    def gui_list_all(self):
        self.listbox.delete(0, tk.END)
        for g in self.mgr.list_all():   # LOOP
            self.listbox.insert(tk.END, self.format_row(g))

    def gui_search(self):               # Modul 4
        kw = self.e_search.get().strip()
        results = self.mgr.search_games(kw)
        self.listbox.delete(0, tk.END)
        for g in results:               # LOOP
            self.listbox.insert(tk.END, self.format_row(g))

    def get_selected_title(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.listbox.get(sel[0])[:30].strip()

    def gui_delete(self):               # Modul 4 + GUI
        title = self.get_selected_title()
        if not title: return messagebox.showwarning("Pilih", "Pilih game terlebih dahulu.")
        if messagebox.askyesno("Konfirmasi", f"Hapus game '{title}'?"):  # Modul 2
            try:
                self.mgr.remove_game(title)
                self.gui_list_all()
                messagebox.showinfo("Sukses", "Game dihapus.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def gui_edit(self):
        title = self.get_selected_title()
        if not title: return messagebox.showwarning("Pilih", "Pilih game terlebih dahulu.")

        g = next((x for x in self.mgr.list_all() if x.title.lower() == title.lower()), None)
        if not g: return messagebox.showerror("Error", "Game tidak ditemukan.")

        # GUI Input using dialogs
        new_title = simpledialog.askstring("Edit", "Title:", initialvalue=g.title)
        new_genre = simpledialog.askstring("Edit", "Genre:", initialvalue=g.genre)
        new_platform = simpledialog.askstring("Edit", "Platform:", initialvalue=g.platform)
        new_year = simpledialog.askstring("Edit", "Year:", initialvalue=str(g.year))
        new_status = simpledialog.askstring("Edit", "Status:", initialvalue=g.status)

        if not (new_title and new_genre and new_platform and new_year and new_status):
            return messagebox.showwarning("Batal", "Input tidak lengkap.")

        if not validate_year(new_year):
            return messagebox.showerror("Error", "Year tidak valid.")

        new_game = Game(new_title.strip(), new_genre.strip(),
                        new_platform.strip(), int(new_year),
                        normalize_status(new_status))

        try:
            self.mgr.edit_game(title, new_game)
            self.gui_list_all()
            messagebox.showinfo("Sukses", "Game diedit.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def gui_undo(self):
        try:
            msg = self.mgr.undo()
            self.gui_list_all()
            messagebox.showinfo("Undo", msg)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def on_double_click(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        title = self.listbox.get(sel[0])[:30].strip()
        g = next((x for x in self.mgr.list_all() if x.title.lower() == title.lower()), None)
        if g:
            self.mgr.push_recent(g)   # Modul 6 → Queue
            messagebox.showinfo("Detail Game", str(g))

    def gui_show_recent(self):
        recent = self.mgr.get_recent()
        if not recent:
            return messagebox.showinfo("Recent", "Belum ada recent view.")
        s = "\n".join(str(g) for g in recent)   # Modul 3 Loop
        messagebox.showinfo("Recent Views", s)

    def export_json(self):
        try:
            self.mgr.save()
            messagebox.showinfo("Export", f"Data berhasil diexport ke {self.mgr.filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {e}")


# Main Program dengan Login
# Modul 4 + Modul 8

def main(username=None):
    root = tk.Tk()

    if username:
        app = GameVaultGUI(root, username)
    else:
        app = LoginScreen(root)

    root.mainloop()

if __name__ == "__main__":
    main()