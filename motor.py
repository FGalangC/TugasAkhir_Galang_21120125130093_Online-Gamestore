import tkinter as tk
from tkinter import messagebox

class AplikasiKecepatanMotor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hitung Kecepatan Motor")
        self.root.geometry("350x350")
        self.root.resizable(False, False)

        # Judul
        tk.Label(root, text="Kalkulator Kecepatan Motor", font=("Arial", 14, "bold")).pack(pady=10)

        # Input Jarak
        frame_jarak = tk.Frame(root)
        frame_jarak.pack(pady=5)
        tk.Label(frame_jarak, text="Jarak (km):").pack(side="left")
        self.entry_jarak = tk.Entry(frame_jarak)
        self.entry_jarak.pack(side="left", padx=5)

        # Input Waktu
        frame_waktu = tk.Frame(root)
        frame_waktu.pack(pady=5)
        tk.Label(frame_waktu, text="Waktu (jam):").pack(side="left")
        self.entry_waktu = tk.Entry(frame_waktu)
        self.entry_waktu.pack(side="left", padx=5)

        # Tombol Hitung
        self.btn_hitung = tk.Button(root, text="Hitung Kecepatan", command=self.hitung_kecepatan,
                                    bg="lightblue", width=20)
        self.btn_hitung.pack(pady=20)

        # Label Hasil
        self.label_hasil = tk.Label(root, text="", font=("Arial", 12))
        self.label_hasil.pack(pady=10)

        # Tambahkan gambar ikon satuan kecepatan
        # Pastikan Anda punya file gambar, misalnya "speed.png"
        try:
            self.img_speed = tk.PhotoImage(file="speed.png")  # gunakan gambar PNG
            self.label_img = tk.Label(root, image=self.img_speed)
            self.label_img.pack(pady=5)
        except Exception as e:
            tk.Label(root, text="(Ikon km/jam tidak ditemukan)", fg="red").pack()

    def hitung_kecepatan(self):
        try:
            jarak = float(self.entry_jarak.get())
            waktu = float(self.entry_waktu.get())

            if waktu <= 0:
                messagebox.showwarning("Peringatan", "Waktu harus lebih dari 0!")
                return

            kecepatan = jarak / waktu  # km/jam
            self.label_hasil.config(text=f"Kecepatan Motor: {kecepatan:.2f} km/jam")

        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid untuk jarak dan waktu!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AplikasiKecepatanMotor(root)
    root.mainloop()