#PhucKhang 24162056
s = input("Nhập chuỗi: ")

result = ""
for ch in s:
    if ch not in result:
        result += ch

print("Chuỗi sau khi loại bỏ trùng lặp:", result)
