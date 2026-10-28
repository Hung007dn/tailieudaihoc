#Vũ Trọng Hung-24162053
import math
n=int(input("Nhập n: "))
hoan_vi=math.factorial(n)
print("Hoán vị của ",n,"=",hoan_vi)
k = int(input("Nhập k: "))
C = math.comb(n, k)
print(f"C({n}, {k}) = {C}")