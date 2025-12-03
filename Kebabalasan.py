# =========================================
# Game Store (Tkinter) —
# - Perbaikan gambar: semua PhotoImage disimpan agar tidak hilang (garbage collection)
# =========================================

import tkinter as tk
from PIL import Image, ImageTk
import os, random

# =========================
# Fungsi utilitas
# =========================
def format_rupiah(value: int) -> str:
    """Mengubah angka menjadi format Rupiah dengan spasi ribuan."""
    return f"Rp {value:,}".replace(",", " ")

def font(name="Motiva Sans", size=12, weight="normal", slant="roman"):
    """Membuat font konsisten Motiva Sans untuk seluruh UI."""
    return (name, size, weight, slant)

# =========================
# Model data Game & Cart
# =========================
class Game:
    """Representasi satu item game katalog (key, title, base price, cover path)."""
    def __init__(self, key, title, price, cover):
        self.key = key
        self.title = title
        self.price = price
        self.cover = cover

class Cart:
    """Keranjang belanja menyimpan snapshot game (judul + harga saat ditambahkan)."""
    def __init__(self):
        self.items = {}  # dictionary {GameSnapshot: qty}

    def add(self, game_snapshot):
        self.items[game_snapshot] = self.items.get(game_snapshot, 0) + 1

    def remove(self, game_snapshot):
        if game_snapshot in self.items:
            self.items[game_snapshot] -= 1
            if self.items[game_snapshot] <= 0:
                del self.items[game_snapshot]

    def clear(self):
        self.items.clear()

    def unique_count(self):
        return len(self.items)

    def total_count(self):
        return sum(self.items.values())

    def total(self):
        """Total dengan contoh diskon keranjang: -20% jika >= 3 game unik."""
        subtotal = sum(g.price * qty for g, qty in self.items.items())
        if self.unique_count() >= 3:
            subtotal *= 0.8
        return int(max(0, subtotal))

    def summary_lines(self):
        """Ringkas setiap item: (title, qty, subtotal, cover)."""
        return [(g.title, qty, g.price * qty, g.cover) for g, qty in self.items.items()]

    def qty_by_title(self, title):
        return sum(qty for g, qty in self.items.items() if g.title == title)

# =========================
# Dialog berwarna (custom)
# =========================
def show_colored_dialog(root, title, message, bg="#1b1b2e", fg_title="#FFD700", fg_msg="white"):
    """Menampilkan dialog custom berwarna yang lebih menarik daripada messagebox polos."""
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("560x300")
    win.configure(bg=bg)
    win.grab_set()

    tk.Label(win, text=title, font=font(size=18, weight="bold"),
             bg=bg, fg=fg_title).pack(pady=14)
    tk.Label(win, text=message, font=font(size=12),
             bg=bg, fg=fg_msg, wraplength=500, justify="center").pack(pady=10)

    tk.Button(win, text="Tutup", command=win.destroy,
              bg="#ff6347", fg="white", font=font(size=12, weight="bold"), width=12).pack(pady=18)

# =========================
# Aplikasi Store
# =========================
class StoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Store")
        self.root.geometry("1200x800")

        # State awal
        self.balance = 500000
        self.cart = Cart()
        self.spin_used = False       # flag spin sudah dimainkan pada transaksi
        self.last_spin_count = 0     # jumlah spin dari transaksi terakhir

        # Harga katalog (asli & aktif), serta banner voucher dari spin
        self.base_price = {}         # {Game: int} harga asli katalog
        self.active_price = {}       # {Game: int} harga aktif (bisa berubah karena daily deal)
        self.next_discount_percent = 0  # voucher diskon dari spin, berlaku ke harga aktif sampai checkout berikutnya
        self.voucher_banner_var = tk.StringVar(value="")

        # Map untuk area label harga per game di katalog
        self.price_area = {}         # {Game: dict} berisi widget label harga asli & diskon

        # Penyimpanan image agar tidak hilang (PhotoImage harus punya referensi)
        self._images = []            # list menyimpan semua ImageTk.PhotoImage
        self._detail_images = []     # list image khusus halaman detail
        self._cart_images = []       # list image khusus halaman cart
        self._receipt_images = []    # list image khusus struk

        # Folder gambar
        base_dir = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
        self.img_dir = os.path.join(base_dir, "images")

        # Daftar game katalog (mengembalikan God of War dan Persona 5 Royal)
        self.games = [
            Game("elden", "Elden Ring", 750000, os.path.join(self.img_dir, "elden.png")),
            Game("mc", "Minecraft", 300000, os.path.join(self.img_dir, "minecraft.png")),
            Game("exp33", "Clair Obscur: Expedition 33", 500000, os.path.join(self.img_dir, "ekspedisi.png")),
            Game("silk", "Hollow Knight: Silksong", 450000, os.path.join(self.img_dir, "silksong.png")),
            Game("gow", "God of War", 600000, os.path.join(self.img_dir, "godwar.png")),
            Game("p5r", "Persona 5 Royal", 550000, os.path.join(self.img_dir, "persona.png")),
        ]
        for g in self.games:
            self.base_price[g] = g.price
            self.active_price[g] = g.price

        # Konten detail game (deskripsi, konten dewasa, spesifikasi, trailer)
        self.details = self._build_details()

        # =========================
        # Siapkan tiga menu (frame): Store, Keranjang, Detail
        # =========================
        self.store_frame = tk.Frame(root, bg="#1e1e2f")
        self.cart_frame = tk.Frame(root, bg="#2f2f4f")
        self.detail_frame = tk.Frame(root, bg="#1b1b2e")

        # Bangun masing-masing UI
        self.build_store()
        self.build_cart()
        self.build_detail_base()  # detail diisi dinamis saat dipanggil

        # Tampilkan store sebagai awal
        self.show_store()

        # Daily deal muncul setelah jeda
        self.root.after(1200, self.daily_deal_popup)

    # =========================
    # Bangun UI Store (katalog)
    # =========================
    def build_store(self):
        # Header
        header = tk.Frame(self.store_frame, bg="#1e1e2f")
        header.pack(fill="x")
        tk.Label(header, text="🎮 Game Store", font=font(size=28, weight="bold"),
                 bg="#1e1e2f", fg="#ffd700").pack(side="left", padx=22, pady=18)
        # Ikon Keranjang
        tk.Button(header, text="🛒 Keranjang", command=self.show_cart,
                  bg="#ffd700", fg="black", font=font(size=12, weight="bold")).pack(side="right", padx=12, pady=12)
        # Saldo
        saldo_frame = tk.Frame(header, bg="#228B22", padx=8, pady=4)
        saldo_frame.pack(side="right", padx=10, pady=8)
        tk.Label(saldo_frame, text="💰", font=font(size=12, weight="bold"),
                 bg="#228B22", fg="white").pack(side="left")
        self.label_balance_store = tk.Label(saldo_frame, text=format_rupiah(self.balance),
                                            font=font(size=12, weight="bold"), bg="#32CD32", fg="black")
        self.label_balance_store.pack(side="left", padx=6)

        # Banner voucher dari spin
        banner = tk.Label(self.store_frame, textvariable=self.voucher_banner_var,
                          font=font(size=12, weight="bold"), bg="#1e1e2f", fg="#32cd32")
        banner.pack(fill="x")

        # Katalog: Canvas agar responsif & scroll
        self.catalog_canvas = tk.Canvas(self.store_frame, bg="#1e1e2f", highlightthickness=0)
        catalog_scrollbar = tk.Scrollbar(self.store_frame, orient="vertical", command=self.catalog_canvas.yview)
        self.catalog_inner = tk.Frame(self.catalog_canvas, bg="#1e1e2f")

        self.catalog_window = self.catalog_canvas.create_window((0,0), window=self.catalog_inner, anchor="nw")
        self.catalog_canvas.bind("<Configure>", lambda e: self.catalog_canvas.itemconfig(self.catalog_window, width=e.width))
        self.catalog_inner.bind("<Configure>", lambda e: self.catalog_canvas.configure(scrollregion=self.catalog_canvas.bbox("all")))

        self.catalog_canvas.configure(yscrollcommand=catalog_scrollbar.set)
        self.catalog_canvas.pack(side="left", fill="both", expand=True)
        catalog_scrollbar.pack(side="right", fill="y")
        self.catalog_canvas.bind_all("<MouseWheel>", self._on_catalog_mousewheel)

        # Grid 3 kolom responsif
        for col in range(3):
            self.catalog_inner.grid_columnconfigure(col, weight=1)

        # Kartu game
        for i, g in enumerate(self.games):
            self.create_game_card(self.catalog_inner, g, i)

    def _on_catalog_mousewheel(self, event):
        self.catalog_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _load_image(self, path, size):
        """Helper aman untuk muat gambar + simpan referensi, agar tidak hilang."""
        img = Image.open(path)
        img = img.convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self._images.append(photo)
        return photo

    def create_game_card(self, parent, game, index):
        """Kartu game menarik, ikon kecil 3 kolom, klik gambar ke menu detail, harga dengan coret jika diskon."""
        card = tk.Frame(parent, bg="#252542", bd=0, relief="flat")
        card.grid(row=index//3, column=index%3, padx=12, pady=16, sticky="nsew")

        container = tk.Frame(card, bg="#2f2f4f", bd=2, relief="ridge")
        container.pack(fill="both", expand=True)

        # Gambar cover kecil (klik untuk detail)
        if os.path.exists(game.cover):
            try:
                photo = self._load_image(game.cover, (210, 130))
                img_box = tk.Label(container, image=photo, bg="#2f2f4f", cursor="hand2")
                img_box.image = photo
                img_box.pack(pady=10)
                img_box.bind("<Button-1>", lambda e, g=game: self.show_detail(g))
            except Exception as e:
                ph = tk.Label(container, text=f"[Gambar gagal: {e}]", bg="#2f2f4f", fg="red", font=font(size=12))
                ph.pack(pady=10)
                ph.bind("<Button-1>", lambda e, g=game: self.show_detail(g))
        else:
            ph = tk.Label(container, text="[Gambar tidak ditemukan]", bg="#2f2f4f", fg="red", font=font(size=12))
            ph.pack(pady=10)
            ph.bind("<Button-1>", lambda e, g=game: self.show_detail(g))

        # Judul
        tk.Label(container, text=game.title, font=font(size=14, weight="bold"),
                 bg="#2f2f4f", fg="white").pack(pady=4)

        # Area harga
        price_area = {"label_asli": tk.Label(container, bg="#2f2f4f"),
                      "label_diskon": tk.Label(container, bg="#2f2f4f")}
        price_area["label_asli"].pack()
        price_area["label_diskon"].pack()
        self.price_area[game] = price_area
        self._render_price_labels(game, price_area)

        # Tombol tambah ke keranjang
        tk.Button(container, text="Tambah ke Keranjang",
                  command=lambda g=game: self.add_to_cart(g),
                  bg="#1e90ff", fg="white", font=font(size=12, weight="bold"), width=22).pack(pady=12)

    def _render_price_labels(self, game, area):
        """Render harga: jika diskon tampilkan harga asli dicoret + harga aktif/voucher."""
        harga_asli = self.base_price[game]
        harga_aktif = self.active_price[game]
        harga_efektif = self.effective_price(game)

        if harga_aktif < harga_asli:
            area["label_asli"].config(
                text=f"{format_rupiah(harga_asli)}",
                font=(font()[0], 12, "overstrike", "bold"), fg="#ff6347", bg="#2f2f4f"
            )
            if harga_efektif < harga_aktif:
                area["label_diskon"].config(
                    text=f"Harga Diskon: {format_rupiah(harga_efektif)} (voucher {self.next_discount_percent}%)",
                    font=font(size=13, weight="bold"), fg="#FFD700", bg="#2f2f4f"
                )
            else:
                area["label_diskon"].config(
                    text=f"Harga Diskon: {format_rupiah(harga_aktif)}",
                    font=font(size=13, weight="bold"), fg="#FFD700", bg="#2f2f4f"
                )
        else:
            area["label_asli"].config(text="", bg="#2f2f4f")
            if self.next_discount_percent > 0 and harga_efektif < harga_asli:
                area["label_asli"].config(
                    text=f"{format_rupiah(harga_asli)}",
                    font=(font()[0], 12, "overstrike", "bold"), fg="#ff6347", bg="#2f2f4f"
                )
                area["label_diskon"].config(
                    text=f"Harga Diskon: {format_rupiah(harga_efektif)} (voucher {self.next_discount_percent}%)",
                    font=font(size=13, weight="bold"), fg="#FFD700", bg="#2f2f4f"
                )
            else:
                area["label_diskon"].config(
                    text=f"Harga: {format_rupiah(harga_asli)}",
                    font=font(size=13, weight="bold"), fg="#FFD700", bg="#2f2f4f"
                )

    def effective_price(self, game):
        """Harga aktif dikurangi voucher spin jika ada."""
        price = self.active_price[game]
        if self.next_discount_percent > 0:
            price = int(price * (1 - self.next_discount_percent / 100))
        return max(0, price)

    def update_catalog_prices(self):
        """Update semua kartu harga dan banner voucher."""
        if self.next_discount_percent > 0:
            self.voucher_banner_var.set(
                f"🎟️ Voucher Diskon {self.next_discount_percent}% aktif. Berlaku hingga checkout berikutnya."
            )
        else:
            self.voucher_banner_var.set("")
        for g, area in self.price_area.items():
            self._render_price_labels(g, area)

    # =========================
    # Build & logic Keranjang
    # =========================
    def build_cart(self):
        cart_header = tk.Frame(self.cart_frame, bg="#2f2f4f")
        cart_header.pack(fill="x")
        tk.Label(cart_header, text="🛒 Keranjang Belanja",
                 font=font(size=18, weight="bold"), bg="#2f2f4f", fg="white").pack(side="left", padx=22, pady=10)
        tk.Button(cart_header, text="⬅️ Back", command=self.show_store,
                  bg="#1e90ff", fg="white", font=font(size=12, weight="bold")).pack(side="right", padx=10, pady=10)

        saldo_cart_frame = tk.Frame(cart_header, bg="#006400", padx=8, pady=4)
        saldo_cart_frame.pack(side="right", padx=10, pady=10)
        tk.Label(saldo_cart_frame, text="💰", font=font(size=12, weight="bold"),
                 bg="#006400", fg="white").pack(side="left")
        self.label_balance_cart = tk.Label(saldo_cart_frame, text=format_rupiah(self.balance),
                                           font=font(size=12, weight="bold"), bg="#32CD32", fg="black")
        self.label_balance_cart.pack(side="left", padx=6)

        # Gift bar
        gift_bar = tk.Frame(self.cart_frame, bg="#2f2f4f")
        gift_bar.pack(fill="x", padx=16, pady=6)
        self.is_gift = tk.BooleanVar(value=False)
        self.recipient_var = tk.StringVar(value="Akun saya")
        tk.Checkbutton(gift_bar, text="Beli sebagai gift", variable=self.is_gift,
                       font=font(size=12), bg="#2f2f4f", fg="white", activebackground="#2f2f4f",
                       selectcolor="#2f2f4f").pack(side="left")
        tk.Label(gift_bar, text="Penerima:", font=font(size=12),
                 bg="#2f2f4f", fg="#ffd700").pack(side="left", padx=10)
        self.entry_recipient = tk.Entry(gift_bar, textvariable=self.recipient_var, font=font(size=12), width=24)
        self.entry_recipient.pack(side="left")

        # Isi keranjang
        self.cart_inner = tk.Frame(self.cart_frame, bg="#3f3f5f")
        self.cart_inner.pack(fill="x", padx=12, pady=8)

        self.label_total = tk.Label(self.cart_frame, text=f"Total: {format_rupiah(0)}",
                                    font=font(size=16, weight="bold"), bg="#2f2f4f", fg="#ffd700")
        self.label_total.pack(pady=6)
        tk.Button(self.cart_frame, text="Checkout", command=self.checkout,
                  bg="#32cd32", fg="white", font=font(size=12, weight="bold")).pack(pady=10)

    def refresh_cart(self):
        """Render ulang isi keranjang dengan kartu kecil, tombol + dan −."""
        for w in self.cart_inner.winfo_children():
            w.destroy()
        self._cart_images.clear()

        if not self.cart.items:
            empty = tk.Frame(self.cart_inner, bg="#3f3f5f")
            empty.pack(fill="x", padx=12, pady=12)
            tk.Label(empty, text="Keranjang kosong. Tambahkan game dari katalog.",
                     font=font(size=12, weight="bold"), bg="#3f3f5f", fg="#ffcc00").pack(pady=8)
            return

        row = tk.Frame(self.cart_inner, bg="#3f3f5f")
        row.pack(fill="x")
        for game, qty in self.cart.items.items():
            card = tk.Frame(row, bg="#4f4f6f", bd=2, relief="ridge", width=360, height=240)
            card.pack(side="left", padx=10, pady=10)
            card.pack_propagate(False)

            left = tk.Frame(card, bg="#4f4f6f"); left.pack(side="left", padx=12, pady=12)
            if os.path.exists(game.cover):
                try:
                    photo = self._load_image(game.cover, (160, 110))
                    self._cart_images.append(photo)
                    lbl = tk.Label(left, image=photo, bg="#4f4f6f")
                    lbl.image = photo; lbl.pack()
                except:
                    tk.Label(left, text="[Img Err]", bg="#4f4f6f", fg="red",
                             font=font(size=12, weight="bold")).pack()
            else:
                tk.Label(left, text="[Img Missing]", bg="#4f4f6f", fg="red",
                         font=font(size=12, weight="bold")).pack()

            mid = tk.Frame(card, bg="#4f4f6f"); mid.pack(side="left", padx=10, pady=10)
            tk.Label(mid, text=game.title, font=font(size=12, weight="bold"),
                     bg="#4f4f6f", fg="white").pack(anchor="w")
            tk.Label(mid, text=f"{format_rupiah(game.price)} x{qty}", font=font(size=11, weight="bold"),
                     bg="#4f4f6f", fg="#FFD700").pack(anchor="w")

            right = tk.Frame(card, bg="#4f4f6f"); right.pack(side="right", padx=10, pady=10)
            tk.Button(right, text="+", command=lambda g=game: self._inc(g),
                      bg="#32cd32", fg="white", font=font(size=11, weight="bold"), width=4).pack(pady=6)
            tk.Button(right, text="-", command=lambda g=game: self._dec(g),
                      bg="#ff6347", fg="white", font=font(size=11, weight="bold"), width=4).pack(pady=6)

        self.update_total()

    def _inc(self, game):
        self.cart.add(game)
        self.refresh_cart()

    def _dec(self, game):
        self.cart.remove(game)
        self.refresh_cart()

    def update_total(self):
        total = self.cart.total()
        label = f"Total: {format_rupiah(total)}"
        if self.cart.unique_count() >= 3:
            label = f"Total (Diskon 20%): {format_rupiah(total)}"
        self.label_total.config(text=label)
        self.label_balance_store.config(text=format_rupiah(self.balance))
        self.label_balance_cart.config(text=format_rupiah(self.balance))

    # =========================
    # Build & logic Detail Game (menu)
    # =========================
    def build_detail_base(self):
        """Menyiapkan struktur dasar detail frame (konten diisi saat show_detail)."""
        # Header (judul dinamis)
        self.detail_header = tk.Frame(self.detail_frame, bg="#1b1b2e")
        self.detail_header.pack(fill="x")
        self.detail_title_lbl = tk.Label(self.detail_header, text="",
                                         font=font(size=22, weight="bold"),
                                         bg="#1b1b2e", fg="#FFD700")
        self.detail_title_lbl.pack(side="left", padx=22, pady=12)
        tk.Button(self.detail_header, text="⬅️ Back", command=self.show_store,
                  bg="#1e90ff", fg="white", font=font(size=12, weight="bold")).pack(side="right", padx=10, pady=10)

        # Kontainer konten detail
        self.detail_content_holder = tk.Frame(self.detail_frame, bg="#1b1b2e")
        self.detail_content_holder.pack(fill="both", expand=True)

    def show_detail(self, game):
        """Masuk ke menu detail game (isi ulang seluruh konten)."""
        self.cart_frame.pack_forget()
        self.store_frame.pack_forget()
        self.detail_frame.pack(fill="both", expand=True)

        # Set judul
        self.detail_title_lbl.config(text=game.title)

        # Bersihkan konten lama & cache image detail
        for w in self.detail_content_holder.winfo_children():
            w.destroy()
        self._detail_images.clear()

        meta = self.details.get(game.key)
        if not meta:
            tk.Label(self.detail_content_holder, text="Detail belum tersedia.",
                     font=font(size=12, weight="bold"), bg="#1b1b2e", fg="#ffcc00").pack(pady=16)
            return

        # Gambar besar
        img_frame = tk.Frame(self.detail_content_holder, bg="#1b1b2e")
        img_frame.pack()
        if os.path.exists(game.cover):
            try:
                photo = self._load_image(game.cover, (520, 320))
                self._detail_images.append(photo)
                lbl = tk.Label(img_frame, image=photo, bg="#1b1b2e")
                lbl.image = photo
                lbl.pack(pady=4)
            except:
                tk.Label(img_frame, text="[Gambar gagal dimuat]", font=font(size=12, weight="bold"),
                         bg="#1b1b2e", fg="#ff6b6b").pack()
        else:
            tk.Label(img_frame, text="[Gambar tidak ditemukan]", font=font(size=12, weight="bold"),
                     bg="#1b1b2e", fg="#ff6b6b").pack()

        # Tombol Trailer
        btns = tk.Frame(self.detail_content_holder, bg="#1b1b2e")
        btns.pack(pady=8)
        tk.Button(btns, text="▶ Putar Trailer", command=lambda: self.play_trailer(meta["trailer"]),
                  bg="#8a2be2", fg="white", font=font(size=12, weight="bold")).pack()

        # Area teks detail (scroll)
        canvas = tk.Canvas(self.detail_content_holder, bg="#23233a", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.detail_content_holder, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#23233a")
        canvas.create_window((0,0), window=inner, anchor="nw", width=1100)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        scrollbar.pack(side="right", fill="y")

        # Bagian deskripsi
        block = tk.Frame(inner, bg="#23233a")
        block.pack(fill="x", padx=10, pady=8)
        tk.Label(block, text="Deskripsi", font=font(size=16, weight="bold"),
                 bg="#23233a", fg="#FFD700").pack(anchor="w")
        tk.Label(block, text=meta["desc"], font=font(size=12),
                 bg="#23233a", fg="white", wraplength=1060, justify="left").pack(anchor="w", pady=4)

        # Bagian konten dewasa
        block2 = tk.Frame(inner, bg="#23233a")
        block2.pack(fill="x", padx=10, pady=8)
        tk.Label(block2, text="Deskripsi Konten Dewasa", font=font(size=16, weight="bold"),
                 bg="#23233a", fg="#ff6b6b").pack(anchor="w")
        tk.Label(block2, text=meta["adult"], font=font(size=12),
                 bg="#23233a", fg="#ffd7d7", wraplength=1060, justify="left").pack(anchor="w", pady=4)

        # Spesifikasi
        block3 = tk.Frame(inner, bg="#23233a")
        block3.pack(fill="x", padx=10, pady=8)
        tk.Label(block3, text="Persyaratan Sistem", font=font(size=16, weight="bold"),
                 bg="#23233a", fg="#32cd32").pack(anchor="w")
        tk.Label(block3, text=meta["spec"], font=font(size=12),
                 bg="#23233a", fg="white", justify="left").pack(anchor="w", pady=4)

        # Developer/Publisher (opsional jika tersedia)
        devpub = meta.get("devpub")
        if devpub:
            block4 = tk.Frame(inner, bg="#23233a")
            block4.pack(fill="x", padx=10, pady=8)
            tk.Label(block4, text=devpub, font=font(size=12, weight="bold"),
                     bg="#23233a", fg="#a0ffea").pack(anchor="w")

    def play_trailer(self, path):
        """Memutar trailer via pemutar default Windows (os.startfile)."""
        if os.path.exists(path):
            try:
                os.startfile(path)  # Buka trailer dengan aplikasi default (Windows)
            except Exception as e:
                show_colored_dialog(self.root, "Gagal Memutar Trailer",
                                    f"Trailer tidak dapat diputar.\n{e}",
                                    bg="#3b1f24", fg_title="#ff6b6b", fg_msg="#ffd7d7")
        else:
            show_colored_dialog(self.root, "Trailer Tidak Ditemukan",
                f"File trailer tidak ditemukan:\n{path}",
                bg="#2b2b44", fg_title="#ffcc00", fg_msg="white")

    # =========================
    # Interaksi Store <-> Cart, Cart logic, Checkout, Struk, Spin
    # =========================
    def show_store(self):
        """Tampilkan menu store."""
        self.cart_frame.pack_forget()
        self.detail_frame.pack_forget()
        self.store_frame.pack(fill="both", expand=True)

    def show_cart(self):
        """Tampilkan menu keranjang dan refresh isinya."""
        self.store_frame.pack_forget()
        self.detail_frame.pack_forget()
        self.cart_frame.pack(fill="both", expand=True)
        self.refresh_cart()

    def add_to_cart(self, game):
        """Tambah snapshot game ke keranjang menggunakan harga efektif saat ini."""
        current_price = self.effective_price(game)
        g_snapshot = Game(game.key, game.title, current_price, game.cover)
        self.cart.add(g_snapshot)
        show_colored_dialog(self.root, "Ditambahkan",
                            f"{game.title} ditambahkan ke keranjang.\nHarga: {format_rupiah(current_price)}",
                            bg="#223b2b", fg_title="#a9ffaf", fg_msg="#dfffe2")
        if self.cart_frame.winfo_ismapped():
            self.refresh_cart()

    def update_total(self):
        total = self.cart.total()
        label = f"Total: {format_rupiah(total)}"
        if self.cart.unique_count() >= 3:
            label = f"Total (Diskon 20%): {format_rupiah(total)}"
        self.label_total.config(text=label)
        self.label_balance_store.config(text=format_rupiah(self.balance))
        self.label_balance_cart.config(text=format_rupiah(self.balance))

    def _inc(self, game):
        self.cart.add(game)
        self.refresh_cart()

    def _dec(self, game):
        self.cart.remove(game)
        self.refresh_cart()

    def checkout(self):
        """Proses checkout: validasi saldo, konfirmasi, bayar, struk, spin, kosongkan keranjang."""
        if not self.cart.items:
            # Dialog berwarna untuk keranjang kosong
            show_colored_dialog(self.root, "Keranjang Kosong",
                                "Belum ada game di keranjang. Tambahkan game dari katalog.",
                                bg="#2b2b44", fg_title="#ffcc00", fg_msg="white")
            return

        total_pay = self.cart.total()
        if self.balance < total_pay:
            # Dialog berwarna untuk saldo tidak cukup
            show_colored_dialog(self.root, "Saldo Tidak Cukup",
                                f"Total belanja {format_rupiah(total_pay)} melebihi saldo {format_rupiah(self.balance)}.",
                                bg="#3b1f24", fg_title="#ff6b6b", fg_msg="#ffd7d7")
            return

        penerima_text = f"Gift untuk {self.recipient_var.get()}" if self.is_gift.get() else "Akun saya"
        if not self.confirm_checkout_ui(total_pay, penerima_text):
            return

        # Bayar
        self.balance -= total_pay
        self.update_total()

        # Spin: jumlah dibatasi sesuai unit game di keranjang
        spin_count = self.cart.total_count()
        self.spin_used = False
        self.last_spin_count = spin_count  # simpan agar spin tidak tak terbatas

        # Simpan ringkasan untuk struk, lalu kosongkan keranjang otomatis
        purchased_summary = self.cart.summary_lines()
        self.cart.clear()
        self.refresh_cart()

        # Tampilkan struk bergambar + tombol spin
        self.show_receipt(purchased_summary, spin_count)

    def confirm_checkout_ui(self, total_pay, penerima_text):
        """Konfirmasi bayar dengan dialog berwarna (custom)."""
        win = tk.Toplevel(self.root)
        win.title("Konfirmasi Pembelian")
        win.geometry("560x480")
        win.configure(bg="#1b1b2e")
        win.grab_set()

        tk.Label(win, text="Apakah Anda yakin membeli?", font=font(size=20, weight="bold"),
                 bg="#1b1b2e", fg="#FFD700").pack(pady=16)

        box = tk.Frame(win, bg="#2a2a46", bd=2, relief="ridge")
        box.pack(fill="x", padx=20, pady=12)

        tk.Label(box, text=f"Total yang akan dibayar: {format_rupiah(total_pay)}",
                 font=font(size=14, weight="bold"), bg="#2a2a46", fg="#32cd32").pack(pady=8)
        tk.Label(box, text=f"Penerima: {penerima_text}",
                 font=font(size=12), bg="#2a2a46", fg="white").pack(pady=4)
        tk.Label(box, text="Pastikan keranjang sesuai sebelum melanjutkan.",
                 font=font(size=11), bg="#2a2a46", fg="#a0a0c0").pack(pady=6)

        actions = tk.Frame(win, bg="#1b1b2e"); actions.pack(pady=18)
        ok_btn = tk.Button(actions, text="Ya, Lanjutkan Pembelian ✅",
                           bg="#32cd32", fg="white", font=font(size=12, weight="bold"), width=24,
                           command=lambda: [setattr(win, "confirmed", True), win.destroy()])
        ok_btn.pack(side="left", padx=10)
        cancel_btn = tk.Button(actions, text="Batalkan ❌",
                               bg="#ff6347", fg="white", font=font(size=12, weight="bold"), width=16,
                               command=lambda: [setattr(win, "confirmed", False), win.destroy()])
        cancel_btn.pack(side="left", padx=10)

        win.confirmed = False
        self.root.wait_window(win)
        return win.confirmed

    def show_receipt(self, purchased_summary, spin_count):
        """Struk bergambar + akses Lucky Spin."""
        win = tk.Toplevel(self.root)
        win.title("Struk Pembelian")
        win.geometry("900x800")
        win.configure(bg="#1e1e2f")

        tk.Label(win, text="✅ Pembelian Berhasil", font=font(size=22, weight="bold"),
                 fg="#32cd32", bg="#1e1e2f").pack(pady=10)
        penerima_text = f"Gift untuk {self.recipient_var.get()}" if self.is_gift.get() else "Akun saya"
        tk.Label(win, text=f"Penerima: {penerima_text}",
                 font=font(size=12, weight="bold"), fg="white", bg="#1e1e2f").pack()

        total_pay = sum(p for _, _, p, _ in purchased_summary)
        tk.Label(win, text=f"Total Dibayar: {format_rupiah(total_pay)}",
                 font=font(size=14, weight="bold"), fg="#FFD700", bg="#1e1e2f").pack(pady=6)
        tk.Label(win, text=f"Sisa Saldo: {format_rupiah(self.balance)}",
                 font=font(size=14, weight="bold"), fg="#1e90ff", bg="#1e1e2f").pack(pady=2)

        list_canvas = tk.Canvas(win, bg="#23233a", height=420, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=list_canvas.yview)
        inner = tk.Frame(list_canvas, bg="#23233a")
        inner.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0, 0), window=inner, anchor="nw", width=860)
        list_canvas.configure(yscrollcommand=scrollbar.set)
        list_canvas.pack(side="left", fill="both", expand=True, padx=16, pady=10)
        scrollbar.pack(side="right", fill="y")

        self._receipt_images.clear()
        for title, qty, subtotal, cover in purchased_summary:
            row = tk.Frame(inner, bg="#2e2e4a", bd=2, relief="ridge")
            row.pack(fill="x", padx=8, pady=8)
            if os.path.exists(cover):
                try:
                    photo = self._load_image(cover, (150, 100))
                    self._receipt_images.append(photo)
                    img_lbl = tk.Label(row, image=photo, bg="#2e2e4a")
                    img_lbl.image = photo
                    img_lbl.pack(side="left", padx=12, pady=10)
                except:
                    tk.Label(row, text="[IMG Err]", font=font(size=12, weight="bold"),
                             bg="#2e2e4a", fg="red").pack(side="left", padx=12, pady=10)
            else:
                tk.Label(row, text="[IMG Missing]", font=font(size=12, weight="bold"),
                         bg="#2e2e4a", fg="red").pack(side="left", padx=12, pady=10)

            info = tk.Frame(row, bg="#2e2e4a")
            info.pack(side="left", padx=10, pady=10)
            tk.Label(info, text=title, font=font(size=12, weight="bold"),
                     bg="#2e2e4a", fg="white").pack(anchor="w")
            tk.Label(info, text=f"Jumlah: {qty}", font=font(size=12),
                     bg="#2e2e4a", fg="#1e90ff").pack(anchor="w")
            tk.Label(info, text=f"Subtotal: {format_rupiah(subtotal)}", font=font(size=12, weight="bold"),
                     bg="#2e2e4a", fg="#FFD700").pack(anchor="w")

        tk.Label(win, text=f"🎲 Kamu mendapatkan {spin_count} spin",
                 font=font(size=14, weight="bold"), fg="#1e90ff", bg="#1e1e2f").pack(pady=12)
        spin_btn = tk.Button(win, text="Mainkan Lucky Spin",
                             bg="#8a2be2", fg="white", font=font(size=12, weight="bold"),
                             command=lambda: self.open_simple_spin(win, spin_btn))
        spin_btn.pack()

        action_bar = tk.Frame(win, bg="#1e1e2f")
        action_bar.pack(pady=16)
        tk.Button(action_bar, text="Tutup", command=win.destroy,
                  bg="#ff6347", fg="white", font=font(size=12, weight="bold"), width=14).pack(side="left", padx=8)
        tk.Button(action_bar, text="Kembali ke Toko", command=lambda: [win.destroy(), self.show_store()],
                  bg="#32cd32", fg="white", font=font(size=12, weight="bold"), width=16).pack(side="left", padx=8)

    # =========================
    # Lucky Spin sederhana (hadiah langsung diterapkan & dibatasi jumlah)
    # =========================
    def open_simple_spin(self, parent, spin_btn):
        """Spin hanya sekali per transaksi dan jumlah spin terbatas sesuai pembelian (last_spin_count)."""
        if self.spin_used:
            show_colored_dialog(self.root, "Spin Selesai",
                                "Spin sudah digunakan untuk transaksi ini.",
                                bg="#2b2b44", fg_title="#ffcc00", fg_msg="white")
            return
        if self.last_spin_count <= 0:
            show_colored_dialog(self.root, "Spin Tidak Tersedia",
                                "Tidak ada spin yang tersedia untuk transaksi ini.",
                                bg="#2b2b44", fg_title="#ffcc00", fg_msg="white")
            return

        self.spin_used = True
        spin_btn.config(state="disabled", text="Spin sudah dimainkan")

        spin_win = tk.Toplevel(parent)
        spin_win.title("🎲 Lucky Spin")
        spin_win.geometry("560x460")
        spin_win.configure(bg="#14142a")
        spin_win.grab_set()

        tk.Label(spin_win, text="Lucky Spin", font=font(size=20, weight="bold"),
                 fg="#FFD700", bg="#14142a").pack(pady=12)
        tk.Label(spin_win, text=f"Jumlah spin: {self.last_spin_count}",
                 font=font(size=12, weight="bold"), fg="#32cd32", bg="#14142a").pack(pady=4)

        result_box = tk.Text(spin_win, height=12, width=62, bg="#1e1e3b", fg="white", font=font(size=11))
        result_box.pack(pady=10)
        result_box.insert("end", "Hasil spin akan muncul di sini...\n")

        rewards = [
            "Saldo Rp 100 000",
            "Voucher Diskon 10%",
            "Bonus Sticker 🎮",
            "Tidak ada hadiah 😅",
        ]

        def apply_reward(reward):
            """Terapkan hadiah: saldo langsung masuk, voucher diskon aktif untuk katalog hingga checkout berikutnya."""
            if reward.startswith("Saldo"):
                self.balance += 100000
                self.update_total()
                result_box.insert("end", "- Saldo bertambah Rp 100 000 dan langsung masuk.\n")
            elif "Voucher Diskon" in reward:
                self.next_discount_percent = 10
                self.update_catalog_prices()
                result_box.insert("end", "- Voucher diskon 10% aktif untuk katalog hingga checkout berikutnya.\n")
            elif "Bonus Sticker" in reward:
                result_box.insert("end", "- Kamu mendapat Bonus Sticker 🎮.\n")
            else:
                result_box.insert("end", "- Tidak ada hadiah kali ini.\n")

        def run_spins(count):
            for _ in range(count):
                reward = random.choice(rewards)
                result_box.insert("end", f"{reward}\n")
                apply_reward(reward)
                result_box.see("end")
            tk.Button(spin_win, text="Tutup", command=spin_win.destroy,
                      bg="#ff6347", fg="white", font=font(size=12, weight="bold")).pack(pady=10)

        tk.Button(spin_win, text="Mulai Spin", command=lambda: run_spins(self.last_spin_count),
                  bg="#8a2be2", fg="white", font=font(size=12, weight="bold")).pack(pady=10)

    # =========================
    # Daily deal informatif (harga dari–menjadi dan persen)
    # =========================
    def daily_deal_popup(self):
        rekom = random.choice(self.games)

        deal_win = tk.Toplevel(self.root)
        deal_win.title("🔥 Daily Deal!")
        deal_win.geometry("640x720")
        deal_win.configure(bg="#1e1e2f")
        deal_win.grab_set()

        tk.Label(deal_win, text="🔥 Game of the Day 🔥", font=font(size=24, weight="bold"),
                 fg="#FFD700", bg="#1e1e2f").pack(pady=20)

        if os.path.exists(rekom.cover):
            try:
                photo = self._load_image(rekom.cover, (400, 250))
                lbl_img = tk.Label(deal_win, image=photo, bg="#1e1e2f")
                lbl_img.image = photo
                lbl_img.pack(pady=12)
            except:
                tk.Label(deal_win, text="[Gambar gagal dimuat]", bg="#1e1e2f", fg="red",
                         font=font(size=12)).pack(pady=12)
        else:
            tk.Label(deal_win, text="[Gambar tidak ditemukan]", bg="#1e1e2f", fg="red",
                     font=font(size=12)).pack(pady=12)

        tk.Label(deal_win, text=rekom.title, font=font(size=18, weight="bold"),
                 fg="white", bg="#1e1e2f").pack(pady=5)

        harga_asli = self.base_price[rekom]
        potongan = random.choice([50000, 100000, 150000])  # variasi potongan untuk demo
        harga_baru = max(0, harga_asli - potongan)
        persen = int(round((potongan / harga_asli) * 100)) if harga_asli > 0 else 0

        tk.Label(deal_win, text=f"Harga asli: {format_rupiah(harga_asli)}",
                 font=font(size=14), fg="#ff6347", bg="#1e1e2f").pack()
        tk.Label(deal_win, text=f"Menjadi: {format_rupiah(harga_baru)}",
                 font=font(size=16, weight="bold"), fg="#32cd32", bg="#1e1e2f").pack(pady=4)
        tk.Label(deal_win, text=f"Diskon: {format_rupiah(potongan)} ({persen}%)",
                 font=font(size=13, weight="bold"), fg="#FFD700", bg="#1e1e2f").pack(pady=6)

        tk.Label(deal_win, text="Tekan 'Terapkan Diskon' untuk mengaktifkan harga di katalog.",
                 font=font(size=11), fg="white", bg="#1e1e2f").pack(pady=10)

        btns = tk.Frame(deal_win, bg="#1e1e2f"); btns.pack(pady=20)

        def apply_discount():
            """Terapkan diskon ke harga aktif katalog untuk game rekomendasi."""
            self.active_price[rekom] = harga_baru
            self.update_catalog_prices()
            deal_win.destroy()

        tk.Button(btns, text="Terapkan Diskon", command=apply_discount,
                  bg="#1e90ff", fg="white", font=font(size=12, weight="bold")).pack(side="left", padx=10)
        tk.Button(btns, text="Tutup", command=deal_win.destroy,
                  bg="#ff6347", fg="white", font=font(size=12, weight="bold")).pack(side="left", padx=10)

    # =========================
    # Detail data builder
    # =========================
    def _build_details(self):
        """Menyusun konten detail ringkas + trailer per game (diringkas dari deskripsi yang kamu berikan)."""
        d = {}
        d["exp33"] = {
            "desc": (
                "Clair Obscur: Expedition 33 adalah RPG turn-based dengan mekanik real-time yang membuat pertarungan imersif.\n"
                "Jelajahi dunia fantasi Belle Époque, kuasai dodge, parry, counter, chain combo, dan target kelemahan musuh.\n"
                "Ikuti Gustave, Maelle, dan Expeditioners lainnya untuk memutus siklus kematian sang Paintress."
            ),
            "adult": "Kekerasan, darah, bunuh diri, imagery yang mengganggu, busana terbuka, partial nudity.",
            "spec": "Minimum: i7-8700K, GTX1060 6GB, RAM 8GB — Rekomendasi: i7-12700K, RTX3060Ti, RAM 16GB (SSD).",
            "trailer": os.path.join(self.img_dir, "ekspedisi_trailer.mp4"),
            "devpub": "Developer: Sandfall Interactive | Publisher: Kepler Interactive"
        }
        d["silk"] = {
            "desc": (
                "Sebagai Hornet, jelajahi Pharloom, kuasai aksi akrobatik, craft tools, selesaikan quest mengejutkan, "
                "hadapi 200+ musuh dan 40+ bos dengan skor orkestra memukau."
            ),
            "adult": "Aksi intens bergaya terhadap serangga & monster.",
            "spec": "Minimum: i3-3240, GTX560Ti, RAM 4GB — Rekomendasi: i5-3470, GTX1050, RAM 8GB.",
            "trailer": os.path.join(self.img_dir, "silksong_trailer.mp4"),
            "devpub": "Developer/Publisher: Team Cherry"
        }
        d["elden"] = {
            "desc": (
                "Rise, Tarnished. Dunia luas dengan dungeon masif, pertarungan menantang, kustomisasi karakter, "
                "dan drama epik dari GRRM. Co-op dan PvP via Colosseum."
            ),
            "adult": "Kekerasan/gore, konten dewasa umum.",
            "spec": "Minimum: i5-8400, GTX1060 3GB, RAM 12GB — Rekomendasi: i7-8700K, GTX1070 8GB, RAM 16GB.",
            "trailer": os.path.join(self.img_dir, "elden_trailer.mp4"),
            "devpub": "Developer: FromSoftware | Publisher: Bandai Namco"
        }
        d["mc"] = {
            "desc": "Minecraft adalah sandbox kreatif: bangun, eksplorasi, bertahan hidup, dan berkreasi tak terbatas.",
            "adult": "—",
            "spec": "Minimum: CPU dual-core, RAM 2GB — Rekomendasi: CPU quad-core, RAM 4GB.",
            "trailer": os.path.join(self.img_dir, "minecraft_trailer.mp4"),
            "devpub": "Developer: Mojang Studios | Publisher: Xbox Game Studios"
        }
        d["gow"] = {
            "desc": "Kratos dan Atreus menempuh perjalanan epik di dunia mitologi Nordik, pertarungan brutal dan kisah ayah-anak yang menyentuh.",
            "adult": "Kekerasan intens dan elemen dewasa.",
            "spec": "Minimum/Recommended: — (isi sesuai platform PC port bila tersedia).",
            "trailer": os.path.join(self.img_dir, "gow_trailer.mp4"),
            "devpub": "Developer: Santa Monica Studio | Publisher: PlayStation PC LLC"
        }
        d["p5r"] = {
            "desc": "Persona 5 Royal: JRPG stylish dengan kisah Phantom Thieves, dungeon unik, life-sim sekolah, dan sistem Persona mendalam.",
            "adult": "Tema dewasa, kekerasan bergaya.",
            "spec": "Minimum/Recommended: — (isi sesuai rilis PC).",
            "trailer": os.path.join(self.img_dir, "p5r_trailer.mp4"),
            "devpub": "Developer: Atlus | Publisher: SEGA"
        }
        return d

# =========================
# Main
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = StoreApp(root)
    root.mainloop()