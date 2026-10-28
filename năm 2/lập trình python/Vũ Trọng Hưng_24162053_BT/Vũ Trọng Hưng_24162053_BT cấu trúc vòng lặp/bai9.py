#Vũ Trọng Hưng-24162053
n = int(input('Nhập vào số n:'))

f1, f2 = 1, 1
tong = 0

for _ in range(n):
    if f1 % 3 == 0:
        tong += f1
    f1, f2 = f2, f1 + f2

print(tong)
