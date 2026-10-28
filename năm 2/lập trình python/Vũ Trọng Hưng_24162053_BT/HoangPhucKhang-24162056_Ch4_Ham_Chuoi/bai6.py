#PhucKhang 24162056
s = input("Nhập chuỗi: ")

result = ""
for ch in s:
    if ch.islower():
        result += ch.upper()
    else:
        result += ch.lower()

print("Chuỗi sau khi chuyển đổi:", result)
