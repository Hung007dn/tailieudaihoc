import math
a = float(input("Nhập số a: "))   
b = float(input("Nhập số b: "))
c = float(input("Nhập số c: "))
tu_so = -b + math.sqrt(b**2 - 4*a*c)
mau_so = 2*a
ket_qua = tu_so / mau_so

print(ket_qua)