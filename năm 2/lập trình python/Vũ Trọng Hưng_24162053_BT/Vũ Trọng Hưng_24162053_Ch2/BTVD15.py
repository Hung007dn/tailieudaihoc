#Vũ Trọng Hưng_24162053
a = int(input("Nhập vào số a: "))
b = int(input("Nhập vào số b: "))
c = int(input("Nhập vào số c: "))

tong = a + b + c
lon_nhat = max(a, b, c)
nho_nhat = min(a, b, c)
lon_nhi = tong - lon_nhat - nho_nhat

print(lon_nhi)