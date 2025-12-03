import tkinter as tk
from tkinter import messagebox

class GradeCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hitung Nilai Akhir Mahasiswa")
        self.root.geometry("500x600")
        self.root.configure(bg="#f0f8ff")  # Light blue background

        # Title
        title_label = tk.Label(root, text="Kalkulator Nilai Akhir Mahasiswa", font=("Arial", 18, "bold"), bg="#f0f8ff", fg="#2e8b57")
        title_label.pack(pady=20)

        # Input Frame
        input_frame = tk.Frame(root, bg="#f0f8ff")
        input_frame.pack(pady=10)

        # Nama
        tk.Label(input_frame, text="Nama:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, sticky="w", pady=5)
        self.nama_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.nama_entry.grid(row=0, column=1, pady=5)

        # NIM
        tk.Label(input_frame, text="NIM:", font=("Arial", 12), bg="#f0f8ff").grid(row=1, column=0, sticky="w", pady=5)
        self.nim_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.nim_entry.grid(row=1, column=1, pady=5)

        # Nilai Tugas
        tk.Label(input_frame, text="Nilai Tugas:", font=("Arial", 12), bg="#f0f8ff").grid(row=2, column=0, sticky="w", pady=5)
        self.tugas_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.tugas_entry.grid(row=2, column=1, pady=5)

        # Nilai UTS
        tk.Label(input_frame, text="Nilai UTS:", font=("Arial", 12), bg="#f0f8ff").grid(row=3, column=0, sticky="w", pady=5)
        self.uts_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.uts_entry.grid(row=3, column=1, pady=5)

        # Nilai UAS
        tk.Label(input_frame, text="Nilai UAS:", font=("Arial", 12), bg="#f0f8ff").grid(row=4, column=0, sticky="w", pady=5)
        self.uas_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.uas_entry.grid(row=4, column=1, pady=5)

        # Calculate Button
        self.calculate_button = tk.Button(root, text="Hitung Nilai Akhir", command=self.calculate_grade, font=("Arial", 14, "bold"), bg="#32cd32", fg="white", width=20)
        self.calculate_button.pack(pady=20)

        # Output Frame
        output_frame = tk.Frame(root, bg="#f0f8ff")
        output_frame.pack(pady=10)

        tk.Label(output_frame, text="Hasil:", font=("Arial", 14, "bold"), bg="#f0f8ff", fg="#2e8b57").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(output_frame, text="Nama:", font=("Arial", 12), bg="#f0f8ff").grid(row=1, column=0, sticky="w")
        self.output_nama = tk.Label(output_frame, text="", font=("Arial", 12, "bold"), bg="#f0f8ff", fg="#000080")
        self.output_nama.grid(row=1, column=1, sticky="w")

        tk.Label(output_frame, text="NIM:", font=("Arial", 12), bg="#f0f8ff").grid(row=2, column=0, sticky="w")
        self.output_nim = tk.Label(output_frame, text="", font=("Arial", 12, "bold"), bg="#f0f8ff", fg="#000080")
        self.output_nim.grid(row=2, column=1, sticky="w")

        tk.Label(output_frame, text="Nilai Akhir:", font=("Arial", 12), bg="#f0f8ff").grid(row=3, column=0, sticky="w")
        self.output_nilai = tk.Label(output_frame, text="", font=("Arial", 12, "bold"), bg="#f0f8ff", fg="#000080")
        self.output_nilai.grid(row=3, column=1, sticky="w")

        tk.Label(output_frame, text="Kategori:", font=("Arial", 12), bg="#f0f8ff").grid(row=4, column=0, sticky="w")
        self.output_kategori = tk.Label(output_frame, text="", font=("Arial", 12, "bold"), bg="#f0f8ff", fg="#000080")
        self.output_kategori.grid(row=4, column=1, sticky="w")

    def calculate_grade(self):
        try:
            nama = self.nama_entry.get().strip()
            nim = self.nim_entry.get().strip()
            tugas = float(self.tugas_entry.get())
            uts = float(self.uts_entry.get())
            uas = float(self.uas_entry.get())

            if not nama or not nim:
                raise ValueError("Nama dan NIM harus diisi.")
            if not (0 <= tugas <= 100) or not (0 <= uts <= 100) or not (0 <= uas <= 100):
                raise ValueError("Nilai harus antara 0 dan 100.")

            nilai_akhir = (0.3 * tugas) + (0.3 * uts) + (0.4 * uas)

            if nilai_akhir > 85:
                kategori = "A"
            elif 70 <= nilai_akhir <= 84:
                kategori = "B"
            else:
                kategori = "C"

            self.output_nama.config(text=nama)
            self.output_nim.config(text=nim)
            self.output_nilai.config(text=f"{nilai_akhir:.2f}")
            self.output_kategori.config(text=kategori)

        except ValueError as e:
            messagebox.showerror("Error", f"Input tidak valid: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GradeCalculatorApp(root)
    root.mainloop()
