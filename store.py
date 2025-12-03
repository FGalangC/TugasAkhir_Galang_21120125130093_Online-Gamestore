import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# === Class Game ===
class Game:
    def __init__(self, title, price, cover):
        self.title = title
        self.price = price
        self.cover = cover

# === Class Cart ===
class Cart:
    def __init__(self):
        self.items = []
    def add(self, game):
        self.items.append(game)
    def total(self):
        return sum(g.price for g in self.items)
    def summary(self):
        return "\n".join([f"{g.title} - Rp{g.price}" for g in self.items])

# === Class StoreApp ===
class StoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Store")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2f")

        # Data game
        self.games = [
            Game("Elden Ring", 750000, "elden.png"),
            Game("Minecraft", 300000, "minecraft.png"),
            Game("Clair Obscur:Expedition 33", 500000, "ekspedisi.png"),
            Game("The Witcher 3", 400000, "witcher.png")
        ]
        self.cart = Cart()

        # Judul
        tk.Label(root,text="🎮 Game Store",font=("Arial",24,"bold"),
                 bg="#1e1e2f",fg="#ffd700").pack(pady=20)

        # Frame daftar game
        self.frame_games = tk.Frame(root,bg="#1e1e2f")
        self.frame_games.pack()

        for i,game in enumerate(self.games):
            self.create_game_card(self.frame_games,game,i)

        # Frame keranjang
        self.frame_cart = tk.Frame(root,bg="#2f2f4f")
        self.frame_cart.pack(fill="x",side="bottom")

        tk.Label(self.frame_cart,text="🛒 Keranjang Belanja",
                 font=("Arial",16,"bold"),bg="#2f2f4f",fg="white").pack(pady=5)

        self.listbox = tk.Listbox(self.frame_cart,width=60,height=5,
                                  bg="#3f3f5f",fg="white",font=("Arial",12))
        self.listbox.pack(pady=5)

        self.label_total = tk.Label(self.frame_cart,text="Total: Rp0",
                                    font=("Arial",14,"bold"),bg="#2f2f4f",fg="#ffd700")
        self.label_total.pack(pady=5)

        tk.Button(self.frame_cart,text="Checkout",command=self.checkout,
                  bg="#32cd32",fg="white",font=("Arial",12,"bold")).pack(pady=10)

    def create_game_card(self,parent,game,index):
        frame=tk.Frame(parent,bg="#2f2f4f",bd=2,relief="ridge")
        frame.grid(row=index//2,column=index%2,padx=20,pady=20)

        img=Image.open(game.cover)
        img=img.resize((200,120))
        photo=ImageTk.PhotoImage(img)
        label_img=tk.Label(frame,image=photo)
        label_img.image=photo
        label_img.pack()

        tk.Label(frame,text=game.title,font=("Arial",14,"bold"),
                 bg="#2f2f4f",fg="white").pack(pady=5)
        tk.Label(frame,text=f"Harga: Rp{game.price}",font=("Arial",12),
                 bg="#2f2f4f",fg="#ffd700").pack()

        tk.Button(frame,text="Tambah ke Keranjang",
                  command=lambda:self.add_to_cart(game),
                  bg="#1e90ff",fg="white",font=("Arial",12,"bold")).pack(pady=10)

    def add_to_cart(self,game):
        self.cart.add(game)
        self.listbox.insert(tk.END,f"{game.title} - Rp{game.price}")
        self.label_total.config(text=f"Total: Rp{self.cart.total()}")

    def checkout(self):
        if not self.cart.items:
            messagebox.showwarning("Keranjang Kosong","Belum ada game di keranjang!")
        else:
            msg=f"Pembelian Berhasil!\n\n{self.cart.summary()}\n\nTotal Bayar: Rp{self.cart.total()}"
            messagebox.showinfo("Checkout",msg)

# === Main Program ===
root=tk.Tk()
app=StoreApp(root)
root.mainloop()