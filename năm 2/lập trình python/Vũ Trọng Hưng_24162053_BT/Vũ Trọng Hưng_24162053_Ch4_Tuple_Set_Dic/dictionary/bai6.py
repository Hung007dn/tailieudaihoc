
s = input("Nhập chuỗi: ")

letters = sum(c.isalpha() for c in s)
digits = sum(c.isdigit() for c in s)

print(f"Số ký tự chữ: {letters}, số ký tự là số: {digits}")