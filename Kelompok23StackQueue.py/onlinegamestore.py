# =========================================
# Game Store (Tkinter) — Versi Penuh
# Bahasa Indonesia untuk seluruh penjelasan (#)
# Fitur:
# - Katalog 3 kolom responsif memenuhi lebar saat resize
# - Kartu game menarik dengan ikon diperkecil agar muat 3 per baris
# - Jika diskon: harga asli dicoret + harga setelah diskon ditampilkan
# - Ikon tombol Keranjang di header
# - Keranjang dengan tombol + dan − (inkrement/dekrement item)
# - Konfirmasi checkout dengan UI menarik
# - Struk bergambar
# - Lucky Spin sederhana: jumlah spin dibatasi sesuai jumlah pembelian
# - Voucher diskon dari spin + saldo langsung masuk
# - Dialog berwarna untuk "Keranjang kosong" & "Saldo tidak cukup"
# - Daily deal informatif (harga dari–menjadi dan persen)
# - Menu saldo awal elegan sebelum masuk ke toko
# - Fitur Top-Up saldo saat klik ikon saldo (E-Wallet / Bank Transfer)
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
    """Representasi satu item game katalog (title, base price, cover path)."""
    def __init__(self, title, price, cover):
        self.title = title
        self.price = price
        self.cover = cover

class Cart:
    """Keranjang belanja menyimpan snapshot game (judul + harga saat ditambahkan)."""
    def __init__(self):
        self.items = {}  # {GameSnapshot: qty}

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
        """Total dengan diskon keranjang: -20% jika >= 3 game unik."""
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
    win.geometry("520x260")
    win.configure(bg=bg)
    win.grab_set()
    tk.Label(win, text=title, font=font(size=18, weight="bold"), bg=bg, fg=fg_title).pack(pady=12)
    tk.Label(win, text=message, font=font(size=12), bg=bg, fg=fg_msg, wraplength=460, justify="center").pack(pady=8)
    tk.Button(win, text="Tutup", command=win.destroy, bg="#ff6347", fg="white", font=font(size=12, weight="bold"), width=12).pack(pady=18)

# =========================
# Aplikasi Store
# =========================
class StoreApp:
    def __init__(self, root, initial_balance=500000):
        self.root = root
        self.root.title("Game Store")
        self.root.geometry("1200x800")

        # State awal
        self.balance = initial_balance
        self.cart = Cart()
        self.spin_used = False
        self.last_spin_count = 0

        # Harga katalog
        self.base_price = {}
        self.active_price = {}
        self.next_discount_percent = 0
        self.voucher_banner_var = tk.StringVar(value="")
        self.price_area = {}

        # Folder gambar
        base_dir = os.path.dirname(__file__) if '__file__' in globals() else os.getcwd()
        self.img_dir = os.path.join(base_dir, "images")

        # Katalog game
        self.games = [
            Game("Elden Ring", 750000, os.path.join(self.img_dir, "elden.png")),
            Game("Minecraft", 300000, os.path.join(self.img_dir, "minecraft.png")),
            Game("Clair Obscur: Expedition 33", 500000, os.path.join(self.img_dir, "ekspedisi.png")),
            Game("The Witcher 3: Wild Hunt", 400000, os.path.join(self.img_dir, "witcher.png")),
            Game("God of War", 600000, os.path.join(self.img_dir, "godwar.png")),
            Game("Persona 5 Royal", 550000, os.path.join(self.img_dir, "persona.png")),
        ]
        for g in self.games:
            self.base_price[g] = g.price
            self.active_price[g] = g.price

        # =========================
        # Header
        # =========================
        self.store_frame = tk.Frame(root)
        self.store_frame.pack(fill="both", expand=True)
        header = tk.Frame(self.store_frame, bg="#1e1e2f")
        header.pack(fill="x")

        tk.Label(header, text="🎮 Game Store", font=font(size=28, weight="bold"), bg="#1e1e2f", fg="#ffd700").pack(side="left", padx=22, pady=18)
        tk.Button(header, text="🛒 Keranjang", command=self.show_cart, bg="#ffd700", fg="black", font=font(size=12, weight="bold")).pack(side="right", padx=12, pady=12)

        saldo_frame = tk.Frame(header, bg="#228B22", padx=8, pady=4)
        saldo_frame.pack(side="right", padx=10, pady=8)
        tk.Label(saldo_frame, text="💰", font=font(size=12, weight="bold"), bg="#228B22", fg="white").pack(side="left")
        self.label_balance_store = tk.Label(saldo_frame, text=format_rupiah(self.balance), font=font(size=12, weight="bold"), bg="#32CD32", fg="black")
        self.label_balance_store.pack(side="left", padx=6)
        # Klik saldo untuk top-up
        saldo_frame.bind("<Button-1>", lambda e: self.open_topup_dialog())

        banner = tk.Label(self.store_frame, textvariable=self.voucher_banner_var, font=font(size=12, weight="bold"), bg="#1e1e2f", fg="#32cd32")
        banner.pack(fill="x")

        # =========================
        # Katalog 3 kolom responsif
        # =========================
        self.catalog_canvas = tk.Canvas(self.store_frame, bg="#1e1e2f", highlightthickness=0)
        catalog_scrollbar = tk.Scrollbar(self.store_frame, orient="vertical", command=self.catalog_canvas.yview)
        self.catalog_inner = tk.Frame(self.catalog_canvas, bg="#1e1e2f")
        self.catalog_window = self.catalog_canvas.create_window((0, 0), window=self.catalog_inner, anchor="nw")
        self.catalog_canvas.bind("<Configure>", lambda e: self.catalog_canvas.itemconfig(self.catalog_window, width=e.width))
        self.catalog_inner.bind("<Configure>", lambda e: self.catalog_canvas.configure(scrollregion=self.catalog_canvas.bbox("all")))
        self.catalog_canvas.configure(yscrollcommand=catalog_scrollbar.set)
        self.catalog_canvas.pack(side="left", fill="both", expand=True)
        catalog_scrollbar.pack(side="right", fill="y")
        self.catalog_canvas.bind_all("<MouseWheel>", self._on_catalog_mousewheel)

        for col in range(3):
            self.catalog_inner.grid_columnconfigure(col, weight=1)
        for i, g in enumerate(self.games):
            self.create_game_card(self.catalog_inner, g, i)

        # =========================
        # Keranjang
        # =========================
        self.cart_frame = tk.Frame(root, bg="#2f2f4f")
        cart_header = tk.Frame(self.cart_frame, bg="#2f2f4f"); cart_header.pack(fill="x")
        tk.Label(cart_header, text="🛒 Keranjang Belanja", font=font(size=18, weight="bold"), bg="#2f2f4f", fg="white").pack(side="left", padx=22, pady=10)
        tk.Button(cart_header, text="⬅️ Back", command=self.show_store, bg="#1e90ff", fg="white", font=font(size=12, weight="bold")).pack(side="right", padx=10, pady=10)

        saldo_cart_frame = tk.Frame(cart_header, bg="#006400", padx=8, pady=4)
        saldo_cart_frame.pack(side="right", padx=10, pady=10)
        tk.Label(saldo_cart_frame, text="💰", font=font(size=12, weight="bold"), bg="#006400", fg="white").pack(side="left")
        self.label_balance_cart = tk.Label(saldo_cart_frame, text=format_rupiah(self.balance), font=font(size=12, weight="bold"), bg="#32CD32", fg="black")
        self.label_balance_cart.pack(side="left", padx=6)
        # Klik saldo di cart untuk top-up juga
        saldo_cart_frame.bind("<Button-1>", lambda e: self.open_topup_dialog())

        gift_bar = tk.Frame(self.cart_frame, bg="#2f2f4f"); gift_bar.pack(fill="x", padx=16, pady=6)
        self.is_gift = tk.BooleanVar(value=False)
        self.recipient_var = tk.StringVar(value="Akun saya")
        tk.Checkbutton(gift_bar, text="Beli sebagai gift", variable=self.is_gift, font=font(size=12), bg="#2f2f4f", fg="white", activebackground="#2f2f4f", selectcolor="#2f2f4f").pack(side="left")
        tk.Label(gift_bar, text="Penerima:", font=font(size=12), bg="#2f2f4f", fg="#ffd700").pack(side="left", padx=10)
        self.entry_recipient = tk.Entry(gift_bar, textvariable=self.recipient_var, font=font(size=12), width=24)
        self.entry_recipient.pack(side="left")

        self.cart_inner = tk.Frame(self.cart_frame, bg="#3f3f5f")
        self.cart_inner.pack(fill="x", padx=12, pady=8)

        self.label_total = tk.Label(self.cart_frame, text=f"Total: {format_rupiah(0)}", font=font(size=16, weight="bold"), bg="#2f2f4f", fg="#ffd700")
        self.label_total.pack(pady=6)
        tk.Button(self.cart_frame, text="Checkout", command=self.checkout, bg="#32cd32", fg="white", font=font(size=12, weight="bold")).pack(pady=10)

        # Daily deal popup
        self.root.after(1200, self.daily_deal_popup)

    # =========================
    # Fungsi katalog & harga
    # =========================
    def _on_catalog_mousewheel(self, event):
        self.catalog_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def effective_price(self, game):
        price = self.active_price[game]
        if self.next_discount_percent > 0:
            price = int(price * (1 - self.next_discount_percent / 100))
        return max(0, price)

    def update_catalog_prices(self):
        if self.next_discount_percent > 0:
            self.voucher_banner_var.set(
                f"🎟️ Voucher Diskon {self.next_discount_percent}% aktif. Berlaku hingga checkout berikutnya."
            )
        else:
            self.voucher_banner_var.set("")
        for g, area in self.price_area.items():
            self._render_price_labels(g, area)

    def create_game_card(self, parent, game, index):
        card = tk.Frame(parent, bg="#252542", bd=0, relief="flat")
        card.grid(row=index//3, column=index%3, padx=12, pady=16, sticky="nsew")

        container = tk.Frame(card, bg="#2f2f4f", bd=2, relief="ridge")
        container.pack(fill="both", expand=True)

        try:
            img = Image.open(game.cover)
            img = img.resize((210, 130))
            photo = ImageTk.PhotoImage(img)
            img_box = tk.Label(container, image=photo, bg="#2f2f4f")
            img_box.image = photo
            img_box.pack(pady=10)
        except:
            tk.Label(container, text="[Gambar tidak ditemukan]", bg="#2f2f4f", fg="red", font=font(size=12)).pack(pady=10)

        tk.Label(container, text=game.title, font=font(size=14, weight="bold"), bg="#2f2f4f", fg="white").pack(pady=4)

        price_area = {"label_asli": tk.Label(container, bg="#2f2f4f"), "label_diskon": tk.Label(container, bg="#2f2f4f")}
        price_area["label_asli"].pack()
        price_area["label_diskon"].pack()
        self.price_area[game] = price_area
        self._render_price_labels(game, price_area)

        tk.Button(container, text="Tambah ke Keranjang", command=lambda g=game: self.add_to_cart(g),
                  bg="#1e90ff", fg="white", font=font(size=12, weight="bold"), width=22).pack(pady=12)

    def _render_price_labels(self, game, area):
        harga_asli = self.base_price[game]
        harga_aktif = self.active_price[game]
        harga_efektif = self.effective_price(game)

        if harga_aktif < harga_asli:
            area["label_asli"].config(text=f"{format_rupiah(harga_asli)}",
                                      font=(font()[0], 12, "overstrike", "bold"), fg="#ff6347", bg="#2f2f4f")
            if harga_efektif < harga_aktif:
                area["label_diskon"].config(
                    text=f"Harga Diskon: {format_rupiah(harga_efektif)} (termasuk voucher {self.next_discount_percent}%)",
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
                area["label_asli"].config(text=f"{format_rupiah(harga_asli)}",
                                          font=(font()[0], 12, "overstrike", "bold"), fg="#ff6347", bg="#2f2f4f")
                area["label_diskon"].config(
                    text=f"Harga Diskon: {format_rupiah(harga_efektif)} (voucher {self.next_discount_percent}%)",
                    font=font(size=13, weight="bold"), fg="#FFD700", bg="#2f2f4f"
                )
            else:
                area["label_diskon"].config(
                    text=f"Harga: {format_rupiah(harga_asli)}",
                    font=font(size=13, weight="bold"), fg="#FFD700", bg="#2f2f4f"
                )

    def add_to_cart(self, game):
        current_price = self.effective_price(game)
        g_snapshot = Game(game.title, current_price, game.cover)
        self.cart.add(g_snapshot)
        self.show_added_popup(g_snapshot)
        if self.cart_frame.winfo_ismapped():
            self.refresh_cart()

    # =========================
    # Popup tambah ke keranjang
    # =========================
    def show_added_popup(self, g_snapshot):
        popup = tk.Toplevel(self.root)
        popup.title("Game Ditambahkan")
        popup.geometry("560x640")
        popup.configure(bg="#1e1e2f")
        popup.grab_set()

        tk.Label(popup, text="✅ Game telah dimasukkan ke keranjang", font=font(size=14, weight="bold"),
                 fg="#32cd32", bg="#1e1e2f").pack(pady=10)

        try:
            img = Image.open(g_snapshot.cover)
            img = img.resize((320, 190))
            photo = ImageTk.PhotoImage(img)
            label_img = tk.Label(popup, image=photo, bg="#1e1e2f")
            label_img.image = photo
            label_img.pack(pady=10)
        except:
            tk.Label(popup, text="[Gambar tidak ditemukan]", bg="#1e1e2f", fg="red", font=font(size=12)).pack(pady=10)

        tk.Label(popup, text=g_snapshot.title, font=font(size=12, weight="bold"), fg="white", bg="#1e1e2f").pack(pady=5)
        tk.Label(popup, text=f"Harga: {format_rupiah(g_snapshot.price)}", font=font(size=12, weight="bold"), fg="#FFD700", bg="#1e1e2f").pack(pady=5)

        qty_var = tk.StringVar(value=f"Jumlah di keranjang: {self.cart.qty_by_title(g_snapshot.title)}")
        tk.Label(popup, textvariable=qty_var, font=font(size=12, weight="bold"), fg="#1e90ff", bg="#1e1e2f").pack(pady=6)

        ctrl = tk.Frame(popup, bg="#1e1e2f"); ctrl.pack(pady=10)
        tk.Button(ctrl, text="Tambah Lagi", command=lambda: self._popup_add(g_snapshot, qty_var),
                  bg="#32cd32", fg="white", font=font(size=11, weight="bold")).pack(side="left", padx=8)
        tk.Button(ctrl, text="Hapus", command=lambda: self._popup_remove(g_snapshot, qty_var),
                  bg="#ff6347", fg="white", font=font(size=11, weight="bold")).pack(side="left", padx=8)

        choose = tk.Frame(popup, bg="#1e1e2f"); choose.pack(pady=20)
        tk.Button(choose, text="Lanjutkan Belanja", command=lambda: self._popup_continue(popup),
                  bg="#1e90ff", fg="white", font=font(size=12, weight="bold")).pack(side="left", padx=12)
        tk.Button(choose, text="Lihat Keranjang Saya", command=lambda: self._popup_go_cart(popup),
                  bg="#FFD700", fg="black", font=font(size=12, weight="bold")).pack(side="left", padx=12)

    def _popup_add(self, g_snapshot, qty_var):
        self.cart.add(g_snapshot)
        qty_var.set(f"Jumlah di keranjang: {self.cart.qty_by_title(g_snapshot.title)}")
        if self.cart_frame.winfo_ismapped():
            self.refresh_cart()

    def _popup_remove(self, g_snapshot, qty_var):
        self.cart.remove(g_snapshot)
        qty_var.set(f"Jumlah di keranjang: {self.cart.qty_by_title(g_snapshot.title)}")
        if self.cart_frame.winfo_ismapped():
            self.refresh_cart()

    def _popup_continue(self, popup):
        popup.destroy()
        self.show_store()

    def _popup_go_cart(self, popup):
        popup.destroy()
        self.show_cart()

    # =========================
    # Keranjang & total
    # =========================
    def show_cart(self):
        self.store_frame.pack_forget()
        self.cart_frame.pack(fill="both", expand=True)
        self.refresh_cart()

    def show_store(self):
        self.cart_frame.pack_forget()
        self.store_frame.pack(fill="both", expand=True)
        self.update_catalog_prices()

    def refresh_cart(self):
        for w in self.cart_inner.winfo_children():
            w.destroy()

        if not self.cart.items:
            empty = tk.Frame(self.cart_inner, bg="#3f3f5f")
            empty.pack(fill="x", padx=12, pady=12)
            tk.Label(empty, text="Keranjang kosong. Tambahkan game dari katalog.", font=font(size=12, weight="bold"),
                     bg="#3f3f5f", fg="#ffcc00").pack(pady=8)
            self.update_total()
            return

        row = tk.Frame(self.cart_inner, bg="#3f3f5f")
        row.pack(fill="x")

        for game, qty in self.cart.items.items():
            card = tk.Frame(row, bg="#4f4f6f", bd=2, relief="ridge", width=360, height=240)
            card.pack(side="left", padx=10, pady=10)
            card.pack_propagate(False)

            left = tk.Frame(card, bg="#4f4f6f"); left.pack(side="left", padx=12, pady=12)
            try:
                img = Image.open(game.cover)
                img = img.resize((160, 110))
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(left, image=photo, bg="#4f4f6f")
                lbl.image = photo
                lbl.pack()
            except:
                tk.Label(left, text="[Img]", bg="#4f4f6f", fg="red", font=font(size=12, weight="bold")).pack()

            mid = tk.Frame(card, bg="#4f4f6f"); mid.pack(side="left", padx=10, pady=10)
            tk.Label(mid, text=game.title, font=font(size=12, weight="bold"), bg="#4f4f6f", fg="white").pack(anchor="w")
            tk.Label(mid, text=f"{format_rupiah(game.price)} x{qty}", font=font(size=11, weight="bold"), bg="#4f4f6f", fg="#FFD700").pack(anchor="w")

            right = tk.Frame(card, bg="#4f4f6f"); right.pack(side="right", padx=10, pady=10)
            tk.Button(right, text="+", command=lambda g=game: self._inc(g), bg="#32cd32", fg="white", font=font(size=11, weight="bold"), width=4).pack(pady=6)
            tk.Button(right, text="-", command=lambda g=game: self._dec(g), bg="#ff6347", fg="white", font=font(size=11, weight="bold"), width=4).pack(pady=6)

        self.update_total()

    def _inc(self, game):
        self.cart.add(game)
        self.refresh_cart()

    def _dec(self, game):
        self.cart.remove(game)
        self.refresh_cart()

    def update_total(self):
        total = self.cart.total()
        text = f"Total: {format_rupiah(total)}"
        if self.cart.unique_count() >= 3:
            text = f"Total (Diskon 20%): {format_rupiah(total)}"

        self.label_total.config(text=text)
        self.label_balance_store.config(text=format_rupiah(self.balance))
        self.label_balance_cart.config(text=format_rupiah(self.balance))

    # =========================
    # Checkout, struk, spin
    # =========================
    def confirm_checkout_ui(self, total_pay, penerima_text):
        win = tk.Toplevel(self.root)
        win.title("Konfirmasi Pembelian")
        win.geometry("560x480")
        win.configure(bg="#1b1b2e")
        win.grab_set()

        tk.Label(win, text="Apakah Anda yakin membeli?", font=font(size=20, weight="bold"), bg="#1b1b2e", fg="#FFD700").pack(pady=16)

        box = tk.Frame(win, bg="#2a2a46", bd=2, relief="ridge"); box.pack(fill="x", padx=20, pady=12)
        tk.Label(box, text=f"Total yang akan dibayar: {format_rupiah(total_pay)}", font=font(size=14, weight="bold"), bg="#2a2a46", fg="#32cd32").pack(pady=8)
        tk.Label(box, text=f"Penerima: {penerima_text}", font=font(size=12), bg="#2a2a46", fg="white").pack(pady=4)
        tk.Label(box, text="Pastikan keranjang sesuai sebelum melanjutkan.", font=font(size=11), bg="#2a2a46", fg="#a0a0c0").pack(pady=6)

        actions = tk.Frame(win, bg="#1b1b2e"); actions.pack(pady=18)
        tk.Button(actions, text="Ya, Lanjutkan Pembelian ✅", bg="#32cd32", fg="white", font=font(size=12, weight="bold"), width=24,
                  command=lambda: [setattr(win, "confirmed", True), win.destroy()]).pack(side="left", padx=10)
        tk.Button(actions, text="Batalkan ❌", bg="#ff6347", fg="white", font=font(size=12, weight="bold"), width=16,
                  command=lambda: [setattr(win, "confirmed", False), win.destroy()]).pack(side="left", padx=10)

        win.confirmed = False
        self.root.wait_window(win)
        return win.confirmed

    def checkout(self):
        if not self.cart.items:
            show_colored_dialog(self.root, "Keranjang Kosong", "Belum ada game di keranjang. Tambahkan game dari katalog.", bg="#2b2b44", fg_title="#ffcc00", fg_msg="white")
            return

        total_pay = self.cart.total()
        if self.balance < total_pay:
            show_colored_dialog(self.root, "Saldo Tidak Cukup", f"Total belanja {format_rupiah(total_pay)} melebihi saldo {format_rupiah(self.balance)}.", bg="#3b1f24", fg_title="#ff6b6b", fg_msg="#ffd7d7")
            return

        penerima_text = f"Gift untuk {self.recipient_var.get()}" if self.is_gift.get() else "Akun saya"
        if not self.confirm_checkout_ui(total_pay, penerima_text):
            return

        self.balance -= total_pay
        self.update_total()

        spin_count = self.cart.total_count()
        self.spin_used = False
        self.last_spin_count = spin_count

        purchased_summary = self.cart.summary_lines()
        self.cart.clear()
        self.refresh_cart()

        self.show_receipt(purchased_summary, spin_count)

    def show_receipt(self, purchased_summary, spin_count):
        win = tk.Toplevel(self.root)
        win.title("Struk Pembelian")
        win.geometry("900x800")
        win.configure(bg="#1e1e2f")

        tk.Label(win, text="✅ Pembelian Berhasil", font=font(size=22, weight="bold"), fg="#32cd32", bg="#1e1e2f").pack(pady=10)

        penerima_text = f"Gift untuk {self.recipient_var.get()}" if self.is_gift.get() else "Akun saya"
        tk.Label(win, text=f"Penerima: {penerima_text}", font=font(size=12, weight="bold"), fg="white", bg="#1e1e2f").pack()

        total_pay = sum(p for _, _, p, _ in purchased_summary)
        tk.Label(win, text=f"Total Dibayar: {format_rupiah(total_pay)}", font=font(size=14, weight="bold"), fg="#FFD700", bg="#1e1e2f").pack(pady=6)
        tk.Label(win, text=f"Sisa Saldo: {format_rupiah(self.balance)}", font=font(size=14, weight="bold"), fg="#1e90ff", bg="#1e1e2f").pack(pady=2)

        list_canvas = tk.Canvas(win, bg="#23233a", height=420, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=list_canvas.yview)
        inner = tk.Frame(list_canvas, bg="#23233a")
        inner.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0, 0), window=inner, anchor="nw", width=860)
        list_canvas.configure(yscrollcommand=scrollbar.set)
        list_canvas.pack(side="left", fill="both", expand=True, padx=16, pady=10)
        scrollbar.pack(side="right", fill="y")

        for title, qty, subtotal, cover in purchased_summary:
            row = tk.Frame(inner, bg="#2e2e4a", bd=2, relief="ridge")
            row.pack(fill="x", padx=8, pady=8)
            try:
                img = Image.open(cover)
                img = img.resize((150, 100))
                photo = ImageTk.PhotoImage(img)
                img_lbl = tk.Label(row, image=photo, bg="#2e2e4a")
                img_lbl.image = photo
                img_lbl.pack(side="left", padx=12, pady=10)
            except:
                tk.Label(row, text="[IMG]", font=font(size=12, weight="bold"), bg="#2e2e4a", fg="red").pack(side="left", padx=12, pady=10)

            info = tk.Frame(row, bg="#2e2e4a"); info.pack(side="left", padx=10, pady=10)
            tk.Label(info, text=title, font=font(size=12, weight="bold"), bg="#2e2e4a", fg="white").pack(anchor="w")
            tk.Label(info, text=f"Jumlah: {qty}", font=font(size=12), bg="#2e2e4a", fg="#1e90ff").pack(anchor="w")
            tk.Label(info, text=f"Subtotal: {format_rupiah(subtotal)}", font=font(size=12, weight="bold"), bg="#2e2e4a", fg="#FFD700").pack(anchor="w")

        tk.Label(win, text=f"🎲 Kamu mendapatkan {spin_count} spin", font=font(size=14, weight="bold"), fg="#1e90ff", bg="#1e1e2f").pack(pady=12)
        spin_btn = tk.Button(win, text="Mainkan Lucky Spin", bg="#8a2be2", fg="white", font=font(size=12, weight="bold"),
                             command=lambda: self.open_simple_spin(win, spin_btn))
        spin_btn.pack()

        action_bar = tk.Frame(win, bg="#1e1e2f"); action_bar.pack(pady=16)
        tk.Button(action_bar, text="Tutup", command=win.destroy, bg="#ff6347", fg="white", font=font(size=12, weight="bold"), width=14).pack(side="left", padx=8)
        tk.Button(action_bar, text="Kembali ke Toko", command=lambda: [win.destroy(), self.show_store()],
                  bg="#32cd32", fg="white", font=font(size=12, weight="bold"), width=16).pack(side="left", padx=8)

    # =========================
    # Lucky Spin
    # =========================
    def open_simple_spin(self, parent, spin_btn):
        if self.spin_used:
            show_colored_dialog(self.root, "Spin Selesai", "Spin sudah digunakan untuk transaksi ini.", bg="#2b2b44", fg_title="#ffcc00", fg_msg="white")
            return
        if self.last_spin_count <= 0:
            show_colored_dialog(self.root, "Spin Tidak Tersedia", "Tidak ada spin yang tersedia untuk transaksi ini.", bg="#2b2b44", fg_title="#ffcc00", fg_msg="white")
            return

        self.spin_used = True
        spin_btn.config(state="disabled", text="Spin sudah dimainkan")

        spin_win = tk.Toplevel(parent)
        spin_win.title("🎲 Lucky Spin")
        spin_win.geometry("560x440")
        spin_win.configure(bg="#14142a")
        spin_win.grab_set()

        tk.Label(spin_win, text="Lucky Spin", font=font(size=20, weight="bold"), fg="#FFD700", bg="#14142a").pack(pady=12)
        tk.Label(spin_win, text=f"Jumlah spin: {self.last_spin_count}", font=font(size=12, weight="bold"), fg="#32cd32", bg="#14142a").pack(pady=4)

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

        tk.Button(spin_win, text="Tutup", command=spin_win.destroy, bg="#ff6347", fg="white", font=font(size=12, weight="bold")).pack(pady=10)
        tk.Button(spin_win, text="Mulai Spin", command=lambda: run_spins(self.last_spin_count), bg="#8a2be2", fg="white", font=font(size=12, weight="bold")).pack(pady=10)

    # =========================
    # Daily deal popup
    # =========================
    def daily_deal_popup(self):
        rekom = random.choice(self.games)
        deal_win = tk.Toplevel(self.root)
        deal_win.title("🔥 Daily Deal!")
        deal_win.geometry("640x720")
        deal_win.configure(bg="#1e1e2f")
        deal_win.grab_set()

        tk.Label(deal_win, text="🔥 Game of the Day 🔥", font=font(size=24, weight="bold"), fg="#FFD700", bg="#1e1e2f").pack(pady=20)

        try:
            img = Image.open(rekom.cover)
            img = img.resize((400, 250))
            photo = ImageTk.PhotoImage(img)
            label_img = tk.Label(deal_win, image=photo, bg="#1e1e2f")
            label_img.image = photo
            label_img.pack(pady=12)
        except:
            tk.Label(deal_win, text="[Gambar tidak ditemukan]", bg="#1e1e2f", fg="red", font=font(size=12)).pack(pady=12)

        tk.Label(deal_win, text=rekom.title, font=font(size=18, weight="bold"), fg="white", bg="#1e1e2f").pack(pady=5)

        harga_asli = self.base_price[rekom]
        potongan = random.choice([50000, 100000, 150000])
        harga_baru = max(0, harga_asli - potongan)
        persen = int(round((potongan / harga_asli) * 100)) if harga_asli > 0 else 0

        tk.Label(deal_win, text=f"Harga asli: {format_rupiah(harga_asli)}", font=font(size=14), fg="#ff6347", bg="#1e1e2f").pack()
        tk.Label(deal_win, text=f"Menjadi: {format_rupiah(harga_baru)}", font=font(size=16, weight="bold"), fg="#32cd32", bg="#1e1e2f").pack(pady=4)
        tk.Label(deal_win, text=f"Diskon: {format_rupiah(potongan)} ({persen}%)", font=font(size=13, weight="bold"), fg="#FFD700", bg="#1e1e2f").pack(pady=6)
        tk.Label(deal_win, text="Tekan 'Terapkan Diskon' untuk mengaktifkan harga di katalog.", font=font(size=11), fg="white", bg="#1e1e2f").pack(pady=10)

        btns = tk.Frame(deal_win, bg="#1e1e2f"); btns.pack(pady=20)

        def apply_discount():
            self.active_price[rekom] = harga_baru
            self.update_catalog_prices()
            deal_win.destroy()

        tk.Button(btns, text="Terapkan Diskon", command=apply_discount, bg="#1e90ff", fg="white", font=font(size=12, weight="bold")).pack(side="left", padx=10)
        tk.Button(btns, text="Tutup", command=deal_win.destroy, bg="#ff6347", fg="white", font=font(size=12, weight="bold")).pack(side="left", padx=10)

    # =========================
    # Top-Up saldo (E-Wallet / Bank)
    # =========================
    def open_topup_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Tambah Saldo")
        win.geometry("420x360")
        win.configure(bg="#1e1e2f")
        win.grab_set()

        tk.Label(win, text="💰 Tambah Saldo", font=font(size=18, weight="bold"), fg="#FFD700", bg="#1e1e2f").pack(pady=12)

        # Pilih metode
        method_var = tk.StringVar(value="E-Wallet")
        fm = tk.Frame(win, bg="#1e1e2f"); fm.pack(pady=6)
        tk.Radiobutton(fm, text="E-Wallet", variable=method_var, value="E-Wallet", font=font(size=12), bg="#1e1e2f", fg="white", selectcolor="#1e1e2f").pack(side="left", padx=10)
        tk.Radiobutton(fm, text="Bank Transfer", variable=method_var, value="Bank", font=font(size=12), bg="#1e1e2f", fg="white", selectcolor="#1e1e2f").pack(side="left", padx=10)

        tk.Label(win, text="Masukkan jumlah saldo:", font=font(size=12), fg="#32cd32", bg="#1e1e2f").pack(pady=6)
        amount_var = tk.StringVar()
        entry_amount = tk.Entry(win, textvariable=amount_var, font=font(size=12), width=20, bg="#23234a", fg="white", insertbackground="white")
        entry_amount.pack(pady=6)

        info_label = tk.Label(win, text="", font=font(size=10, weight="bold"), fg="#ff6b6b", bg="#1e1e2f")
        info_label.pack(pady=6)

        def confirm_topup():
            s = amount_var.get().replace(" ", "")
            if not s.isdigit() or int(s) <= 0:
                info_label.config(text="Masukkan angka yang valid.", fg="#ff6b6b")
                return
            amt = int(s)
            self.balance += amt
            self.update_total()
            info_label.config(text=f"Saldo bertambah {format_rupiah(amt)} via {method_var.get()} ✅", fg="#32cd32")

        tk.Button(win, text="Tambah Saldo", command=confirm_topup, bg="#32cd32", fg="white", font=font(size=12, weight="bold")).pack(pady=10)
        tk.Button(win, text="Tutup", command=win.destroy, bg="#ff6347", fg="white", font=font(size=12, weight="bold")).pack(pady=6)

# =========================
# Menu saldo awal elegan
# =========================
class BalanceMenu:
    """Menu awal untuk memilih saldo dengan UI elegan dan validasi aman."""
    def __init__(self, root, default_balance=500000, on_start=None):
        self.root = root
        self.default_balance = default_balance
        self.on_start = on_start

        self.win = tk.Toplevel(root)
        self.win.title("Selamat Datang — Atur Saldo Awal")
        self.win.geometry("520x360")
        self.win.configure(bg="#121225")
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._use_default)  # kalau ditutup, pakai default
        self.win.grab_set()

        header = tk.Frame(self.win, bg="#121225"); header.pack(fill="x", pady=14)
        tk.Label(header, text="🎉 Selamat Datang di Game Store", font=font(size=18, weight="bold"), fg="#FFD700", bg="#121225").pack()
        tk.Label(header, text="Tentukan saldo awal untuk akun kamu.", font=font(size=11), fg="#a7a7c7", bg="#121225").pack(pady=2)

        card = tk.Frame(self.win, bg="#1b1b35", bd=2, relief="ridge"); card.pack(fill="x", padx=18, pady=12)
        tk.Label(card, text="Saldo Awal (angka saja):", font=font(size=12, weight="bold"), fg="#32cd32", bg="#1b1b35").pack(pady=10)

        self.entry_var = tk.StringVar(value=str(default_balance))
        self.entry = tk.Entry(card, textvariable=self.entry_var, font=font(size=12), width=26, bg="#23234a", fg="white", insertbackground="white")
        self.entry.pack(pady=8)
        self.entry.select_range(0, tk.END)
        self.entry.focus_set()

        tk.Label(card, text="Contoh: 500000 atau 1 000 000 (spasi akan diabaikan)", font=font(size=10), fg="#d0d0ef", bg="#1b1b35").pack(pady=4)
        self.error_label = tk.Label(card, text="", font=font(size=10, weight="bold"), fg="#ff6b6b", bg="#1b1b35")
        self.error_label.pack(pady=2)

        actions = tk.Frame(self.win, bg="#121225"); actions.pack(pady=16)
        tk.Button(actions, text="Mulai", command=self._start, bg="#32cd32", fg="white", font=font(size=12, weight="bold"), width=14).pack(side="left", padx=8)
        tk.Button(actions, text="Gunakan Default", command=self._use_default, bg="#FFD700", fg="black", font=font(size=12, weight="bold"), width=16).pack(side="left", padx=8)

        tk.Label(self.win, text="Kamu bisa tambah saldo via Lucky Spin (demo).", font=font(size=10), fg="#a7a7c7", bg="#121225").pack(pady=4)

    def _clean_to_int(self, s: str):
        cleaned = "".join(ch for ch in s if ch.isdigit())
        if cleaned.isdigit() and len(cleaned) > 0:
            return int(cleaned)
        return None

    def _start(self):
        val = self._clean_to_int(self.entry_var.get())
        if val is None:
            self.error_label.config(text="Masukkan angka yang valid. Contoh: 500000 atau 1 000 000.")
            return
        if self.on_start:
            self.on_start(val)
        self.win.destroy()

    def _use_default(self):
        if self.on_start:
            self.on_start(self.default_balance)
        self.win.destroy()

# =========================
# Main
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # sembunyikan root sampai saldo dipilih

    def start_app(initial_balance):
        # Pastikan tidak instantiate sebelum menu ditutup
        root.deiconify()
        StoreApp(root, initial_balance=initial_balance)  # buat app

    # Penting: mainloop dijalankan sekali saja
    BalanceMenu(root, default_balance=500000, on_start=start_app)
    root.mainloop()

    