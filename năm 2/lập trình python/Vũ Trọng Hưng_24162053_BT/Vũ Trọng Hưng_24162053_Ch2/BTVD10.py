#Vũ Trọng Hưng_24162053
a = float(input("Nhập vào số a: "))
b = float(input("Nhập vào số b: "))
c = float(input("Nhập vào số c: "))
d = float(input("Nhập vào số d: "))
e = float(input("Nhập vào số e: "))

so_duong = 0
so_am = 0
so_khong = 0

for num in [a, b, c, d, e]:
    if num > 0:
        so_duong += 1
    elif num < 0:
        so_am += 1
    else:
        so_khong += 1

print("Số dương:", so_duong)
print("Số âm:", so_am)
print("Số bằng 0:", so_khong)