def arrayProcessor(arr, operasi):
    """
    Memproses array angka berdasarkan operasi yang diminta.

    Parameter:
    - arr: list berisi angka (int atau float)
    - operasi: string ('sum', 'avg', 'max', 'min')

    Return:
    - Hasil dari operasi yang diminta
    """

    # Validasi tipe dan isi array
    if not isinstance(arr, list):
        raise TypeError("Input harus berupa list.")
    if not arr:
        raise ValueError("Array tidak boleh kosong.")
    if not all(isinstance(x, (int, float)) for x in arr):
        raise ValueError("Semua elemen harus berupa angka.")
    if any(x < 0 for x in arr):
        raise ValueError("Array tidak boleh mengandung nilai negatif.")

    # Peta operasi ke fungsi Python
    operasi = operasi.lower()
    operasi_map = {
        "sum": sum,
        "avg": lambda x: sum(x) / len(x),
        "max": max,
        "min": min
    }

    # Eksekusi
    if operasi in operasi_map:
        return operasi_map[operasi](arr)
    else:
        raise ValueError(f"Operasi '{operasi}' tidak dikenali. Gunakan 'sum', 'avg', 'max', atau 'min'.")
    
    
data = [10, 20, 30, 40]

print(arrayProcessor(data, "sum"))  # Output: 100
print(arrayProcessor(data, "avg"))  # Output: 25.0
print(arrayProcessor(data, "max"))  # Output: 40
print(arrayProcessor(data, "min"))  # Output: 10