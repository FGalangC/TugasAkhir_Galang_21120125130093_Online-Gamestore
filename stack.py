stack = []
stack.append("Mobil")
stack.append("Motor")
stack.append("Pesawat")
print(f"Data Stack setelah push: {stack}")

top_element = stack[-1]
print(f"Data teratas (peek): {top_element}")
if stack:
    popped_element = stack.pop()
print(f"Data yang di-pop: {popped_element}")
print(f"Data Stack setelah pop: {stack}")
if not stack:
    print("Stack sekarang kosong.")
print(f"Jumlah data dalam stack: {len(stack)}")