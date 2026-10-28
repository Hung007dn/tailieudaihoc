#Vũ Trọng Hưng-24162053

s = input("Nhập chuỗi: ")

digits = 0
upper = 0
lower = 0
special = 0

for ch in s:
    if ch.isdigit():
        digits += 1
    elif ch.isupper():
        upper += 1
    elif ch.islower():
        lower += 1
    else:
        special += 1

print("Ký tự số:", digits)
print("Chữ in hoa:", upper)
print("Chữ thường:", lower)
print("Ký tự đặc biệt:", special)
